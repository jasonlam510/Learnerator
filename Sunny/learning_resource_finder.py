"""
Learning Resource Finder Tool

A tool for finding educational resources including basics tutorials and demonstration videos
for any given topic and project purpose. Designed to be used by agentic LLMs.
"""

import json
import os
import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from langchain_together import Together
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@dataclass
class SearchConfig:
    """Configuration for the learning resource finder."""
    max_results: int = 3
    max_websites: int = 3
    max_youtube_channels: int = 2
    max_domains: int = 4
    llm_max_tokens: int = 500
    

@dataclass
class ResourceSources:
    """Container for resource sources from LLM recommendations."""
    websites: List[str]
    youtube_channels: List[str]


@dataclass
class SearchResult:
    """Container for search results."""
    urls: List[str]
    has_basics_tutorial: bool
    has_youtube_demo: bool
    error: Optional[str] = None


class LearningResourceFinder:
    """
    A tool for finding educational resources for any topic and project purpose.
    
    This tool ensures that results include:
    1. At least one tutorial that introduces the basics of the topic
    2. At least one YouTube video that demonstrates practical usage
    """
    
    def __init__(self, config: Optional[SearchConfig] = None):
        """Initialize the learning resource finder."""
        self.config = config or SearchConfig()
        self._load_api_credentials()
        self._initialize_services()
    
    def _load_api_credentials(self) -> None:
        """Load API credentials from environment variables."""
        self.together_api_key = os.getenv("TOGETHER_API_KEY")
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        self.cse_id = os.getenv("GOOGLE_CSE_ID")
        
        if not all([self.together_api_key, self.google_api_key, self.cse_id]):
            raise ValueError("Missing required API credentials in environment variables")
    
    def _initialize_services(self) -> None:
        """Initialize external services."""
        self.llm = Together(
            model="mistralai/Mixtral-8x7B-Instruct-v0.1",
            together_api_key=self.together_api_key,
            max_tokens=self.config.llm_max_tokens
        )
        
        self.search_service = build('customsearch', 'v1', developerKey=self.google_api_key)
    
    def _query_llm_for_sources(self, topic: str, project_purpose: str) -> ResourceSources:
        """Query LLM for recommended learning sources."""
        prompt_template = PromptTemplate.from_template(
            """
            What are the best free tutorial websites and YouTube channels to learn {topic} for the following project: {project_purpose}? 
            
            I need:
            1. Tutorial websites (like GeeksforGeeks, Real Python, freeCodeCamp) that have beginner-friendly introductions and basics
            2. YouTube channels that demonstrate practical usage and examples
            
            Exclude course-based platforms like Coursera, edX, or Khan Academy. 
            Return the response in JSON format with fields: websites, youtube_channels, each containing a list of domains or URLs.
            
            Example format:
            {{
                "websites": ["realpython.com", "geeksforgeeks.org"],
                "youtube_channels": ["youtube.com/@coreyms", "youtube.com/@sentdex"]
            }}
            """
        )
        
        try:
            prompt = prompt_template.format(topic=topic, project_purpose=project_purpose)
            response = self.llm.invoke(prompt)
            
            # Parse JSON from response
            sources_data = self._extract_json_from_response(str(response))
            
            return ResourceSources(
                websites=sources_data.get('websites', []),
                youtube_channels=sources_data.get('youtube_channels', [])
            )
            
        except Exception as e:
            print(f"LLM query error: {e}")
            # Return fallback sources
            return ResourceSources(
                websites=['geeksforgeeks.org', 'freecodecamp.org', 'realpython.com'],
                youtube_channels=['youtube.com/@coreyms', 'youtube.com/@sentdex']
            )
    
    def _extract_json_from_response(self, response_text: str) -> Dict:
        """Extract JSON data from LLM response text."""
        try:
            # Look for all JSON blocks in the response
            json_blocks = re.findall(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', response_text)
            
            # Try to parse each JSON block until we find a valid one
            for json_str in json_blocks:
                try:
                    sources = json.loads(json_str)
                    if 'websites' in sources or 'youtube_channels' in sources:
                        return sources
                except json.JSONDecodeError:
                    continue
            
            raise json.JSONDecodeError("No valid JSON found", response_text, 0)
            
        except json.JSONDecodeError:
            print(f"Error: LLM response is not valid JSON: {response_text}")
            return {'websites': [], 'youtube_channels': []}
    
    def _extract_domains(self, sources: ResourceSources) -> Tuple[List[str], List[str]]:
        """Extract and process domains from LLM sources."""
        # Process website domains
        key_domains = []
        for website in sources.websites[:self.config.max_websites]:
            if isinstance(website, str):
                domain = website.replace('https://', '').replace('http://', '').split('/')[0]
                key_domains.append(domain)
        
        # Process YouTube channels
        youtube_channels = []
        for channel in sources.youtube_channels[:self.config.max_youtube_channels]:
            if isinstance(channel, str) and 'youtube.com' in channel:
                youtube_channels.append(channel)
        
        # Add fallback domains
        fallback_domains = ['geeksforgeeks.org', 'freecodecamp.org', 'realpython.com']
        for domain in fallback_domains:
            if len(key_domains) >= self.config.max_domains:
                break
            if domain not in key_domains:
                key_domains.append(domain)
        
        return list(dict.fromkeys(key_domains))[:self.config.max_domains], youtube_channels
    
    def _search_basics_tutorial(self, topic: str, domains: List[str]) -> Optional[str]:
        """Search for a basics/introduction tutorial."""
        for domain in domains:
            query = f'{topic} basics introduction tutorial beginner site:{domain}'
            
            try:
                result = self.search_service.cse().list(
                    q=query,
                    cx=self.cse_id,
                    num=3
                ).execute()
                
                if 'items' in result:
                    for item in result['items']:
                        url = item.get('link')
                        title = item.get('title', '').lower()
                        snippet = item.get('snippet', '').lower()
                        
                        if url and self._is_valid_basics_tutorial(url, title, snippet):
                            print(f"Found basics tutorial: {url}")
                            return url
                            
            except HttpError as e:
                print(f"Search error for basics tutorial on {domain}: {e}")
                continue
        
        return None
    
    def _search_youtube_demo(self, topic: str, youtube_channels: List[str]) -> Optional[str]:
        """Search for a YouTube demonstration video."""
        youtube_domains = [domain for domain in youtube_channels if 'youtube.com' in domain] + ['youtube.com']
        
        for domain in youtube_domains:
            query = f'{topic} demo demonstration tutorial example site:{domain}'
            
            try:
                result = self.search_service.cse().list(
                    q=query,
                    cx=self.cse_id,
                    num=5
                ).execute()
                
                if 'items' in result:
                    for item in result['items']:
                        url = item.get('link')
                        title = item.get('title', '').lower()
                        snippet = item.get('snippet', '').lower()
                        
                        if url and self._is_valid_youtube_demo(url, title, snippet):
                            print(f"Found YouTube demo: {url}")
                            return url
                            
            except HttpError as e:
                print(f"Search error for YouTube demo: {e}")
                continue
        
        return None
    
    def _search_additional_resources(self, topic: str, domains: List[str], current_urls: List[str], needed: int) -> List[str]:
        """Search for additional tutorial resources."""
        additional_urls = []
        
        for domain in domains:
            if len(additional_urls) >= needed:
                break
                
            query = f'{topic} tutorial site:{domain}'
            
            try:
                result = self.search_service.cse().list(
                    q=query,
                    cx=self.cse_id,
                    num=min(needed - len(additional_urls), 2)
                ).execute()
                
                if 'items' in result:
                    for item in result['items']:
                        if len(additional_urls) >= needed:
                            break
                        
                        url = item.get('link')
                        title = item.get('title', '').lower()
                        snippet = item.get('snippet', '').lower()
                        
                        if url and url not in current_urls and self._is_valid_tutorial(url, title, snippet):
                            additional_urls.append(url)
                            
            except HttpError as e:
                print(f"Search error for domain {domain}: {e}")
                continue
        
        return additional_urls
    
    def _is_valid_basics_tutorial(self, url: str, title: str, snippet: str) -> bool:
        """Check if a URL is a valid basics tutorial."""
        basics_terms = ['basics', 'introduction', 'beginner', 'getting started', 'tutorial']
        excluded_terms = ['login', 'signup', 'pay', 'subscribe']
        
        return (
            any(term in title or term in snippet for term in basics_terms) and
            all(term not in url.lower() for term in excluded_terms) and
            'youtube.com' not in url
        )
    
    def _is_valid_youtube_demo(self, url: str, title: str, snippet: str) -> bool:
        """Check if a URL is a valid YouTube demonstration."""
        demo_terms = ['demo', 'demonstration', 'example', 'tutorial', 'how to']
        excluded_terms = ['login', 'signup', 'pay', 'subscribe']
        
        return (
            'youtube.com' in url and '/watch' in url and
            any(term in title or term in snippet for term in demo_terms) and
            all(term not in url.lower() for term in excluded_terms)
        )
    
    def _is_valid_tutorial(self, url: str, title: str, snippet: str) -> bool:
        """Check if a URL is a valid tutorial."""
        tutorial_terms = ['tutorial', 'learn', 'guide', 'how to']
        excluded_terms = ['login', 'signup', 'pay', 'subscribe']
        
        return (
            any(term in title or term in snippet for term in tutorial_terms) and
            all(term not in url.lower() for term in excluded_terms)
        )
    
    def find_learning_resources(self, topic: str, project_purpose: str, max_results: int = None) -> SearchResult:
        """
        Find learning resources for a given topic and project purpose.
        
        Args:
            topic: The topic to learn about (e.g., "AWS S3", "Python Pandas")
            project_purpose: Description of the project/purpose for learning
            max_results: Maximum number of URLs to return (defaults to config value)
        
        Returns:
            SearchResult containing URLs and metadata about the search
        """
        if max_results is None:
            max_results = self.config.max_results
        
        try:
            # Step 1: Get recommended sources from LLM
            sources = self._query_llm_for_sources(topic, project_purpose)
            
            # Step 2: Extract and process domains
            domains, youtube_channels = self._extract_domains(sources)
            
            # Step 3: Search for required resource types
            urls = []
            
            # Find basics tutorial
            basics_url = self._search_basics_tutorial(topic, domains)
            if basics_url:
                urls.append(basics_url)
            
            # Find YouTube demonstration
            youtube_url = self._search_youtube_demo(topic, youtube_channels)
            if youtube_url:
                urls.append(youtube_url)
            
            # Fill remaining slots with additional resources
            remaining_needed = max_results - len(urls)
            if remaining_needed > 0:
                additional_urls = self._search_additional_resources(topic, domains, urls, remaining_needed)
                urls.extend(additional_urls)
            
            # Validate results
            has_basics = any('youtube.com' not in url for url in urls)
            has_youtube = any('youtube.com' in url for url in urls)
            
            print(f"Found {len(urls)} URLs - Basics tutorial: {has_basics}, YouTube demo: {has_youtube}")
            
            if len(urls) < max_results:
                print(f"Warning: Only found {len(urls)} URLs for topic: {topic}")
            
            return SearchResult(
                urls=urls,
                has_basics_tutorial=has_basics,
                has_youtube_demo=has_youtube,
                error=None
            )
            
        except HttpError as e:
            error_msg = f"Google API error: {e}"
            print(error_msg)
            return SearchResult(urls=[], has_basics_tutorial=False, has_youtube_demo=False, error=error_msg)
        
        except Exception as e:
            error_msg = f"Unexpected error: {e}"
            print(error_msg)
            return SearchResult(urls=[], has_basics_tutorial=False, has_youtube_demo=False, error=error_msg)


# Tool interface for agentic LLMs
def find_learning_resources(topic: str, project_purpose: str, max_results: int = 3) -> Dict:
    """
    Tool function for finding learning resources.
    
    This tool finds educational resources for any given topic, ensuring results include
    both basics tutorials and practical demonstration videos.
    
    Args:
        topic (str): The topic to learn about (e.g., "AWS S3", "Python Pandas", "React.js")
        project_purpose (str): Description of the project or purpose for learning this topic
        max_results (int, optional): Maximum number of URLs to return. Defaults to 3.
    
    Returns:
        Dict: Contains 'urls' list, 'has_basics_tutorial' bool, 'has_youtube_demo' bool, 
              and optional 'error' string
    
    Example:
        >>> result = find_learning_resources(
        ...     topic="AWS S3",
        ...     project_purpose="Build a photo-sharing app with image uploads",
        ...     max_results=3
        ... )
        >>> print(result['urls'])
        ['https://example.com/aws-s3-basics', 'https://youtube.com/watch?v=demo']
    """
    try:
        finder = LearningResourceFinder()
        result = finder.find_learning_resources(topic, project_purpose, max_results)
        
        return {
            'urls': result.urls,
            'has_basics_tutorial': result.has_basics_tutorial,
            'has_youtube_demo': result.has_youtube_demo,
            'error': result.error
        }
    
    except Exception as e:
        return {
            'urls': [],
            'has_basics_tutorial': False,
            'has_youtube_demo': False,
            'error': f"Tool initialization error: {e}"
        }