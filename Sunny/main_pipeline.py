"""
Main Learning Resource Pipeline

This script orchestrates the complete learning resource pipeline:
1. URL Collection (Web/YouTube)
2. Content Extraction and Embedding
3. Vector Database Storage
4. RAG-based Analysis
5. HTML Dashboard Generation
6. Local Server for Dashboard Viewing

Usage:
    python main_pipeline.py
    
Then open http://localhost:8000 in your browser to view the dashboard.
"""

import os
import sys
import asyncio
import webbrowser
from datetime import datetime
from typing import List, Optional
import http.server
import socketserver
import threading
import time

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

# Import our modules
from url_module.learning_resource_finder import LearningResourceFinder
from rag_module.vector_database import create_learning_vector_db
from summary_module.content_analyzer import ContentAnalyzer
from summary_module.html_generator import LearningDashboardGenerator


class LearningResourcePipeline:
    """Main pipeline orchestrator for the learning resource system."""
    
    def __init__(self):
        self.resource_finder = LearningResourceFinder()
        self.vector_db = None
        self.content_analyzer = ContentAnalyzer()
        self.dashboard_generator = LearningDashboardGenerator()
        self.server_thread = None
        
    async def run_complete_pipeline(self, topics: List[str], 
                                   max_results_per_topic: int = 3,
                                   include_quiz: bool = True,
                                   auto_open_browser: bool = True) -> bool:
        """Run the complete learning resource pipeline."""
        
        print("🚀 Starting Learning Resource Pipeline")
        print("=" * 60)
        
        try:
            # Step 1: Initialize Vector Database
            print("\\n📊 Step 1: Initializing Vector Database...")
            self.vector_db = create_learning_vector_db()
            if not self.vector_db:
                print("❌ Failed to initialize vector database")
                return False
            print("✅ Vector database initialized")
            
            # Step 2: Collect Learning Resources
            print(f"\\n🔍 Step 2: Collecting learning resources for topics: {', '.join(topics)}")
            all_resources = []
            
            for topic in topics:
                print(f"\\n  🎯 Processing topic: {topic}")
                
                # Get web resources
                print("    📄 Finding web resources...")
                web_resources = await self.resource_finder.find_comprehensive_resources(
                    topic=topic,
                    max_results=max_results_per_topic
                )
                
                # Get YouTube resources  
                print("    📺 Finding YouTube resources...")
                youtube_resources = await self.resource_finder.find_youtube_resources(
                    topic=topic,
                    max_results=max_results_per_topic
                )
                
                topic_resources = web_resources + youtube_resources
                all_resources.extend(topic_resources)
                
                print(f"    ✅ Found {len(topic_resources)} resources for {topic}")
            
            print(f"\\n✅ Total resources collected: {len(all_resources)}")
            
            if not all_resources:
                print("⚠️ No resources found. Using mock data for demonstration.")
                return await self._generate_dashboard_with_mock_data(include_quiz, auto_open_browser)
            
            # Step 3: Process and Store Content
            print("\\n📝 Step 3: Processing and storing content...")
            stored_count = 0
            
            for i, resource in enumerate(all_resources, 1):
                try:
                    print(f"    Processing {i}/{len(all_resources)}: {resource.title[:50]}...")
                    
                    if resource.content:
                        # Add to vector database
                        success = self.vector_db.add_content(
                            content=resource.content,
                            metadata={
                                'title': resource.title,
                                'url': resource.url,
                                'source_type': resource.source_type,
                                'topic_category': resource.topic_category,
                                'date_added': datetime.now().isoformat()
                            }
                        )
                        
                        if success:
                            stored_count += 1
                            
                except Exception as e:
                    print(f"    ⚠️ Error processing resource: {e}")
                    continue
            
            print(f"\\n✅ Successfully stored {stored_count} resources in vector database")
            
            # Step 4: Generate Dashboard
            print("\\n🎨 Step 4: Generating interactive dashboard...")
            dashboard_success = self.dashboard_generator.generate_complete_dashboard(
                include_quiz=include_quiz,
                output_file=os.path.join(project_root, "learning_dashboard.html")
            )
            
            if not dashboard_success:
                print("❌ Failed to generate dashboard")
                return False
            
            # Step 5: Start Local Server
            print("\\n🌐 Step 5: Starting local server...")
            server_success = self._start_local_server()
            
            if server_success and auto_open_browser:
                print("\\n🌍 Opening dashboard in browser...")
                time.sleep(2)  # Give server time to start
                webbrowser.open('http://localhost:8000')
            
            print("\\n🎉 Pipeline completed successfully!")
            print("📊 Dashboard available at: http://localhost:8000")
            print("📁 HTML file saved as: learning_dashboard.html")
            print("\\n⏹️ Press Ctrl+C to stop the server")
            
            return True
            
        except Exception as e:
            print(f"\\n❌ Pipeline failed with error: {e}")
            return False
    
    async def _generate_dashboard_with_mock_data(self, include_quiz: bool, auto_open_browser: bool) -> bool:
        """Generate dashboard using mock data when no resources are found."""
        
        print("\\n🎨 Generating dashboard with mock data...")
        
        dashboard_success = self.dashboard_generator.generate_complete_dashboard(
            include_quiz=include_quiz,
            output_file=os.path.join(project_root, "learning_dashboard.html")
        )
        
        if dashboard_success:
            server_success = self._start_local_server()
            
            if server_success and auto_open_browser:
                print("\\n🌍 Opening dashboard in browser...")
                time.sleep(2)
                webbrowser.open('http://localhost:8000')
            
            print("\\n🎉 Mock dashboard generated successfully!")
            print("📊 Dashboard available at: http://localhost:8000")
            return True
        
        return False
    
    def _start_local_server(self, port: int = 8000) -> bool:
        """Start a local HTTP server to serve the dashboard."""
        
        try:
            # Change to project directory for serving files
            os.chdir(project_root)
            
            # Create a custom handler that serves our HTML file as index
            class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
                def do_GET(self):
                    if self.path == '/' or self.path == '/index.html':
                        self.path = '/learning_dashboard.html'
                    return super().do_GET()
                
                def log_message(self, format, *args):
                    # Suppress server logs for cleaner output
                    pass
            
            # Start server in a separate thread
            def run_server():
                with socketserver.TCPServer(("", port), CustomHTTPRequestHandler) as httpd:
                    print(f"✅ Server started on http://localhost:{port}")
                    httpd.serve_forever()
            
            self.server_thread = threading.Thread(target=run_server, daemon=True)
            self.server_thread.start()
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to start server: {e}")
            return False
    
    def add_manual_resources(self, urls: List[str]) -> bool:
        """Add manual URLs to the pipeline."""
        
        print(f"\\n📎 Adding {len(urls)} manual resources...")
        
        if not self.vector_db:
            print("❌ Vector database not initialized")
            return False
        
        added_count = 0
        for url in urls:
            try:
                print(f"  Processing: {url}")
                
                # Determine if it's a YouTube URL
                if 'youtube.com' in url or 'youtu.be' in url:
                    resource = self.resource_finder._process_youtube_video(url)
                else:
                    resource = self.resource_finder._extract_web_content(url)
                
                if resource and resource.content:
                    success = self.vector_db.add_content(
                        content=resource.content,
                        metadata={
                            'title': resource.title,
                            'url': resource.url,
                            'source_type': resource.source_type,
                            'topic_category': resource.topic_category or 'manual',
                            'date_added': datetime.now().isoformat()
                        }
                    )
                    
                    if success:
                        added_count += 1
                        print(f"  ✅ Added: {resource.title}")
                    else:
                        print(f"  ❌ Failed to add: {resource.title}")
                else:
                    print(f"  ⚠️ Could not extract content from: {url}")
                    
            except Exception as e:
                print(f"  ❌ Error processing {url}: {e}")
        
        print(f"\\n✅ Successfully added {added_count}/{len(urls)} manual resources")
        return added_count > 0


def print_welcome():
    """Print welcome message and instructions."""
    
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    🎓 LEARNING RESOURCE PIPELINE 🎓                          ║
║                                                                              ║
║  This pipeline will:                                                         ║
║  1. 🔍 Search for learning resources on specified topics                     ║
║  2. 📺 Find relevant YouTube videos                                          ║
║  3. 🧠 Extract and analyze content using AI                                  ║
║  4. 💾 Store content in vector database for RAG                             ║
║  5. 🎨 Generate interactive HTML dashboard                                    ║
║  6. 🌐 Serve dashboard on localhost:8000                                     ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
""")


async def main():
    """Main function to run the pipeline with user input."""
    
    print_welcome()
    
    pipeline = LearningResourcePipeline()
    
    # Get user input for topics
    print("\\n📋 Topic Selection:")
    print("Enter learning topics (comma-separated) or press Enter for demo topics:")
    print("Example: python programming, machine learning, web development")
    
    user_input = input("Topics: ").strip()
    
    if user_input:
        topics = [topic.strip() for topic in user_input.split(',')]
    else:
        topics = ["python programming", "machine learning", "web development"]
        print(f"Using demo topics: {', '.join(topics)}")
    
    # Get optional manual URLs
    print("\\n🔗 Manual URLs (optional):")
    print("Enter additional URLs (comma-separated) or press Enter to skip:")
    
    manual_urls_input = input("URLs: ").strip()
    manual_urls = []
    if manual_urls_input:
        manual_urls = [url.strip() for url in manual_urls_input.split(',')]
    
    # Configuration
    max_results = 3
    include_quiz = True
    auto_open_browser = True
    
    print(f"\\n⚙️ Configuration:")
    print(f"  📊 Max results per topic: {max_results}")
    print(f"  📝 Include quiz: {include_quiz}")
    print(f"  🌍 Auto-open browser: {auto_open_browser}")
    
    # Run the pipeline
    try:
        success = await pipeline.run_complete_pipeline(
            topics=topics,
            max_results_per_topic=max_results,
            include_quiz=include_quiz,
            auto_open_browser=auto_open_browser
        )
        
        # Add manual URLs if provided
        if manual_urls and success:
            pipeline.add_manual_resources(manual_urls)
            
            # Regenerate dashboard with new content
            print("\\n🔄 Regenerating dashboard with manual resources...")
            pipeline.dashboard_generator.generate_complete_dashboard(
                include_quiz=include_quiz,
                output_file=os.path.join(pipeline.resource_finder.__module__.split('.')[0], "learning_dashboard.html")
            )
        
        if success:
            print("\\n" + "="*60)
            print("🎊 PIPELINE COMPLETED SUCCESSFULLY! 🎊")
            print("="*60)
            print("\\n📱 Next steps:")
            print("  • Open http://localhost:8000 in your browser")
            print("  • Explore the interactive knowledge map")
            print("  • Browse learning resources")
            print("  • Take the generated quiz")
            print("  • Press Ctrl+C to stop the server when done")
            
            # Keep the server running
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\\n\\n👋 Server stopped. Goodbye!")
        else:
            print("\\n❌ Pipeline failed. Please check the logs above for details.")
            
    except KeyboardInterrupt:
        print("\\n\\n⏹️ Pipeline interrupted by user.")
    except Exception as e:
        print(f"\\n❌ Unexpected error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
