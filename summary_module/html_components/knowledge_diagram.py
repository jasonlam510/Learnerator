"""
Knowledge Diagram Generator for Learning Dashboard

Generates interactive D3.js knowledge maps showing relationships between concepts.
"""

import os
import sys
from typing import List, Dict, Any

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from utils.schema import KnowledgeMap, ContentSummary


class KnowledgeDiagramGenerator:
    """Generates interactive knowledge diagrams using D3.js."""
    
    def generate(self, knowledge_map: KnowledgeMap, content_summaries: List[ContentSummary]) -> str:
        """Generate interactive knowledge diagram HTML."""
        
        # Create nodes and links data for D3.js
        nodes_data = self._create_nodes_data(knowledge_map, content_summaries)
        links_data = self._create_links_data(knowledge_map)
        
        return f"""
        <div class="knowledge-map-container">
            <div class="knowledge-map" id="knowledge-map">
                <div class="map-controls">
                    <button class="map-control-btn" onclick="resetZoom()" title="Reset Zoom">🔍</button>
                    <button class="map-control-btn" onclick="toggleLabels()" title="Toggle Labels">🏷️</button>
                    <button class="map-control-btn" onclick="rearrangeLayout()" title="Rearrange">🔄</button>
                </div>
                <div class="map-tooltip" id="map-tooltip"></div>
                <div class="map-legend">
                    <div class="legend-item">
                        <div class="legend-color" style="background: var(--primary-color);"></div>
                        <span>Concept Node</span>
                    </div>
                    <div class="legend-item">
                        <div class="legend-color" style="background: var(--accent-color);"></div>
                        <span>Selected</span>
                    </div>
                    <div class="legend-item">
                        <div class="legend-color" style="background: var(--gray-400);"></div>
                        <span>Connection</span>
                    </div>
                </div>
            </div>
        </div>
        
        <script>
            // Knowledge Map D3.js Implementation
            const nodes = {nodes_data};
            const links = {links_data};
            
            const width = document.getElementById('knowledge-map').clientWidth;
            const height = 600;
            
            const svg = d3.select('#knowledge-map')
                .append('svg')
                .attr('width', width)
                .attr('height', height);
            
            const simulation = d3.forceSimulation(nodes)
                .force('link', d3.forceLink(links).id(d => d.id).distance(100))
                .force('charge', d3.forceManyBody().strength(-300))
                .force('center', d3.forceCenter(width / 2, height / 2));
            
            const link = svg.append('g')
                .selectAll('line')
                .data(links)
                .enter().append('line')
                .attr('class', 'knowledge-link')
                .attr('stroke-width', 2);
            
            const node = svg.append('g')
                .selectAll('circle')
                .data(nodes)
                .enter().append('circle')
                .attr('class', 'knowledge-node')
                .attr('r', d => Math.max(8, Math.min(20, d.importance * 10)))
                .call(d3.drag()
                    .on('start', dragstarted)
                    .on('drag', dragged)
                    .on('end', dragended))
                .on('mouseover', showTooltip)
                .on('mouseout', hideTooltip)
                .on('click', highlightNode);
            
            const label = svg.append('g')
                .selectAll('text')
                .data(nodes)
                .enter().append('text')
                .attr('class', 'node-label')
                .text(d => d.name)
                .attr('dy', 25);
            
            simulation.on('tick', () => {{
                link
                    .attr('x1', d => d.source.x)
                    .attr('y1', d => d.source.y)
                    .attr('x2', d => d.target.x)
                    .attr('y2', d => d.target.y);
                
                node
                    .attr('cx', d => d.x)
                    .attr('cy', d => d.y);
                
                label
                    .attr('x', d => d.x)
                    .attr('y', d => d.y);
            }});
            
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
            
            function showTooltip(event, d) {{
                const tooltip = document.getElementById('map-tooltip');
                tooltip.innerHTML = `
                    <strong>${{d.name}}</strong><br>
                    Topic: ${{d.topic}}<br>
                    Importance: ${{d.importance.toFixed(2)}}<br>
                    Sources: ${{d.sources}}
                `;
                tooltip.style.left = (event.pageX + 10) + 'px';
                tooltip.style.top = (event.pageY - 10) + 'px';
                tooltip.classList.add('visible');
            }}
            
            function hideTooltip() {{
                document.getElementById('map-tooltip').classList.remove('visible');
            }}
            
            function highlightNode(event, d) {{
                // Reset all nodes and links
                node.classed('highlighted', false);
                link.classed('highlighted', false);
                
                // Highlight selected node
                d3.select(this).classed('highlighted', true);
                
                // Highlight connected links and nodes
                link.classed('highlighted', l => l.source === d || l.target === d);
                node.classed('highlighted', n => links.some(l => 
                    (l.source === d && l.target === n) || (l.target === d && l.source === n)
                ));
            }}
            
            function resetZoom() {{
                svg.transition().duration(750).call(
                    d3.zoom().transform,
                    d3.zoomIdentity
                );
            }}
            
            function toggleLabels() {{
                const labels = svg.selectAll('.node-label');
                const isVisible = labels.style('opacity') !== '0';
                labels.transition().duration(300).style('opacity', isVisible ? 0 : 1);
            }}
            
            function rearrangeLayout() {{
                simulation.alpha(1).restart();
            }}
            
            // Add zoom behavior
            svg.call(d3.zoom()
                .extent([[0, 0], [width, height]])
                .scaleExtent([0.1, 4])
                .on('zoom', (event) => {{
                    svg.selectAll('g').attr('transform', event.transform);
                }}));
        </script>
        """
    
    def _create_nodes_data(self, knowledge_map: KnowledgeMap, content_summaries: List[ContentSummary]) -> str:
        """Create nodes data for D3.js visualization."""
        
        # Collect all unique concepts
        concepts = set()
        concept_info = {}
        
        # Add concepts from knowledge map
        for relationship in knowledge_map.relationships:
            concepts.add(relationship.concept_a)
            concepts.add(relationship.concept_b)
        
        # Calculate importance based on frequency and sources
        for summary in content_summaries:
            for concept in summary.key_concepts:
                if concept in concepts:
                    if concept not in concept_info:
                        concept_info[concept] = {'sources': 0, 'topic': summary.topic_category}
                    concept_info[concept]['sources'] += 1
        
        # Create nodes array
        nodes = []
        for i, concept in enumerate(concepts):
            info = concept_info.get(concept, {'sources': 1, 'topic': 'general'})
            nodes.append({
                'id': concept,
                'name': concept,
                'topic': info['topic'],
                'importance': min(1.0, info['sources'] / len(content_summaries)),
                'sources': info['sources']
            })
        
        return str(nodes).replace("'", '"')
    
    def _create_links_data(self, knowledge_map: KnowledgeMap) -> str:
        """Create links data for D3.js visualization."""
        
        links = []
        for relationship in knowledge_map.relationships:
            links.append({
                'source': relationship.concept_a,
                'target': relationship.concept_b,
                'relationship': relationship.relationship_type,
                'description': relationship.description,
                'strength': relationship.strength
            })
        
        return str(links).replace("'", '"')
