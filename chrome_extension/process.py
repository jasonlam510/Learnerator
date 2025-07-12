from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from ollama import chat
import json

# Pydantic models for structured output
class Stage(BaseModel):
    header: str
    details: str
    keywords: List[str]  # Added keywords attribute for online searching
    status: str = "pending"

class LearningPlan(BaseModel):
    topic_name: str
    stages: List[Stage]

# Function to generate learning plan using Ollama
def generate_learning_plan(topic: str, model: str = "llama3.2") -> LearningPlan:
    if not topic or not topic.strip():
        raise ValueError("Topic cannot be empty")

    # Define the prompt for Ollama
    prompt = f"""
    You are an educational assistant. Given the topic '{topic}', generate a structured learning plan with:
    
    1. A refined topic name (fix typos, capitalize properly, make concise).
    2. A list of 5-10 stages, each with:
       - A header (concise stage title).
       - A details field (description of what the stage covers).
       - A keywords field (list of 3-5 relevant keywords/phrases for online searching).
       - A status field (set to "pending").
    
    Make sure the learning plan is comprehensive, well-structured, and progresses logically from basic to advanced concepts.
    The keywords should be specific and useful for finding relevant online resources.
    """

    try:
        print(f"🤖 Generating learning plan for: '{topic}' using model: {model}")
        
        response = chat(
            messages=[
                {
                    'role': 'system',
                    'content': 'You are a helpful educational assistant that generates structured JSON output for learning plans.'
                },
                {
                    'role': 'user',
                    'content': prompt
                }
            ],
            model=model,
            format=LearningPlan.model_json_schema()
        )
        print(f"🔍 Response structure: {type(response)}")
        print(f"🔍 Response keys: {response.keys() if isinstance(response, dict) else 'Not a dict'}")
        print(f"🔍 Full response: {response}")
        
        # Parse and validate response using Pydantic
        # Handle different response formats from Ollama
        if isinstance(response, dict):
            if 'message' in response:
                content = response['message'].get('content', '')
            else:
                # Sometimes Ollama returns the content directly
                content = response.get('content', str(response))
        else:
            # If it's an object with attributes
            content = response.message.content if hasattr(response, 'message') else str(response)
        
        print(f"🔍 Extracted content: {content}")
        learning_plan = LearningPlan.model_validate_json(content)
        
        print(f"✅ Successfully generated plan with {len(learning_plan.stages)} stages")
        return learning_plan
        
    except Exception as e:
        print(f"❌ Error generating learning plan: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate learning plan: {str(e)}")

# FastAPI application
app = FastAPI(
    title="Learning Plan Generator with Ollama",
    description="""
    ## Learning Plan Generator API
    
    This API generates structured learning plans for any given topic using Ollama's local LLM models.
    Each learning plan consists of multiple stages with detailed descriptions and search keywords.
    
    ### Features:
    - Generate personalized learning plans for any topic
    - Each stage includes relevant keywords for online research
    - Structured JSON response format using Pydantic models
    - Local LLM processing with Ollama (no API keys required)
    - Error handling for invalid inputs and API failures
    
    ### Prerequisites:
    - Ollama installed and running locally
    - Compatible model pulled (e.g., llama3.2, llama3.2, mistral)
    
    ### Setup Ollama:
    ```bash
    # Install Ollama (visit ollama.ai for instructions)
    # Pull a model
    ollama pull llama3.2
    ```
    """,
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "chrome-extension://*",  # Allow all Chrome extensions
        "http://localhost:3000",  # Allow local backend
        "http://localhost:8000",  # Allow self
    ],
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# Request model for FastAPI endpoint
class TopicRequest(BaseModel):
    topic: str
    model: str = "llama3.2"  # Allow model selection
    
    class Config:
        schema_extra = {
            "example": {
                "topic": "machine learning fundamentals",
                "model": "llama3.2"
            }
        }

@app.post("/generate-plan", response_model=LearningPlan)
async def generate_plan(request: TopicRequest):
    """
    Generate a structured learning plan for a given topic using Ollama.
    
    ## Request Format
    
    Send a POST request with a JSON body containing:
    
    ```json
    {
        "topic": "your learning topic here",
        "model": "llama3.2"
    }
    ```
    
    ### Example Request:
    ```bash
    curl -X POST "http://localhost:8000/generate-plan" \
         -H "Content-Type: application/json" \
         -d '{"topic": "machine learning fundamentals", "model": "llama3.2"}'
    ```
    
    ## Response Format
    
    The API returns a structured learning plan with the following format:
    
    ```json
    {
        "topic_name": "Machine Learning Fundamentals",
        "stages": [
            {
                "header": "Introduction to Machine Learning",
                "details": "Learn the basic concepts and types of machine learning algorithms",
                "keywords": ["machine learning basics", "ML algorithms", "supervised learning"],
                "status": "pending"
            },
            {
                "header": "Data Preprocessing",
                "details": "Understand data cleaning, normalization, and feature engineering",
                "keywords": ["data preprocessing", "feature engineering", "data cleaning"],
                "status": "pending"
            }
        ]
    }
    ```
    
    ### Response Fields:
    - **topic_name**: Refined and properly formatted topic name
    - **stages**: Array of learning stages, each containing:
        - **header**: Concise title for the learning stage
        - **details**: Detailed description of what the stage covers
        - **keywords**: List of 3-5 relevant search terms for online research
        - **status**: Current status (always "pending" for new plans)
    
    ## Error Responses
    
    - **400 Bad Request**: Invalid topic (empty or whitespace-only)
    - **500 Internal Server Error**: Ollama API errors or model not available
    
    ### Example Error Response:
    ```json
    {
        "detail": "Topic cannot be empty"
    }
    ```
    
    ## Available Models
    
    You can use any Ollama model that supports structured output:
    - llama3.2c(recommended)
    - llama3.2
    - mistral
    - codellama
    - And others available in your Ollama installation
    
    Check available models with: `ollama list`
    """
    try:
        plan = generate_learning_plan(request.topic, request.model)
        return plan
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating plan: {str(e)}")

# Additional endpoint to check available models
@app.get("/models")
async def get_available_models():
    """
    Get list of available Ollama models.
    
    Returns a list of models available in your local Ollama installation.
    """
    try:
        import subprocess
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
        if result.returncode == 0:
            # Parse the output to extract model names
            lines = result.stdout.strip().split('\n')[1:]  # Skip header
            models = []
            for line in lines:
                if line.strip():
                    model_name = line.split()[0]
                    models.append(model_name)
            return {"models": models}
        else:
            raise HTTPException(status_code=500, detail="Failed to fetch models from Ollama")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching models: {str(e)}")

# Health check endpoint
@app.get("/health")
async def health_check():
    """
    Health check endpoint to verify the API and Ollama are working.
    """
    try:
        # Test Ollama connection
        response = chat(
            messages=[{"role": "user", "content": "Hello"}],
            model="llama3.2"
        )
        return {
            "status": "healthy",
            "ollama_status": "connected",
            "message": "Learning Plan Generator API is running with Ollama"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "ollama_status": "disconnected",
            "error": str(e),
            "message": "Ollama may not be running or model not available"
        }

# Run the server (for local testing)
if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Learning Plan Generator API with Ollama...")
    print("📚 Make sure Ollama is running: ollama serve")
    print("🤖 Available at: http://localhost:8000")
    print("📖 Documentation: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)