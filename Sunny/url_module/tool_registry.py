"""
OpenAI Function Calling Schema for Learning Resource Discovery Tool
"""

import json
from typing import Dict, List, Any
from url_module.learning_resource_finder import find_learning_resources

# OpenAI Function Definition - Enhanced function for targeted learning resource discovery
OPENAI_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "find_learning_resources",
            "description": "Discover educational resources URLs for any topic with specific learning objectives. Returns dedicated resources for each learning topic with balanced coverage of YouTube videos and tutorial pages. Ensures one resource per specific topic.",
            "parameters": {
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "description": "The main topic to learn about (e.g., 'javascript fundamentals', 'python data science', 'react.js', 'machine learning')"
                    },
                    "content": {
                        "type": "string", 
                        "description": "Specific learning objectives/features to master. Format as '[item1, item2, item3]' or 'item1, item2, item3'. Examples: '[es6+ features, async/await, promises, arrow functions]' or '[pandas dataframes, matplotlib plotting, numpy arrays]'"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of URLs to return (recommended: number of learning objectives + 2-3 extra)",
                        "minimum": 1,
                        "maximum": 15,
                        "default": 5
                    }
                },
                "required": ["topic", "content"]
            }
        }
    }
]

def openai_find_learning_resources(topic: str, content: str, max_results: int = 5) -> Dict[str, Any]:
    """OpenAI function implementation for finding learning resources URLs with specific objectives"""
    try:
        result = find_learning_resources(topic, content, max_results)
        
        return {
            "urls": result.get("urls", []),
            "topic": topic,
            "learning_objectives": result.get("covered_topics", []),
            "topic_coverage": result.get("topic_coverage", {}),
            "has_basics_tutorial": result.get("has_basics_tutorial", False),
            "has_youtube_demo": result.get("has_youtube_demo", False),
            "total_found": len(result.get("urls", [])),
            "youtube_count": len([url for url in result.get("urls", []) if 'youtube.com' in url]),
            "tutorial_count": len([url for url in result.get("urls", []) if 'youtube.com' not in url]),
            "coverage_ratio": f"{len(result.get('covered_topics', []))}/{len(result.get('covered_topics', []) + [t for t in content.replace('[', '').replace(']', '').split(',') if t.strip() and t.strip() not in result.get('covered_topics', [])])}",
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

def get_tool_examples():
    """Get example usage for the learning resource finder tool"""
    return {
        "javascript_fundamentals": {
            "topic": "javascript fundamentals",
            "content": "[es6+ features, async/await, promises, arrow functions, destructuring]",
            "max_results": 8,
            "description": "Find resources to master modern JavaScript features"
        },
        "python_data_science": {
            "topic": "python data science",
            "content": "[pandas dataframes, matplotlib plotting, numpy arrays, data cleaning]",
            "max_results": 6,
            "description": "Learn Python tools for data analysis and visualization"
        },
        "react_development": {
            "topic": "react.js development",
            "content": "[components, hooks, state management, routing, context api]",
            "max_results": 7,
            "description": "Master React.js for modern web development"
        },
        "aws_cloud": {
            "topic": "aws cloud services",
            "content": "[s3 storage, ec2 instances, lambda functions, rds databases]",
            "max_results": 6,
            "description": "Learn essential AWS services for cloud development"
        }
    }

def validate_learning_content_format(content: str) -> bool:
    """Validate that learning content is in the correct format"""
    if not content or not content.strip():
        return False
    
    # Check for bracketed format
    if content.strip().startswith('[') and content.strip().endswith(']'):
        return True
    
    # Check for comma-separated format
    if ',' in content:
        return True
    
    # Single item is also valid
    return len(content.strip()) > 0

def process_openai_function_call(function_call):
    """Process an OpenAI function call"""
    function_name = function_call.get("name")
    arguments = json.loads(function_call.get("arguments", "{}"))
    
    return execute_openai_function(function_name, arguments)

def demo_cli():
    """Interactive CLI demo for the learning resource finder"""
    print("🚀 Learning Resource Finder - Enhanced Edition")
    print("=" * 60)
    print("Find dedicated resources for specific learning objectives!")
    print()
    
    while True:
        print("📚 Enter learning details (or 'quit' to exit):")
        
        # Get topic
        topic = input("🎯 Main topic (e.g., 'javascript fundamentals'): ").strip()
        if topic.lower() in ['quit', 'exit', 'q']:
            break
        
        # Get learning content
        print("\n📝 Learning objectives format examples:")
        print("  • [es6+ features, async/await, promises, arrow functions]")
        print("  • pandas dataframes, matplotlib plotting, numpy arrays")
        
        content = input("📋 Learning objectives: ").strip()
        if not validate_learning_content_format(content):
            print("⚠️ Invalid format. Please use comma-separated items or [item1, item2, ...]")
            continue
        
        # Get max results
        try:
            max_results = int(input("🔢 Max results (default 5): ") or "5")
            max_results = max(1, min(15, max_results))  # Clamp between 1-15
        except ValueError:
            max_results = 5
        
        print(f"\n🔍 Searching for {topic} resources...")
        print("=" * 60)
        
        # Execute search
        try:
            result = openai_find_learning_resources(topic, content, max_results)
            
            if result.get("status") == "success":
                print(f"✅ Found {result['total_found']} resources!")
                print(f"📺 YouTube: {result['youtube_count']}, 📖 Tutorials: {result['tutorial_count']}")
                print(f"🎯 Coverage: {result['coverage_ratio']}")
                
                print(f"\n📚 Resources:")
                for i, url in enumerate(result['urls'], 1):
                    icon = "📺" if 'youtube.com' in url else "📖"
                    print(f"  {icon} {i}. {url}")
                
                if result.get('learning_objectives'):
                    print(f"\n🎯 Covered objectives:")
                    for obj in result['learning_objectives']:
                        print(f"  ✅ {obj}")
                
            else:
                print(f"❌ {result.get('error', 'No resources found')}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("\n" + "=" * 60)
        continue_search = input("🔄 Search again? (y/n): ").strip().lower()
        if continue_search not in ['y', 'yes']:
            break
    
    print("\n👋 Thanks for using Learning Resource Finder!")

if __name__ == "__main__":
    demo_cli()