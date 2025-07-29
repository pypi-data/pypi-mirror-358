#!/usr/bin/env python3
"""
Smart Page Break Decision Engine
Context-aware page break insertion system that considers content hierarchy,
visual elements, and professional document layout principles.
"""

import json
import math
from typing import List, Dict, Tuple, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
from ai_content_parser import DocumentStructure, ContentBlock, ContentRelationship, ContentType

class BreakReason(Enum):
    """Reasons for page breaks"""
    CONTENT_OVERFLOW = "content_overflow"
    SECTION_BOUNDARY = "section_boundary"
    VISUAL_BALANCE = "visual_balance"
    AVOID_ORPHAN = "avoid_orphan"
    DIAGRAM_POSITIONING = "diagram_positioning"
    CONTENT_COHERENCE = "content_coherence"
    PROFESSIONAL_LAYOUT = "professional_layout"

class BreakPriority(Enum):
    """Priority levels for page breaks"""
    MANDATORY = "mandatory"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    AVOID = "avoid"

@dataclass
class PageBreakDecision:
    """Enhanced page break decision with AI reasoning"""
    block_id: str
    line_number: int
    reason: BreakReason
    priority: BreakPriority
    confidence: float  # 0.0 to 1.0
    visual_impact_score: float
    content_coherence_score: float
    alternative_locations: List[int] = field(default_factory=list)
    affected_groups: List[str] = field(default_factory=list)
    reasoning: str = ""
    
@dataclass
class PageLayout:
    """Represents a page layout with content blocks"""
    page_number: int
    blocks: List[str]  # Block IDs
    estimated_lines: int
    visual_weight: float
    content_coherence: float
    has_orphans: bool = False
    has_widows: bool = False

class SmartPageBreakEngine:
    """AI-powered page break decision engine"""
    
    def __init__(self):
        self.layout_rules = {
            'min_page_lines': 20,
            'max_page_lines': 45,
            'optimal_page_lines': 35,
            'comfortable_range': (25, 40),
            'orphan_threshold': 3,
            'widow_threshold': 2,
            'diagram_padding': 2,
            'section_spacing': 1.5
        }
        
        self.decision_weights = {
            'content_overflow': 1.0,
            'visual_balance': 0.8,
            'content_coherence': 0.9,
            'professional_appearance': 0.7,
            'user_preference': 0.6
        }
    
    def analyze_optimal_page_breaks(self, document_structure: DocumentStructure,
                                  content_groups: List[Dict]) -> List[PageBreakDecision]:
        """Analyze and determine optimal page break locations"""
        
        # Step 1: Create initial page layout simulation
        initial_layout = self._simulate_initial_layout(document_structure)
        
        # Step 2: Identify problem areas
        problems = self._identify_layout_problems(initial_layout, document_structure, content_groups)
        
        # Step 3: Generate page break candidates
        candidates = self._generate_break_candidates(document_structure, content_groups, problems)
        
        # Step 4: Evaluate and score candidates
        scored_candidates = self._score_break_candidates(candidates, document_structure, content_groups)
        
        # Step 5: Optimize break selection
        optimal_breaks = self._optimize_break_selection(scored_candidates, document_structure)
        
        # Step 6: Validate final layout
        final_layout = self._simulate_layout_with_breaks(document_structure, optimal_breaks)
        validated_breaks = self._validate_final_layout(optimal_breaks, final_layout, document_structure)
        
        return validated_breaks
    
    def _simulate_initial_layout(self, document_structure: DocumentStructure) -> List[PageLayout]:
        """Simulate initial page layout without intelligent breaks"""
        pages = []
        current_page = PageLayout(page_number=1, blocks=[], estimated_lines=0, visual_weight=0.0, content_coherence=1.0)
        
        for block in document_structure.blocks:
            # Check if adding this block would exceed page limit
            if (current_page.estimated_lines + block.estimated_pdf_lines > self.layout_rules['max_page_lines'] and
                current_page.estimated_lines > self.layout_rules['min_page_lines']):
                
                # Start new page
                pages.append(current_page)
                current_page = PageLayout(
                    page_number=len(pages) + 1,
                    blocks=[block.id],
                    estimated_lines=block.estimated_pdf_lines,
                    visual_weight=block.visual_weight,
                    content_coherence=1.0
                )
            else:
                # Add to current page
                current_page.blocks.append(block.id)
                current_page.estimated_lines += block.estimated_pdf_lines
                current_page.visual_weight += block.visual_weight
        
        if current_page.blocks:
            pages.append(current_page)
        
        return pages
    
    def _identify_layout_problems(self, layout: List[PageLayout], 
                                document_structure: DocumentStructure,
                                content_groups: List[Dict]) -> List[Dict]:
        """Identify problems in the current layout"""
        problems = []
        
        for page in layout:
            # Check for orphans and widows
            orphan_problems = self._check_orphan_problems(page, document_structure)
            problems.extend(orphan_problems)
            
            # Check for split content groups
            split_problems = self._check_split_groups(page, layout, content_groups)
            problems.extend(split_problems)
            
            # Check for poor visual balance
            balance_problems = self._check_visual_balance(page, document_structure)
            problems.extend(balance_problems)
            
            # Check for diagram positioning issues
            diagram_problems = self._check_diagram_positioning(page, document_structure)
            problems.extend(diagram_problems)
        
        return problems
    
    def _generate_break_candidates(self, document_structure: DocumentStructure,
                                 content_groups: List[Dict],
                                 problems: List[Dict]) -> List[PageBreakDecision]:
        """Generate candidate page break locations"""
        candidates = []
        
        # Generate candidates based on content structure
        for i, block in enumerate(document_structure.blocks):
            if i == 0:  # Skip first block
                continue
            
            # Evaluate this location as a potential break point
            decision = self._evaluate_break_location(block, document_structure, content_groups, problems)
            if decision:
                candidates.append(decision)
        
        return candidates
    
    def _evaluate_break_location(self, block: ContentBlock, 
                               document_structure: DocumentStructure,
                               content_groups: List[Dict],
                               problems: List[Dict]) -> Optional[PageBreakDecision]:
        """Evaluate a specific location for a page break"""
        
        # Calculate various scores for this break location
        visual_impact = self._calculate_visual_impact_score(block, document_structure)
        coherence_score = self._calculate_coherence_score(block, document_structure, content_groups)
        
        # Determine break reason and priority
        reason, priority = self._determine_break_reason_and_priority(block, document_structure, problems)
        
        if priority == BreakPriority.AVOID:
            return None
        
        # Calculate confidence based on multiple factors
        confidence = self._calculate_break_confidence(block, visual_impact, coherence_score, priority)
        
        # Find alternative locations
        alternatives = self._find_alternative_locations(block, document_structure)
        
        # Identify affected content groups
        affected_groups = self._identify_affected_groups(block, content_groups)
        
        # Generate reasoning
        reasoning = self._generate_break_reasoning(block, reason, visual_impact, coherence_score)
        
        return PageBreakDecision(
            block_id=block.id,
            line_number=block.start_line,
            reason=reason,
            priority=priority,
            confidence=confidence,
            visual_impact_score=visual_impact,
            content_coherence_score=coherence_score,
            alternative_locations=alternatives,
            affected_groups=affected_groups,
            reasoning=reasoning
        )
    
    def _calculate_visual_impact_score(self, block: ContentBlock, 
                                     document_structure: DocumentStructure) -> float:
        """Calculate visual impact score for breaking before this block"""
        score = 0.5  # Base score
        
        # Content type impact
        if block.content_type == ContentType.HEADING:
            score += 0.3 * (4 - block.heading_level) / 3  # Higher level headings = better breaks
        elif block.content_type == ContentType.DIAGRAM:
            score += 0.4  # Diagrams are good break points
        elif block.content_type == ContentType.CODE_BLOCK:
            score += 0.2
        
        # Visual weight consideration
        if block.visual_weight > 2.0:
            score += 0.2
        
        # Position in document
        block_index = next(i for i, b in enumerate(document_structure.blocks) if b.id == block.id)
        relative_position = block_index / len(document_structure.blocks)
        
        # Avoid breaks too early or too late in document
        if 0.1 < relative_position < 0.9:
            score += 0.1
        
        return min(1.0, score)
    
    def _calculate_coherence_score(self, block: ContentBlock,
                                 document_structure: DocumentStructure,
                                 content_groups: List[Dict]) -> float:
        """Calculate content coherence score for breaking before this block"""
        score = 0.5  # Base score
        
        # Check if break would split content groups
        for group in content_groups:
            if block.id in group['block_ids']:
                if group['keep_together']:
                    score -= 0.4  # Penalty for splitting groups that should stay together
                else:
                    score -= 0.2  # Smaller penalty for flexible groups
        
        # Check relationships
        strong_relationships = [
            rel for rel in document_structure.relationships
            if rel.target_id == block.id and rel.strength > 0.7 and rel.requires_proximity
        ]
        
        if strong_relationships:
            score -= 0.3 * len(strong_relationships)  # Penalty for breaking strong relationships
        
        # Hierarchy consideration
        if block.parent_section:
            # Check if we're breaking within a section
            parent_block = next((b for b in document_structure.blocks if b.id == block.parent_section), None)
            if parent_block and parent_block.content_type == ContentType.HEADING:
                if block.heading_level > parent_block.heading_level:
                    score -= 0.2  # Penalty for breaking subsections from parent
        
        return max(0.0, score)

    def _determine_break_reason_and_priority(self, block: ContentBlock,
                                           document_structure: DocumentStructure,
                                           problems: List[Dict]) -> Tuple[BreakReason, BreakPriority]:
        """Determine the reason and priority for a page break"""

        # Check for mandatory breaks
        if block.content_type == ContentType.HEADING and block.heading_level == 1:
            return BreakReason.SECTION_BOUNDARY, BreakPriority.HIGH

        # Check if this break would solve a problem
        for problem in problems:
            if problem.get('solution_block_id') == block.id:
                if problem['type'] == 'orphan':
                    return BreakReason.AVOID_ORPHAN, BreakPriority.HIGH
                elif problem['type'] == 'split_group':
                    return BreakReason.CONTENT_COHERENCE, BreakPriority.MEDIUM
                elif problem['type'] == 'diagram_split':
                    return BreakReason.DIAGRAM_POSITIONING, BreakPriority.HIGH

        # Content-based reasons
        if block.content_type == ContentType.HEADING and block.heading_level <= 2:
            return BreakReason.SECTION_BOUNDARY, BreakPriority.MEDIUM

        if block.content_type == ContentType.DIAGRAM:
            return BreakReason.DIAGRAM_POSITIONING, BreakPriority.MEDIUM

        # Check for visual balance
        block_index = next(i for i, b in enumerate(document_structure.blocks) if b.id == block.id)
        if block_index > 0:
            prev_blocks_lines = sum(b.estimated_pdf_lines for b in document_structure.blocks[:block_index])
            if prev_blocks_lines > self.layout_rules['optimal_page_lines']:
                return BreakReason.VISUAL_BALANCE, BreakPriority.MEDIUM

        # Default
        return BreakReason.PROFESSIONAL_LAYOUT, BreakPriority.LOW

    def _calculate_break_confidence(self, block: ContentBlock, visual_impact: float,
                                  coherence_score: float, priority: BreakPriority) -> float:
        """Calculate confidence score for a page break decision"""

        # Base confidence from priority
        priority_scores = {
            BreakPriority.MANDATORY: 0.95,
            BreakPriority.HIGH: 0.8,
            BreakPriority.MEDIUM: 0.6,
            BreakPriority.LOW: 0.4
        }

        base_confidence = priority_scores.get(priority, 0.3)

        # Adjust based on visual impact and coherence
        confidence = base_confidence * 0.5 + visual_impact * 0.3 + coherence_score * 0.2

        # Boost for certain content types
        if block.content_type == ContentType.HEADING and block.heading_level <= 2:
            confidence += 0.1

        if block.content_type == ContentType.DIAGRAM:
            confidence += 0.05

        return min(1.0, confidence)

    def _find_alternative_locations(self, block: ContentBlock,
                                  document_structure: DocumentStructure) -> List[int]:
        """Find alternative break locations near the proposed break"""
        alternatives = []
        block_index = next(i for i, b in enumerate(document_structure.blocks) if b.id == block.id)

        # Look for nearby headings
        for i in range(max(0, block_index - 3), min(len(document_structure.blocks), block_index + 4)):
            if i != block_index:
                nearby_block = document_structure.blocks[i]
                if nearby_block.content_type == ContentType.HEADING:
                    alternatives.append(nearby_block.start_line)

        return alternatives

    def _identify_affected_groups(self, block: ContentBlock, content_groups: List[Dict]) -> List[str]:
        """Identify content groups affected by this page break"""
        affected = []

        for group in content_groups:
            if block.id in group['block_ids']:
                affected.append(group['group_id'])

        return affected

    def _generate_break_reasoning(self, block: ContentBlock, reason: BreakReason,
                                visual_impact: float, coherence_score: float) -> str:
        """Generate human-readable reasoning for the page break decision"""

        reasoning_templates = {
            BreakReason.SECTION_BOUNDARY: f"Major section boundary ({block.content_type.value} level {block.heading_level})",
            BreakReason.AVOID_ORPHAN: f"Prevents orphaning of {block.content_type.value}",
            BreakReason.DIAGRAM_POSITIONING: f"Optimal positioning for {block.content_type.value}",
            BreakReason.VISUAL_BALANCE: f"Maintains visual balance (impact: {visual_impact:.2f})",
            BreakReason.CONTENT_COHERENCE: f"Preserves content coherence (score: {coherence_score:.2f})",
            BreakReason.PROFESSIONAL_LAYOUT: "Professional document layout standards"
        }

        base_reason = reasoning_templates.get(reason, "Layout optimization")

        # Add additional context
        if visual_impact > 0.8:
            base_reason += " - High visual impact"
        if coherence_score < 0.3:
            base_reason += " - May affect content flow"

        return base_reason

    def _check_orphan_problems(self, page: PageLayout, document_structure: DocumentStructure) -> List[Dict]:
        """Check for orphan and widow problems on a page"""
        problems = []

        if not page.blocks:
            return problems

        # Check for orphaned headings (heading with little content after)
        for block_id in page.blocks:
            block = next(b for b in document_structure.blocks if b.id == block_id)
            if block.content_type == ContentType.HEADING:
                # Count content after this heading on the same page
                block_index = page.blocks.index(block_id)
                content_after = sum(
                    next(b for b in document_structure.blocks if b.id == bid).estimated_pdf_lines
                    for bid in page.blocks[block_index + 1:]
                )

                if content_after < self.layout_rules['orphan_threshold']:
                    problems.append({
                        'type': 'orphan',
                        'page_number': page.page_number,
                        'block_id': block_id,
                        'severity': 'high' if content_after == 0 else 'medium',
                        'solution_block_id': block_id  # Break before this block
                    })

        return problems

    def _check_split_groups(self, page: PageLayout, layout: List[PageLayout],
                          content_groups: List[Dict]) -> List[Dict]:
        """Check for content groups that are split across pages"""
        problems = []

        for group in content_groups:
            if not group['keep_together']:
                continue

            # Check if group is split across multiple pages
            group_pages = set()
            for block_id in group['block_ids']:
                for p in layout:
                    if block_id in p.blocks:
                        group_pages.add(p.page_number)
                        break

            if len(group_pages) > 1:
                # Find the best place to break to keep group together
                first_block_id = group['block_ids'][0]
                problems.append({
                    'type': 'split_group',
                    'group_id': group['group_id'],
                    'pages': list(group_pages),
                    'severity': group['priority'],
                    'solution_block_id': first_block_id
                })

        return problems

    def _check_visual_balance(self, page: PageLayout, document_structure: DocumentStructure) -> List[Dict]:
        """Check for visual balance problems"""
        problems = []

        # Check for overly short or long pages
        if page.estimated_lines < self.layout_rules['min_page_lines']:
            problems.append({
                'type': 'short_page',
                'page_number': page.page_number,
                'lines': page.estimated_lines,
                'severity': 'medium'
            })
        elif page.estimated_lines > self.layout_rules['max_page_lines']:
            problems.append({
                'type': 'long_page',
                'page_number': page.page_number,
                'lines': page.estimated_lines,
                'severity': 'high'
            })

        return problems

    def _check_diagram_positioning(self, page: PageLayout, document_structure: DocumentStructure) -> List[Dict]:
        """Check for diagram positioning problems"""
        problems = []

        for block_id in page.blocks:
            block = next(b for b in document_structure.blocks if b.id == block_id)
            if block.content_type == ContentType.DIAGRAM:
                # Check if diagram is at the very end of a page (poor positioning)
                if page.blocks.index(block_id) == len(page.blocks) - 1:
                    remaining_space = self.layout_rules['max_page_lines'] - page.estimated_lines
                    if remaining_space < self.layout_rules['diagram_padding']:
                        problems.append({
                            'type': 'diagram_split',
                            'page_number': page.page_number,
                            'block_id': block_id,
                            'severity': 'high',
                            'solution_block_id': block_id
                        })

        return problems

    def _score_break_candidates(self, candidates: List[PageBreakDecision],
                              document_structure: DocumentStructure,
                              content_groups: List[Dict]) -> List[PageBreakDecision]:
        """Score and rank page break candidates"""

        for candidate in candidates:
            # Calculate composite score
            priority_weight = {
                BreakPriority.MANDATORY: 1.0,
                BreakPriority.HIGH: 0.8,
                BreakPriority.MEDIUM: 0.6,
                BreakPriority.LOW: 0.4
            }.get(candidate.priority, 0.2)

            # Weighted score combining multiple factors
            composite_score = (
                candidate.confidence * 0.4 +
                candidate.visual_impact_score * 0.3 +
                candidate.content_coherence_score * 0.2 +
                priority_weight * 0.1
            )

            # Store score in confidence field for sorting
            candidate.confidence = composite_score

        # Sort by score (descending)
        return sorted(candidates, key=lambda x: x.confidence, reverse=True)

    def _optimize_break_selection(self, candidates: List[PageBreakDecision],
                                document_structure: DocumentStructure) -> List[PageBreakDecision]:
        """Optimize selection of page breaks to avoid conflicts"""

        selected_breaks = []
        used_blocks = set()

        for candidate in candidates:
            # Skip if we've already selected a break near this location
            if candidate.block_id in used_blocks:
                continue

            # Check for conflicts with already selected breaks
            conflict = False
            for selected in selected_breaks:
                if abs(candidate.line_number - selected.line_number) < 10:  # Too close
                    conflict = True
                    break

            if not conflict and candidate.confidence > 0.5:
                selected_breaks.append(candidate)
                used_blocks.add(candidate.block_id)

                # Mark nearby blocks as used to avoid clustering
                block_index = next(i for i, b in enumerate(document_structure.blocks) if b.id == candidate.block_id)
                for i in range(max(0, block_index - 2), min(len(document_structure.blocks), block_index + 3)):
                    used_blocks.add(document_structure.blocks[i].id)

        return selected_breaks

    def _simulate_layout_with_breaks(self, document_structure: DocumentStructure,
                                   breaks: List[PageBreakDecision]) -> List[PageLayout]:
        """Simulate page layout with the proposed breaks"""

        break_lines = set(brk.line_number for brk in breaks)
        pages = []
        current_page = PageLayout(page_number=1, blocks=[], estimated_lines=0, visual_weight=0.0, content_coherence=1.0)

        for block in document_structure.blocks:
            # Check if we should break before this block
            if block.start_line in break_lines and current_page.blocks:
                pages.append(current_page)
                current_page = PageLayout(
                    page_number=len(pages) + 1,
                    blocks=[],
                    estimated_lines=0,
                    visual_weight=0.0,
                    content_coherence=1.0
                )

            # Add block to current page
            current_page.blocks.append(block.id)
            current_page.estimated_lines += block.estimated_pdf_lines
            current_page.visual_weight += block.visual_weight

        if current_page.blocks:
            pages.append(current_page)

        return pages

    def _validate_final_layout(self, breaks: List[PageBreakDecision],
                             layout: List[PageLayout],
                             document_structure: DocumentStructure) -> List[PageBreakDecision]:
        """Validate the final layout and adjust if necessary"""

        validated_breaks = []

        for break_decision in breaks:
            # Check if this break creates any new problems
            problems = self._identify_layout_problems(layout, document_structure, [])

            # If break creates problems, reduce confidence
            creates_problems = any(
                problem.get('solution_block_id') == break_decision.block_id
                for problem in problems
            )

            if creates_problems:
                break_decision.confidence *= 0.7  # Reduce confidence
                break_decision.reasoning += " (may create layout issues)"

            # Only keep breaks with sufficient confidence
            if break_decision.confidence > 0.4:
                validated_breaks.append(break_decision)

        return validated_breaks

    def export_decisions(self, decisions: List[PageBreakDecision], output_path: str):
        """Export page break decisions to JSON file"""

        export_data = {
            'page_break_decisions': [
                {
                    'block_id': decision.block_id,
                    'line_number': decision.line_number,
                    'reason': decision.reason.value,
                    'priority': decision.priority.value,
                    'confidence': decision.confidence,
                    'visual_impact_score': decision.visual_impact_score,
                    'content_coherence_score': decision.content_coherence_score,
                    'alternative_locations': decision.alternative_locations,
                    'affected_groups': decision.affected_groups,
                    'reasoning': decision.reasoning
                }
                for decision in decisions
            ],
            'summary': {
                'total_decisions': len(decisions),
                'high_confidence': len([d for d in decisions if d.confidence > 0.8]),
                'medium_confidence': len([d for d in decisions if 0.6 <= d.confidence <= 0.8]),
                'low_confidence': len([d for d in decisions if d.confidence < 0.6]),
                'mandatory_breaks': len([d for d in decisions if d.priority == BreakPriority.MANDATORY]),
                'high_priority': len([d for d in decisions if d.priority == BreakPriority.HIGH]),
            }
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)

def main():
    """Test the smart page break engine"""
    from ai_content_parser import AIContentParser
    from pathlib import Path

    # Initialize components
    parser = AIContentParser()
    engine = SmartPageBreakEngine()

    # Test file
    test_file = "blueprint-ceo.md"

    if Path(test_file).exists():
        print(f"Analyzing page breaks for {test_file}...")

        # Parse document
        document_structure = parser.parse_document(test_file)
        content_groups = parser.get_content_groups_for_page_breaks(document_structure)

        # Analyze optimal page breaks
        decisions = engine.analyze_optimal_page_breaks(document_structure, content_groups)

        # Export decisions
        decisions_file = "smart_page_break_decisions.json"
        engine.export_decisions(decisions, decisions_file)

        # Print summary
        print(f"\n📊 Page Break Analysis Summary:")
        print(f"   • Total break decisions: {len(decisions)}")
        print(f"   • High confidence breaks: {len([d for d in decisions if d.confidence > 0.8])}")
        print(f"   • Medium confidence breaks: {len([d for d in decisions if 0.6 <= d.confidence <= 0.8])}")
        print(f"   • Low confidence breaks: {len([d for d in decisions if d.confidence < 0.6])}")

        print(f"\n🎯 Break Reasons:")
        reason_counts = {}
        for decision in decisions:
            reason_counts[decision.reason.value] = reason_counts.get(decision.reason.value, 0) + 1

        for reason, count in reason_counts.items():
            print(f"   • {reason}: {count}")

        print(f"\n💾 Decisions exported to: {decisions_file}")

        # Show top decisions
        top_decisions = sorted(decisions, key=lambda x: x.confidence, reverse=True)[:5]
        print(f"\n🏆 Top 5 Page Break Decisions:")
        for i, decision in enumerate(top_decisions, 1):
            print(f"   {i}. Line {decision.line_number} - {decision.reasoning} (confidence: {decision.confidence:.2f})")

    else:
        print(f"Test file {test_file} not found!")

if __name__ == "__main__":
    main()
