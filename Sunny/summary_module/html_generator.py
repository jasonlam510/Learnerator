"""
Main HTML Generator for Learning Resource Dashboard

This module coordinates the generation of HTML components and creates
the final interactive dashboard.
"""

import os
from typing import Optional
from datetime import datetime
from summary_module.content_analyzer import ContentAnalyzer
from utils.schema import DatabaseSummary
from summary_module.html_components.knowledge_diagram import KnowledgeDiagramGenerator
from summary_module.html_components.content_cards import ContentCardsGenerator
from summary_module.html_components.quiz_interface import QuizInterfaceGenerator
from summary_module.html_components.navigation import NavigationGenerator
from summary_module.html_components.styles import StylesGenerator


class LearningDashboardGenerator:
    """Main generator for the learning resource dashboard."""
    
    def __init__(self, db):
        self.analyzer = ContentAnalyzer(db)
        self.knowledge_diagram = KnowledgeDiagramGenerator()
        self.content_cards = ContentCardsGenerator()
        self.quiz_interface = QuizInterfaceGenerator()
        self.navigation = NavigationGenerator()
        self.styles = StylesGenerator()
    
    def generate_complete_dashboard(self, include_quiz: bool = True, output_file: str = "learning_dashboard.html") -> bool:
        """Generate the complete interactive learning dashboard."""
        
        print("🚀 Generating Learning Resource Dashboard...")
        print("=" * 50)
        
        # Analyze content
        print("📊 Analyzing vector database content...")
        summary = self.analyzer.generate_complete_summary(include_quiz=include_quiz)
        
        if not summary:
            print("❌ Failed to analyze content")
            return False
        
        # Generate HTML components
        print("🎨 Generating HTML components...")
        
        try:
            # Generate each component
            knowledge_diagram_html = self.knowledge_diagram.generate(summary.knowledge_map, summary.content_summaries)
            content_cards_html = self.content_cards.generate(summary.content_summaries)
            navigation_html = self.navigation.generate(summary.topic_clusters)
            styles_css = self.styles.generate_all_styles()
            
            quiz_html = ""
            if summary.quiz:
                quiz_html = self.quiz_interface.generate(summary.quiz)
            
            # Combine into final HTML
            final_html = self._generate_main_html(
                summary=summary,
                knowledge_diagram=knowledge_diagram_html,
                content_cards=content_cards_html,
                navigation=navigation_html,
                quiz=quiz_html,
                styles=styles_css
            )
            
            # Write to file
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(final_html)
            
            print(f"✅ Dashboard generated successfully: {output_file}")
            print(f"📊 Included {len(summary.content_summaries)} sources")
            print(f"🔗 Mapped {len(summary.knowledge_map)} relationships")
            if summary.quiz:
                print(f"📝 Generated {len(summary.quiz.questions)} quiz questions")
            
            return True
            
        except Exception as e:
            print(f"❌ Error generating dashboard: {e}")
            return False
    
    def _generate_main_html(self, summary: DatabaseSummary, knowledge_diagram: str, 
                           content_cards: str, navigation: str, quiz: str, styles: str) -> str:
        """Generate the main HTML structure."""
        
        quiz_tab = ""
        quiz_content = ""
        if quiz:
            quiz_tab = '<li><a href="#quiz-section" onclick="showSection(\'quiz-section\')">📝 Quiz</a></li>'
            quiz_content = f'<div id="quiz-section" class="content-section" style="display: none;">{quiz}</div>'
        
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Learning Resource Dashboard</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        {styles}
    </style>
</head>
<body>
    <div class="dashboard-container">
        <!-- Header -->
        <header class="dashboard-header">
            <h1>🎓 Learning Resource Dashboard</h1>
            <p class="subtitle">Interactive knowledge map and learning resources</p>
            <div class="stats">
                <span class="stat">📚 {summary.total_sources} Sources</span>
                <span class="stat">🔗 {len(summary.knowledge_map)} Connections</span>
                <span class="stat">🎯 {len(summary.topic_clusters)} Topics</span>
                {f'<span class="stat">📝 {len(summary.quiz.questions)} Quiz Questions</span>' if summary.quiz else ''}
            </div>
        </header>

        <!-- Navigation -->
        <nav class="dashboard-nav">
            <ul>
                <li><a href="#overview-section" onclick="showSection('overview-section')" class="active">🏠 Overview</a></li>
                <li><a href="#knowledge-map-section" onclick="showSection('knowledge-map-section')">🧠 Knowledge Map</a></li>
                <li><a href="#resources-section" onclick="showSection('resources-section')">📚 Resources</a></li>
                {quiz_tab}
            </ul>
        </nav>

        <!-- Main Content -->
        <main class="dashboard-main">
            <!-- Overview Section -->
            <div id="overview-section" class="content-section">
                {navigation}
            </div>

            <!-- Knowledge Map Section -->
            <div id="knowledge-map-section" class="content-section" style="display: none;">
                <h2>🧠 Interactive Knowledge Map</h2>
                <p class="section-description">
                    Explore the relationships between different concepts and technologies.
                    Click on nodes to see details, hover over edges to see connection descriptions.
                </p>
                {knowledge_diagram}
            </div>

            <!-- Resources Section -->
            <div id="resources-section" class="content-section" style="display: none;">
                <h2>📚 Learning Resources</h2>
                <p class="section-description">
                    Detailed breakdown of each learning resource with practical examples and key concepts.
                </p>
                {content_cards}
            </div>

            {quiz_content}
        </main>

        <!-- Footer -->
        <footer class="dashboard-footer">
            <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 
               <a href="#" onclick="location.reload()">🔄 Refresh</a> | 
               <a href="https://github.com" target="_blank">📖 Documentation</a>
            </p>
        </footer>
    </div>

    <script>
        // Navigation functionality
        function showSection(sectionId) {{
            // Hide all sections
            const sections = document.querySelectorAll('.content-section');
            sections.forEach(section => section.style.display = 'none');
            
            // Show selected section
            document.getElementById(sectionId).style.display = 'block';
            
            // Update navigation
            const navLinks = document.querySelectorAll('.dashboard-nav a');
            navLinks.forEach(link => link.classList.remove('active'));
            document.querySelector(`[href="#${{sectionId}}"]`).classList.add('active');
        }}
        
        // Initialize dashboard
        document.addEventListener('DOMContentLoaded', function() {{
            // Any initialization code here
            console.log('Learning Dashboard loaded successfully');
        }});
    </script>
</body>
</html>"""


def main():
    """Test the dashboard generator."""
    
    generator = LearningDashboardGenerator()
    success = generator.generate_complete_dashboard(
        include_quiz=True,
        output_file="learning_dashboard.html"
    )
    
    if success:
        print("\\n🎉 Dashboard generation complete!")
        print("Open 'learning_dashboard.html' in your browser to view the interactive dashboard")
    else:
        print("\\n❌ Dashboard generation failed")


if __name__ == "__main__":
    main()
