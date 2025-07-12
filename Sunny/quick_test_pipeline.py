"""
Quick Test Script for Learning Resource Pipeline

This script tests the main pipeline with minimal setup.
"""

import asyncio
import os
import sys

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

from main_pipeline import LearningResourcePipeline


async def quick_test():
    """Run a quick test of the pipeline."""
    
    print("🧪 Quick Pipeline Test")
    print("=" * 30)
    
    pipeline = LearningResourcePipeline()
    
    # Test with just one topic and minimal results
    test_topics = ["python basics"]
    
    try:
        success = await pipeline.run_complete_pipeline(
            topics=test_topics,
            max_results_per_topic=1,  # Just 1 result for quick testing
            include_quiz=False,  # Skip quiz for faster testing
            auto_open_browser=False  # Don't auto-open browser
        )
        
        if success:
            print("\\n✅ Quick test completed successfully!")
            print("🌐 Dashboard should be available at http://localhost:8000")
            print("📁 Check learning_dashboard.html in the project root")
        else:
            print("\\n❌ Quick test failed")
            
    except Exception as e:
        print(f"\\n❌ Test error: {e}")


if __name__ == "__main__":
    asyncio.run(quick_test())
