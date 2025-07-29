#!/usr/bin/env python3
"""
AI-Powered Content Parser
Advanced content parsing system that identifies logical content boundaries,
recognizes content relationships, and understands document hierarchy.
"""

import re
import json
import numpy as np
from typing import List, Dict, Tuple, Optional, Set
from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime
from enum import Enum

class ContentType(Enum):
    """Types of content blocks"""
    HEADING = "heading"
    PARAGRAPH = "paragraph"
    LIST = "list"
    CODE_BLOCK = "code_block"
    DIAGRAM = "diagram"
    TABLE = "table"
    QUOTE = "quote"
    SEPARATOR = "separator"

class RelationshipType(Enum):
    """Types of content relationships"""
    EXPLAINS = "explains"          # Section explains a concept
    REFERENCES = "references"      # Section references another
    CONTINUES = "continues"        # Section continues previous topic
    SUPPORTS = "supports"          # Section supports with evidence/examples
    CONTRASTS = "contrasts"        # Section provides contrasting view
    SUMMARIZES = "summarizes"      # Section summarizes previous content
    INTRODUCES = "introduces"      # Section introduces upcoming content

@dataclass
class ContentBlock:
    """Enhanced content block with semantic information"""
    id: str
    start_line: int
    end_line: int
    content_type: ContentType
    raw_content: str
    processed_content: str
    heading_level: int = 0
    estimated_pdf_lines: int = 0
    visual_weight: float = 1.0
    semantic_keywords: List[str] = field(default_factory=list)
    contains_visual_elements: bool = False
    visual_elements: List[str] = field(default_factory=list)
    parent_section: Optional[str] = None
    child_sections: List[str] = field(default_factory=list)
    
@dataclass
class ContentRelationship:
    """Relationship between content blocks"""
    source_id: str
    target_id: str
    relationship_type: RelationshipType
    strength: float  # 0.0 to 1.0
    evidence: List[str]  # Evidence for the relationship
    requires_proximity: bool = False  # Should stay on same/adjacent pages

@dataclass
class DocumentStructure:
    """Complete document structure with relationships"""
    blocks: List[ContentBlock]
    relationships: List[ContentRelationship]
    content_clusters: List[List[str]]  # Groups of related content IDs
    visual_flow: List[str]  # Optimal visual ordering of content
    metadata: Dict[str, any] = field(default_factory=dict)

class AIContentParser:
    """AI-powered content parser with semantic understanding"""
    
    def __init__(self):
        self.keyword_patterns = self._load_keyword_patterns()
        self.relationship_indicators = self._load_relationship_indicators()
        self.visual_element_patterns = self._load_visual_patterns()
        
    def parse_document(self, file_path: str) -> DocumentStructure:
        """Parse document with advanced semantic analysis"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\n')
        
        # Step 1: Parse content blocks
        blocks = self._parse_content_blocks(lines)
        
        # Step 2: Enhance blocks with semantic information
        self._enhance_semantic_information(blocks)
        
        # Step 3: Analyze relationships between blocks
        relationships = self._analyze_content_relationships(blocks)
        
        # Step 4: Create content clusters
        clusters = self._create_content_clusters(blocks, relationships)
        
        # Step 5: Determine optimal visual flow
        visual_flow = self._determine_visual_flow(blocks, relationships, clusters)
        
        return DocumentStructure(
            blocks=blocks,
            relationships=relationships,
            content_clusters=clusters,
            visual_flow=visual_flow,
            metadata={
                'parsed_at': datetime.now().isoformat(),
                'total_blocks': len(blocks),
                'total_relationships': len(relationships),
                'total_clusters': len(clusters)
            }
        )
    
    def _parse_content_blocks(self, lines: List[str]) -> List[ContentBlock]:
        """Parse content into logical blocks with enhanced detection"""
        blocks = []
        current_block = None
        block_counter = 0
        in_code_block = False
        code_block_type = None
        
        for i, line in enumerate(lines):
            line_stripped = line.strip()
            
            # Skip page break markers
            if self._is_page_break_marker(line):
                continue
            
            # Handle code blocks
            if line_stripped.startswith('```'):
                if in_code_block:
                    # End of code block
                    if current_block:
                        current_block.end_line = i
                        current_block.estimated_pdf_lines = self._estimate_pdf_lines(current_block)
                        blocks.append(current_block)
                    in_code_block = False
                    code_block_type = None
                    current_block = None
                else:
                    # Start of code block
                    if current_block:
                        current_block.end_line = i - 1
                        current_block.estimated_pdf_lines = self._estimate_pdf_lines(current_block)
                        blocks.append(current_block)
                    
                    code_block_type = line_stripped[3:].strip()
                    content_type = ContentType.DIAGRAM if self._is_diagram_code(code_block_type) else ContentType.CODE_BLOCK
                    
                    current_block = ContentBlock(
                        id=f"block_{block_counter}",
                        start_line=i,
                        end_line=i,
                        content_type=content_type,
                        raw_content=line,
                        processed_content=line_stripped,
                        contains_visual_elements=content_type == ContentType.DIAGRAM
                    )
                    block_counter += 1
                    in_code_block = True
                continue
            
            if in_code_block:
                if current_block:
                    current_block.raw_content += '\n' + line
                    current_block.processed_content += '\n' + line_stripped
                    if content_type == ContentType.DIAGRAM:
                        current_block.visual_elements.append(code_block_type)
                continue
            
            # Handle headings
            if line_stripped.startswith('#'):
                if current_block:
                    current_block.end_line = i - 1
                    current_block.estimated_pdf_lines = self._estimate_pdf_lines(current_block)
                    blocks.append(current_block)
                
                heading_level = len(line_stripped) - len(line_stripped.lstrip('#'))
                current_block = ContentBlock(
                    id=f"block_{block_counter}",
                    start_line=i,
                    end_line=i,
                    content_type=ContentType.HEADING,
                    raw_content=line,
                    processed_content=line_stripped,
                    heading_level=heading_level
                )
                block_counter += 1
                continue
            
            # Handle lists
            if self._is_list_item(line_stripped):
                if current_block and current_block.content_type != ContentType.LIST:
                    current_block.end_line = i - 1
                    current_block.estimated_pdf_lines = self._estimate_pdf_lines(current_block)
                    blocks.append(current_block)
                    current_block = None
                
                if not current_block:
                    current_block = ContentBlock(
                        id=f"block_{block_counter}",
                        start_line=i,
                        end_line=i,
                        content_type=ContentType.LIST,
                        raw_content=line,
                        processed_content=line_stripped
                    )
                    block_counter += 1
                else:
                    current_block.raw_content += '\n' + line
                    current_block.processed_content += '\n' + line_stripped
                    current_block.end_line = i
                continue
            
            # Handle empty lines
            if not line_stripped:
                if current_block and current_block.content_type == ContentType.PARAGRAPH:
                    current_block.end_line = i - 1
                    current_block.estimated_pdf_lines = self._estimate_pdf_lines(current_block)
                    blocks.append(current_block)
                    current_block = None
                continue
            
            # Handle regular paragraphs
            if current_block and current_block.content_type == ContentType.PARAGRAPH:
                current_block.raw_content += '\n' + line
                current_block.processed_content += '\n' + line_stripped
                current_block.end_line = i
            else:
                if current_block:
                    current_block.end_line = i - 1
                    current_block.estimated_pdf_lines = self._estimate_pdf_lines(current_block)
                    blocks.append(current_block)
                
                current_block = ContentBlock(
                    id=f"block_{block_counter}",
                    start_line=i,
                    end_line=i,
                    content_type=ContentType.PARAGRAPH,
                    raw_content=line,
                    processed_content=line_stripped
                )
                block_counter += 1
        
        # Handle final block
        if current_block:
            current_block.estimated_pdf_lines = self._estimate_pdf_lines(current_block)
            blocks.append(current_block)
        
        return blocks
    
    def _enhance_semantic_information(self, blocks: List[ContentBlock]):
        """Enhance blocks with semantic information"""
        for block in blocks:
            # Extract keywords
            block.semantic_keywords = self._extract_keywords(block.processed_content)
            
            # Calculate visual weight
            block.visual_weight = self._calculate_visual_weight(block)
            
            # Detect visual elements in text
            if block.content_type != ContentType.DIAGRAM:
                visual_refs = self._detect_visual_references(block.processed_content)
                if visual_refs:
                    block.contains_visual_elements = True
                    block.visual_elements.extend(visual_refs)
        
        # Establish parent-child relationships
        self._establish_hierarchy(blocks)
    
    def _analyze_content_relationships(self, blocks: List[ContentBlock]) -> List[ContentRelationship]:
        """Analyze relationships between content blocks"""
        relationships = []
        
        for i, block1 in enumerate(blocks):
            for j, block2 in enumerate(blocks[i+1:], i+1):
                relationship = self._detect_relationship(block1, block2)
                if relationship:
                    relationships.append(relationship)
        
        return relationships
    
    def _create_content_clusters(self, blocks: List[ContentBlock], 
                               relationships: List[ContentRelationship]) -> List[List[str]]:
        """Create clusters of related content"""
        # Build adjacency list from relationships
        adjacency = {block.id: [] for block in blocks}
        for rel in relationships:
            if rel.strength >= 0.5:  # Only strong relationships
                adjacency[rel.source_id].append(rel.target_id)
                adjacency[rel.target_id].append(rel.source_id)
        
        # Find connected components (clusters)
        visited = set()
        clusters = []
        
        for block in blocks:
            if block.id not in visited:
                cluster = self._dfs_cluster(block.id, adjacency, visited)
                if len(cluster) > 1:  # Only meaningful clusters
                    clusters.append(cluster)
        
        return clusters
    
    def _determine_visual_flow(self, blocks: List[ContentBlock], 
                             relationships: List[ContentRelationship],
                             clusters: List[List[str]]) -> List[str]:
        """Determine optimal visual flow of content"""
        # Start with original order
        flow = [block.id for block in blocks]
        
        # Optimize based on relationships and clusters
        # This is a simplified version - could use more sophisticated algorithms
        optimized_flow = self._optimize_flow_order(flow, relationships, clusters)
        
        return optimized_flow

    def _load_keyword_patterns(self) -> Dict[str, List[str]]:
        """Load keyword patterns for semantic analysis"""
        return {
            'technical': ['implementation', 'architecture', 'system', 'component', 'module', 'api', 'database'],
            'risk': ['risk', 'challenge', 'issue', 'problem', 'concern', 'limitation', 'constraint'],
            'process': ['process', 'workflow', 'procedure', 'step', 'phase', 'stage', 'methodology'],
            'business': ['business', 'requirement', 'stakeholder', 'user', 'customer', 'market', 'value'],
            'operational': ['deployment', 'monitoring', 'maintenance', 'support', 'operation', 'management'],
            'conclusion': ['conclusion', 'summary', 'result', 'outcome', 'finding', 'recommendation']
        }

    def _load_relationship_indicators(self) -> Dict[RelationshipType, List[str]]:
        """Load indicators for different relationship types"""
        return {
            RelationshipType.EXPLAINS: ['explains', 'describes', 'defines', 'clarifies', 'details'],
            RelationshipType.REFERENCES: ['refers to', 'mentions', 'cites', 'points to', 'see', 'as shown'],
            RelationshipType.CONTINUES: ['furthermore', 'additionally', 'moreover', 'also', 'continuing'],
            RelationshipType.SUPPORTS: ['for example', 'such as', 'including', 'specifically', 'evidence'],
            RelationshipType.CONTRASTS: ['however', 'but', 'although', 'despite', 'on the other hand'],
            RelationshipType.SUMMARIZES: ['in summary', 'to conclude', 'overall', 'in total', 'finally'],
            RelationshipType.INTRODUCES: ['introduces', 'presents', 'outlines', 'overview', 'begins with']
        }

    def _load_visual_patterns(self) -> List[str]:
        """Load patterns for detecting visual element references"""
        return [
            r'diagram\s+\d+', r'figure\s+\d+', r'table\s+\d+', r'chart\s+\d+',
            r'as shown', r'illustrated', r'depicted', r'visualized',
            r'see\s+(above|below)', r'following\s+(diagram|figure|table|chart)'
        ]

    def _is_page_break_marker(self, line: str) -> bool:
        """Check if line is a page break marker"""
        return 'Page ' in line and ('---' in line or '___' in line)

    def _is_diagram_code(self, code_type: str) -> bool:
        """Check if code block contains a diagram"""
        diagram_types = ['mermaid', 'flowchart', 'graph', 'sequence', 'class', 'gantt', 'pie']
        return any(dtype in code_type.lower() for dtype in diagram_types)

    def _is_list_item(self, line: str) -> bool:
        """Check if line is a list item"""
        return (line.startswith(('-', '*', '+')) or
                re.match(r'^\d+\.', line) or
                re.match(r'^[a-zA-Z]\.', line))

    def _estimate_pdf_lines(self, block: ContentBlock) -> int:
        """Estimate PDF lines for a content block"""
        content = block.raw_content
        lines = content.split('\n')
        pdf_lines = 0

        if block.content_type == ContentType.HEADING:
            pdf_lines = 2 + block.heading_level * 0.5  # Headings take more space
        elif block.content_type == ContentType.CODE_BLOCK:
            pdf_lines = len(lines) + 2  # Code blocks with padding
        elif block.content_type == ContentType.DIAGRAM:
            pdf_lines = max(8, len(lines))  # Diagrams take significant space
        elif block.content_type == ContentType.LIST:
            pdf_lines = len([l for l in lines if l.strip()]) * 1.2  # Lists with spacing
        else:
            # Regular paragraphs - estimate word wrapping
            total_chars = sum(len(line) for line in lines)
            pdf_lines = max(1, total_chars / 80)  # ~80 chars per line

        return int(pdf_lines)

    def _extract_keywords(self, content: str) -> List[str]:
        """Extract semantic keywords from content"""
        keywords = []
        content_lower = content.lower()

        for category, patterns in self.keyword_patterns.items():
            for pattern in patterns:
                if pattern in content_lower:
                    keywords.append(f"{category}:{pattern}")

        return keywords

    def _calculate_visual_weight(self, block: ContentBlock) -> float:
        """Calculate visual weight of a content block"""
        weight = 1.0

        # Heading weight based on level
        if block.content_type == ContentType.HEADING:
            weight += (7 - block.heading_level) * 0.3

        # Content type weights
        type_weights = {
            ContentType.DIAGRAM: 2.0,
            ContentType.CODE_BLOCK: 1.5,
            ContentType.TABLE: 1.8,
            ContentType.LIST: 1.2,
            ContentType.QUOTE: 1.1
        }
        weight *= type_weights.get(block.content_type, 1.0)

        # Length weight
        if block.estimated_pdf_lines > 10:
            weight += 0.5
        elif block.estimated_pdf_lines > 20:
            weight += 1.0

        # Visual elements weight
        if block.contains_visual_elements:
            weight += 0.3 * len(block.visual_elements)

        return weight

    def _detect_visual_references(self, content: str) -> List[str]:
        """Detect references to visual elements in text"""
        references = []
        content_lower = content.lower()

        for pattern in self.visual_element_patterns:
            matches = re.findall(pattern, content_lower)
            references.extend(matches)

        return references

    def _establish_hierarchy(self, blocks: List[ContentBlock]):
        """Establish parent-child relationships between blocks"""
        heading_stack = []  # Stack of (level, block_id)

        for block in blocks:
            if block.content_type == ContentType.HEADING:
                # Pop headings of same or lower level
                while heading_stack and heading_stack[-1][0] >= block.heading_level:
                    heading_stack.pop()

                # Set parent if stack not empty
                if heading_stack:
                    parent_id = heading_stack[-1][1]
                    block.parent_section = parent_id
                    # Find parent block and add this as child
                    for parent_block in blocks:
                        if parent_block.id == parent_id:
                            parent_block.child_sections.append(block.id)
                            break

                heading_stack.append((block.heading_level, block.id))
            else:
                # Non-heading blocks belong to current heading
                if heading_stack:
                    parent_id = heading_stack[-1][1]
                    block.parent_section = parent_id

    def _detect_relationship(self, block1: ContentBlock, block2: ContentBlock) -> Optional[ContentRelationship]:
        """Detect relationship between two content blocks"""
        # Skip if blocks are too far apart (more than 10 blocks)
        if abs(block1.start_line - block2.start_line) > 200:  # Rough line distance
            return None

        # Check for explicit relationship indicators
        for rel_type, indicators in self.relationship_indicators.items():
            for indicator in indicators:
                if indicator in block2.processed_content.lower():
                    strength = self._calculate_relationship_strength(block1, block2, rel_type)
                    if strength > 0.3:
                        return ContentRelationship(
                            source_id=block1.id,
                            target_id=block2.id,
                            relationship_type=rel_type,
                            strength=strength,
                            evidence=[indicator],
                            requires_proximity=rel_type in [RelationshipType.EXPLAINS, RelationshipType.SUPPORTS]
                        )

        # Check for semantic similarity
        similarity = self._calculate_semantic_similarity(block1, block2)
        if similarity > 0.6:
            return ContentRelationship(
                source_id=block1.id,
                target_id=block2.id,
                relationship_type=RelationshipType.CONTINUES,
                strength=similarity,
                evidence=['semantic_similarity'],
                requires_proximity=True
            )

        # Check for visual element relationships
        if block1.contains_visual_elements and block2.contains_visual_elements:
            if any(elem in block2.visual_elements for elem in block1.visual_elements):
                return ContentRelationship(
                    source_id=block1.id,
                    target_id=block2.id,
                    relationship_type=RelationshipType.REFERENCES,
                    strength=0.8,
                    evidence=['shared_visual_elements'],
                    requires_proximity=True
                )

        return None

    def _calculate_relationship_strength(self, block1: ContentBlock, block2: ContentBlock,
                                       rel_type: RelationshipType) -> float:
        """Calculate strength of relationship between blocks"""
        strength = 0.5  # Base strength

        # Distance factor (closer blocks have stronger relationships)
        distance = abs(block2.start_line - block1.start_line)
        distance_factor = max(0.1, 1.0 - (distance / 100))
        strength *= distance_factor

        # Keyword overlap factor
        overlap = len(set(block1.semantic_keywords) & set(block2.semantic_keywords))
        if overlap > 0:
            strength += 0.2 * min(overlap, 3)  # Cap at 3 overlapping keywords

        # Hierarchy factor
        if block1.parent_section == block2.parent_section:
            strength += 0.3  # Same parent section

        # Content type compatibility
        type_compatibility = {
            (ContentType.HEADING, ContentType.PARAGRAPH): 0.9,
            (ContentType.PARAGRAPH, ContentType.LIST): 0.8,
            (ContentType.PARAGRAPH, ContentType.DIAGRAM): 0.9,
            (ContentType.LIST, ContentType.PARAGRAPH): 0.7,
            (ContentType.DIAGRAM, ContentType.PARAGRAPH): 0.9
        }

        compatibility = type_compatibility.get((block1.content_type, block2.content_type), 0.5)
        strength *= compatibility

        return min(1.0, strength)

    def _calculate_semantic_similarity(self, block1: ContentBlock, block2: ContentBlock) -> float:
        """Calculate semantic similarity between blocks (simplified version)"""
        # This is a simplified implementation
        # In a full implementation, you'd use word embeddings or NLP models

        words1 = set(block1.processed_content.lower().split())
        words2 = set(block2.processed_content.lower().split())

        if not words1 or not words2:
            return 0.0

        intersection = len(words1 & words2)
        union = len(words1 | words2)

        jaccard_similarity = intersection / union if union > 0 else 0.0

        # Boost similarity for keyword matches
        keyword_matches = len(set(block1.semantic_keywords) & set(block2.semantic_keywords))
        keyword_boost = min(0.3, keyword_matches * 0.1)

        return min(1.0, jaccard_similarity + keyword_boost)

    def _dfs_cluster(self, node_id: str, adjacency: Dict[str, List[str]], visited: Set[str]) -> List[str]:
        """Depth-first search to find connected components (clusters)"""
        if node_id in visited:
            return []

        visited.add(node_id)
        cluster = [node_id]

        for neighbor in adjacency.get(node_id, []):
            cluster.extend(self._dfs_cluster(neighbor, adjacency, visited))

        return cluster

    def _optimize_flow_order(self, original_flow: List[str],
                           relationships: List[ContentRelationship],
                           clusters: List[List[str]]) -> List[str]:
        """Optimize the flow order based on relationships and clusters"""
        # This is a simplified optimization
        # In practice, you might use more sophisticated algorithms

        optimized = original_flow.copy()

        # Try to keep strongly related content together
        for rel in relationships:
            if rel.strength > 0.8 and rel.requires_proximity:
                source_idx = optimized.index(rel.source_id)
                target_idx = optimized.index(rel.target_id)

                # If they're far apart, try to move them closer
                if abs(source_idx - target_idx) > 3:
                    # Simple heuristic: move target closer to source
                    optimized.remove(rel.target_id)
                    insert_pos = min(source_idx + 1, len(optimized))
                    optimized.insert(insert_pos, rel.target_id)

        return optimized

    def export_analysis(self, document_structure: DocumentStructure, output_path: str):
        """Export document analysis to JSON file"""
        export_data = {
            'metadata': document_structure.metadata,
            'blocks': [
                {
                    'id': block.id,
                    'start_line': block.start_line,
                    'end_line': block.end_line,
                    'content_type': block.content_type.value,
                    'heading_level': block.heading_level,
                    'estimated_pdf_lines': block.estimated_pdf_lines,
                    'visual_weight': block.visual_weight,
                    'semantic_keywords': block.semantic_keywords,
                    'contains_visual_elements': block.contains_visual_elements,
                    'visual_elements': block.visual_elements,
                    'parent_section': block.parent_section,
                    'child_sections': block.child_sections,
                    'content_preview': block.processed_content[:100] + '...' if len(block.processed_content) > 100 else block.processed_content
                }
                for block in document_structure.blocks
            ],
            'relationships': [
                {
                    'source_id': rel.source_id,
                    'target_id': rel.target_id,
                    'relationship_type': rel.relationship_type.value,
                    'strength': rel.strength,
                    'evidence': rel.evidence,
                    'requires_proximity': rel.requires_proximity
                }
                for rel in document_structure.relationships
            ],
            'content_clusters': document_structure.content_clusters,
            'visual_flow': document_structure.visual_flow
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)

    def get_content_groups_for_page_breaks(self, document_structure: DocumentStructure) -> List[Dict]:
        """Get content groups that should be kept together for page break decisions"""
        groups = []

        # Add clusters as groups
        for i, cluster in enumerate(document_structure.content_clusters):
            if len(cluster) > 1:
                cluster_blocks = [block for block in document_structure.blocks if block.id in cluster]
                total_lines = sum(block.estimated_pdf_lines for block in cluster_blocks)

                groups.append({
                    'group_id': f'cluster_{i}',
                    'block_ids': cluster,
                    'group_type': 'semantic_cluster',
                    'estimated_lines': total_lines,
                    'keep_together': total_lines <= 30,  # Only keep together if reasonable size
                    'priority': 'high' if any(block.visual_weight > 2.0 for block in cluster_blocks) else 'medium'
                })

        # Add visual element groups
        visual_groups = self._find_visual_element_groups(document_structure)
        groups.extend(visual_groups)

        # Add hierarchical groups (parent-child relationships)
        hierarchical_groups = self._find_hierarchical_groups(document_structure)
        groups.extend(hierarchical_groups)

        return groups

    def _find_visual_element_groups(self, document_structure: DocumentStructure) -> List[Dict]:
        """Find groups of content that should stay with visual elements"""
        groups = []

        for block in document_structure.blocks:
            if block.content_type == ContentType.DIAGRAM:
                # Find related text blocks
                related_blocks = [block.id]

                # Look for blocks that reference this diagram
                for rel in document_structure.relationships:
                    if (rel.target_id == block.id and
                        rel.relationship_type in [RelationshipType.REFERENCES, RelationshipType.EXPLAINS] and
                        rel.requires_proximity):
                        related_blocks.append(rel.source_id)

                if len(related_blocks) > 1:
                    total_lines = sum(
                        b.estimated_pdf_lines for b in document_structure.blocks
                        if b.id in related_blocks
                    )

                    groups.append({
                        'group_id': f'visual_{block.id}',
                        'block_ids': related_blocks,
                        'group_type': 'visual_element_group',
                        'estimated_lines': total_lines,
                        'keep_together': total_lines <= 25,
                        'priority': 'high'  # Visual elements have high priority
                    })

        return groups

    def _find_hierarchical_groups(self, document_structure: DocumentStructure) -> List[Dict]:
        """Find hierarchical groups (sections with their subsections)"""
        groups = []

        for block in document_structure.blocks:
            if (block.content_type == ContentType.HEADING and
                block.heading_level <= 2 and
                len(block.child_sections) > 0):

                # Include the heading and its immediate children
                group_blocks = [block.id] + block.child_sections[:3]  # Limit to avoid huge groups

                total_lines = sum(
                    b.estimated_pdf_lines for b in document_structure.blocks
                    if b.id in group_blocks
                )

                groups.append({
                    'group_id': f'section_{block.id}',
                    'block_ids': group_blocks,
                    'group_type': 'hierarchical_section',
                    'estimated_lines': total_lines,
                    'keep_together': total_lines <= 35,
                    'priority': 'medium'
                })

        return groups

def main():
    """Test the AI content parser"""
    parser = AIContentParser()

    # Test with an existing document
    test_file = "blueprint-ceo.md"

    if Path(test_file).exists():
        print(f"Parsing {test_file} with AI content parser...")

        # Parse the document
        try:
            document_structure = parser.parse_document(test_file)
            print(f"✅ Successfully parsed document")

            # Export analysis
            analysis_file = "ai_content_analysis.json"
            parser.export_analysis(document_structure, analysis_file)
            print(f"✅ Exported analysis to {analysis_file}")

            # Get content groups for page breaks
            content_groups = parser.get_content_groups_for_page_breaks(document_structure)

            # Print summary
            print(f"\n📊 Analysis Summary:")
            print(f"   • Total content blocks: {len(document_structure.blocks)}")
            print(f"   • Content relationships: {len(document_structure.relationships)}")
            print(f"   • Content clusters: {len(document_structure.content_clusters)}")
            print(f"   • Content groups for page breaks: {len(content_groups)}")

            print(f"\n📋 Content Block Types:")
            type_counts = {}
            for block in document_structure.blocks:
                type_counts[block.content_type.value] = type_counts.get(block.content_type.value, 0) + 1

            for content_type, count in type_counts.items():
                print(f"   • {content_type}: {count}")

            print(f"\n🔗 Relationship Types:")
            rel_counts = {}
            for rel in document_structure.relationships:
                rel_counts[rel.relationship_type.value] = rel_counts.get(rel.relationship_type.value, 0) + 1

            for rel_type, count in rel_counts.items():
                print(f"   • {rel_type}: {count}")

            print(f"\n💾 Analysis exported to: {analysis_file}")

            # Show some high-priority content groups
            high_priority_groups = [g for g in content_groups if g['priority'] == 'high']
            if high_priority_groups:
                print(f"\n🎯 High-Priority Content Groups (should stay together):")
                for group in high_priority_groups[:5]:  # Show first 5
                    print(f"   • {group['group_id']} ({group['group_type']}): {group['estimated_lines']} lines")

        except Exception as e:
            print(f"❌ Error parsing document: {e}")
            import traceback
            traceback.print_exc()

    else:
        print(f"Test file {test_file} not found!")

if __name__ == "__main__":
    main()
