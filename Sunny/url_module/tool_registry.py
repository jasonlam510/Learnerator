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