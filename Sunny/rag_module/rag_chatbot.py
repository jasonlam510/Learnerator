"""
RAG Chatbot for Learning Resources

A chatbot that uses Retrieval-Augmented Generation to answer questions
about content stored in the vector database.
"""

import os
import logging
from typing import List
from dataclasses import dataclass

# Try to import LLM for chatbot functionality
try:
    from langchain_together import Together
    from langchain_core.prompts import PromptTemplate
    from dotenv import load_dotenv
    load_dotenv()
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False

# Import types - avoid circular import
from typing import List, TYPE_CHECKING
if TYPE_CHECKING:
    from vector_database import VectorDatabase, SearchResult
else:
    VectorDatabase = None
    SearchResult = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ChatResponse:
    """Represents a chatbot response with sources."""
    answer: str
    sources: List[any]  # List[SearchResult] - avoiding circular import
    confidence: float
    query: str
    error: str = None


class RAGChatbot:
    """RAG-based chatbot for answering questions about stored content."""
    
    def __init__(self, vector_db):  # vector_db: VectorDatabase - avoiding circular import
        self.vector_db = vector_db
        self.llm = None
        self._initialize_llm()
    
    def _initialize_llm(self):
        """Initialize the LLM for generating responses."""
        if not LLM_AVAILABLE:
            logger.warning("LLM not available. Install langchain_together and set TOGETHER_API_KEY.")
            return
        
        try:
            together_api_key = os.getenv("TOGETHER_API_KEY")
            if together_api_key:
                self.llm = Together(
                    model="mistralai/Mixtral-8x7B-Instruct-v0.1",
                    together_api_key=together_api_key,
                    max_tokens=1000,
                    temperature=0.7
                )
                logger.info("LLM initialized successfully for chatbot")
            else:
                logger.warning("TOGETHER_API_KEY not found. Chatbot will use simple retrieval only.")
        except Exception as e:
            logger.error(f"Failed to initialize LLM: {e}")
    
    def ask(self, question: str, max_sources: int = 3) -> ChatResponse:
        """Ask a question and get an AI-generated answer based on stored content."""
        try:
            # Validate input
            if not question or not question.strip():
                return ChatResponse(
                    answer="Please provide a valid question.",
                    sources=[],
                    confidence=0.0,
                    query=question,
                    error="Empty question"
                )
            
            question = question.strip()
            
            # Search for relevant content
            search_results = self.vector_db.search(question, limit=max_sources * 2)
            
            if not search_results:
                return ChatResponse(
                    answer="I couldn't find any relevant information in the knowledge base to answer your question. Try asking about topics that are covered in the stored learning resources.",
                    sources=[],
                    confidence=0.0,
                    query=question
                )
            
            # Filter and rank results
            relevant_sources = []
            for result in search_results:
                if result.similarity > 0.5:  # Only include reasonably similar content
                    relevant_sources.append(result)
                if len(relevant_sources) >= max_sources:
                    break
            
            if not relevant_sources:
                # Use lower threshold if no good matches
                relevant_sources = search_results[:max_sources]
                return ChatResponse(
                    answer="I found some content that might be related to your question, but it doesn't seem directly relevant. Here's what I found:",
                    sources=relevant_sources,
                    confidence=0.3,
                    query=question
                )
            
            # Generate answer using LLM if available
            if self.llm:
                answer = self._generate_llm_answer(question, relevant_sources)
                confidence = min(0.9, max(0.6, sum(r.similarity for r in relevant_sources) / len(relevant_sources)))
            else:
                answer = self._generate_simple_answer(question, relevant_sources)
                confidence = 0.5
            
            return ChatResponse(
                answer=answer,
                sources=relevant_sources,
                confidence=confidence,
                query=question
            )
            
        except Exception as e:
            logger.error(f"Error processing question: {e}")
            return ChatResponse(
                answer=f"Sorry, I encountered an error while processing your question. Please try again.",
                sources=[],
                confidence=0.0,
                query=question,
                error=str(e)
            )
    
    def _generate_llm_answer(self, question: str, sources: List[SearchResult]) -> str:
        """Generate an answer using the LLM based on retrieved sources."""
        try:
            # Prepare context from sources
            context_parts = []
            for i, source in enumerate(sources, 1):
                # Truncate very long content
                content = source.chunk.content
                if len(content) > 1000:
                    content = content[:1000] + "..."
                
                context_parts.append(f"Source {i} - {source.chunk.title}:\n{content}\n")
            
            context = "\n".join(context_parts)
            
            # Create prompt template
            prompt_template = PromptTemplate.from_template(
                """You are a helpful AI assistant that answers questions based on learning resources. Use the following context to answer the user's question accurately and helpfully.

Context from Learning Resources:
{context}

Question: {question}

Instructions:
- Provide a clear, concise answer based primarily on the given context
- If referencing specific information, mention which source it comes from
- If the context doesn't fully answer the question, be honest about limitations
- Keep the answer focused and practical
- Use a helpful, educational tone
- Format your response in a readable way with proper paragraphs

Answer:"""
            )
            
            # Generate response
            prompt = prompt_template.format(context=context, question=question)
            response = self.llm.invoke(prompt)
            
            # Clean up the response
            answer = str(response).strip()
            if answer.startswith("Answer:"):
                answer = answer[7:].strip()
            
            return answer
            
        except Exception as e:
            logger.error(f"Error generating LLM answer: {e}")
            return self._generate_simple_answer(question, sources)
    
    def _generate_simple_answer(self, question: str, sources: List[SearchResult]) -> str:
        """Generate a simple answer by combining relevant source content."""
        answer_parts = []
        answer_parts.append("Based on the learning resources in my knowledge base:\n")
        
        for i, source in enumerate(sources, 1):
            # Truncate content to most relevant part
            content = source.chunk.content
            if len(content) > 300:
                content = content[:300] + "..."
            
            answer_parts.append(f"**{i}. From '{source.chunk.title}':**")
            answer_parts.append(f"{content}")
            answer_parts.append("")
        
        answer_parts.append("For more detailed information, please refer to the original sources.")
        
        return "\n".join(answer_parts)
    
    def get_similar_questions(self, question: str, limit: int = 3) -> List[str]:
        """Generate similar questions that might be interesting to ask."""
        try:
            # Search for content related to the question
            search_results = self.vector_db.search(question, limit=limit * 2)
            
            similar_questions = []
            for result in search_results:
                # Extract key topics from the content
                content = result.chunk.content[:200]  # First 200 chars
                
                # Generate questions based on content topics
                if 'python' in content.lower():
                    similar_questions.append("How do I use Python for this task?")
                if 'tutorial' in content.lower():
                    similar_questions.append("Can you explain this step by step?")
                if 'example' in content.lower():
                    similar_questions.append("Can you show me an example?")
                
                if len(similar_questions) >= limit:
                    break
            
            return similar_questions[:limit]
            
        except Exception as e:
            logger.error(f"Error generating similar questions: {e}")
            return []
    
    def chat_session(self):
        """Start an interactive chat session with the user."""
        print("\n🤖 Welcome to the Learning Resource Chatbot!")
        print("💬 Ask me questions about the stored learning resources.")
        print("🔚 Type 'quit', 'exit', or 'bye' to end the chat.\n")
        
        try:
            while True:
                # Get user input
                user_input = input("👤 You: ").strip()
                
                # Check for exit commands
                if user_input.lower() in ['quit', 'exit', 'bye', 'q']:
                    print("👋 Goodbye! Thanks for chatting!")
                    break
                
                # Skip empty input
                if not user_input:
                    continue
                
                # Get response from chatbot
                print("🤖 Assistant: ", end="", flush=True)
                
                try:
                    response = self.ask(user_input)
                    
                    # Print the answer
                    print(response.answer)
                    
                    # Show confidence and sources if available
                    if response.confidence > 0:
                        print(f"\n📊 Confidence: {response.confidence:.1%}")
                    
                    if response.sources:
                        print(f"\n📚 Sources ({len(response.sources)}):")
                        for i, source in enumerate(response.sources, 1):
                            print(f"   {i}. {source.chunk.title[:60]}... (relevance: {source.similarity:.1%})")
                    
                    # Show related questions
                    similar_questions = self.get_similar_questions(user_input, limit=2)
                    if similar_questions:
                        print(f"\n💡 You might also ask:")
                        for q in similar_questions:
                            print(f"   • {q}")
                    
                except Exception as e:
                    print(f"Sorry, I encountered an error: {e}")
                    logger.error(f"Chat session error: {e}")
                
                print()  # Add spacing between interactions
                
        except KeyboardInterrupt:
            print("\n\n👋 Chat interrupted. Goodbye!")
        except Exception as e:
            print(f"\n❌ Chat session error: {e}")
            logger.error(f"Chat session error: {e}")

def create_chatbot(vector_db: VectorDatabase) -> RAGChatbot:
    """Create a RAG chatbot instance."""
    return RAGChatbot(vector_db)
