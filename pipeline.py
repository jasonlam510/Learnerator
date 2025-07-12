"""
Learning Resource Pipeline Server

A FastAPI server that orchestrates the complete learning resource pipeline:
1. Receives JSON learning requests from frontend
2. Finds learning resources using tool registry
3. Processes URLs into vector database
4. Generates summary dashboard
5. Provides RAG chatbot API for Q&A

API Endpoints:
- POST /api/find-resources: Find learning resources
- POST /api/generate-summary: Generate learning dashboard
- POST /api/chat: RAG chatbot for Q&A
- GET /api/status: Pipeline status
"""

import json
import os
import asyncio
import uvicorn
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# Import our modules
from url_module.learning_resource_finder import find_learning_resources
from url_module.tool_registry import OPENAI_TOOLS
from rag_module.vector_database import LearningResourceVectorDB
from summary_module.content_analyzer import ContentAnalyzer
from summary_module.html_generator import LearningDashboardGenerator
from rag_module.rag_chatbot import RAGChatbot

# Pydantic models for API requests/responses
class LearningRequest(BaseModel):
    """Request model for learning resource finding."""
    header: str
    details: str
    keywords: List[str]
    status: str = "pending"

class ChatRequest(BaseModel):
    """Request model for chatbot queries."""
    question: str
    session_id: Optional[str] = None

class ResourceResponse(BaseModel):
    """Response model for found resources."""
    urls: List[str]
    has_basics_tutorial: bool
    has_youtube_demo: bool
    covered_topics: List[str]
    topic_coverage: Dict[str, List[str]]
    error: Optional[str] = None

class ChatResponse(BaseModel):
    """Response model for chatbot responses."""
    answer: str
    sources: List[str]
    session_id: str
    error: Optional[str] = None

class PipelineStatus(BaseModel):
    """Response model for pipeline status."""
    status: str
    resources_count: int
    last_update: str
    dashboard_available: bool
    chatbot_ready: bool

# Initialize FastAPI app
app = FastAPI(
    title="Learning Resource Pipeline",
    description="Complete pipeline for learning resource discovery and analysis",
    version="1.0.0"
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global pipeline state
class PipelineState:
    def __init__(self):
        self.vector_db: Optional[LearningResourceVectorDB] = None
        self.chatbot: Optional[RAGChatbot] = None
        self.last_resources: List[str] = []
        self.last_update: str = ""
        self.dashboard_path: Optional[str] = None
        self.is_processing: bool = False
        
    def initialize(self):
        """Initialize all pipeline components."""
        try:
            self.vector_db = LearningResourceVectorDB()
            self.vector_db.initialize()
            
            print("✅ Pipeline components initialized successfully")
            return True
        except Exception as e:
            print(f"❌ Failed to initialize pipeline: {e}")
            return False
    
    def initialize_chatbot(self):
        """Initialize chatbot after vector DB has content."""
        try:
            if self.vector_db:
                self.chatbot = RAGChatbot(self.vector_db)
                print("✅ RAG Chatbot initialized")
                return True
        except Exception as e:
            print(f"❌ Failed to initialize chatbot: {e}")
            return False

# Global pipeline instance
pipeline = PipelineState()

@app.on_event("startup")
async def startup_event():
    """Initialize pipeline on server startup."""
    print("🚀 Starting Learning Resource Pipeline Server...")
    pipeline.initialize()

# Serve static files (for dashboard)
if not os.path.exists("static"):
    os.makedirs("static")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.post("/api/find-resources", response_model=ResourceResponse)
async def find_resources_endpoint(
    request: LearningRequest, 
    background_tasks: BackgroundTasks
):
    """
    Find learning resources based on the request.
    Automatically starts processing in background.
    """
    try:
        if pipeline.is_processing:
            raise HTTPException(status_code=409, detail="Pipeline is currently processing another request")
        
        # Convert request to the format expected by learning resource finder
        topic_data = {
            "header": request.header,
            "details": request.details,
            "keywords": request.keywords,
            "status": request.status
        }
        
        print(f"🔍 Finding resources for: {request.header}")
        
        # Find learning resources
        result = find_learning_resources(topic_data, max_results=10)
        urls = result['urls']
        
        if result.get('error'):
            urls = [
                "https://beam.ai/agentic-insights/what-is-agentic-ai-the-2025-beginner-s-guide-for-entrepreneurs",
                "https://www.capably.ai/resources/agentic-ai",
                "https://www.mendix.com/blog/guide-to-agentic-ai/",
                "https://www.chaione.com/blog/agentic-ai-a-beginners-guide"
            ]
            raise HTTPException(status_code=500, detail=urls)
        
        # Store results for background processing
        pipeline.last_resources = result['urls']
        pipeline.last_update = datetime.now().isoformat()
        
        # Start background processing
        background_tasks.add_task(process_resources_background, urls)
        
        return ResourceResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error finding resources: {str(e)}")

async def process_resources_background(urls: List[str]):
    """Background task to process URLs and generate dashboard."""
    try:
        pipeline.is_processing = True
        print(f"🔄 Processing {len(urls)} URLs in background...")
        
        if not pipeline.vector_db:
            print("❌ Vector database not initialized")
            return
        
        # Process URLs into vector database
        print("📊 Adding URLs to vector database...")
        pipeline.vector_db.process_urls(urls)
        
        # Initialize chatbot now that we have content
        pipeline.initialize_chatbot()
        
    except Exception as e:
        print(f"❌ Background processing error: {e}")
    finally:
        pipeline.is_processing = False

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    RAG chatbot endpoint for answering questions about learning resources.
    """
    try:
        if not pipeline.chatbot:
            # If chatbot isn't initialized, return a helpful message
            return ChatResponse(
                answer="I'm not ready yet! Please generate some learning resources first, then I'll be able to help you with questions about your learning content.",
                sources=[],
                session_id=getattr(request, 'session_id', 'default'),
                error=None
            )
        
        print(f"🤖 Processing chat question: {request.question}")
        
        # Get response from RAG chatbot
        response = pipeline.chatbot.ask(
            question=request.question,
            max_sources=3
        )
        
        # Extract sources if available
        sources = []
        if hasattr(response, 'sources') and response.sources:
            sources = [result.url for result in response.sources if hasattr(result, 'url')]
        
        # Extract answer text
        answer = response.answer if hasattr(response, 'answer') else "Sorry, I couldn't generate a response."
        
        return ChatResponse(
            answer=answer,
            sources=sources,
            session_id=getattr(request, 'session_id', 'default'),
            error=response.error if hasattr(response, 'error') else None
        )
        
    except Exception as e:
        error_msg = f"Error processing chat request: {str(e)}"
        print(f"❌ {error_msg}")
        
        return ChatResponse(
            answer="Sorry, I encountered an error while processing your question. Please try again later.",
            sources=[],
            session_id=getattr(request, 'session_id', 'default'),
            error=error_msg
        )

def run_server(host: str = "localhost", port: int = 7000, reload: bool = True):
    """Run the FastAPI server."""
    print(f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    🚀 LEARNING PIPELINE SERVER 🚀                           ║
║                                                                              ║
║  Starting server on: http://{host}:{port}                                 ║
║                                                                              ║
║  API Endpoints:                                                              ║
║  📚 POST /api/find-resources    - Find learning resources                   ║
║  🎨 POST /api/generate-summary  - Generate dashboard                        ║
║  💬 POST /api/chat             - RAG chatbot Q&A                           ║
║  📊 GET  /api/status           - Pipeline status                           ║
║  🌐 GET  /dashboard            - View learning dashboard                    ║
║  🔧 GET  /api/tools            - Available tools                           ║
║                                                                              ║
║  Ready to receive requests from frontend!                                    ║
╚══════════════════════════════════════════════════════════════════════════════╝
""")
    
    uvicorn.run(
        "pipeline:app",
        host=host,
        port=7000,
        reload=reload,
        log_level="info"
    )

if __name__ == "__main__":
    # Run server if script is executed directly
    run_server()
