#!/usr/bin/env python3
"""
Intelligent Page Break Detection System
Analyzes manual page break patterns and automatically determines optimal page break locations
"""

import re
import json
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class PageBreakPattern:
    """Represents a detected page break pattern"""
    line_number: int
    content_before: str
    content_after: str
    pattern_type: str
    confidence: float
    context: Dict

@dataclass
class ContentBlock:
    """Represents a logical content block"""
    start_line: int
    end_line: int
    content_type: str  # heading, paragraph, code_block, diagram, list
    level: int  # for headings
    content: str
    estimated_length: int  # estimated lines when rendered

class IntelligentPageBreakDetector:
    """Analyzes content and suggests optimal page break locations"""
    
    def __init__(self):
        self.patterns = []
        self.content_blocks = []
        self.page_break_rules = {
            'min_lines_per_page': 20,
            'max_lines_per_page': 45,
            'preferred_lines_per_page': 35,
            'avoid_orphan_lines': 3,
            'avoid_widow_lines': 2,
            'heading_break_weight': 10,
            'section_end_weight': 8,
            'diagram_break_weight': 6,
            'paragraph_break_weight': 3
        }
    
    def analyze_manual_breaks(self, file_path: str) -> List[PageBreakPattern]:
        """Analyze existing manual page breaks to learn patterns"""
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        patterns = []
        page_break_regex = r'Page \d+'
        
        for i, line in enumerate(lines):
            if re.search(page_break_regex, line):
                # Analyze context around the page break
                before_context = self._get_context_before(lines, i, 5)
                after_context = self._get_context_after(lines, i, 5)
                
                pattern_type = self._classify_break_pattern(before_context, after_context)
                confidence = self._calculate_confidence(before_context, after_context, pattern_type)
                
                pattern = PageBreakPattern(
                    line_number=i + 1,
                    content_before=before_context,
                    content_after=after_context,
                    pattern_type=pattern_type,
                    confidence=confidence,
                    context={
                        'lines_since_last_break': self._lines_since_last_break(patterns, i),
                        'heading_level_after': self._get_heading_level(after_context),
                        'has_diagram_before': 'mermaid' in before_context.lower() or '```' in before_context,
                        'has_diagram_after': 'mermaid' in after_context.lower() or '```' in after_context
                    }
                )
                patterns.append(pattern)
        
        self.patterns = patterns
        return patterns
    
    def _get_context_before(self, lines: List[str], index: int, context_size: int) -> str:
        """Get context lines before the page break"""
        start = max(0, index - context_size)
        return ''.join(lines[start:index]).strip()
    
    def _get_context_after(self, lines: List[str], index: int, context_size: int) -> str:
        """Get context lines after the page break"""
        end = min(len(lines), index + context_size + 1)
        return ''.join(lines[index + 1:end]).strip()
    
    def _classify_break_pattern(self, before: str, after: str) -> str:
        """Classify the type of page break pattern"""
        # Check if break is before a major heading
        if re.match(r'^#\s+', after):
            return 'before_major_heading'
        elif re.match(r'^##\s+', after):
            return 'before_section_heading'
        elif re.match(r'^###\s+', after):
            return 'before_subsection_heading'
        
        # Check if break is after a diagram or code block
        if '```' in before and not '```' in after:
            return 'after_code_block'
        
        # Check if break is after a section with multiple blank lines
        if before.count('\n\n') >= 2:
            return 'after_section_end'
        
        # Check if break is in the middle of content (less ideal)
        if before.strip() and after.strip() and not after.startswith('#'):
            return 'content_break'
        
        return 'unknown'
    
    def _calculate_confidence(self, before: str, after: str, pattern_type: str) -> float:
        """Calculate confidence score for the page break placement"""
        confidence = 0.5  # base confidence
        
        # Higher confidence for breaks before headings
        if pattern_type.endswith('_heading'):
            confidence += 0.3
        
        # Higher confidence for breaks after code blocks
        if pattern_type == 'after_code_block':
            confidence += 0.2
        
        # Higher confidence for breaks after section ends
        if pattern_type == 'after_section_end':
            confidence += 0.25
        
        # Lower confidence for content breaks
        if pattern_type == 'content_break':
            confidence -= 0.2
        
        # Adjust based on blank lines
        blank_lines_before = before.count('\n\n')
        blank_lines_after = after.count('\n\n')
        
        if blank_lines_before >= 2:
            confidence += 0.1
        if blank_lines_after >= 1:
            confidence += 0.05
        
        return min(1.0, max(0.0, confidence))
    
    def _lines_since_last_break(self, patterns: List[PageBreakPattern], current_line: int) -> int:
        """Calculate lines since the last page break"""
        if not patterns:
            return current_line
        return current_line - patterns[-1].line_number
    
    def _get_heading_level(self, content: str) -> int:
        """Get the heading level of content (0 if not a heading)"""
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('#'):
                return len(line) - len(line.lstrip('#'))
        return 0
    
    def parse_content_blocks(self, file_path: str) -> List[ContentBlock]:
        """Parse content into logical blocks"""
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        blocks = []
        current_block_start = 0
        current_block_type = 'paragraph'
        current_block_level = 0
        in_code_block = False
        
        for i, line in enumerate(lines):
            line_stripped = line.strip()
            
            # Skip page break markers
            if 'Page ' in line and '---' in line:
                continue
            
            # Detect code blocks
            if line_stripped.startswith('```'):
                if in_code_block:
                    # End of code block
                    blocks.append(ContentBlock(
                        start_line=current_block_start,
                        end_line=i,
                        content_type='code_block',
                        level=0,
                        content=''.join(lines[current_block_start:i+1]),
                        estimated_length=i - current_block_start + 1
                    ))
                    in_code_block = False
                    current_block_start = i + 1
                else:
                    # Start of code block
                    if current_block_start < i:
                        blocks.append(ContentBlock(
                            start_line=current_block_start,
                            end_line=i-1,
                            content_type=current_block_type,
                            level=current_block_level,
                            content=''.join(lines[current_block_start:i]),
                            estimated_length=i - current_block_start
                        ))
                    in_code_block = True
                    current_block_start = i
                continue
            
            if in_code_block:
                continue
            
            # Detect headings
            if line_stripped.startswith('#'):
                # Save previous block
                if current_block_start < i:
                    blocks.append(ContentBlock(
                        start_line=current_block_start,
                        end_line=i-1,
                        content_type=current_block_type,
                        level=current_block_level,
                        content=''.join(lines[current_block_start:i]),
                        estimated_length=i - current_block_start
                    ))
                
                # Start new heading block
                heading_level = len(line_stripped) - len(line_stripped.lstrip('#'))
                current_block_start = i
                current_block_type = 'heading'
                current_block_level = heading_level
            
            # Detect paragraph breaks (empty lines)
            elif not line_stripped and current_block_type != 'heading':
                if current_block_start < i:
                    blocks.append(ContentBlock(
                        start_line=current_block_start,
                        end_line=i-1,
                        content_type=current_block_type,
                        level=current_block_level,
                        content=''.join(lines[current_block_start:i]),
                        estimated_length=i - current_block_start
                    ))
                    current_block_start = i + 1
                    current_block_type = 'paragraph'
                    current_block_level = 0
        
        # Add final block
        if current_block_start < len(lines):
            blocks.append(ContentBlock(
                start_line=current_block_start,
                end_line=len(lines)-1,
                content_type=current_block_type,
                level=current_block_level,
                content=''.join(lines[current_block_start:]),
                estimated_length=len(lines) - current_block_start
            ))
        
        self.content_blocks = blocks
        return blocks
    
    def suggest_page_breaks(self, file_path: str) -> List[Dict]:
        """Suggest optimal page break locations based on learned patterns"""
        self.analyze_manual_breaks(file_path)
        self.parse_content_blocks(file_path)
        
        suggestions = []
        current_page_length = 0
        last_break_line = 0
        
        for block in self.content_blocks:
            block_length = block.estimated_length
            
            # Check if adding this block would exceed page length
            if (current_page_length + block_length > self.page_break_rules['max_lines_per_page'] or
                (current_page_length > self.page_break_rules['min_lines_per_page'] and 
                 self._should_break_before_block(block, current_page_length))):
                
                # Suggest page break before this block
                break_score = self._calculate_break_score(block, current_page_length)
                
                suggestions.append({
                    'line_number': block.start_line,
                    'reason': self._get_break_reason(block, current_page_length),
                    'confidence': break_score,
                    'page_length': current_page_length,
                    'block_type': block.content_type,
                    'block_level': block.level,
                    'estimated_new_page_length': block_length
                })
                
                current_page_length = block_length
                last_break_line = block.start_line
            else:
                current_page_length += block_length
        
        return suggestions
    
    def _should_break_before_block(self, block: ContentBlock, current_page_length: int) -> bool:
        """Determine if we should break before this block"""
        # Always break before major headings if page has reasonable content
        if block.content_type == 'heading' and block.level <= 2 and current_page_length >= self.page_break_rules['min_lines_per_page']:
            return True
        
        # Break before code blocks if page is getting long
        if block.content_type == 'code_block' and current_page_length >= self.page_break_rules['preferred_lines_per_page']:
            return True
        
        # Break if we're approaching max page length
        if current_page_length >= self.page_break_rules['preferred_lines_per_page']:
            return True
        
        return False
    
    def _calculate_break_score(self, block: ContentBlock, current_page_length: int) -> float:
        """Calculate a score for how good this page break location is"""
        score = 0.5  # base score
        
        # Prefer breaks before headings
        if block.content_type == 'heading':
            score += 0.3 * (3 - block.level) / 3  # Higher score for higher-level headings
        
        # Prefer breaks before code blocks
        if block.content_type == 'code_block':
            score += 0.2
        
        # Prefer breaks when page length is optimal
        optimal_length = self.page_break_rules['preferred_lines_per_page']
        length_score = 1.0 - abs(current_page_length - optimal_length) / optimal_length
        score += 0.2 * length_score
        
        # Avoid breaks that create very short or very long pages
        if current_page_length < self.page_break_rules['min_lines_per_page']:
            score -= 0.3
        elif current_page_length > self.page_break_rules['max_lines_per_page']:
            score += 0.3
        
        return min(1.0, max(0.0, score))
    
    def _get_break_reason(self, block: ContentBlock, current_page_length: int) -> str:
        """Get human-readable reason for the page break"""
        if block.content_type == 'heading':
            return f"Before level {block.level} heading"
        elif block.content_type == 'code_block':
            return "Before code block/diagram"
        elif current_page_length >= self.page_break_rules['max_lines_per_page']:
            return "Page length exceeded"
        elif current_page_length >= self.page_break_rules['preferred_lines_per_page']:
            return "Optimal page length reached"
        else:
            return "Content boundary"
    
    def generate_report(self, file_path: str) -> Dict:
        """Generate a comprehensive analysis report"""
        patterns = self.analyze_manual_breaks(file_path)
        suggestions = self.suggest_page_breaks(file_path)
        
        # Analyze pattern statistics
        pattern_types = {}
        confidence_scores = []
        
        for pattern in patterns:
            pattern_types[pattern.pattern_type] = pattern_types.get(pattern.pattern_type, 0) + 1
            confidence_scores.append(pattern.confidence)
        
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
        
        report = {
            'analysis_timestamp': datetime.now().isoformat(),
            'file_analyzed': file_path,
            'manual_breaks_found': len(patterns),
            'pattern_distribution': pattern_types,
            'average_confidence': round(avg_confidence, 3),
            'suggested_breaks': len(suggestions),
            'patterns': [
                {
                    'line': p.line_number,
                    'type': p.pattern_type,
                    'confidence': round(p.confidence, 3),
                    'context': p.context
                } for p in patterns
            ],
            'suggestions': suggestions,
            'rules_used': self.page_break_rules
        }
        
        return report

def main():
    """Main function for testing the page break detector"""
    detector = IntelligentPageBreakDetector()
    
    # Analyze the architectural vision document
    file_path = "architectural-vision-enhanced-final.md"
    
    if Path(file_path).exists():
        print(f"Analyzing page break patterns in {file_path}...")
        
        report = detector.generate_report(file_path)
        
        # Save report
        with open("page_break_analysis_report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
        
        print(f"Analysis complete!")
        print(f"Found {report['manual_breaks_found']} manual page breaks")
        print(f"Suggested {report['suggested_breaks']} optimal break locations")
        print(f"Average pattern confidence: {report['average_confidence']:.3f}")
        print(f"Report saved to: page_break_analysis_report.json")
        
        # Print pattern distribution
        print("\nPattern Distribution:")
        for pattern_type, count in report['pattern_distribution'].items():
            print(f"  {pattern_type}: {count}")
        
    else:
        print(f"File {file_path} not found!")

if __name__ == "__main__":
    main()
