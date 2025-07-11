"""
Vector Database for Learning Resources

A system to store and search web content and YouTube transcripts using Milvus vector database.
Extracts content, generates embeddings, and provides semantic search capabilities.
"""

import os
import re
import json
import hashlib
import logging
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from urllib.parse import urlparse, urljoin
import time

import requests
from bs4 import BeautifulSoup
from youtube_transcript_api import YouTubeTranscriptApi
from sentence_transformers import SentenceTransformer
import numpy as np
from pymilvus import (
    connections,
    utility,
    FieldSchema,
    CollectionSchema,
    DataType,
    Collection,
    MilvusException
)

# Import RAG chatbot
try:
    from rag_chatbot import RAGChatbot
    CHATBOT_AVAILABLE = True
except ImportError:
    CHATBOT_AVAILABLE = False
    RAGChatbot = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ContentChunk:
    """Represents a chunk of content with metadata."""
    id: str
    content: str
    source_url: str
    content_type: str  # 'web' or 'youtube'
    title: str
    chunk_index: int
    total_chunks: int
    timestamp: float
    metadata: Dict


@dataclass
class SearchResult:
    """Represents a search result with similarity score."""
    chunk: ContentChunk
    similarity: float


@dataclass
class ChatResponse:
    """Represents a chatbot response with sources."""
    answer: str
    sources: List[SearchResult]
    confidence: float
    query: str


class ContentExtractor:
    """Extracts content from web pages and YouTube videos."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def extract_web_content(self, url: str) -> Optional[Dict]:
        """Extract text content from a web page."""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()
            
            # Extract title
            title = soup.find('title')
            title_text = title.get_text().strip() if title else "No Title"
            
            # Extract main content
            content_selectors = [
                'main', 'article', '.content', '.post-content', 
                '.entry-content', '#content', '.tutorial-content'
            ]
            
            main_content = None
            for selector in content_selectors:
                main_content = soup.select_one(selector)
                if main_content:
                    break
            
            if not main_content:
                main_content = soup.find('body')
            
            if not main_content:
                return None
            
            # Extract text and clean it
            text = main_content.get_text()
            text = re.sub(r'\s+', ' ', text).strip()
            
            if len(text) < 100:  # Too short to be useful
                return None
            
            return {
                'title': title_text,
                'content': text,
                'url': url,
                'content_type': 'web',
                'metadata': {
                    'domain': urlparse(url).netloc,
                    'content_length': len(text)
                }
            }
            
        except Exception as e:
            logger.error(f"Error extracting web content from {url}: {e}")
            return None
    
    def extract_youtube_transcript(self, url: str) -> Optional[Dict]:
        """Extract transcript from a YouTube video."""
        try:
            # Extract video ID from URL
            video_id = self._extract_youtube_id(url)
            if not video_id:
                logger.error(f"Could not extract video ID from {url}")
                return None
            
            # Get transcript
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            
            # Try to get English transcript first
            transcript = None
            try:
                transcript = transcript_list.find_transcript(['en', 'en-US'])
            except:
                # If no English, get the first available
                try:
                    transcript = transcript_list.find_manually_created_transcript(['en'])
                except:
                    # Get auto-generated if no manual
                    available_transcripts = list(transcript_list)
                    if available_transcripts:
                        transcript = available_transcripts[0]
            
            if not transcript:
                logger.error(f"No transcript available for {url}")
                return None
            
            # Fetch transcript data
            transcript_data = transcript.fetch()
            
            # Combine transcript text - handle both dict and object formats
            full_text_parts = []
            for entry in transcript_data:
                if hasattr(entry, 'text'):
                    # FetchedTranscriptSnippet object
                    full_text_parts.append(entry.text)
                elif isinstance(entry, dict) and 'text' in entry:
                    # Dictionary format
                    full_text_parts.append(entry['text'])
                else:
                    # Try to convert to string as fallback
                    full_text_parts.append(str(entry))
            
            full_text = " ".join(full_text_parts)
            full_text = re.sub(r'\s+', ' ', full_text).strip()
            
            if len(full_text) < 50:  # Too short to be useful
                return None
            
            # Get video title (try to extract from page)
            title = self._get_youtube_title(url) or f"YouTube Video {video_id}"
            
            # Calculate duration safely
            duration = 0
            try:
                if transcript_data:
                    last_entry = transcript_data[-1]
                    if hasattr(last_entry, 'start') and hasattr(last_entry, 'duration'):
                        duration = last_entry.start + last_entry.duration
                    elif isinstance(last_entry, dict):
                        duration = last_entry.get('start', 0) + last_entry.get('duration', 0)
            except:
                duration = 0
            
            return {
                'title': title,
                'content': full_text,
                'url': url,
                'content_type': 'youtube',
                'metadata': {
                    'video_id': video_id,
                    'transcript_language': transcript.language_code if hasattr(transcript, 'language_code') else 'unknown',
                    'content_length': len(full_text),
                    'duration_seconds': duration
                }
            }
            
        except Exception as e:
            logger.error(f"Error extracting YouTube transcript from {url}: {e}")
            logger.debug(f"YouTube transcript error details: {type(e).__name__}: {str(e)}")
            return None
    
    def _extract_youtube_id(self, url: str) -> Optional[str]:
        """Extract YouTube video ID from URL."""
        patterns = [
            r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([^&\n?#]+)',
            r'youtube\.com/watch\?.*v=([^&\n?#]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
    
    def _get_youtube_title(self, url: str) -> Optional[str]:
        """Get YouTube video title."""
        try:
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Try multiple selectors for title
            title_selectors = [
                'meta[property="og:title"]',
                'meta[name="title"]',
                'title'
            ]
            
            for selector in title_selectors:
                element = soup.select_one(selector)
                if element:
                    title = element.get('content') or element.get_text()
                    if title and title.strip():
                        return title.strip()
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting YouTube title: {e}")
            return None


class VectorDatabase:
    """Milvus vector database for storing and searching content embeddings."""
    
    def __init__(self, 
                 host: str = "localhost", 
                 port: str = "19530",
                 collection_name: str = "learning_resources"):
        self.host = host
        self.port = port
        self.collection_name = collection_name
        self.collection = None
        
        # Initialize sentence transformer for embeddings
        logger.info("Loading sentence transformer model...")
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.embedding_dim = 384  # Dimension for all-MiniLM-L6-v2
        
        # Chunk settings
        self.chunk_size = 500  # Characters per chunk
        self.chunk_overlap = 50  # Overlap between chunks
    
    def connect(self):
        """Connect to Milvus database."""
        try:
            connections.connect(
                alias="default",
                host=self.host,
                port=self.port
            )
            logger.info(f"Connected to Milvus at {self.host}:{self.port}")
            
            # Create or load collection
            self._create_collection()
            
        except MilvusException as e:
            logger.error(f"Failed to connect to Milvus: {e}")
            raise
    
    def _create_collection(self):
        """Create or load the collection schema."""
        fields = [
            FieldSchema(name="id", dtype=DataType.VARCHAR, max_length=128, is_primary=True),
            FieldSchema(name="content", dtype=DataType.VARCHAR, max_length=10000),
            FieldSchema(name="source_url", dtype=DataType.VARCHAR, max_length=500),
            FieldSchema(name="content_type", dtype=DataType.VARCHAR, max_length=50),
            FieldSchema(name="title", dtype=DataType.VARCHAR, max_length=500),
            FieldSchema(name="chunk_index", dtype=DataType.INT64),
            FieldSchema(name="total_chunks", dtype=DataType.INT64),
            FieldSchema(name="timestamp", dtype=DataType.DOUBLE),
            FieldSchema(name="metadata", dtype=DataType.VARCHAR, max_length=2000),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=self.embedding_dim)
        ]
        
        schema = CollectionSchema(fields, f"Learning resources collection")
        
        # Check if collection exists and has compatible schema
        if utility.has_collection(self.collection_name):
            try:
                self.collection = Collection(self.collection_name)
                # Test if schema is compatible by checking field names
                collection_schema = self.collection.schema
                existing_fields = [field.name for field in collection_schema.fields]
                expected_fields = [field.name for field in fields]
                
                if set(existing_fields) != set(expected_fields):
                    logger.warning(f"Schema mismatch detected. Dropping existing collection.")
                    utility.drop_collection(self.collection_name)
                    self.collection = Collection(self.collection_name, schema)
                    logger.info(f"Created new collection with updated schema: {self.collection_name}")
                else:
                    logger.info(f"Loaded existing collection: {self.collection_name}")
                    
            except Exception as e:
                logger.warning(f"Error loading existing collection: {e}")
                logger.info("Creating new collection...")
                utility.drop_collection(self.collection_name)
                self.collection = Collection(self.collection_name, schema)
                logger.info(f"Created new collection: {self.collection_name}")
        else:
            self.collection = Collection(self.collection_name, schema)
            logger.info(f"Created new collection: {self.collection_name}")
        
        # Create index on embedding field
        index_params = {
            "metric_type": "COSINE",
            "index_type": "IVF_FLAT",
            "params": {"nlist": 128}
        }
        
        if not self.collection.has_index():
            self.collection.create_index("embedding", index_params)
            logger.info("Created index on embedding field")
        
        # Load collection
        self.collection.load()
    
    def _chunk_text(self, text: str) -> List[str]:
        """Split text into overlapping chunks."""
        if len(text) <= self.chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self.chunk_size
            
            # Try to break at sentence boundary
            if end < len(text):
                # Look for sentence endings
                for punct in ['. ', '! ', '? ', '\n\n']:
                    last_punct = text.rfind(punct, start, end)
                    if last_punct > start + self.chunk_size // 2:
                        end = last_punct + len(punct)
                        break
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = end - self.chunk_overlap
            
            if start >= len(text):
                break
        
        return chunks
    
    def _generate_id(self, content: str, source_url: str, chunk_index: int) -> str:
        """Generate unique ID for content chunk."""
        content_hash = hashlib.md5(f"{source_url}:{chunk_index}:{content[:100]}".encode()).hexdigest()
        return f"{content_hash}_{chunk_index}"
    
    def add_content(self, content_data: Dict) -> bool:
        """Add content to the vector database."""
        try:
            # Chunk the content
            chunks = self._chunk_text(content_data['content'])
            
            if not chunks:
                logger.warning(f"No chunks generated for {content_data['url']}")
                return False
            
            # Prepare data for insertion
            ids = []
            contents = []
            source_urls = []
            content_types = []
            titles = []
            chunk_indices = []
            total_chunks = []
            timestamps = []
            metadatas = []
            embeddings = []
            
            current_time = time.time()
            
            for i, chunk in enumerate(chunks):
                # Generate embedding
                embedding = self.model.encode(chunk).tolist()
                
                # Create chunk data
                chunk_id = self._generate_id(chunk, content_data['url'], i)
                
                ids.append(chunk_id)
                contents.append(chunk)
                source_urls.append(content_data['url'])
                content_types.append(content_data['content_type'])
                titles.append(content_data['title'])
                chunk_indices.append(i)
                total_chunks.append(len(chunks))
                timestamps.append(current_time)
                metadatas.append(json.dumps(content_data.get('metadata', {})))
                embeddings.append(embedding)
            
            # Insert into collection
            data = [
                ids, contents, source_urls, content_types, titles,
                chunk_indices, total_chunks, timestamps, metadatas, embeddings
            ]
            
            self.collection.insert(data)
            self.collection.flush()
            
            logger.info(f"Added {len(chunks)} chunks from {content_data['url']}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding content to database: {e}")
            return False
    
    def search(self, query: str, limit: int = 5, content_type: str = None) -> List[SearchResult]:
        """Search for similar content."""
        try:
            # Generate query embedding
            query_embedding = self.model.encode(query).tolist()
            
            # Prepare search parameters
            search_params = {"metric_type": "COSINE", "params": {"nprobe": 10}}
            
            # Add filter if content type specified
            filter_expr = None
            if content_type:
                filter_expr = f'content_type == "{content_type}"'
            
            # Perform search
            results = self.collection.search(
                data=[query_embedding],
                anns_field="embedding",
                param=search_params,
                limit=limit,
                expr=filter_expr,
                output_fields=["content", "source_url", "content_type", "title", 
                              "chunk_index", "total_chunks", "timestamp", "metadata"]
            )
            
            # Process results
            search_results = []
            for hit in results[0]:
                chunk = ContentChunk(
                    id=hit.id,
                    content=hit.entity.get('content'),
                    source_url=hit.entity.get('source_url'),
                    content_type=hit.entity.get('content_type'),
                    title=hit.entity.get('title'),
                    chunk_index=hit.entity.get('chunk_index'),
                    total_chunks=hit.entity.get('total_chunks'),
                    timestamp=hit.entity.get('timestamp'),
                    metadata=json.loads(hit.entity.get('metadata', '{}'))
                )
                
                search_results.append(SearchResult(
                    chunk=chunk,
                    similarity=hit.score
                ))
            
            return search_results
            
        except Exception as e:
            logger.error(f"Error searching database: {e}")
            return []
    
    def get_collection_stats(self) -> Dict:
        """Get statistics about the collection."""
        try:
            stats = self.collection.num_entities
            return {
                'total_chunks': stats,
                'collection_name': self.collection_name
            }
        except Exception as e:
            logger.error(f"Error getting collection stats: {e}")
            return {}
    
    def delete_by_url(self, source_url: str) -> bool:
        """Delete all chunks from a specific URL."""
        try:
            expr = f'source_url == "{source_url}"'
            self.collection.delete(expr)
            self.collection.flush()
            logger.info(f"Deleted content from {source_url}")
            return True
        except Exception as e:
            logger.error(f"Error deleting content: {e}")
            return False


class LearningResourceVectorDB:
    """Main class for managing learning resource vector database."""
    
    def __init__(self, milvus_host: str = "localhost", milvus_port: str = "19530"):
        self.extractor = ContentExtractor()
        self.vector_db = VectorDatabase(milvus_host, milvus_port)
        self.chatbot = None
    
    def initialize(self):
        """Initialize the vector database connection."""
        self.vector_db.connect()
        
        # Initialize chatbot
        self.chatbot = None
        if CHATBOT_AVAILABLE:
            try:
                self.chatbot = RAGChatbot(self.vector_db)
                logger.info("RAG Chatbot initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize chatbot: {e}")
        else:
            logger.warning("Chatbot not available. Install rag_chatbot module.")
            
        logger.info("Learning Resource Vector Database initialized successfully")
    
    def process_urls(self, urls: List[str]) -> Dict:
        """Process a list of URLs and add to vector database."""
        results = {
            'processed': 0,
            'failed': 0,
            'skipped': 0,
            'details': []
        }
        
        for url in urls:
            try:
                logger.info(f"Processing URL: {url}")
                
                # Determine content type and extract
                if 'youtube.com' in url or 'youtu.be' in url:
                    content_data = self.extractor.extract_youtube_transcript(url)
                else:
                    content_data = self.extractor.extract_web_content(url)
                
                if content_data:
                    # Add to vector database
                    if self.vector_db.add_content(content_data):
                        results['processed'] += 1
                        results['details'].append({
                            'url': url,
                            'status': 'success',
                            'title': content_data['title'],
                            'content_length': len(content_data['content'])
                        })
                    else:
                        results['failed'] += 1
                        results['details'].append({
                            'url': url,
                            'status': 'failed',
                            'error': 'Could not add to database'
                        })
                else:
                    results['skipped'] += 1
                    results['details'].append({
                        'url': url,
                        'status': 'skipped',
                        'error': 'Could not extract content'
                    })
                
                # Small delay to be respectful
                time.sleep(1)
                
            except Exception as e:
                results['failed'] += 1
                results['details'].append({
                    'url': url,
                    'status': 'error',
                    'error': str(e)
                })
        
        return results
    
    def search_resources(self, query: str, limit: int = 5, content_type: str = None) -> List[SearchResult]:
        """Search for learning resources."""
        return self.vector_db.search(query, limit, content_type)
    
    def get_stats(self) -> Dict:
        """Get database statistics."""
        return self.vector_db.get_collection_stats()
    
    def ask_question(self, question: str, max_sources: int = 3) -> ChatResponse:
        """Ask a question about the stored content."""
        if not self.chatbot:
            raise RuntimeError("Database not initialized. Call initialize() first.")
        return self.chatbot.ask(question, max_sources)
    
    def start_chat(self):
        """Start an interactive chat session."""
        if not self.chatbot:
            raise RuntimeError("Database not initialized. Call initialize() first.")
        self.chatbot.chat_session()
    
    def add_resource(self, url: str, title: str = None) -> bool:
        """Add a single resource to the database."""
        try:
            logger.info(f"Adding resource: {url}")
            
            # Determine content type and extract
            if 'youtube.com' in url or 'youtu.be' in url:
                content_data = self.extractor.extract_youtube_transcript(url)
            else:
                content_data = self.extractor.extract_web_content(url)
            
            if content_data:
                # Override title if provided
                if title:
                    content_data['title'] = title
                
                # Add to vector database
                success = self.vector_db.add_content(content_data)
                if success:
                    logger.info(f"Successfully added: {content_data['title']}")
                return success
            else:
                logger.warning(f"Could not extract content from {url}")
                return False
                
        except Exception as e:
            logger.error(f"Error adding resource {url}: {e}")
            return False


# Convenience function for external use
def create_learning_vector_db(milvus_host: str = "localhost", milvus_port: str = "19530") -> LearningResourceVectorDB:
    """Create and initialize a learning resource vector database."""
    db = LearningResourceVectorDB(milvus_host, milvus_port)
    db.initialize()
    return db

if __name__ == "__main__":
    # Example usage
    print("Learning Resource Vector Database")
    print("Note: Make sure Milvus standalone is running on localhost:19530")
    
    try:
        # Initialize database
        db = create_learning_vector_db()
        
        # Example URLs (you can replace with actual URLs)
        test_urls = [
            "https://realpython.com/pandas-python-explore-dataset/",
            "https://youtube.com/watch?v=vmEHCJofslg"  # Example YouTube URL
        ]
        
        print(f"\nProcessing {len(test_urls)} URLs...")
        results = db.process_urls(test_urls)
        
        print(f"\nProcessing Results:")
        print(f"Processed: {results['processed']}")
        print(f"Failed: {results['failed']}")
        print(f"Skipped: {results['skipped']}")
        
        # Example search
        print(f"\nSearching for 'pandas dataframe'...")
        search_results = db.search_resources("pandas dataframe", limit=3)
        
        for i, result in enumerate(search_results, 1):
            print(f"\n{i}. {result.chunk.title}")
            print(f"   URL: {result.chunk.source_url}")
            print(f"   Type: {result.chunk.content_type}")
            print(f"   Similarity: {result.similarity:.3f}")
            print(f"   Content preview: {result.chunk.content[:200]}...")
        
        # Get stats
        stats = db.get_stats()
        print(f"\nDatabase Stats: {stats}")
        
        # Example chatbot interaction
        print("\nStarting chatbot interaction...")
        db.start_chat()
        
    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure Milvus standalone is running. See setup instructions.")
