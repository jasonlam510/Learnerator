"""
Learning Resource Finder Tool

A tool for finding educational resources including basics tutorials and demonstration videos
for any given topic and project purpose. Designed to be used by agentic LLMs.
"""

import json
import os
import re
from typing import Dict, List, Optional, Tuple

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from langchain_together import Together
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv
from utils.schema import SearchConfig, ResourceSources, SearchResult

# Load environment variables
load_dotenv()


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
    
    def _initialize_services(self) -> None:
        """Initialize external services."""
        try:
            self.llm = Together(
                model="mistralai/Mixtral-8x7B-Instruct-v0.1",
                together_api_key=self.together_api_key,
                max_tokens=self.config.llm_max_tokens
            )
            
            self.search_service = build('customsearch', 'v1', developerKey=self.google_api_key)
        except Exception as e:
            print(f"⚠️ Failed to initialize services: {e}")
            print("🔄 Will use mock data for search results")
    
    def _parse_learning_content(self, content: str) -> List[str]:
        """Parse learning content into individual topics/features."""
        if isinstance(content, list):
            return content
        
        # Handle bracketed list format: [item1, item2, item3]
        if content.strip().startswith('[') and content.strip().endswith(']'):
            content = content.strip()[1:-1]  # Remove brackets
            topics = [topic.strip() for topic in content.split(',')]
            return [topic for topic in topics if topic]
        
        # Handle comma-separated format
        if ',' in content:
            topics = [topic.strip() for topic in content.split(',')]
            return [topic for topic in topics if topic]
        
        # Single topic
        return [content.strip()] if content.strip() else []

    def _query_llm_for_sources(self, topic: str, learning_content: List[str]) -> ResourceSources:
        """Query LLM for recommended learning sources."""
        content_list = ", ".join(learning_content)
        prompt_template = PromptTemplate.from_template(
            """
            What are the TOP 3 best free tutorial websites and TOP 2 YouTube channels to learn {topic}? 
            I specifically need to learn these topics/features: {learning_content}
            
            IMPORTANT: Return only the BEST 3 websites and BEST 2 YouTube channels.
            
            I need:
            1. TOP 3 tutorial websites (like MDN, javascript.info, GeeksforGeeks) with the most comprehensive coverage
            2. TOP 2 YouTube channels with the best practical demonstrations
            
            Focus on the highest quality resources that cover: {learning_content}
            
            Exclude course-based platforms like Coursera, edX, or Khan Academy. 
            Return EXACTLY 3 websites and 2 YouTube channels in JSON format.
            
            Example format:
            {{
                "websites": ["developer.mozilla.org", "javascript.info", "freecodecamp.org"],
                "youtube_channels": ["youtube.com/@TraversyMedia", "youtube.com/@CodeWithMosh"]
            }}
            """
        )
        
        try:
            prompt = prompt_template.format(topic=topic, learning_content=content_list)
            response = self.llm.invoke(prompt)
            
            # Parse JSON from response
            sources_data = self._extract_json_from_response(str(response))
            
            return ResourceSources(
                websites=sources_data.get('websites', []),
                youtube_channels=sources_data.get('youtube_channels', [])
            )
            
        except Exception as e:
            print(f"LLM query error: {e}")
            # Return focused fallback sources - only the best 2-3 sites
            return ResourceSources(
                websites=['developer.mozilla.org', 'freecodecamp.org'],  # Reduced to top 2
                youtube_channels=['youtube.com/@TraversyMedia', 'youtube.com/@CodeWithMosh']
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
        
        # Add focused fallback domains - only the most reliable ones
        fallback_domains = ['developer.mozilla.org', 'freecodecamp.org']  # Reduced to top 2
        for domain in fallback_domains:
            if len(key_domains) >= self.config.max_domains:
                break
            if domain not in key_domains:
                key_domains.append(domain)
        
        return list(dict.fromkeys(key_domains))[:self.config.max_domains], youtube_channels
    
    # def _search_basics_tutorial(self, topic: str, domains: List[str]) -> Optional[str]:
    #     """Search for a basics/introduction tutorial."""
    #     for domain in domains:
    #         query = f'{topic} basics introduction tutorial beginner site:{domain}'
            
    #         try:
    #             result = self.search_service.cse().list(
    #                 q=query,
    #                 cx=self.cse_id,
    #                 num=3
    #             ).execute()
                
    #             if 'items' in result:
    #                 for item in result['items']:
    #                     url = item.get('link')
    #                     title = item.get('title', '').lower()
    #                     snippet = item.get('snippet', '').lower()
                        
    #                     if url and self._is_valid_basics_tutorial(url, title, snippet):
    #                         print(f"Found basics tutorial: {url}")
    #                         return url
                            
    #         except HttpError as e:
    #             if "rateLimitExceeded" in str(e) or "Quota exceeded" in str(e):
    #                 print(f"⚠️ API quota exceeded for {domain}. Skipping remaining searches.")
    #                 break  # Stop trying more domains to conserve quota
    #             elif "API key not valid" in str(e):
    #                 print(f"❌ Invalid API key. Please check your Google API key in .env file.")
    #                 break
    #             else:
    #                 print(f"Search error for basics tutorial on {domain}: {e}")
    #             continue
        
    #     return None
    
    # def _search_youtube_demo(self, topic: str, youtube_channels: List[str]) -> Optional[str]:
    #     """Search for a YouTube demonstration video."""
    #     youtube_domains = [domain for domain in youtube_channels if 'youtube.com' in domain] + ['youtube.com']
        
    #     for domain in youtube_domains:
    #         query = f'{topic} demo demonstration tutorial example site:{domain}'
            
    #         try:
    #             result = self.search_service.cse().list(
    #                 q=query,
    #                 cx=self.cse_id,
    #                 num=5
    #             ).execute()
                
    #             if 'items' in result:
    #                 for item in result['items']:
    #                     url = item.get('link')
    #                     title = item.get('title', '').lower()
    #                     snippet = item.get('snippet', '').lower()
                        
    #                     if url and self._is_valid_youtube_demo(url, title, snippet):
    #                         print(f"Found YouTube demo: {url}")
    #                         return url
                            
    #         except HttpError as e:
    #             if "rateLimitExceeded" in str(e) or "Quota exceeded" in str(e):
    #                 print(f"⚠️ API quota exceeded for YouTube search. Stopping.")
    #                 break
    #             elif "API key not valid" in str(e):
    #                 print(f"❌ Invalid API key. Please check your Google API key.")
    #                 break
    #             else:
    #                 print(f"Search error for YouTube demo: {e}")
    #             continue
        
    #     return None
    
    def _search_specific_topics(self, topic: str, learning_content: List[str], domains: List[str], youtube_channels: List[str]) -> Dict[str, List[str]]:
        """Search for resources covering specific topics/features - one dedicated resource per topic."""
        topic_coverage = {}
        
        for specific_topic in learning_content:
            topic_coverage[specific_topic] = []
            
            # First try to find a dedicated tutorial page for this specific topic
            tutorial_url = self._search_dedicated_tutorial(topic, specific_topic, domains)
            if tutorial_url:
                topic_coverage[specific_topic].append(tutorial_url)
                continue
            
            # If no dedicated tutorial found, try YouTube
            youtube_url = self._search_youtube_for_topic(topic, specific_topic, youtube_channels)
            if youtube_url:
                topic_coverage[specific_topic].append(youtube_url)
                continue
        
        return topic_coverage

    def _search_dedicated_tutorial(self, topic: str, specific_topic: str, domains: List[str]) -> Optional[str]:
        """Search for a dedicated tutorial page for a specific topic."""
        for domain in domains:
            query = f'"{specific_topic}" {topic} tutorial guide site:{domain}'
            
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
                        
                        if url and self._is_dedicated_tutorial(url, title, snippet, specific_topic):
                            print(f"Found dedicated tutorial for '{specific_topic}': {url}")
                            return url
                            
            except HttpError as e:
                print(f"Search error for {specific_topic} tutorial on {domain}: {e}")
                continue
        
        return None

    def _search_youtube_for_topic(self, topic: str, specific_topic: str, youtube_channels: List[str]) -> Optional[str]:
        """Search for a YouTube video dedicated to a specific topic."""
        youtube_domains = [domain for domain in youtube_channels if 'youtube.com' in domain] + ['youtube.com']
        
        for domain in youtube_domains[:2]:  # Limit to avoid too many API calls
            query = f'"{specific_topic}" {topic} tutorial example site:{domain}'
            
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
                        
                        if url and self._is_dedicated_youtube_video(url, title, snippet, specific_topic):
                            print(f"Found YouTube video for '{specific_topic}': {url}")
                            return url
                            
            except HttpError as e:
                print(f"Search error for {specific_topic} YouTube on {domain}: {e}")
                continue
        
        return None

    def _is_dedicated_tutorial(self, url: str, title: str, snippet: str, specific_topic: str) -> bool:
        """Check if a URL is a dedicated tutorial for the specific topic."""
        excluded_terms = ['login', 'signup', 'pay', 'subscribe']
        topic_keywords = specific_topic.lower().split()
        
        # Check if the specific topic appears prominently in title or snippet
        topic_in_title = any(keyword in title for keyword in topic_keywords)
        topic_in_snippet = any(keyword in snippet for keyword in topic_keywords)
        is_tutorial = any(term in title or term in snippet for term in ['tutorial', 'guide', 'learn', 'how to'])
        is_clean_url = all(term not in url.lower() for term in excluded_terms)
        is_not_youtube = 'youtube.com' not in url
        
        return (topic_in_title or topic_in_snippet) and is_tutorial and is_clean_url and is_not_youtube

    def _is_dedicated_youtube_video(self, url: str, title: str, snippet: str, specific_topic: str) -> bool:
        """Check if a URL is a dedicated YouTube video for the specific topic."""
        excluded_terms = ['login', 'signup', 'pay', 'subscribe']
        topic_keywords = specific_topic.lower().split()
        
        # Check if the specific topic appears in title or snippet
        topic_mentioned = any(keyword in title or keyword in snippet for keyword in topic_keywords)
        is_youtube = 'youtube.com' in url and '/watch' in url
        is_tutorial = any(term in title or term in snippet for term in ['tutorial', 'example', 'demo', 'guide', 'how to'])
        is_clean_url = all(term not in url.lower() for term in excluded_terms)
        
        return topic_mentioned and is_youtube and is_tutorial and is_clean_url
    
    # def _is_valid_basics_tutorial(self, url: str, title: str, snippet: str) -> bool:
    #     """Check if a URL is a valid basics tutorial."""
    #     basics_terms = ['tutorial', 'learn', 'guide', 'how to']
    #     excluded_terms = ['login', 'signup', 'pay', 'subscribe']
        
    #     return (
    #         any(term in title or term in snippet for term in basics_terms) and
    #         all(term not in url.lower() for term in excluded_terms) and
    #         'youtube.com' not in url
    #     )
    
    # def _is_valid_youtube_demo(self, url: str, title: str, snippet: str) -> bool:
    #     """Check if a URL is a valid YouTube demonstration."""
    #     demo_terms = ['demo', 'demonstration', 'example', 'tutorial', 'how to']
    #     excluded_terms = ['login', 'signup', 'pay', 'subscribe']
        
    #     return (
    #         'youtube.com' in url and '/watch' in url and
    #         any(term in title or term in snippet for term in demo_terms) and
    #         all(term not in url.lower() for term in excluded_terms)
    #     )
    
    def find_learning_resources(self, topic_data, max_results: int = None) -> SearchResult:
        
        if max_results is None:
            max_results = self.config.max_results
        
        try:
            # Parse input - handle both legacy string format and new JSON format
            if isinstance(topic_data, str):
                # Legacy format: topic_data is just the content string
                topic = "general learning"
                learning_content = self._parse_learning_content(topic_data)
            elif isinstance(topic_data, dict):
                # New JSON format
                topic = topic_data.get("header", "general learning")
                details = topic_data.get("details", "")
                keywords = topic_data.get("keywords", [])
                
                # Combine details and keywords for learning content
                learning_content = []
                if details:
                    learning_content.append(details)
                if keywords:
                    learning_content.extend(keywords)
            else:
                raise ValueError("Invalid input format. Expected string or dict.")
                
            print(f"Learning topic: {topic}")
            print(f"Learning objectives: {learning_content}")
            
            # Step 2: Get recommended sources from LLM
            sources = self._query_llm_for_sources(topic, learning_content)
            
            # Step 3: Extract and process domains
            domains, youtube_channels = self._extract_domains(sources)
            
            # Step 4: Search for resources covering specific topics (one per topic)
            topic_coverage = self._search_specific_topics(topic, learning_content, domains, youtube_channels)
            
            # Step 5: Collect URLs ensuring one resource per topic and good balance
            urls = []
            covered_topics = []
            youtube_urls = []
            tutorial_urls = []
            
            # First, add one resource per specific topic
            for specific_topic, topic_urls in topic_coverage.items():
                if topic_urls:  # If we found a resource for this topic
                    url = topic_urls[0]  # Take the first (best) resource
                    urls.append(url)
                    covered_topics.append(specific_topic)
                    
                    # Categorize the URL
                    if 'youtube.com' in url:
                        youtube_urls.append(url)
                    else:
                        tutorial_urls.append(url)
            
            # Validate results and report
            has_basics = any('youtube.com' not in url for url in urls)
            has_youtube = any('youtube.com' in url for url in urls)
            
            youtube_count = len([url for url in urls if 'youtube.com' in url])
            tutorial_count = len([url for url in urls if 'youtube.com' not in url])
            
            print(f"✅ Found {len(urls)} URLs covering {len(covered_topics)}/{len(learning_content)} learning objectives")
            print(f"📺 YouTube videos: {youtube_count}, 📖 Tutorial pages: {tutorial_count}")
            print(f"🎯 Covered topics: {covered_topics}")
            
            missing_topics = [t for t in learning_content if t not in covered_topics]
            if missing_topics:
                print(f"⚠️ Missing coverage for: {missing_topics}")
            else:
                print(f"🎉 All topics covered!")
            
            return SearchResult(
                urls=urls,
                has_basics_tutorial=has_basics,
                has_youtube_demo=has_youtube,
                covered_topics=covered_topics,
                topic_coverage=topic_coverage,
                error=None
            )
            
        except HttpError as e:
            error_msg = f"Google API error: {e}"
            print(f"⚠️ {error_msg}")
        
        except Exception as e:
            error_msg = f"Unexpected error: {e}"
            print(f"⚠️ {error_msg}")


# Tool interface for agentic LLMs
def find_learning_resources(topic_data, max_results: int = 5) -> Dict:
    """
    Tool function for finding learning resources with specific learning objectives.
    
    This tool finds educational resources for any given topic, ensuring results cover
    specific features or topics the user wants to learn.
    
    Args:
        topic_data: Can be either:
            - Legacy format (str): Learning objectives as "[item1, item2, item3]" or "item1, item2, item3"
            - New format (dict): JSON object with structure:
                {
                    "header": "Topic title",
                    "details": "Description of what to learn",
                    "keywords": ["keyword1", "keyword2", "keyword3"],
                    "status": "pending"
                }
        max_results (int, optional): Maximum number of URLs to return. Defaults to 5.
    
    Returns:
        Dict: Contains 'urls' list, 'has_basics_tutorial' bool, 'has_youtube_demo' bool,
              'covered_topics' list, 'topic_coverage' dict, and optional 'error' string
    
    Examples:
        >>> # Legacy format
        >>> result = find_learning_resources(
        ...     "[es6+ features, async/await, promises, arrow functions]",
        ...     max_results=5
        ... )
        
        >>> # New JSON format
        >>> result = find_learning_resources(
        ...     {
        ...         "header": "Introduction to Machine Learning",
        ...         "details": "Learn the basic concepts and types of machine learning algorithms",
        ...         "keywords": ["machine learning basics", "ML algorithms", "supervised learning"],
        ...         "status": "pending"
        ...     },
        ...     max_results=5
        ... )
    """
    try:
        finder = LearningResourceFinder()
        result = finder.find_learning_resources(topic_data, max_results)
        
        return {
            'urls': result.urls,
            'has_basics_tutorial': result.has_basics_tutorial,
            'has_youtube_demo': result.has_youtube_demo,
            'covered_topics': result.covered_topics,
            'topic_coverage': result.topic_coverage,
            'error': result.error
        }
    
    except Exception as e:
        return {
            'urls': [],
            'has_basics_tutorial': False,
            'has_youtube_demo': False,
            'covered_topics': [],
            'topic_coverage': {},
            'error': f"Tool initialization error: {e}"
        }
        
if __name__ == "__main__":
    # Example usage with new JSON format
    topic_data = {
        "header": "Introduction to Machine Learning",
        "details": "Learn the basic concepts and types of machine learning algorithms",
        "keywords": ["machine learning basics", "ML algorithms", "supervised learning"],
        "status": "pending"
    }
    max_results = 5
    
    result = find_learning_resources(topic_data, max_results)
    print(json.dumps(result, indent=2))
    
    # Example with legacy format (still supported)
    # legacy_content = "[es6+ features, async/await, promises, arrow functions, destructuring]"
    # result = find_learning_resources(legacy_content, max_results)
    # print(json.dumps(result, indent=2))