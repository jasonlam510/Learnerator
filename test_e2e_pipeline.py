"""
End-to-End Test Runner for Learning Resource Pipeline with Full Features

This script demonstrates the complete pipeline with React focus:
1. Mocks React learning URLs (no full content, just URLs)
2. Adds them to vector database with realistic content
3. Performs RAG analysis with knowledge mapping
4. Generates FULL HTML dashboard with quizzes, diagrams, and navigation
5. Serves it on localhost:8000

Includes: Knowledge Diagrams, Interactive Quizzes, Content Cards, Navigation
Focus: React and Frontend Development
"""

import os
import sys
import time
import threading
import webbrowser
import http.server
import socketserver
from datetime import datetime
from typing import List, Dict, Any

from rag_module.vector_database import LearningResourceVectorDB
from summary_module.content_analyzer import ContentAnalyzer
from summary_module.html_generator import LearningDashboardGenerator

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

# Mock React-focused URLs with realistic content
MOCK_REACT_URLS = [
    "https://react.dev/learn",
    "https://react.dev/learn/thinking-in-react", 
    "https://www.youtube.com/watch?v=Tn6-PIqc4UM",
    "https://reactjs.org/docs/hooks-intro.html",
    "https://www.youtube.com/watch?v=O6P86uwfdR0",
]

class TestRunner:
    """Main test runner for the learning resource pipeline."""
    
    def __init__(self):
        self.db = LearningResourceVectorDB()
        self.server_thread = None
    
    def run_complete_test(self) -> bool:
        """Run the complete end-to-end test."""
        
        print("🧪 Learning Resource Pipeline End-to-End Test")
        print("=" * 60)
        print(f"📅 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # Step 1: Initialize Mock Database
        print("\\n📊 Step 1: Initializing Mock Vector Database...")
        
        # Step 2: Add Mock Learning Resources
        self.db.initialize()
        self.db.process_urls(MOCK_REACT_URLS)
        
        # Step 3: Generate Dashboard
        print("\\n🎨 Step 2: Generating HTML Dashboard...")
        summaryGenerator = ContentAnalyzer(self.db)
        summary = summaryGenerator.generate_complete_summary(include_quiz=True)
        HTMLgenerator = LearningDashboardGenerator()
        success = HTMLgenerator.generate_complete_dashboard(summary)
    
    def _start_local_server(self, port: int = 8000) -> bool:
        """Start local HTTP server."""
        try:
            class CustomHandler(http.server.SimpleHTTPRequestHandler):
                def do_GET(self):
                    if self.path == '/' or self.path == '/index.html':
                        self.path = '/learning_dashboard.html'
                    return super().do_GET()
                
                def log_message(self, format, *args):
                    pass  # Suppress logs
            
            def run_server():
                with socketserver.TCPServer(("", port), CustomHandler) as httpd:
                    print(f"✅ Server running on http://localhost:{port}")
                    httpd.serve_forever()
            
            self.server_thread = threading.Thread(target=run_server, daemon=True)
            self.server_thread.start()
            return True
            
        except Exception as e:
            print(f"❌ Failed to start server: {e}")
            return False


def main():
    """Run the end-to-end test."""
    
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    🧪 LEARNING PIPELINE E2E TEST 🧪                          ║
║                                                                              ║
║  This test demonstrates the complete pipeline using mock data:               ║
║  📚 Mock learning resources → 💾 Vector database → 🧠 RAG analysis          ║
║  🎨 HTML dashboard generation → 🌐 Local server deployment                   ║
║                                                                              ║
║  No external APIs required - pure demonstration mode!                       ║
╚══════════════════════════════════════════════════════════════════════════════╝
""")
    
    runner = TestRunner()
    success = runner.run_complete_test()
    
    if not success:
        print("\\n❌ Test failed. Check the error messages above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
