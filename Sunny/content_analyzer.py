"""
Content Analyzer and Summary Generator for Vector Database

This module analyzes stored learning content and generates structured summaries
with knowledge relationships for frontend display.
"""

import json
import re
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass
from collections import defaultdict, Counter
import numpy as np
from vector_database import create_learning_vector_db
from langchain_together import Together
from langchain_core.prompts import PromptTemplate
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@dataclass
class ContentSummary:
    """Summary of content from a single source."""
    source_url: str
    title: str
    content_type: str
    key_topics: List[str]
    main_concepts: List[str]
    learning_objectives: List[str]
    difficulty_level: str
    estimated_time: str
    summary: str
    chunk_count: int


@dataclass
class KnowledgeRelationship:
    """Relationship between knowledge concepts."""
    source_concept: str
    target_concept: str
    relationship_type: str  # 'prerequisite', 'builds_on', 'related_to', 'applies_to'
    strength: float  # 0.0 to 1.0
    source_urls: List[str]


@dataclass
class DatabaseSummary:
    """Complete summary of the vector database content."""
    total_sources: int
    content_summaries: List[ContentSummary]
    knowledge_map: List[KnowledgeRelationship]
    topic_clusters: Dict[str, List[str]]
    learning_paths: List[List[str]]
    generated_at: str


class ContentAnalyzer:
    """Analyzes content stored in vector database and generates summaries."""
    
    def __init__(self):
        self.db = None
        self.llm = None
        self._initialize_llm()
    
    def _initialize_llm(self):
        """Initialize the LLM for content analysis."""
        try:
            together_api_key = os.getenv("TOGETHER_API_KEY")
            if together_api_key:
                self.llm = Together(
                    model="mistralai/Mixtral-8x7B-Instruct-v0.1",
                    together_api_key=together_api_key,
                    max_tokens=1000
                )
        except Exception as e:
            print(f"Warning: Could not initialize LLM: {e}")
    
    def connect_database(self):
        """Connect to the vector database."""
        try:
            self.db = create_learning_vector_db()
            print("✅ Connected to vector database")
            return True
        except Exception as e:
            print(f"❌ Failed to connect to vector database: {e}")
            return False
    
    def get_all_sources(self, limit: int = 100) -> Dict[str, List]:
        """Get all unique sources and their content chunks."""
        if not self.db:
            return {}
        
        try:
            # Search for all content with a broad query
            all_results = self.db.search_resources("tutorial guide learning", limit=limit)
            
            # Group by source URL
            sources = defaultdict(list)
            for result in all_results:
                sources[result.chunk.source_url].append(result.chunk)
            
            return dict(sources)
            
        except Exception as e:
            print(f"Error getting sources: {e}")
            return {}
    
    def analyze_source_content(self, url: str, chunks: List) -> ContentSummary:
        """Analyze content from a single source and generate summary."""
        
        # Combine all chunks for this source
        full_content = " ".join([chunk.content for chunk in chunks])
        title = chunks[0].title if chunks else "Unknown Title"
        content_type = chunks[0].content_type if chunks else "unknown"
        
        # Extract key information using text analysis
        key_topics = self._extract_key_topics(full_content)
        main_concepts = self._extract_main_concepts(full_content)
        
        # Use LLM for advanced analysis if available
        if self.llm:
            llm_analysis = self._llm_analyze_content(full_content, title)
            learning_objectives = llm_analysis.get('learning_objectives', [])
            difficulty_level = llm_analysis.get('difficulty_level', 'Intermediate')
            estimated_time = llm_analysis.get('estimated_time', '30-60 minutes')
            summary = llm_analysis.get('summary', self._generate_basic_summary(full_content))
        else:
            learning_objectives = self._extract_learning_objectives(full_content)
            difficulty_level = self._estimate_difficulty(full_content)
            estimated_time = self._estimate_time(full_content)
            summary = self._generate_basic_summary(full_content)
        
        return ContentSummary(
            source_url=url,
            title=title,
            content_type=content_type,
            key_topics=key_topics,
            main_concepts=main_concepts,
            learning_objectives=learning_objectives,
            difficulty_level=difficulty_level,
            estimated_time=estimated_time,
            summary=summary,
            chunk_count=len(chunks)
        )
    
    def _llm_analyze_content(self, content: str, title: str) -> Dict:
        """Use LLM to analyze content and extract structured information."""
        
        prompt_template = PromptTemplate.from_template(
            """
            Analyze this educational content and extract structured information:
            
            Title: {title}
            Content: {content}
            
            Please provide a JSON response with:
            1. learning_objectives: 3-5 specific learning objectives
            2. difficulty_level: Beginner, Intermediate, or Advanced
            3. estimated_time: How long to complete (e.g., "30-45 minutes")
            4. summary: 2-3 sentence summary of what this content teaches
            
            Format as valid JSON:
            {{
                "learning_objectives": ["objective1", "objective2", "objective3"],
                "difficulty_level": "Intermediate",
                "estimated_time": "45 minutes",
                "summary": "Brief summary of the content..."
            }}
            """
        )
        
        try:
            # Truncate content if too long
            truncated_content = content[:2000] + "..." if len(content) > 2000 else content
            
            prompt = prompt_template.format(title=title, content=truncated_content)
            response = self.llm.invoke(prompt)
            
            # Extract JSON from response
            json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', str(response))
            if json_match:
                return json.loads(json_match.group())
            
        except Exception as e:
            print(f"LLM analysis error: {e}")
        
        return {}
    
    def _extract_key_topics(self, content: str) -> List[str]:
        """Extract key topics from content using keyword analysis."""
        
        # Common technical keywords to look for
        tech_keywords = [
            'python', 'javascript', 'react', 'vue', 'angular', 'node.js', 'express',
            'django', 'flask', 'fastapi', 'pandas', 'numpy', 'matplotlib', 'tensorflow',
            'pytorch', 'scikit-learn', 'docker', 'kubernetes', 'aws', 'azure', 'gcp',
            'mongodb', 'postgresql', 'mysql', 'redis', 'elasticsearch', 'git', 'github',
            'api', 'rest', 'graphql', 'microservices', 'database', 'sql', 'nosql',
            'machine learning', 'data science', 'artificial intelligence', 'deep learning',
            'web development', 'frontend', 'backend', 'fullstack', 'devops', 'cloud'
        ]
        
        content_lower = content.lower()
        found_topics = []
        
        for keyword in tech_keywords:
            if keyword in content_lower:
                # Count occurrences to prioritize important topics
                count = content_lower.count(keyword)
                if count >= 2:  # Must appear at least twice
                    found_topics.append((keyword, count))
        
        # Sort by frequency and return top topics
        found_topics.sort(key=lambda x: x[1], reverse=True)
        return [topic[0] for topic in found_topics[:5]]
    
    def _extract_main_concepts(self, content: str) -> List[str]:
        """Extract main concepts being taught."""
        
        # Look for patterns that indicate concepts
        concept_patterns = [
            r'learn (?:about )?(\w+(?:\s+\w+){0,2})',
            r'understand (\w+(?:\s+\w+){0,2})',
            r'how to (\w+(?:\s+\w+){0,2})',
            r'introduction to (\w+(?:\s+\w+){0,2})',
            r'getting started with (\w+(?:\s+\w+){0,2})',
            r'basics of (\w+(?:\s+\w+){0,2})',
            r'fundamentals of (\w+(?:\s+\w+){0,2})'
        ]
        
        concepts = set()
        content_lower = content.lower()
        
        for pattern in concept_patterns:
            matches = re.findall(pattern, content_lower, re.IGNORECASE)
            for match in matches:
                if len(match.split()) <= 3:  # Keep concepts concise
                    concepts.add(match.strip())
        
        return list(concepts)[:6]
    
    def _extract_learning_objectives(self, content: str) -> List[str]:
        """Extract learning objectives from content."""
        
        # Look for common learning objective patterns
        objective_patterns = [
            r'(?:after|by) (?:reading|completing) this.*?you will (?:be able to )?(\w+.*?)(?:\.|$)',
            r'this tutorial (?:will )?(?:teach|show|help) you (?:how )?to (\w+.*?)(?:\.|$)',
            r'you will learn (?:how )?to (\w+.*?)(?:\.|$)',
            r'learn to (\w+.*?)(?:\.|$)'
        ]
        
        objectives = set()
        
        for pattern in objective_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE | re.DOTALL)
            for match in matches:
                clean_objective = re.sub(r'\s+', ' ', match.strip())[:100]
                if len(clean_objective.split()) >= 3:
                    objectives.add(clean_objective)
        
        return list(objectives)[:4]
    
    def _estimate_difficulty(self, content: str) -> str:
        """Estimate difficulty level based on content complexity."""
        
        beginner_indicators = ['beginner', 'introduction', 'getting started', 'basics', 'fundamentals']
        advanced_indicators = ['advanced', 'expert', 'optimization', 'performance', 'architecture']
        
        content_lower = content.lower()
        
        beginner_score = sum(1 for indicator in beginner_indicators if indicator in content_lower)
        advanced_score = sum(1 for indicator in advanced_indicators if indicator in content_lower)
        
        if beginner_score > advanced_score:
            return "Beginner"
        elif advanced_score > beginner_score:
            return "Advanced"
        else:
            return "Intermediate"
    
    def _estimate_time(self, content: str) -> str:
        """Estimate time to complete based on content length."""
        
        words = len(content.split())
        
        if words < 500:
            return "15-30 minutes"
        elif words < 1500:
            return "30-60 minutes"
        elif words < 3000:
            return "1-2 hours"
        else:
            return "2+ hours"
    
    def _generate_basic_summary(self, content: str) -> str:
        """Generate a basic summary without LLM."""
        
        # Take first few sentences as summary
        sentences = re.split(r'[.!?]+', content)
        clean_sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
        
        summary = '. '.join(clean_sentences[:3])
        if len(summary) > 300:
            summary = summary[:300] + "..."
        
        return summary
    
    def analyze_knowledge_relationships(self, summaries: List[ContentSummary]) -> List[KnowledgeRelationship]:
        """Analyze relationships between knowledge concepts across sources."""
        
        relationships = []
        
        # Extract all concepts from all sources
        all_concepts = []
        concept_to_sources = defaultdict(list)
        
        for summary in summaries:
            concepts = summary.key_topics + summary.main_concepts
            for concept in concepts:
                all_concepts.append(concept)
                concept_to_sources[concept].append(summary.source_url)
        
        # Find concept relationships
        concept_pairs = []
        for i, concept1 in enumerate(all_concepts):
            for j, concept2 in enumerate(all_concepts[i+1:], i+1):
                if concept1 != concept2:
                    # Calculate relationship strength based on co-occurrence
                    common_sources = set(concept_to_sources[concept1]) & set(concept_to_sources[concept2])
                    strength = len(common_sources) / max(len(concept_to_sources[concept1]), len(concept_to_sources[concept2]))
                    
                    if strength > 0.3:  # Only include strong relationships
                        relationship_type = self._determine_relationship_type(concept1, concept2)
                        relationships.append(KnowledgeRelationship(
                            source_concept=concept1,
                            target_concept=concept2,
                            relationship_type=relationship_type,
                            strength=strength,
                            source_urls=list(common_sources)
                        ))
        
        return relationships
    
    def _determine_relationship_type(self, concept1: str, concept2: str) -> str:
        """Determine the type of relationship between concepts."""
        
        # Simple heuristics for relationship types
        prerequisite_pairs = [
            ('python', 'django'), ('python', 'flask'), ('python', 'fastapi'),
            ('javascript', 'react'), ('javascript', 'vue'), ('javascript', 'angular'),
            ('html', 'css'), ('css', 'javascript'),
            ('sql', 'database'), ('git', 'github')
        ]
        
        for prereq, advanced in prerequisite_pairs:
            if (prereq in concept1.lower() and advanced in concept2.lower()) or \
               (prereq in concept2.lower() and advanced in concept1.lower()):
                return 'prerequisite'
        
        # Default to related_to
        return 'related_to'
    
    def generate_topic_clusters(self, summaries: List[ContentSummary]) -> Dict[str, List[str]]:
        """Group related topics into clusters."""
        
        clusters = defaultdict(list)
        
        for summary in summaries:
            # Determine primary cluster based on key topics
            primary_topic = None
            
            if any('python' in topic for topic in summary.key_topics):
                primary_topic = 'Python Development'
            elif any(topic in ['javascript', 'react', 'vue', 'angular'] for topic in summary.key_topics):
                primary_topic = 'Frontend Development'
            elif any(topic in ['docker', 'kubernetes', 'aws', 'devops'] for topic in summary.key_topics):
                primary_topic = 'DevOps & Cloud'
            elif any(topic in ['machine learning', 'data science', 'pandas', 'numpy'] for topic in summary.key_topics):
                primary_topic = 'Data Science & ML'
            elif any(topic in ['database', 'sql', 'mongodb', 'postgresql'] for topic in summary.key_topics):
                primary_topic = 'Databases'
            else:
                primary_topic = 'General Programming'
            
            clusters[primary_topic].append(summary.source_url)
        
        return dict(clusters)
    
    def generate_learning_paths(self, summaries: List[ContentSummary]) -> List[List[str]]:
        """Generate suggested learning paths based on difficulty and prerequisites."""
        
        paths = []
        
        # Group by difficulty
        by_difficulty = defaultdict(list)
        for summary in summaries:
            by_difficulty[summary.difficulty_level].append(summary)
        
        # Create paths for each topic cluster
        clusters = self.generate_topic_clusters(summaries)
        
        for cluster_name, urls in clusters.items():
            cluster_summaries = [s for s in summaries if s.source_url in urls]
            
            # Sort by difficulty: Beginner -> Intermediate -> Advanced
            difficulty_order = {'Beginner': 0, 'Intermediate': 1, 'Advanced': 2}
            cluster_summaries.sort(key=lambda x: difficulty_order.get(x.difficulty_level, 1))
            
            if len(cluster_summaries) >= 2:
                path = [s.source_url for s in cluster_summaries]
                paths.append(path)
        
        return paths
    
    def generate_complete_summary(self, limit: int = 100) -> Optional[DatabaseSummary]:
        """Generate complete summary of the vector database content."""
        
        if not self.connect_database():
            return None
        
        print("🔍 Analyzing vector database content...")
        
        # Get all sources with limit
        sources = self.get_all_sources(limit=limit)
        
        if not sources:
            print("❌ No content found in database")
            return None
        
        print(f"📚 Found {len(sources)} sources to analyze")
        
        # Analyze each source
        content_summaries = []
        for url, chunks in sources.items():
            print(f"📖 Analyzing: {url}")
            summary = self.analyze_source_content(url, chunks)
            content_summaries.append(summary)
        
        # Analyze relationships
        print("🔗 Analyzing knowledge relationships...")
        knowledge_map = self.analyze_knowledge_relationships(content_summaries)
        
        # Generate clusters and paths
        print("🎯 Generating topic clusters and learning paths...")
        topic_clusters = self.generate_topic_clusters(content_summaries)
        learning_paths = self.generate_learning_paths(content_summaries)
        
        from datetime import datetime
        
        return DatabaseSummary(
            total_sources=len(sources),
            content_summaries=content_summaries,
            knowledge_map=knowledge_map,
            topic_clusters=topic_clusters,
            learning_paths=learning_paths,
            generated_at=datetime.now().isoformat()
        )


def main():
    """Test the content analyzer."""
    
    print("🚀 CONTENT ANALYZER TEST")
    print("=" * 40)
    
    analyzer = ContentAnalyzer()
    summary = analyzer.generate_complete_summary()
    
    if summary:
        print(f"\n📊 ANALYSIS COMPLETE")
        print(f"Total sources: {summary.total_sources}")
        print(f"Content summaries: {len(summary.content_summaries)}")
        print(f"Knowledge relationships: {len(summary.knowledge_map)}")
        print(f"Topic clusters: {len(summary.topic_clusters)}")
        print(f"Learning paths: {len(summary.learning_paths)}")
        
        print(f"\n📚 CONTENT SUMMARIES:")
        for i, content in enumerate(summary.content_summaries, 1):
            print(f"\n{i}. {content.title}")
            print(f"   🔗 {content.source_url}")
            print(f"   📝 Type: {content.content_type}")
            print(f"   🎯 Topics: {', '.join(content.key_topics[:3])}")
            print(f"   📊 Difficulty: {content.difficulty_level}")
            print(f"   ⏱️  Time: {content.estimated_time}")
        
        print(f"\n🔗 KNOWLEDGE RELATIONSHIPS:")
        for rel in summary.knowledge_map[:5]:  # Show first 5
            print(f"   {rel.source_concept} --{rel.relationship_type}--> {rel.target_concept} (strength: {rel.strength:.2f})")
        
        print(f"\n🎯 TOPIC CLUSTERS:")
        for cluster, urls in summary.topic_clusters.items():
            print(f"   {cluster}: {len(urls)} resources")
        
        return summary
    else:
        print("❌ Failed to generate summary")
        return None


if __name__ == "__main__":
    main()
