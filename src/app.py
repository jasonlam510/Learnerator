import sys
from pathlib import Path
import os

# Load .env file into os.environ
from dotenv import load_dotenv

project_root = Path.cwd()  # Get the current directory
sys.path.append(str(project_root))

# Look for .env in the project root and load it
dotenv_path = project_root / ".env"
if dotenv_path.exists():
    load_dotenv(dotenv_path)
else:
    load_dotenv()  # fallback to default behavior

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.db_router import router

# Create FastAPI app
app = FastAPI(
    title="LearnFlow API",
    description="A learning management API for the LearnFlow Chrome extension",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your Chrome extension's origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the router
app.include_router(router)

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "LearnFlow API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health"
    }

# Health check at root level
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "message": "LearnFlow API is running"
    }

if __name__ == "__main__":
    # Get port from environment or default to 3000
    port = int(os.getenv("PORT", 3000))
    
    # Run the server
    app = FastAPI()