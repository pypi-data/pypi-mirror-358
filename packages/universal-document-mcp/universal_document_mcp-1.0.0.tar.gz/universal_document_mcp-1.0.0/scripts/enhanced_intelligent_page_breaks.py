#!/usr/bin/env python3
"""
Enhanced Intelligent Page Break System
Addresses the orphan/widow problem by making smarter decisions about page breaks
based on content context, visual balance, and section coherence.
"""

import re
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from pathlib import Path

@dataclass
class ContentSection:
    """Represents a logical content section with its properties"""
    start_line: int
    end_line: int
    heading: str
    heading_level: int
    content_lines: int
    content_type: str  # 'section', 'subsection', 'list', 'paragraph', 'code', 'diagram'
    estimated_pdf_lines: int
    has_subsections: bool
    subsection_count: int
    visual_weight: float  # How much visual space this takes

@dataclass
class PageBreakDecision:
    """Represents a page break decision with reasoning"""
    line_number: int
    reason: str
    confidence: float
    visual_impact: str
    content_coherence: float
    alternative_locations: List[int]

class EnhancedIntelligentPageBreaks:
    """Enhanced page break system with visual and content awareness"""
    
    def __init__(self):
        self.rules = {
            # Visual balance rules
            'min_content_after_heading': 5,  # Minimum lines of content after a heading
            'max_orphan_tolerance': 3,       # Maximum lines that can be orphaned
            'preferred_section_completeness': 0.7,  # Prefer to keep 70% of section together
            
            # Page length rules (estimated PDF lines)
            'min_page_lines': 20,
            'max_page_lines': 45,
            'optimal_page_lines': 35,
            'comfortable_page_range': (25, 40),
            
            # Content coherence rules
            'keep_list_together': True,
            'keep_code_together': True,
            'keep_diagram_together': True,
            'section_break_preference': 0.8,  # Prefer breaks between sections
            
            # Visual aesthetics
            'avoid_single_line_orphans': True,
            'avoid_heading_widows': True,
            'prefer_natural_breaks': True,
        }
    
    def analyze_document_structure(self, file_path: str) -> List[ContentSection]:
        """Analyze document structure to understand content sections"""
        
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        sections = []
        current_section = None
        
        for i, line in enumerate(lines):
            line_stripped = line.strip()
            
            # Detect headings
            if line_stripped.startswith('#'):
                # Save previous section
                if current_section:
                    current_section.end_line = i - 1
                    current_section.content_lines = current_section.end_line - current_section.start_line
                    current_section.estimated_pdf_lines = self._estimate_pdf_lines(
                        lines[current_section.start_line:current_section.end_line + 1]
                    )
                    sections.append(current_section)
                
                # Start new section
                heading_level = len(line_stripped) - len(line_stripped.lstrip('#'))
                current_section = ContentSection(
                    start_line=i,
                    end_line=i,
                    heading=line_stripped,
                    heading_level=heading_level,
                    content_lines=0,
                    content_type='section' if heading_level <= 2 else 'subsection',
                    estimated_pdf_lines=0,
                    has_subsections=False,
                    subsection_count=0,
                    visual_weight=0.0
                )
        
        # Handle last section
        if current_section:
            current_section.end_line = len(lines) - 1
            current_section.content_lines = current_section.end_line - current_section.start_line
            current_section.estimated_pdf_lines = self._estimate_pdf_lines(
                lines[current_section.start_line:current_section.end_line + 1]
            )
            sections.append(current_section)
        
        # Analyze subsections
        self._analyze_subsections(sections)
        
        return sections
    
    def _estimate_pdf_lines(self, content_lines: List[str]) -> int:
        """Estimate how many lines this content will take in PDF"""
        pdf_lines = 0
        in_code_block = False
        
        for line in content_lines:
            line_stripped = line.strip()
            
            # Code blocks
            if line_stripped.startswith('```'):
                in_code_block = not in_code_block
                pdf_lines += 1
                continue
            
            if in_code_block:
                pdf_lines += 1
                continue
            
            # Headings take more visual space
            if line_stripped.startswith('#'):
                pdf_lines += 2  # Heading + spacing
            # Lists
            elif line_stripped.startswith(('-', '*', '+')):
                pdf_lines += 1
            # Numbered lists
            elif re.match(r'^\d+\.', line_stripped):
                pdf_lines += 1
            # Empty lines
            elif not line_stripped:
                pdf_lines += 0.5  # Half line for spacing
            # Regular paragraphs
            else:
                # Estimate word wrapping (assuming ~80 chars per line)
                estimated_lines = max(1, len(line) / 80)
                pdf_lines += estimated_lines
        
        return int(pdf_lines)
    
    def _analyze_subsections(self, sections: List[ContentSection]):
        """Analyze which sections have subsections"""
        for i, section in enumerate(sections):
            if section.heading_level <= 2:  # Major sections
                # Count subsections
                subsection_count = 0
                for j in range(i + 1, len(sections)):
                    if sections[j].heading_level <= section.heading_level:
                        break
                    if sections[j].heading_level == section.heading_level + 1:
                        subsection_count += 1
                
                section.has_subsections = subsection_count > 0
                section.subsection_count = subsection_count
                section.visual_weight = self._calculate_visual_weight(section)
    
    def _calculate_visual_weight(self, section: ContentSection) -> float:
        """Calculate the visual weight/importance of a section"""
        weight = 1.0
        
        # Higher level headings have more weight
        weight += (4 - section.heading_level) * 0.2
        
        # Sections with subsections have more weight
        if section.has_subsections:
            weight += section.subsection_count * 0.1
        
        # Longer sections have more weight
        if section.estimated_pdf_lines > 20:
            weight += 0.3
        elif section.estimated_pdf_lines > 10:
            weight += 0.1
        
        return weight
    
    def suggest_intelligent_page_breaks(self, file_path: str) -> List[PageBreakDecision]:
        """Suggest intelligent page breaks based on content analysis"""
        
        sections = self.analyze_document_structure(file_path)
        decisions = []
        current_page_lines = 0
        
        for i, section in enumerate(sections):
            # Calculate if this section should start on a new page
            decision = self._evaluate_page_break_for_section(
                section, current_page_lines, sections, i
            )
            
            if decision:
                decisions.append(decision)
                current_page_lines = section.estimated_pdf_lines
            else:
                current_page_lines += section.estimated_pdf_lines
            
            # Check if we need to break within the section
            if current_page_lines > self.rules['max_page_lines']:
                internal_break = self._find_internal_break_point(section, current_page_lines)
                if internal_break:
                    decisions.append(internal_break)
                    current_page_lines = section.estimated_pdf_lines - internal_break.line_number + section.start_line
        
        return decisions
    
    def _evaluate_page_break_for_section(
        self, 
        section: ContentSection, 
        current_page_lines: int, 
        all_sections: List[ContentSection], 
        section_index: int
    ) -> Optional[PageBreakDecision]:
        """Evaluate whether a section should start on a new page"""
        
        # Don't break before the first section
        if section_index == 0:
            return None
        
        # Calculate total lines if we include this section
        total_lines = current_page_lines + section.estimated_pdf_lines
        
        # Reasons to force a page break
        force_break_reasons = []
        
        # 1. Page would be too long
        if total_lines > self.rules['max_page_lines']:
            force_break_reasons.append("Page length would exceed maximum")
        
        # 2. Major section (h1, h2) with significant content
        if (section.heading_level <= 2 and 
            section.estimated_pdf_lines >= self.rules['min_content_after_heading'] and
            current_page_lines >= self.rules['min_page_lines']):
            force_break_reasons.append("Major section with substantial content")
        
        # 3. Avoid orphaning section headings
        if (section.estimated_pdf_lines > self.rules['min_content_after_heading'] and
            current_page_lines > self.rules['comfortable_page_range'][1]):
            force_break_reasons.append("Avoid orphaning section heading")
        
        # Reasons to prefer a page break
        prefer_break_reasons = []
        
        # 1. Natural section boundary
        if section.heading_level <= 2:
            prefer_break_reasons.append("Natural section boundary")
        
        # 2. Good page length
        if self.rules['comfortable_page_range'][0] <= current_page_lines <= self.rules['comfortable_page_range'][1]:
            prefer_break_reasons.append("Good page length achieved")
        
        # 3. Section has high visual weight
        if section.visual_weight > 1.5:
            prefer_break_reasons.append("High visual weight section")
        
        # Calculate confidence
        confidence = 0.5
        
        if force_break_reasons:
            confidence = 0.9
        elif prefer_break_reasons:
            confidence = 0.7
        elif total_lines > self.rules['optimal_page_lines']:
            confidence = 0.6
        else:
            return None  # No break needed
        
        # Determine visual impact
        visual_impact = self._assess_visual_impact(section, current_page_lines, total_lines)
        
        # Calculate content coherence
        coherence = self._calculate_content_coherence(section, all_sections, section_index)
        
        return PageBreakDecision(
            line_number=section.start_line,
            reason="; ".join(force_break_reasons + prefer_break_reasons),
            confidence=confidence,
            visual_impact=visual_impact,
            content_coherence=coherence,
            alternative_locations=self._find_alternative_break_points(section, current_page_lines)
        )
    
    def _assess_visual_impact(self, section: ContentSection, current_lines: int, total_lines: int) -> str:
        """Assess the visual impact of the page break decision"""
        
        if current_lines < self.rules['min_page_lines']:
            return "Creates short page - poor visual balance"
        elif current_lines > self.rules['max_page_lines']:
            return "Prevents overly long page - good visual balance"
        elif self.rules['comfortable_page_range'][0] <= current_lines <= self.rules['comfortable_page_range'][1]:
            return "Optimal page length - excellent visual balance"
        else:
            return "Acceptable visual balance"
    
    def _calculate_content_coherence(
        self, 
        section: ContentSection, 
        all_sections: List[ContentSection], 
        section_index: int
    ) -> float:
        """Calculate how well the content flows with this break"""
        
        coherence = 0.5  # Base coherence
        
        # Higher coherence for breaks between major sections
        if section.heading_level <= 2:
            coherence += 0.3
        
        # Lower coherence if breaking related subsections
        if section_index > 0:
            prev_section = all_sections[section_index - 1]
            if (prev_section.heading_level < section.heading_level and
                section.heading_level > 2):
                coherence -= 0.2  # Breaking related subsections
        
        # Higher coherence if section is self-contained
        if not section.has_subsections and section.estimated_pdf_lines >= 10:
            coherence += 0.2
        
        return min(1.0, max(0.0, coherence))
    
    def _find_alternative_break_points(self, section: ContentSection, current_lines: int) -> List[int]:
        """Find alternative break points near the suggested location"""
        alternatives = []
        
        # Could break before previous section if it's a subsection
        if section.heading_level > 2:
            alternatives.append(section.start_line - 1)
        
        # Could break within the section if it's long
        if section.estimated_pdf_lines > 15:
            mid_point = section.start_line + (section.end_line - section.start_line) // 2
            alternatives.append(mid_point)
        
        return alternatives
    
    def _find_internal_break_point(self, section: ContentSection, current_lines: int) -> Optional[PageBreakDecision]:
        """Find a good break point within a long section"""
        
        # This is a simplified version - in practice, you'd analyze the section content
        # to find natural break points like between paragraphs, after lists, etc.
        
        if section.estimated_pdf_lines > 20:
            mid_point = section.start_line + (section.end_line - section.start_line) // 2
            
            return PageBreakDecision(
                line_number=mid_point,
                reason="Long section requires internal break",
                confidence=0.6,
                visual_impact="Prevents overly long section",
                content_coherence=0.4,  # Lower coherence for internal breaks
                alternative_locations=[]
            )
        
        return None
