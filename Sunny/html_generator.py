"""
HTML Summary Generator for Learning Resources

Generates beautiful HTML summaries with knowledge relationship diagrams
for frontend display of vector database content.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from content_analyzer import ContentAnalyzer, DatabaseSummary, ContentSummary, KnowledgeRelationship


class HTMLSummaryGenerator:
    """Generates HTML summaries with interactive diagrams."""
    
    def __init__(self):
        self.template_dir = "templates"
        self.output_dir = "generated_summaries"
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Create necessary directories."""
        os.makedirs(self.template_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)
    
    def generate_html_summary(self, summary: DatabaseSummary, output_file: str = None) -> str:
        """Generate complete HTML summary with tabs and diagrams."""
        
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"{self.output_dir}/learning_summary_{timestamp}.html"
        
        html_content = self._generate_html_template(summary)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ HTML summary generated: {output_file}")
        return output_file
    
    def _generate_html_template(self, summary: DatabaseSummary) -> str:
        """Generate the complete HTML template."""
        
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Learning Resources Summary</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        {self._generate_css()}
    </style>
</head>
<body>
    <div class="container">
        <header class="header">
            <h1>🚀 Learning Resources Summary</h1>
            <div class="stats">
                <div class="stat-item">
                    <span class="stat-number">{summary.total_sources}</span>
                    <span class="stat-label">Sources</span>
                </div>
                <div class="stat-item">
                    <span class="stat-number">{len(summary.knowledge_map)}</span>
                    <span class="stat-label">Relationships</span>
                </div>
                <div class="stat-item">
                    <span class="stat-number">{len(summary.topic_clusters)}</span>
                    <span class="stat-label">Topics</span>
                </div>
                <div class="stat-item">
                    <span class="stat-number">{len(summary.learning_paths)}</span>
                    <span class="stat-label">Learning Paths</span>
                </div>
            </div>
            <p class="generated-date">Generated: {summary.generated_at}</p>
        </header>

        <div class="tabs">
            <button class="tab-button active" onclick="openTab(event, 'overview')">📊 Overview</button>
            <button class="tab-button" onclick="openTab(event, 'sources')">📚 Sources</button>
            <button class="tab-button" onclick="openTab(event, 'relationships')">🔗 Knowledge Map</button>
            <button class="tab-button" onclick="openTab(event, 'clusters')">🎯 Topic Clusters</button>
            <button class="tab-button" onclick="openTab(event, 'paths')">🛤️ Learning Paths</button>
        </div>

        <div id="overview" class="tab-content active">
            {self._generate_overview_tab(summary)}
        </div>

        <div id="sources" class="tab-content">
            {self._generate_sources_tab(summary.content_summaries)}
        </div>

        <div id="relationships" class="tab-content">
            {self._generate_relationships_tab(summary.knowledge_map)}
        </div>

        <div id="clusters" class="tab-content">
            {self._generate_clusters_tab(summary.topic_clusters)}
        </div>

        <div id="paths" class="tab-content">
            {self._generate_paths_tab(summary.learning_paths, summary.content_summaries)}
        </div>
    </div>

    <script>
        {self._generate_javascript(summary)}
    </script>
</body>
</html>"""
    
    def _generate_css(self) -> str:
        """Generate CSS styles for the HTML."""
        
        return """
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }

        .header {
            background: rgba(255, 255, 255, 0.95);
            padding: 30px;
            border-radius: 15px;
            margin-bottom: 30px;
            text-align: center;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }

        .header h1 {
            font-size: 2.5em;
            margin-bottom: 20px;
            background: linear-gradient(45deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .stats {
            display: flex;
            justify-content: center;
            gap: 40px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }

        .stat-item {
            text-align: center;
        }

        .stat-number {
            display: block;
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }

        .stat-label {
            font-size: 0.9em;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .generated-date {
            color: #666;
            font-size: 0.9em;
        }

        .tabs {
            display: flex;
            background: rgba(255, 255, 255, 0.9);
            border-radius: 10px;
            padding: 5px;
            margin-bottom: 20px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
            flex-wrap: wrap;
            gap: 5px;
        }

        .tab-button {
            flex: 1;
            padding: 15px 20px;
            border: none;
            background: transparent;
            cursor: pointer;
            border-radius: 8px;
            font-size: 1em;
            transition: all 0.3s ease;
            min-width: 150px;
        }

        .tab-button:hover {
            background: rgba(102, 126, 234, 0.1);
        }

        .tab-button.active {
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
            font-weight: bold;
        }

        .tab-content {
            display: none;
            background: rgba(255, 255, 255, 0.95);
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            min-height: 500px;
        }

        .tab-content.active {
            display: block;
        }

        .source-card {
            background: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 10px;
            padding: 25px;
            margin-bottom: 20px;
            transition: transform 0.3s ease;
        }

        .source-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
        }

        .source-title {
            font-size: 1.3em;
            font-weight: bold;
            margin-bottom: 15px;
            color: #333;
        }

        .source-url {
            color: #667eea;
            text-decoration: none;
            font-size: 0.9em;
            margin-bottom: 15px;
            display: block;
            word-break: break-all;
        }

        .source-url:hover {
            text-decoration: underline;
        }

        .source-meta {
            display: flex;
            gap: 20px;
            margin-bottom: 15px;
            flex-wrap: wrap;
        }

        .meta-item {
            background: #667eea;
            color: white;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.8em;
        }

        .topics {
            margin-bottom: 15px;
        }

        .topic-tag {
            display: inline-block;
            background: #e9ecef;
            color: #495057;
            padding: 5px 10px;
            border-radius: 15px;
            font-size: 0.8em;
            margin: 2px;
        }

        .objectives {
            background: #f1f3f4;
            border-left: 4px solid #667eea;
            padding: 15px;
            margin: 15px 0;
        }

        .objectives h4 {
            margin-bottom: 10px;
            color: #333;
        }

        .objectives ul {
            margin-left: 20px;
        }

        .summary-text {
            color: #555;
            line-height: 1.6;
            margin-top: 15px;
        }

        .cluster-section {
            margin-bottom: 30px;
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
        }

        .cluster-title {
            font-size: 1.4em;
            font-weight: bold;
            margin-bottom: 15px;
            color: #333;
        }

        .cluster-resources {
            display: grid;
            gap: 10px;
        }

        .cluster-resource {
            background: white;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }

        .learning-path {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
        }

        .path-title {
            font-size: 1.2em;
            font-weight: bold;
            margin-bottom: 15px;
            color: #333;
        }

        .path-steps {
            display: flex;
            align-items: center;
            gap: 15px;
            overflow-x: auto;
            padding: 10px 0;
        }

        .path-step {
            background: white;
            padding: 15px;
            border-radius: 8px;
            min-width: 200px;
            text-align: center;
            border: 2px solid #e9ecef;
            position: relative;
        }

        .path-step::after {
            content: '→';
            position: absolute;
            right: -25px;
            top: 50%;
            transform: translateY(-50%);
            font-size: 1.5em;
            color: #667eea;
        }

        .path-step:last-child::after {
            display: none;
        }

        .diagram-container {
            background: white;
            border-radius: 10px;
            padding: 20px;
            margin: 20px 0;
            min-height: 400px;
        }

        #knowledge-graph {
            width: 100%;
            height: 500px;
            border: 1px solid #e9ecef;
            border-radius: 8px;
        }

        .node {
            fill: #667eea;
            stroke: #fff;
            stroke-width: 2px;
            cursor: pointer;
        }

        .node:hover {
            fill: #5a67d8;
        }

        .link {
            stroke: #999;
            stroke-opacity: 0.6;
            stroke-width: 2px;
        }

        .node-label {
            font-size: 12px;
            fill: #333;
            text-anchor: middle;
            pointer-events: none;
        }

        .overview-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }

        .overview-card {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            border-left: 4px solid #667eea;
        }

        .overview-card h3 {
            margin-bottom: 15px;
            color: #333;
        }

        .no-content {
            text-align: center;
            color: #666;
            font-style: italic;
            padding: 40px;
        }

        @media (max-width: 768px) {
            .stats {
                gap: 20px;
            }
            
            .source-meta {
                flex-direction: column;
                gap: 10px;
            }
            
            .path-steps {
                flex-direction: column;
            }
            
            .path-step::after {
                content: '↓';
                right: 50%;
                bottom: -25px;
                top: auto;
                transform: translateX(50%);
            }
        }
        """
    
    def _generate_overview_tab(self, summary: DatabaseSummary) -> str:
        """Generate the overview tab content."""
        
        return f"""
        <h2>📊 Overview</h2>
        <p>This summary analyzes {summary.total_sources} learning resources stored in your vector database, 
        identifying key topics, relationships, and learning paths.</p>
        
        <div class="overview-grid">
            <div class="overview-card">
                <h3>📚 Content Distribution</h3>
                <ul>
                    {"".join([f"<li>{content.content_type.title()}: {sum(1 for c in summary.content_summaries if c.content_type == content.content_type)} resources</li>" 
                             for content in summary.content_summaries])}
                </ul>
            </div>
            
            <div class="overview-card">
                <h3>🎯 Difficulty Levels</h3>
                <ul>
                    {"".join([f"<li>{level}: {sum(1 for c in summary.content_summaries if c.difficulty_level == level)} resources</li>" 
                             for level in ['Beginner', 'Intermediate', 'Advanced']])}
                </ul>
            </div>
            
            <div class="overview-card">
                <h3>🔗 Top Relationships</h3>
                <ul>
                    {"".join([f"<li>{rel.source_concept} → {rel.target_concept}</li>" 
                             for rel in sorted(summary.knowledge_map, key=lambda x: x.strength, reverse=True)[:5]])}
                </ul>
            </div>
            
            <div class="overview-card">
                <h3>⏱️ Time Estimates</h3>
                <ul>
                    {"".join([f"<li>{time}: {sum(1 for c in summary.content_summaries if c.estimated_time == time)} resources</li>" 
                             for time in set(c.estimated_time for c in summary.content_summaries)])}
                </ul>
            </div>
        </div>
        """
    
    def _generate_sources_tab(self, summaries: List[ContentSummary]) -> str:
        """Generate the sources tab content."""
        
        if not summaries:
            return '<div class="no-content">No content sources found.</div>'
        
        sources_html = "<h2>📚 Content Sources</h2>"
        
        for i, summary in enumerate(summaries, 1):
            objectives_html = ""
            if summary.learning_objectives:
                objectives_html = f"""
                <div class="objectives">
                    <h4>🎯 Learning Objectives:</h4>
                    <ul>
                        {"".join([f"<li>{obj}</li>" for obj in summary.learning_objectives])}
                    </ul>
                </div>
                """
            
            sources_html += f"""
            <div class="source-card">
                <div class="source-title">{i}. {summary.title}</div>
                <a href="{summary.source_url}" target="_blank" class="source-url">{summary.source_url}</a>
                
                <div class="source-meta">
                    <span class="meta-item">📱 {summary.content_type.title()}</span>
                    <span class="meta-item">📊 {summary.difficulty_level}</span>
                    <span class="meta-item">⏱️ {summary.estimated_time}</span>
                    <span class="meta-item">📄 {summary.chunk_count} chunks</span>
                </div>
                
                <div class="topics">
                    <strong>🏷️ Topics:</strong><br>
                    {"".join([f'<span class="topic-tag">{topic}</span>' for topic in summary.key_topics])}
                </div>
                
                {"<div><strong>🧠 Concepts:</strong><br>" + ", ".join(summary.main_concepts) + "</div>" if summary.main_concepts else ""}
                
                {objectives_html}
                
                <div class="summary-text">
                    <strong>📝 Summary:</strong><br>
                    {summary.summary}
                </div>
            </div>
            """
        
        return sources_html
    
    def _generate_relationships_tab(self, relationships: List[KnowledgeRelationship]) -> str:
        """Generate the knowledge relationships tab with interactive diagram."""
        
        if not relationships:
            return '<div class="no-content">No knowledge relationships found.</div>'
        
        return f"""
        <h2>🔗 Knowledge Relationships</h2>
        <p>This diagram shows how concepts from different learning resources relate to each other.</p>
        
        <div class="diagram-container">
            <svg id="knowledge-graph"></svg>
        </div>
        
        <h3>📋 Relationship Details</h3>
        <div style="margin-top: 20px;">
            {"".join([f'''
            <div class="source-card">
                <strong>{rel.source_concept}</strong> 
                <span style="color: #667eea;">--{rel.relationship_type}--></span> 
                <strong>{rel.target_concept}</strong>
                <br>
                <small>Strength: {rel.strength:.2f} | Sources: {len(rel.source_urls)}</small>
            </div>
            ''' for rel in sorted(relationships, key=lambda x: x.strength, reverse=True)])}
        </div>
        """
    
    def _generate_clusters_tab(self, clusters: Dict[str, List[str]]) -> str:
        """Generate the topic clusters tab."""
        
        if not clusters:
            return '<div class="no-content">No topic clusters found.</div>'
        
        clusters_html = "<h2>🎯 Topic Clusters</h2>"
        clusters_html += "<p>Learning resources grouped by related topics and technologies.</p>"
        
        for cluster_name, urls in clusters.items():
            clusters_html += f"""
            <div class="cluster-section">
                <div class="cluster-title">📚 {cluster_name}</div>
                <div class="cluster-resources">
                    {"".join([f'<div class="cluster-resource">🔗 {url}</div>' for url in urls])}
                </div>
            </div>
            """
        
        return clusters_html
    
    def _generate_paths_tab(self, paths: List[List[str]], summaries: List[ContentSummary]) -> str:
        """Generate the learning paths tab."""
        
        if not paths:
            return '<div class="no-content">No learning paths found.</div>'
        
        # Create a mapping from URL to summary for easy lookup
        url_to_summary = {s.source_url: s for s in summaries}
        
        paths_html = "<h2>🛤️ Suggested Learning Paths</h2>"
        paths_html += "<p>Recommended sequences for learning based on difficulty and prerequisites.</p>"
        
        for i, path in enumerate(paths, 1):
            # Determine path topic based on first resource
            first_url = path[0] if path else ""
            first_summary = url_to_summary.get(first_url)
            path_topic = "Learning Path"
            
            if first_summary and first_summary.key_topics:
                path_topic = f"{first_summary.key_topics[0].title()} Learning Path"
            
            paths_html += f"""
            <div class="learning-path">
                <div class="path-title">Path {i}: {path_topic}</div>
                <div class="path-steps">
                    {"".join([f'''
                    <div class="path-step">
                        <div style="font-weight: bold; margin-bottom: 5px;">
                            {url_to_summary.get(url, type('', (), {'title': 'Unknown', 'difficulty_level': 'Unknown'})).title[:30]}...
                        </div>
                        <div style="font-size: 0.8em; color: #666;">
                            {url_to_summary.get(url, type('', (), {'difficulty_level': 'Unknown'})).difficulty_level}
                        </div>
                    </div>
                    ''' for url in path])}
                </div>
            </div>
            """
        
        return paths_html
    
    def _generate_javascript(self, summary: DatabaseSummary) -> str:
        """Generate JavaScript for interactivity."""
        
        # Prepare data for D3.js knowledge graph
        nodes = []
        links = []
        node_set = set()
        
        for rel in summary.knowledge_map:
            if rel.source_concept not in node_set:
                nodes.append({"id": rel.source_concept, "group": 1})
                node_set.add(rel.source_concept)
            
            if rel.target_concept not in node_set:
                nodes.append({"id": rel.target_concept, "group": 1})
                node_set.add(rel.target_concept)
            
            links.append({
                "source": rel.source_concept,
                "target": rel.target_concept,
                "value": rel.strength * 10
            })
        
        return f"""
        function openTab(evt, tabName) {{
            var i, tabcontent, tablinks;
            tabcontent = document.getElementsByClassName("tab-content");
            for (i = 0; i < tabcontent.length; i++) {{
                tabcontent[i].classList.remove("active");
            }}
            tablinks = document.getElementsByClassName("tab-button");
            for (i = 0; i < tablinks.length; i++) {{
                tablinks[i].classList.remove("active");
            }}
            document.getElementById(tabName).classList.add("active");
            evt.currentTarget.classList.add("active");
            
            // Initialize knowledge graph when relationships tab is opened
            if (tabName === 'relationships') {{
                setTimeout(initKnowledgeGraph, 100);
            }}
        }}
        
        function initKnowledgeGraph() {{
            const svg = d3.select("#knowledge-graph");
            svg.selectAll("*").remove(); // Clear previous graph
            
            const width = svg.node().getBoundingClientRect().width;
            const height = 500;
            
            const data = {{
                nodes: {json.dumps(nodes)},
                links: {json.dumps(links)}
            }};
            
            if (data.nodes.length === 0) {{
                svg.append("text")
                   .attr("x", width / 2)
                   .attr("y", height / 2)
                   .attr("text-anchor", "middle")
                   .attr("fill", "#666")
                   .text("No relationships to visualize");
                return;
            }}
            
            const simulation = d3.forceSimulation(data.nodes)
                .force("link", d3.forceLink(data.links).id(d => d.id).distance(100))
                .force("charge", d3.forceManyBody().strength(-300))
                .force("center", d3.forceCenter(width / 2, height / 2));
            
            const link = svg.append("g")
                .attr("class", "links")
                .selectAll("line")
                .data(data.links)
                .enter().append("line")
                .attr("class", "link")
                .attr("stroke-width", d => Math.sqrt(d.value));
            
            const node = svg.append("g")
                .attr("class", "nodes")
                .selectAll("circle")
                .data(data.nodes)
                .enter().append("circle")
                .attr("class", "node")
                .attr("r", 8)
                .call(d3.drag()
                    .on("start", dragstarted)
                    .on("drag", dragged)
                    .on("end", dragended));
            
            const label = svg.append("g")
                .attr("class", "labels")
                .selectAll("text")
                .data(data.nodes)
                .enter().append("text")
                .attr("class", "node-label")
                .attr("dy", -12)
                .text(d => d.id);
            
            simulation
                .nodes(data.nodes)
                .on("tick", ticked);
            
            simulation.force("link")
                .links(data.links);
            
            function ticked() {{
                link
                    .attr("x1", d => d.source.x)
                    .attr("y1", d => d.source.y)
                    .attr("x2", d => d.target.x)
                    .attr("y2", d => d.target.y);
                
                node
                    .attr("cx", d => d.x)
                    .attr("cy", d => d.y);
                
                label
                    .attr("x", d => d.x)
                    .attr("y", d => d.y);
            }}
            
            function dragstarted(event, d) {{
                if (!event.active) simulation.alphaTarget(0.3).restart();
                d.fx = d.x;
                d.fy = d.y;
            }}
            
            function dragged(event, d) {{
                d.fx = event.x;
                d.fy = event.y;
            }}
            
            function dragended(event, d) {{
                if (!event.active) simulation.alphaTarget(0);
                d.fx = null;
                d.fy = null;
            }}
        }}
        
        // Initialize the first tab
        document.addEventListener('DOMContentLoaded', function() {{
            // Auto-open overview tab
            document.querySelector('.tab-button').click();
        }});
        """


def main():
    """Test the HTML generator."""
    
    print("🎨 HTML SUMMARY GENERATOR TEST")
    print("=" * 40)
    
    # Generate content analysis
    analyzer = ContentAnalyzer()
    summary = analyzer.generate_complete_summary()
    
    if summary:
        # Generate HTML
        generator = HTMLSummaryGenerator()
        html_file = generator.generate_html_summary(summary)
        
        print(f"\n🎉 HTML summary generated successfully!")
        print(f"📁 File: {html_file}")
        print(f"🌐 Open in browser to view the interactive summary")
        
        return html_file
    else:
        print("❌ Failed to generate summary")
        return None


if __name__ == "__main__":
    main()
