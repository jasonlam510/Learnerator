"""
Generate a comprehensive summary of the learning resources stored in the vector database.

This script analyzes all stored content, generates summaries, identifies relationships,
and creates an interactive HTML report.
"""

import os
from datetime import datetime
from content_analyzer import ContentAnalyzer
from summary_module.html_generator import HTMLSummaryGenerator


def main():
    """Generate comprehensive learning resource summary."""
    
    print("🚀 Starting Learning Resource Analysis...")
    
    # Initialize analyzer
    analyzer = ContentAnalyzer()
    
    # Connect to database
    if not analyzer.connect_database():
        print("❌ Could not connect to vector database. Please ensure Milvus is running.")
        return
    
    # Generate complete database summary
    print("\n📊 Analyzing database content...")
    try:
        summary = analyzer.generate_complete_summary()
        
        print(f"\n✅ Analysis complete!")
        print(f"   📚 Sources analyzed: {summary.total_sources}")
        print(f"   🔗 Knowledge relationships: {len(summary.knowledge_map)}")
        print(f"   🎯 Topic clusters: {len(summary.topic_clusters)}")
        print(f"   🛤️ Learning paths: {len(summary.learning_paths)}")
        
        # Generate HTML summary
        print("\n🎨 Generating HTML summary...")
        html_generator = HTMLSummaryGenerator()
        
        # Create output filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"learning_summary_{timestamp}.html"
        
        html_file = html_generator.generate_html_summary(summary, output_file)
        
        print(f"\n🎉 Summary generated successfully!")
        print(f"   📄 HTML file: {html_file}")
        print(f"   🌐 Open in browser to view interactive summary")
        
        # Print quick overview
        print("\n📋 Quick Overview:")
        print("=" * 50)
        
        for i, content_summary in enumerate(summary.content_summaries, 1):
            print(f"\n{i}. {content_summary.title}")
            print(f"   URL: {content_summary.source_url}")
            print(f"   Type: {content_summary.content_type}")
            print(f"   Difficulty: {content_summary.difficulty_level}")
            print(f"   Topics: {', '.join(content_summary.key_topics[:3])}...")
            print(f"   Summary: {content_summary.summary[:100]}...")
        
        if summary.knowledge_map:
            print(f"\n🔗 Key Knowledge Relationships:")
            for rel in summary.knowledge_map[:5]:  # Show top 5
                print(f"   • {rel.source_concept} → {rel.target_concept} ({rel.relationship_type})")
        
        if summary.topic_clusters:
            print(f"\n🎯 Main Topic Clusters:")
            for topic, sources in list(summary.topic_clusters.items())[:3]:  # Show top 3
                print(f"   • {topic}: {len(sources)} resources")
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
