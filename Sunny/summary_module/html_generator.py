"""
Main HTML Generator for Learning Resource Dashboard

This module coordinates the generation of HTML components and creates
the final interactive dashboard.
"""

import os
import sys
from typing import Optional
from datetime import datetime

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import required modules
from utils.schema import DatabaseSummary
from summary_module.html_components.knowledge_diagram import KnowledgeDiagramGenerator
from summary_module.html_components.content_cards import ContentCardsGenerator
from summary_module.html_components.quiz_interface import QuizInterfaceGenerator
from summary_module.html_components.navigation import NavigationGenerator
from summary_module.html_components.styles import StylesGenerator


class LearningDashboardGenerator:
    """Main generator for the learning resource dashboard."""
    
    def __init__(self):
        self.knowledge_diagram = KnowledgeDiagramGenerator()
        self.content_cards = ContentCardsGenerator()
        self.quiz_interface = QuizInterfaceGenerator()
        self.navigation = NavigationGenerator()
        self.styles = StylesGenerator()
    
    def generate_complete_dashboard(self, summary: DatabaseSummary, include_quiz: bool = True, output_file: str = "learning_dashboard.html") -> bool:
        """Generate the complete interactive learning dashboard."""
        
        print("🚀 Generating Learning Resource Dashboard...")
        print("=" * 50)
        
        if not summary:
            print("❌ No summary provided")
            return False
        
        # Generate HTML components
        print("🎨 Generating HTML components...")
        
        try:
            # Generate each component with error handling
            print("  🧠 Generating knowledge diagram...")
            knowledge_diagram_html = self.knowledge_diagram.generate(summary.knowledge_map, summary.content_summaries)
            
            print("  📚 Generating content cards...")
            content_cards_html = self.content_cards.generate(summary.content_summaries)
            
            print("  🧭 Generating navigation...")
            navigation_html = self.navigation.generate(summary.topic_clusters)
            
            print("  🎨 Generating styles...")
            styles_css = self.styles.generate_all_styles()
            
            quiz_html = ""
            if summary.quiz:
                print("  📝 Generating quiz interface...")
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
            print(f"🔗 Mapped {len(summary.knowledge_map.relationships)} relationships")
            if summary.quiz:
                print(f"📝 Generated {len(summary.quiz.questions)} quiz questions")
            
            return True
            
        except Exception as e:
            print(f"❌ Error generating dashboard: {e}")
            import traceback
            traceback.print_exc()
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
                <span class="stat">🔗 {len(summary.knowledge_map.relationships)} Connections</span>
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
    """Test the dashboard generator with mock data."""
    
    from utils.schema import DatabaseSummary, KnowledgeMap, ConceptRelationship, Quiz, QuizQuestion, MOCK_CONTENT_SUMMARIES
    
    # Create mock data for testing
    mock_relationships = [
        ConceptRelationship(
            concept_a="variables",
            concept_b="functions",
            relationship_type="prerequisite",
            description="Variables are needed to understand function parameters",
            strength=0.8
        ),
        ConceptRelationship(
            concept_a="functions",
            concept_b="loops",
            relationship_type="builds_on",
            description="Functions can contain loops for iteration",
            strength=0.7
        )
    ]
    
    mock_quiz = Quiz(
        title="Python Fundamentals Quiz",
        description="Test your understanding of Python basics",
        questions=[
            QuizQuestion(
                question="What is a variable in Python?",
                options=[
                    "A container that stores data values",
                    "A type of loop",
                    "A function parameter",
                    "A Python keyword"
                ],
                correct_answer=0,
                explanation="A variable is a named container that stores data values and can be referenced later in the program.",
                concept="variables",
                source_url="https://docs.python.org/3/tutorial/"
            )
        ],
        passing_score=70,
        estimated_time="10 minutes"
    )
    
    mock_summary = DatabaseSummary(
        total_sources=2,
        content_summaries=MOCK_CONTENT_SUMMARIES,
        knowledge_map=KnowledgeMap(relationships=mock_relationships),
        topic_clusters={"Python": ["variables", "functions", "loops"]},
        learning_paths=[["variables", "functions", "loops"]],
        quiz=mock_quiz,
        generated_at="2025-07-12 12:00:00"
    )
    
    generator = LearningDashboardGenerator()
    success = generator.generate_complete_dashboard(
        summary=mock_summary,
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
