"""
Navigation Generator for Learning Dashboard

Generates navigation components including topic clusters,
learning paths, and overview sections.
"""

import os
import sys
from typing import Dict, List

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from utils.schema import ContentSummary


class NavigationGenerator:
    """Generates navigation and overview HTML components."""
    
    def generate(self, topic_clusters: Dict[str, List[str]]) -> str:
        """Generate complete overview section with navigation elements."""
        
        overview_html = self._generate_overview_cards(topic_clusters)
        learning_paths_html = self._generate_learning_paths_preview()
        stats_html = self._generate_stats_overview(topic_clusters)
        
        return f"""
        <div class="overview-container">
            <div class="welcome-section">
                <h2>🎓 Welcome to Your Learning Dashboard</h2>
                <p class="welcome-text">
                    This interactive dashboard helps you explore and navigate your learning resources. 
                    Discover knowledge connections, track your progress, and test your understanding.
                </p>
            </div>
            
            {stats_html}
            
            <div class="overview-sections">
                <div class="overview-grid">
                    {overview_html}
                </div>
                
                {learning_paths_html}
            </div>
            
            <div class="quick-actions">
                <h3>🚀 Quick Actions</h3>
                <div class="action-buttons">
                    <button onclick="showSection('knowledge-map-section')" class="action-btn primary">
                        🧠 Explore Knowledge Map
                    </button>
                    <button onclick="showSection('resources-section')" class="action-btn secondary">
                        📚 Browse Resources
                    </button>
                    <button onclick="showSection('quiz-section')" class="action-btn accent">
                        📝 Take Quiz
                    </button>
                    <button onclick="exportProgress()" class="action-btn outline">
                        📊 Export Progress
                    </button>
                </div>
            </div>
        </div>
        
        {self._generate_overview_javascript()}
        """
    
    def _generate_overview_cards(self, topic_clusters: Dict[str, List[str]]) -> str:
        """Generate topic cluster overview cards."""
        
        if not topic_clusters:
            return '<div class="no-clusters">No topic clusters found.</div>'
        
        cards_html = []
        
        # Define icons and colors for different topics
        topic_icons = {
            'Python Development': '🐍',
            'Frontend Development': '🎨',
            'DevOps & Cloud': '☁️',
            'Data Science & ML': '📊',
            'Databases': '🗄️',
            'General Programming': '💻',
            'Web Development': '🌐',
            'Mobile Development': '📱',
            'AI & Machine Learning': '🤖',
            'Backend Development': '⚙️'
        }
        
        topic_colors = {
            'Python Development': 'python-color',
            'Frontend Development': 'frontend-color',
            'DevOps & Cloud': 'devops-color',
            'Data Science & ML': 'datascience-color',
            'Databases': 'database-color',
            'General Programming': 'general-color',
            'Web Development': 'web-color',
            'Mobile Development': 'mobile-color',
            'AI & Machine Learning': 'ai-color',
            'Backend Development': 'backend-color'
        }
        
        for cluster_name, urls in topic_clusters.items():
            icon = topic_icons.get(cluster_name, '📁')
            color_class = topic_colors.get(cluster_name, 'default-color')
            
            card_html = f"""
            <div class="topic-card {color_class}" onclick="filterResourcesByTopic('{cluster_name}')">
                <div class="topic-icon">{icon}</div>
                <div class="topic-content">
                    <h4>{cluster_name}</h4>
                    <p>{len(urls)} resource{'' if len(urls) == 1 else 's'}</p>
                    <div class="topic-preview">
                        <small>Click to explore resources</small>
                    </div>
                </div>
                <div class="topic-arrow">→</div>
            </div>
            """
            cards_html.append(card_html)
        
        return "".join(cards_html)
    
    def _generate_learning_paths_preview(self) -> str:
        """Generate learning paths preview section."""
        
        return f"""
        <div class="learning-paths-preview">
            <h3>🛤️ Suggested Learning Paths</h3>
            <p class="paths-description">
                Follow these curated learning paths to build your knowledge systematically.
            </p>
            
            <div class="path-cards">
                <div class="path-card beginner">
                    <div class="path-header">
                        <span class="path-icon">🌱</span>
                        <h4>Beginner Path</h4>
                    </div>
                    <p>Start with fundamentals and basic concepts</p>
                    <div class="path-steps">
                        <span class="step">Basics</span>
                        <span class="step-arrow">→</span>
                        <span class="step">Practice</span>
                        <span class="step-arrow">→</span>
                        <span class="step">Projects</span>
                    </div>
                </div>
                
                <div class="path-card intermediate">
                    <div class="path-header">
                        <span class="path-icon">🚀</span>
                        <h4>Intermediate Path</h4>
                    </div>
                    <p>Build on existing knowledge with advanced topics</p>
                    <div class="path-steps">
                        <span class="step">Concepts</span>
                        <span class="step-arrow">→</span>
                        <span class="step">Implementation</span>
                        <span class="step-arrow">→</span>
                        <span class="step">Optimization</span>
                    </div>
                </div>
                
                <div class="path-card advanced">
                    <div class="path-header">
                        <span class="path-icon">🎯</span>
                        <h4>Advanced Path</h4>
                    </div>
                    <p>Master complex topics and best practices</p>
                    <div class="path-steps">
                        <span class="step">Architecture</span>
                        <span class="step-arrow">→</span>
                        <span class="step">Patterns</span>
                        <span class="step-arrow">→</span>
                        <span class="step">Mastery</span>
                    </div>
                </div>
            </div>
            
            <button class="view-all-paths" onclick="showDetailedPaths()">
                View Detailed Learning Paths
            </button>
        </div>
        """
    
    def _generate_stats_overview(self, topic_clusters: Dict[str, List[str]]) -> str:
        """Generate statistics overview section."""
        
        total_resources = sum(len(urls) for urls in topic_clusters.values())
        total_topics = len(topic_clusters)
        
        return f"""
        <div class="stats-overview">
            <div class="stat-card">
                <div class="stat-icon">📚</div>
                <div class="stat-content">
                    <h3>{total_resources}</h3>
                    <p>Learning Resources</p>
                </div>
            </div>
            
            <div class="stat-card">
                <div class="stat-icon">🎯</div>
                <div class="stat-content">
                    <h3>{total_topics}</h3>
                    <p>Topic Areas</p>
                </div>
            </div>
            
            <div class="stat-card">
                <div class="stat-icon">🔗</div>
                <div class="stat-content">
                    <h3 id="connection-count">0</h3>
                    <p>Knowledge Connections</p>
                </div>
            </div>
            
            <div class="stat-card">
                <div class="stat-icon">📈</div>
                <div class="stat-content">
                    <h3 id="progress-percentage">0%</h3>
                    <p>Completion Progress</p>
                </div>
            </div>
        </div>
        """
    
    def _generate_overview_javascript(self) -> str:
        """Generate JavaScript for overview functionality."""
        
        return """
        <script>
        // Overview functionality
        function filterResourcesByTopic(topicName) {
            // Switch to resources section
            showSection('resources-section');
            
            // Filter resources by topic (this would integrate with the content cards component)
            setTimeout(() => {
                const event = new CustomEvent('filterByTopic', { detail: { topic: topicName } });
                document.dispatchEvent(event);
            }, 300);
        }
        
        function showDetailedPaths() {
            // This could open a modal or expand the paths section
            alert('Detailed learning paths feature coming soon!');
        }
        
        function exportProgress() {
            // Generate a progress report
            const progressData = {
                timestamp: new Date().toISOString(),
                totalResources: document.querySelectorAll('.content-card').length,
                completedQuizzes: 0, // This would be tracked
                topicsExplored: document.querySelectorAll('.topic-card').length
            };
            
            const dataStr = JSON.stringify(progressData, null, 2);
            const dataBlob = new Blob([dataStr], {type: 'application/json'});
            
            const link = document.createElement('a');
            link.href = URL.createObjectURL(dataBlob);
            link.download = 'learning-progress.json';
            link.click();
        }
        
        // Update connection count when knowledge map is loaded
        function updateConnectionCount(count) {
            document.getElementById('connection-count').textContent = count;
        }
        
        // Update progress percentage based on quiz results or other metrics
        function updateProgressPercentage(percentage) {
            document.getElementById('progress-percentage').textContent = percentage + '%';
        }
        
        // Initialize overview
        document.addEventListener('DOMContentLoaded', function() {
            // Any initialization for the overview section
            console.log('Overview section initialized');
            
            // Listen for knowledge map updates
            document.addEventListener('knowledgeMapLoaded', function(event) {
                if (event.detail && event.detail.connectionCount) {
                    updateConnectionCount(event.detail.connectionCount);
                }
            });
            
            // Listen for quiz completion
            document.addEventListener('quizCompleted', function(event) {
                if (event.detail && event.detail.percentage) {
                    updateProgressPercentage(event.detail.percentage);
                }
            });
        });
        </script>
        """
