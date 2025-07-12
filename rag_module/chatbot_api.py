from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
import logging
import os
from datetime import datetime
from contextlib import asynccontextmanager

# Import our modules
from vector_database import create_learning_vector_db, LearningResourceVectorDB

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables
db: Optional[LearningResourceVectorDB] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize and cleanup database connections."""
    global db
    
    try:
        logger.info("🚀 Starting Learning Resource Chatbot API...")
        
        # Initialize vector database
        db = create_learning_vector_db()
        
        logger.info("✅ Database and chatbot initialized successfully")
        yield
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize: {e}")
        raise
    finally:
        # Cleanup
        if db:
            logger.info("Closing database connections...")

app = FastAPI(
    title="Learning Resource Chatbot API",
    description="AI-powered chatbot for answering questions about stored learning resources",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QuestionRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=1000, description="The question to ask")
    max_sources: int = Field(default=3, ge=1, le=10, description="Maximum number of sources to use")

class SourceInfo(BaseModel):
    title: str
    url: str
    content_type: str
    similarity: float
    content_preview: str

class ChatResponseModel(BaseModel):
    answer: str
    sources: List[SourceInfo]
    confidence: float
    query: str
    timestamp: str
    error: Optional[str] = None

class AddResourceRequest(BaseModel):
    url: str = Field(..., description="URL of the resource to add")
    title: Optional[str] = Field(None, description="Optional custom title for the resource")

# Main chat endpoint
@app.post("/chat", response_model=ChatResponseModel)
async def chat(request: QuestionRequest):
    """Ask a question to the chatbot."""
    try:
        if not db or not db.chatbot:
            raise HTTPException(status_code=503, detail="Chatbot not initialized")
        
        logger.info(f"Processing question: {request.question[:100]}...")
        
        # Get response from chatbot
        response = db.chatbot.ask(request.question, request.max_sources)
        
        # Convert sources to API model
        source_infos = []
        for source in response.sources:
            source_infos.append(SourceInfo(
                title=source.chunk.title,
                url=source.chunk.source_url,
                content_type=source.chunk.content_type,
                similarity=source.similarity,
                content_preview=source.chunk.content[:200] + "..." if len(source.chunk.content) > 200 else source.chunk.content
            ))
        
        return ChatResponseModel(
            answer=response.answer,
            sources=source_infos,
            confidence=response.confidence,
            query=response.query,
            timestamp=datetime.now().isoformat(),
            error=response.error
        )
        
    except Exception as e:
        logger.error(f"Error processing chat request: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing question: {str(e)}")


# Add resource endpoint
@app.post("/add-resource")
async def add_resource(request: AddResourceRequest, background_tasks: BackgroundTasks):
    """Add a new learning resource to the database."""
    try:
        if not db:
            raise HTTPException(status_code=503, detail="Database not initialized")
        
        logger.info(f"Adding resource: {request.url}")
        
        # Add the resource in the background
        def add_resource_task():
            try:
                success = db.add_resource(request.url, request.title)
                if success:
                    logger.info(f"Successfully added resource: {request.url}")
                else:
                    logger.warning(f"Failed to add resource: {request.url}")
            except Exception as e:
                logger.error(f"Error adding resource: {e}")
        
        background_tasks.add_task(add_resource_task)
        
        return {
            "status": "accepted",
            "message": "Resource addition started in background",
            "url": request.url,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error adding resource: {e}")
        raise HTTPException(status_code=500, detail=f"Error adding resource: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Starting Learning Resource Chatbot API Server...")
    print("📊 API Documentation: http://localhost:8000/docs")
    print("🏠 Homepage: http://localhost:8000")
    print("💬 Chat Endpoint: POST http://localhost:8000/chat")
    
    uvicorn.run(
        "chatbot_api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
