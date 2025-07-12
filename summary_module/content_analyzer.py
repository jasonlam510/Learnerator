"""
Content Analyzer and Summary Generator for Vector Database

This module analyzes stored learning content and generates structured summaries
with knowledge relationships for frontend display.
"""

import json
import re
import os
import sys
from typing import Dict, List, Optional, Tuple, Set
from collections import defaultdict, Counter
import numpy as np
from dotenv import load_dotenv

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_together import Together
from langchain_core.prompts import PromptTemplate
from utils.schema import (
    ContentSummary, KnowledgeMap, ConceptRelationship, QuizQuestion, Quiz, 
    DatabaseSummary, MOCK_CONTENT_SUMMARIES
)

# Load environment variables
load_dotenv()


class ContentAnalyzer:
    """Analyzes content stored in vector database and generates summaries."""
    
    def __init__(self, db):
        self.llm = None
        self._initialize_llm()
        try:
            self.db = db
            print("✅ Connected to vector database")
            return
        except Exception as e:
            print(f"❌ Failed to connect to vector database: {e}")
            return
    
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
            practical_examples = llm_analysis.get('practical_examples', [])
            key_concepts = llm_analysis.get('key_concepts', {})
            implementation_summary = llm_analysis.get('implementation_summary', self._generate_basic_summary(full_content))
            common_patterns = llm_analysis.get('common_patterns', [])
        else:
            practical_examples = self._extract_practical_examples(full_content)
            key_concepts = self._extract_key_concepts_with_definitions(full_content)
            implementation_summary = self._generate_basic_summary(full_content)
            common_patterns = self._extract_common_patterns(full_content)
        
        return ContentSummary(
            source_url=url,
            title=title,
            content_type=content_type,
            key_topics=key_topics,
            key_concepts=key_concepts,
            practical_examples=practical_examples,
            implementation_summary=implementation_summary,
            common_patterns=common_patterns,
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
            1. practical_examples: 3-5 real code examples or use cases from this content
            2. key_concepts: Main concepts/knowledge explained with brief definitions
            3. implementation_summary: How this knowledge is actually used in practice
            4. common_patterns: Common patterns or best practices mentioned
            
            Format as valid JSON:
            {{
                "practical_examples": ["example1: code snippet or use case", "example2: ...", "example3: ..."],
                "key_concepts": {{"concept1": "definition1", "concept2": "definition2"}},
                "implementation_summary": "How this knowledge is actually applied in real projects...",
                "common_patterns": ["pattern1", "pattern2", "pattern3"]
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
    
    def _extract_practical_examples(self, content: str) -> List[str]:
        """Extract practical examples and code snippets from content."""
        examples = []
        
        # Look for code blocks
        code_blocks = re.findall(r'```[\w]*\n(.*?)\n```', content, re.DOTALL)
        for code in code_blocks[:3]:  # Take first 3 code blocks
            clean_code = code.strip()[:200]  # Limit length
            if clean_code:
                examples.append(f"Code example: {clean_code}")
        
        # Look for example patterns
        example_patterns = [
            r'(?:for example|example:|e\.g\.)[:\s]*(.*?)(?:\.|$)',
            r'(?:consider|suppose|imagine)[:\s]*(.*?)(?:\.|$)',
            r'(?:usage|use case)[:\s]*(.*?)(?:\.|$)'
        ]
        
        for pattern in example_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches[:2]:  # Limit to 2 per pattern
                clean_example = re.sub(r'\s+', ' ', match.strip())[:150]
                if len(clean_example) > 20:
                    examples.append(f"Example: {clean_example}")
        
        return examples[:5]  # Max 5 examples

    def _extract_key_concepts_with_definitions(self, content: str) -> Dict[str, str]:
        """Extract key concepts with their definitions."""
        concepts = {}
        
        # Look for definition patterns
        definition_patterns = [
            r'(\w+(?:\s+\w+){0,2})\s+is\s+(?:a|an|the)?\s*([^.]{10,100})',
            r'(\w+(?:\s+\w+){0,2})\s*[:]\s*([^.]{10,100})',
            r'(?:define|definition of)\s+(\w+(?:\s+\w+){0,2})\s*[:]\s*([^.]{10,100})'
        ]
        
        for pattern in definition_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for concept, definition in matches:
                clean_concept = concept.strip().lower()
                clean_definition = re.sub(r'\s+', ' ', definition.strip())
                if len(clean_definition) > 15 and len(concepts) < 8:
                    concepts[clean_concept] = clean_definition
        
        return concepts

    def _extract_common_patterns(self, content: str) -> List[str]:
        """Extract common patterns and best practices."""
        patterns = []
        
        # Look for pattern indicators
        pattern_indicators = [
            r'(?:best practice|pattern|convention|guideline)[:\s]*(.*?)(?:\.|$)',
            r'(?:always|never|should|must)[:\s]*(.*?)(?:\.|$)',
            r'(?:tip|note|important)[:\s]*(.*?)(?:\.|$)',
            r'(?:recommended|suggested)[:\s]*(.*?)(?:\.|$)'
        ]
        
        for pattern in pattern_indicators:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches[:2]:
                clean_pattern = re.sub(r'\s+', ' ', match.strip())[:120]
                if len(clean_pattern) > 15:
                    patterns.append(clean_pattern)
        
        return patterns[:6]  # Max 6 patterns

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
    
    def analyze_knowledge_relationships(self, summaries: List[ContentSummary]) -> KnowledgeMap:
        """Analyze relationships between knowledge concepts across sources."""
        
        relationships = []
        
        # Extract all concepts from all sources
        all_concepts = []
        concept_to_sources = defaultdict(list)
        
        for summary in summaries:
            concepts = summary.key_topics + list(summary.key_concepts.keys())
            for concept in concepts:
                all_concepts.append(concept)
                concept_to_sources[concept].append(summary.source_url)
        
        # Find concept relationships
        for i, concept1 in enumerate(all_concepts):
            for j, concept2 in enumerate(all_concepts[i+1:], i+1):
                if concept1 != concept2:
                    # Calculate relationship strength based on co-occurrence
                    common_sources = set(concept_to_sources[concept1]) & set(concept_to_sources[concept2])
                    strength = len(common_sources) / max(len(concept_to_sources[concept1]), len(concept_to_sources[concept2]))
                    
                    if strength > 0.3:  # Only include strong relationships
                        relationship_type, connection_desc = self._determine_relationship_type_and_description(concept1, concept2)
                        relationships.append(ConceptRelationship(
                            concept_a=concept1,
                            concept_b=concept2,
                            relationship_type=relationship_type,
                            description=connection_desc,
                            strength=strength
                        ))
        
        return KnowledgeMap(relationships=relationships)
    
    def _determine_relationship_type_and_description(self, concept1: str, concept2: str) -> Tuple[str, str]:
        """Determine the type of relationship and description between concepts."""
        
        # Detailed relationship mappings
        relationship_mappings = [
            # Prerequisites
            (('python', 'django'), 'prerequisite', 'Python fundamentals are required before learning Django framework'),
            (('python', 'flask'), 'prerequisite', 'Python knowledge is essential for Flask web development'),
            (('javascript', 'react'), 'prerequisite', 'JavaScript mastery is needed before React development'),
            (('javascript', 'vue'), 'prerequisite', 'JavaScript skills are fundamental for Vue.js'),
            (('html', 'css'), 'prerequisite', 'HTML structure knowledge comes before CSS styling'),
            (('css', 'javascript'), 'builds_on', 'JavaScript enhances CSS with dynamic interactions'),
            
            # Extensions and builds upon
            (('react', 'next.js'), 'extends', 'Next.js extends React with server-side rendering and routing'),
            (('javascript', 'typescript'), 'extends', 'TypeScript adds static typing to JavaScript'),
            (('sql', 'postgresql'), 'applies_to', 'SQL knowledge applies directly to PostgreSQL database'),
            
            # Related technologies
            (('docker', 'kubernetes'), 'builds_on', 'Kubernetes orchestrates Docker containers at scale'),
            (('git', 'github'), 'applies_to', 'Git version control is used through GitHub platform'),
            (('pandas', 'numpy'), 'builds_on', 'Pandas is built on top of NumPy for data manipulation'),
            (('matplotlib', 'pandas'), 'related_to', 'Matplotlib and Pandas work together for data visualization'),
        ]
        
        # Check for exact matches
        for (term1, term2), rel_type, description in relationship_mappings:
            if (term1 in concept1.lower() and term2 in concept2.lower()) or \
               (term1 in concept2.lower() and term2 in concept1.lower()):
                return rel_type, description
        
        # General relationship patterns
        if any(term in concept1.lower() for term in ['basic', 'fundamental', 'intro']) and \
           any(term in concept2.lower() for term in ['advanced', 'expert', 'optimization']):
            return 'prerequisite', f'{concept1} provides foundational knowledge for {concept2}'
        
        # Default relationship
        return 'related_to', f'{concept1} and {concept2} are commonly used together in development'
    
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
        
        # Group by difficulty - we'll use a simple heuristic based on content complexity
        clusters = self.generate_topic_clusters(summaries)
        
        for cluster_name, urls in clusters.items():
            cluster_summaries = [s for s in summaries if s.source_url in urls]
            
            # Sort by content complexity (number of concepts as proxy)
            cluster_summaries.sort(key=lambda x: len(getattr(x, 'key_concepts', {})))
            
            if len(cluster_summaries) >= 2:
                path = [s.source_url for s in cluster_summaries]
                paths.append(path)
        
        return paths
    
    def generate_quiz(self, summaries: List[ContentSummary]) -> Optional[Quiz]:
        """Generate a comprehensive quiz based on the analyzed content."""
        
        if not self.llm:
            print("⚠️ LLM not available - using basic quiz generation")
            return self._generate_basic_quiz(summaries)
        
        questions = []
        
        # Generate questions for key concepts from each source
        for summary in summaries[:5]:  # Limit to first 5 sources to avoid too many questions
            for concept, definition in list(summary.key_concepts.items())[:2]:  # 2 questions per source
                question = self._generate_concept_question(concept, definition, summary)
                if question:
                    questions.append(question)
        
        if not questions:
            return None
        
        return Quiz(
            title="Knowledge Assessment Quiz",
            description="Test your understanding of the key concepts from the learning resources",
            questions=questions,
            passing_score=70,  # 70% to pass
            estimated_time=f"{len(questions) * 2} minutes"  # 2 minutes per question
        )
    
    def _generate_concept_question(self, concept: str, definition: str, summary: ContentSummary) -> Optional[QuizQuestion]:
        """Generate a quiz question for a specific concept using LLM."""
        
        prompt_template = PromptTemplate.from_template(
            """
            Create a multiple choice question to test understanding of this concept:
            
            Concept: {concept}
            Definition: {definition}
            Context: This is from learning material about {title}
            
            Generate a question with 4 options where:
            - Option A, B, C, D are provided
            - Only one is correct
            - The incorrect options are plausible but wrong
            - Include a brief explanation of why the correct answer is right
            
            Format as JSON:
            {{
                "question": "What is...",
                "options": ["A: ...", "B: ...", "C: ...", "D: ..."],
                "correct_answer": 0,
                "explanation": "The correct answer is A because..."
            }}
            """
        )
        
        try:
            prompt = prompt_template.format(
                concept=concept,
                definition=definition,
                title=summary.title
            )
            response = self.llm.invoke(prompt)
            
            # Clean the response to remove control characters
            cleaned_response = ''.join(char for char in str(response) if ord(char) >= 32 or char in '\n\r\t')
            
            # Extract JSON from cleaned response
            json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', cleaned_response)
            if json_match:
                try:
                    question_data = json.loads(json_match.group())
                    
                    return QuizQuestion(
                        question=question_data.get('question', ''),
                        options=question_data.get('options', []),
                        correct_answer=question_data.get('correct_answer', 0),
                        explanation=question_data.get('explanation', ''),
                        concept=concept,
                        source_url=summary.source_url
                    )
                except json.JSONDecodeError as je:
                    print(f"JSON parsing error for {concept}: {je}")
                    print(f"Problematic JSON: {json_match.group()[:200]}...")
        
        except Exception as e:
            print(f"Error generating question for {concept}: {e}")
        
        return None
    
    def _generate_basic_quiz(self, summaries: List[ContentSummary]) -> Quiz:
        """Generate a basic quiz without LLM."""
        
        questions = []
        
        # Create simple questions from key concepts
        for summary in summaries[:3]:
            for concept in list(summary.key_concepts.keys())[:2]:
                question = QuizQuestion(
                    question=f"Which of the following best describes {concept}?",
                    options=[
                        f"A: {concept} is a programming language",
                        f"B: {concept} is a database system", 
                        f"C: {concept} is a web framework",
                        f"D: {concept} is a development tool"
                    ],
                    correct_answer=0,  # Default to A
                    explanation=f"This question tests knowledge of {concept}",
                    concept=concept,
                    source_url=summary.source_url
                )
                questions.append(question)
        
        return Quiz(
            title="Basic Knowledge Quiz",
            description="Simple quiz based on the learning content",
            questions=questions,
            passing_score=60,
            estimated_time=f"{len(questions) * 2} minutes"
        )

    def generate_complete_summary(self, limit: int = 100, include_quiz: bool = False) -> Optional[DatabaseSummary]:
        """Generate complete summary of the vector database content."""
    
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
        
        # Generate quiz if requested
        quiz = None
        if include_quiz:
            print("📝 Generating knowledge quiz...")
            quiz = self.generate_quiz(content_summaries)
        
        from datetime import datetime
        
        return DatabaseSummary(
            total_sources=len(sources),
            content_summaries=content_summaries,
            knowledge_map=knowledge_map,
            topic_clusters=topic_clusters,
            learning_paths=learning_paths,
            quiz=quiz,
            generated_at=datetime.now().isoformat()
        )