"""
Schema definitions for the Learning Resource System

This module contains all dataclass definitions used throughout the system.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass


# Vector Database Schema
@dataclass
class ContentChunk:
    """A chunk of content from a learning resource."""
    content: str
    source_url: str
    title: str
    content_type: str
    chunk_index: int
    metadata: Dict


@dataclass
class SearchResult:
    """A search result from the vector database."""
    chunk: ContentChunk
    similarity_score: float
    metadata: Dict


# Content Analysis Schema
@dataclass
class ContentSummary:
    """Summary of content from a single source."""
    source_url: str
    title: str
    content_type: str
    key_topics: List[str]
    key_concepts: Dict[str, str]  # concept -> definition
    practical_examples: List[str]  # Real examples and code snippets
    implementation_summary: str  # How it's used in practice
    common_patterns: List[str]  # Best practices and patterns
    chunk_count: int


@dataclass
class KnowledgeMap:
    """Relationship between knowledge concepts."""
    source_concept: str
    target_concept: str
    relationship_type: str  # 'prerequisite', 'builds_on', 'related_to', 'applies_to', 'extends'
    connection_description: str  # How they are connected
    strength: float  # 0.0 to 1.0
    source_urls: List[str]


# Quiz Schema
@dataclass
class QuizQuestion:
    """A quiz question with multiple choice answers."""
    question: str
    options: List[str]  # 4 options (A, B, C, D)
    correct_answer: int  # Index of correct answer (0-3)
    explanation: str
    concept: str  # Which concept this tests
    source_url: str


@dataclass
class Quiz:
    """Complete quiz for testing knowledge."""
    title: str
    description: str
    questions: List[QuizQuestion]
    passing_score: int  # Percentage needed to pass
    estimated_time: str


# Database Summary Schema
@dataclass
class DatabaseSummary:
    """Complete summary of the vector database content."""
    total_sources: int
    content_summaries: List[ContentSummary]
    knowledge_map: List[KnowledgeMap]
    topic_clusters: Dict[str, List[str]]
    learning_paths: List[List[str]]
    quiz: Optional[Quiz]  # Optional quiz for testing knowledge
    generated_at: str


# Learning Resource Finder Schema
# Learning Resource Finder Schema
@dataclass
class SearchConfig:
    """Configuration for resource search."""
    max_results: int = 3
    max_websites: int = 2  # Reduced to 2 for API efficiency
    max_youtube_channels: int = 2
    max_domains: int = 3  # Reduced to 3 for API efficiency
    llm_max_tokens: int = 500
    results_per_topic: int = 1  # One dedicated resource per specific topic
    min_youtube_ratio: float = 0.3  # At least 30% should be YouTube videos
    min_tutorial_ratio: float = 0.3  # At least 30% should be tutorial pages


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
    covered_topics: List[str]  # Topics/features covered by the resources
    topic_coverage: Dict[str, List[str]]  # Maps topic to URLs covering it
    error: Optional[str] = None


@dataclass
class ResourceSearchResult:
    """Result from resource search operation."""
    success: bool
    websites: List[str]
    youtube_urls: List[str]
    error_message: Optional[str] = None
    used_mock_data: bool = False


# RAG Chatbot Schema
@dataclass
class ChatResponse:
    """Response from the RAG chatbot."""
    answer: str
    sources: List[str]
    method_used: str  # 'llm' or 'retrieval'
    confidence: float

MOCK_CONTENT_SUMMARIES = [
    ContentSummary(
        source_url="https://docs.python.org/3/tutorial/",
        title="Python Tutorial - Official Documentation",
        content_type="documentation",
        key_topics=["python", "programming", "tutorial"],
        key_concepts={
            "variables": "Named containers that store data values",
            "functions": "Reusable blocks of code that perform specific tasks",
            "loops": "Structures that repeat code execution based on conditions"
        },
        practical_examples=[
            "Creating variables: name = 'John', age = 25",
            "Writing functions: def greet(name): return f'Hello {name}'",
            "Using loops: for i in range(10): print(i)"
        ],
        implementation_summary="Python fundamentals for building applications, scripts, and data analysis tools",
        common_patterns=[
            "Use descriptive variable names",
            "Follow PEP 8 style guidelines",
            "Write docstrings for functions"
        ],
        chunk_count=15
    ),
    ContentSummary(
        source_url="https://realpython.com/python-basics/",
        title="Python Basics: A Practical Introduction",
        content_type="tutorial",
        key_topics=["python", "basics", "programming"],
        key_concepts={
            "data types": "Different kinds of data like strings, integers, lists",
            "control flow": "Directing program execution with if/else and loops",
            "error handling": "Managing exceptions and errors gracefully"
        },
        practical_examples=[
            "Data types: name = 'Alice', numbers = [1, 2, 3], score = 85.5",
            "Control flow: if score > 80: print('Good job!')",
            "Error handling: try/except blocks for safe code execution"
        ],
        implementation_summary="Essential Python concepts for writing robust, maintainable code",
        common_patterns=[
            "Use meaningful variable names",
            "Handle errors explicitly",
            "Keep functions small and focused"
        ],
        chunk_count=12
    )
]