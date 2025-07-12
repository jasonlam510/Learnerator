"""
Learning Resource Pipeline Launcher

Simple launcher script for the learning resource pipeline.
Provides common configuration options and easy startup.
"""

import asyncio
import os
import sys
from datetime import datetime

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

from main_pipeline import LearningResourcePipeline


def print_banner():
    """Print application banner."""
    print("""
    ╔════════════════════════════════════════════════════════════╗
    ║           🎓 LEARNING RESOURCE DASHBOARD 🎓                ║
    ║                                                            ║
    ║   AI-Powered Learning Resource Discovery & Analysis        ║
    ║                                                            ║
    ╚════════════════════════════════════════════════════════════╝
    """)


def get_preset_topics():
    """Get preset topic configurations."""
    return {
        "1": {
            "name": "Web Development Fundamentals",
            "topics": ["HTML CSS basics", "JavaScript fundamentals", "React introduction"],
            "description": "Core web development technologies"
        },
        "2": {
            "name": "Python Programming",
            "topics": ["Python basics", "Object oriented programming Python", "Python data structures"],
            "description": "Complete Python programming foundation"
        },
        "3": {
            "name": "Data Science Essentials",
            "topics": ["Python data analysis", "Machine learning basics", "Data visualization"],
            "description": "Essential data science skills"
        },
        "4": {
            "name": "DevOps & Cloud",
            "topics": ["Docker containers", "Kubernetes basics", "AWS fundamentals"],
            "description": "Modern DevOps and cloud technologies"
        },
        "5": {
            "name": "AI & Machine Learning",
            "topics": ["Machine learning algorithms", "Deep learning neural networks", "Natural language processing"],
            "description": "AI and ML concepts and applications"
        }
    }


async def run_preset_configuration(preset_key: str):
    """Run pipeline with preset configuration."""
    
    presets = get_preset_topics()
    preset = presets[preset_key]
    
    print(f"\\n🎯 Running: {preset['name']}")
    print(f"📋 Topics: {', '.join(preset['topics'])}")
    print(f"📝 Description: {preset['description']}")
    
    pipeline = LearningResourcePipeline()
    
    return await pipeline.run_complete_pipeline(
        topics=preset['topics'],
        max_results_per_topic=2,
        include_quiz=True,
        auto_open_browser=True
    )


async def run_custom_configuration():
    """Run pipeline with custom user input."""
    
    print("\\n📝 Custom Configuration")
    print("-" * 30)
    
    # Get topics
    print("Enter learning topics (comma-separated):")
    print("Example: python programming, web development, machine learning")
    topics_input = input("Topics: ").strip()
    
    if not topics_input:
        print("❌ No topics provided")
        return False
    
    topics = [topic.strip() for topic in topics_input.split(',')]
    
    # Get number of results
    print("\\nNumber of results per topic (1-5, default 2):")
    results_input = input("Results: ").strip()
    try:
        max_results = int(results_input) if results_input else 2
        max_results = max(1, min(5, max_results))  # Clamp between 1-5
    except ValueError:
        max_results = 2
    
    # Get quiz preference
    print("\\nInclude quiz generation? (y/n, default y):")
    quiz_input = input("Quiz: ").strip().lower()
    include_quiz = quiz_input != 'n'
    
    print(f"\\n🎯 Custom Configuration:")
    print(f"  📋 Topics: {', '.join(topics)}")
    print(f"  📊 Results per topic: {max_results}")
    print(f"  📝 Include quiz: {include_quiz}")
    
    pipeline = LearningResourcePipeline()
    
    return await pipeline.run_complete_pipeline(
        topics=topics,
        max_results_per_topic=max_results,
        include_quiz=include_quiz,
        auto_open_browser=True
    )


async def main():
    """Main launcher function."""
    
    print_banner()
    
    print("🚀 Welcome to the Learning Resource Pipeline!")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    print("\\n🎯 Choose your learning path:")
    print("-" * 40)
    
    presets = get_preset_topics()
    for key, preset in presets.items():
        print(f"  {key}. {preset['name']}")
        print(f"     {preset['description']}")
        print()
    
    print("  6. Custom Topics (Enter your own)")
    print("  7. Quick Demo (Python basics only)")
    print("  0. Exit")
    
    choice = input("\\nEnter your choice (0-7): ").strip()
    
    try:
        if choice == "0":
            print("👋 Goodbye!")
            return
        
        elif choice in presets:
            success = await run_preset_configuration(choice)
        
        elif choice == "6":
            success = await run_custom_configuration()
        
        elif choice == "7":
            print("\\n🏃‍♂️ Quick Demo Mode")
            pipeline = LearningResourcePipeline()
            success = await pipeline.run_complete_pipeline(
                topics=["python basics"],
                max_results_per_topic=1,
                include_quiz=False,
                auto_open_browser=True
            )
        
        else:
            print("❌ Invalid choice. Please try again.")
            return await main()
        
        if success:
            print("\\n" + "="*60)
            print("🎊 PIPELINE COMPLETED SUCCESSFULLY! 🎊")
            print("="*60)
            print("\\n📊 Your learning dashboard is ready!")
            print("🌐 URL: http://localhost:8000")
            print("📁 File: learning_dashboard.html")
            print("\\n⏹️ Press Ctrl+C to stop the server")
            
            # Keep server running
            try:
                while True:
                    await asyncio.sleep(1)
            except KeyboardInterrupt:
                print("\\n\\n👋 Server stopped. Thanks for using the Learning Resource Pipeline!")
        
        else:
            print("\\n❌ Pipeline failed. Please check the error messages above.")
    
    except KeyboardInterrupt:
        print("\\n\\n⏹️ Interrupted by user. Goodbye!")
    except Exception as e:
        print(f"\\n❌ Unexpected error: {e}")
        print("Please try again or check your configuration.")


if __name__ == "__main__":
    asyncio.run(main())
