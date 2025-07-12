"""
Content Cards Generator for Learning Dashboard

Generates HTML cards for displaying learning resource summaries.
"""

import os
import sys
from typing import List

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from utils.schema import ContentSummary


class ContentCardsGenerator:
    """Generates content cards for learning resources."""
    
    def generate(self, content_summaries: List[ContentSummary]) -> str:
        """Generate HTML cards for all content summaries."""
        
        if not content_summaries:
            return self._generate_empty_state()
        
        cards_html = []
        for summary in content_summaries:
            cards_html.append(self._generate_single_card(summary))
        
        return f"""
        <div class="content-cards-container">
            {''.join(cards_html)}
        </div>
        """
    
    def _generate_single_card(self, summary: ContentSummary) -> str:
        """Generate HTML for a single content card."""
        
        # Generate tags for key concepts
        concept_tags = ''.join([
            f'<span class="tag {self._get_topic_color_class(summary.topic_category)}">{concept}</span>'
            for concept in summary.key_concepts[:5]  # Limit to 5 concepts
        ])
        
        # Generate practical examples
        examples_html = ""
        if summary.practical_examples:
            examples_list = ''.join([
                f'<li>{example}</li>' for example in summary.practical_examples[:3]
            ])
            examples_html = f"""
            <div class="practical-examples">
                <h5>🛠️ Practical Examples:</h5>
                <ul>{examples_list}</ul>
            </div>
            """
        
        # Generate real-world summary
        real_world_html = ""
        if summary.real_world_summary:
            real_world_html = f"""
            <div class="real-world-summary">
                <h5>🌍 Real-World Application:</h5>
                <p>{summary.real_world_summary}</p>
            </div>
            """
        
        return f"""
        <div class="content-card">
            <div class="card-header">
                <div>
                    <h3 class="card-title">{summary.title}</h3>
                    <p class="card-subtitle">{summary.source_type.title()} • {summary.topic_category.title()}</p>
                </div>
                <span class="card-type-badge">{summary.source_type}</span>
            </div>
            
            <div class="card-content">
                <div class="summary-text">
                    <p>{summary.summary}</p>
                </div>
                
                {examples_html}
                
                {real_world_html}
                
                <div class="key-concepts">
                    <h5>🔑 Key Concepts:</h5>
                    <div class="concepts-tags">
                        {concept_tags}
                    </div>
                </div>
            </div>
            
            <div class="card-footer">
                <div class="source-info">
                    <a href="{summary.url}" target="_blank" rel="noopener noreferrer">
                        📖 View Source
                    </a>
                </div>
                <div class="metadata">
                    Added: {summary.date_added.strftime('%Y-%m-%d') if summary.date_added else 'Unknown'}
                </div>
            </div>
        </div>
        """
    
    def _get_topic_color_class(self, topic: str) -> str:
        """Get CSS color class based on topic category."""
        
        topic_colors = {
            'python': 'python-color',
            'frontend': 'frontend-color', 
            'devops': 'devops-color',
            'data science': 'datascience-color',
            'database': 'database-color',
            'web': 'web-color',
            'mobile': 'mobile-color',
            'ai': 'ai-color',
            'backend': 'backend-color'
        }
        
        return topic_colors.get(topic.lower(), 'general-color')
    
    def _generate_empty_state(self) -> str:
        """Generate empty state when no content is available."""
        
        return """
        <div class="empty-state">
            <div class="empty-state-content">
                <h3>📚 No Learning Resources Found</h3>
                <p>Add some learning resources to see them displayed here.</p>
                <div class="empty-state-actions">
                    <button class="btn btn-primary" onclick="location.reload()">
                        🔄 Refresh Dashboard
                    </button>
                </div>
            </div>
        </div>
        """
