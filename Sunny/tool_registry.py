"""
OpenAI Function Calling Schema for Learning Resource Discovery Tool
"""

import json
from typing import Dict, List, Any
from learning_resource_finder import find_learning_resources

# OpenAI Function Definition - Single function for URL discovery
OPENAI_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "find_learning_resources",
            "description": "Discover educational resources URLs for any topic including basics tutorials and demonstration videos. Returns a list of URLs for learning the specified topic.",
            "parameters": {
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "description": "The topic to learn about (e.g., 'AWS S3', 'Python Pandas', 'React.js', 'Machine Learning')"
                    },
                    "project_purpose": {
                        "type": "string", 
                        "description": "Description of the project or purpose for learning this topic (e.g., 'Build a photo-sharing app with image uploads', 'Analyze sales data for business insights')"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of URLs to return",
                        "minimum": 1,
                        "maximum": 10,
                        "default": 3
                    }
                },
                "required": ["topic", "project_purpose"]
            }
        }
    }
]

def openai_find_learning_resources(topic: str, project_purpose: str, max_results: int = 3) -> Dict[str, Any]:
    """OpenAI function implementation for finding learning resources URLs"""
    try:
        result = find_learning_resources(topic, project_purpose, max_results)
        return {
            "urls": result.get("urls", []),
            "topic": topic,
            "has_basics_tutorial": result.get("has_basics_tutorial", False),
            "has_youtube_demo": result.get("has_youtube_demo", False),
            "total_found": len(result.get("urls", [])),
            "status": "success" if result.get("urls") else "no_results"
        }
    except Exception as e:
        return {
            "urls": [],
            "error": f"Failed to find learning resources: {str(e)}",
            "status": "error"
        }

# Function mapping for OpenAI function calling
OPENAI_FUNCTION_MAP = {
    "find_learning_resources": openai_find_learning_resources
}

def execute_openai_function(function_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Execute an OpenAI function call"""
    if function_name not in OPENAI_FUNCTION_MAP:
        return {"error": f"Unknown function: {function_name}", "status": "error"}
    
    try:
        func = OPENAI_FUNCTION_MAP[function_name]
        return func(**arguments)
    except Exception as e:
        return {"error": f"Function execution failed: {str(e)}", "status": "error"}

def get_openai_tools():
    """Get the tools list for OpenAI function calling"""
    return OPENAI_TOOLS

def process_openai_function_call(function_call):
    """Process an OpenAI function call"""
    function_name = function_call.get("name")
    arguments = json.loads(function_call.get("arguments", "{}"))
    
    return execute_openai_function(function_name, arguments)
