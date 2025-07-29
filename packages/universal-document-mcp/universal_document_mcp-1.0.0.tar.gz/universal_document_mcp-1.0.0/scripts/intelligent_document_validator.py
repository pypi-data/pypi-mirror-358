#!/usr/bin/env python3
"""
Intelligent Document Validation Tool for MCP Server
Automatically detects and flags unintentional duplicate content while preserving legitimate repetitions
"""

import re
import glob
import json
import hashlib
from pathlib import Path
from typing import List, Dict, Tuple, Set, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
from difflib import SequenceMatcher
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class DuplicateIssue:
    """Represents a detected duplicate content issue"""
    file_path: str
    issue_type: str  # 'exact_duplicate', 'near_duplicate', 'inconsistent_heading', 'broken_flow'
    severity: str    # 'critical', 'warning', 'info'
    line_numbers: List[int]
    content: str
    context: str
    similarity_score: float
    suggested_action: str
    is_legitimate: bool
    confidence: float

@dataclass
class ValidationReport:
    """Complete validation report for a document"""
    file_path: str
    total_issues: int
    critical_issues: int
    warning_issues: int
    info_issues: int
    issues: List[DuplicateIssue]
    processing_time: float
    timestamp: str

class IntelligentDocumentValidator:
    """Advanced document validator with contextual analysis"""
    
    def __init__(self):
        self.legitimate_patterns = self._load_legitimate_patterns()
        self.section_templates = self._load_section_templates()
        self.validation_reports = []
        
    def _load_legitimate_patterns(self) -> Dict[str, List[str]]:
        """Load patterns that are considered legitimate duplicates"""
        return {
            'technical_specs': [
                r'#### Technical Specifications',
                r'### Technical Requirements',
                r'## Implementation Details'
            ],
            'tier_structures': [
                r'#### Tier \d+:',
                r'### Phase \d+:',
                r'## Stage \d+'
            ],
            'standard_sections': [
                r'### Key Components',
                r'### Objectives',
                r'### Deliverables',
                r'### Success Metrics'
            ],
            'document_structure': [
                r'## Executive Summary',
                r'## Conclusion',
                r'## Next Steps'
            ]
        }
    
    def _load_section_templates(self) -> Dict[str, Set[str]]:
        """Load common section templates that legitimately repeat"""
        return {
            'tier_sections': {
                'Key Components', 'Technical Specifications', 'Performance Metrics',
                'Integration Points', 'Validation Criteria'
            },
            'phase_sections': {
                'Objectives', 'Deliverables', 'Success Metrics', 'Timeline',
                'Resources Required', 'Risk Assessment'
            },
            'analysis_sections': {
                'Current State', 'Proposed Solution', 'Benefits', 'Implementation',
                'Risks', 'Mitigation Strategies'
            }
        }
    
    def _calculate_content_similarity(self, content1: str, content2: str) -> float:
        """Calculate similarity between two content blocks"""
        # Normalize content for comparison
        norm1 = re.sub(r'\s+', ' ', content1.strip().lower())
        norm2 = re.sub(r'\s+', ' ', content2.strip().lower())
        
        return SequenceMatcher(None, norm1, norm2).ratio()
    
    def _extract_content_blocks(self, lines: List[str]) -> List[Dict]:
        """Extract content blocks with their context"""
        blocks = []
        current_block = {'lines': [], 'start_line': 0, 'heading': '', 'level': 0}
        
        for i, line in enumerate(lines):
            if line.startswith('#'):
                # Save previous block if it has content
                if current_block['lines']:
                    current_block['end_line'] = i - 1
                    current_block['content'] = '\n'.join(current_block['lines'])
                    blocks.append(current_block.copy())
                
                # Start new block
                level = len(line) - len(line.lstrip('#'))
                heading = line.lstrip('#').strip()
                current_block = {
                    'lines': [],
                    'start_line': i,
                    'heading': heading,
                    'level': level,
                    'heading_line': i
                }
            else:
                current_block['lines'].append(line)
        
        # Add final block
        if current_block['lines']:
            current_block['end_line'] = len(lines) - 1
            current_block['content'] = '\n'.join(current_block['lines'])
            blocks.append(current_block)
        
        return blocks
    
    def _is_legitimate_duplicate(self, heading: str, content: str, context: Dict) -> Tuple[bool, float, str]:
        """Determine if a duplicate is legitimate based on context"""
        confidence = 0.0
        reason = ""
        
        # Check for tier/phase patterns
        if re.search(r'(tier|phase|stage|step)\s+\d+', heading.lower()):
            confidence += 0.4
            reason += "Numbered section pattern; "
        
        # Check for template sections
        for template_type, sections in self.section_templates.items():
            if heading in sections:
                confidence += 0.3
                reason += f"Standard {template_type} template; "
        
        # Check for legitimate patterns
        for pattern_type, patterns in self.legitimate_patterns.items():
            for pattern in patterns:
                if re.search(pattern, f"# {heading}", re.IGNORECASE):
                    confidence += 0.3
                    reason += f"Matches {pattern_type} pattern; "
        
        # Check content context
        if len(content.strip()) < 100:  # Short sections are more likely to be templates
            confidence += 0.2
            reason += "Short template section; "
        
        # Check for technical specifications pattern
        if 'specification' in heading.lower() or 'requirement' in heading.lower():
            confidence += 0.2
            reason += "Technical specification section; "
        
        # Check for different parent contexts
        parent_context = context.get('parent_heading', '')
        if parent_context and 'tier' in parent_context.lower():
            confidence += 0.3
            reason += "Different tier context; "
        
        is_legitimate = confidence >= 0.5
        return is_legitimate, min(confidence, 1.0), reason.strip('; ')
    
    def _detect_exact_duplicates(self, blocks: List[Dict]) -> List[DuplicateIssue]:
        """Detect exact duplicate headings and content"""
        issues = []
        heading_occurrences = {}
        
        for block in blocks:
            heading = block['heading']
            if not heading:
                continue
                
            heading_key = f"{heading}_{block['level']}"
            
            if heading_key in heading_occurrences:
                # Found duplicate heading
                original_block = heading_occurrences[heading_key]
                
                # Check if it's legitimate
                context = {
                    'parent_heading': self._get_parent_heading(blocks, block),
                    'document_section': self._get_document_section(blocks, block)
                }
                
                is_legitimate, confidence, reason = self._is_legitimate_duplicate(
                    heading, block['content'], context
                )
                
                if not is_legitimate:
                    issue = DuplicateIssue(
                        file_path="",  # Will be set by caller
                        issue_type="exact_duplicate",
                        severity="critical" if confidence < 0.2 else "warning",
                        line_numbers=[original_block['heading_line'] + 1, block['heading_line'] + 1],
                        content=heading,
                        context=f"Original at line {original_block['heading_line'] + 1}, duplicate at line {block['heading_line'] + 1}",
                        similarity_score=1.0,
                        suggested_action="Remove duplicate section or merge content",
                        is_legitimate=False,
                        confidence=1.0 - confidence
                    )
                    issues.append(issue)
            else:
                heading_occurrences[heading_key] = block
        
        return issues
    
    def _detect_near_duplicates(self, blocks: List[Dict], threshold: float = 0.9) -> List[DuplicateIssue]:
        """Detect near-duplicate content blocks"""
        issues = []
        
        for i, block1 in enumerate(blocks):
            for j, block2 in enumerate(blocks[i+1:], i+1):
                if not block1['content'].strip() or not block2['content'].strip():
                    continue
                
                similarity = self._calculate_content_similarity(
                    block1['content'], block2['content']
                )
                
                if similarity >= threshold:
                    # Check if it's legitimate
                    context = {
                        'parent_heading': self._get_parent_heading(blocks, block2),
                        'document_section': self._get_document_section(blocks, block2)
                    }
                    
                    is_legitimate, confidence, reason = self._is_legitimate_duplicate(
                        block2['heading'], block2['content'], context
                    )
                    
                    if not is_legitimate:
                        issue = DuplicateIssue(
                            file_path="",
                            issue_type="near_duplicate",
                            severity="warning" if similarity < 0.95 else "critical",
                            line_numbers=[block1['start_line'] + 1, block2['start_line'] + 1],
                            content=f"Block 1: {block1['heading'][:50]}...\nBlock 2: {block2['heading'][:50]}...",
                            context=f"Similarity: {similarity:.2%}, Reason: {reason}",
                            similarity_score=similarity,
                            suggested_action="Review and merge similar content or mark as intentional",
                            is_legitimate=False,
                            confidence=similarity
                        )
                        issues.append(issue)
        
        return issues
    
    def _get_parent_heading(self, blocks: List[Dict], target_block: Dict) -> str:
        """Get the parent heading for a block"""
        target_level = target_block['level']
        target_line = target_block['start_line']
        
        for block in reversed(blocks):
            if (block['start_line'] < target_line and 
                block['level'] < target_level and 
                block['heading']):
                return block['heading']
        
        return ""
    
    def _get_document_section(self, blocks: List[Dict], target_block: Dict) -> str:
        """Get the document section (top-level heading) for a block"""
        target_line = target_block['start_line']
        
        for block in reversed(blocks):
            if block['start_line'] < target_line and block['level'] == 1:
                return block['heading']
        
        return "Document Start"

    def _detect_inconsistent_headings(self, blocks: List[Dict]) -> List[DuplicateIssue]:
        """Detect inconsistent heading levels for the same content"""
        issues = []
        heading_levels = {}

        for block in blocks:
            heading = block['heading']
            if not heading:
                continue

            level = block['level']

            if heading in heading_levels:
                existing_levels = heading_levels[heading]
                if level not in [l['level'] for l in existing_levels]:
                    # Found inconsistent heading level
                    issue = DuplicateIssue(
                        file_path="",
                        issue_type="inconsistent_heading",
                        severity="warning",
                        line_numbers=[l['line'] + 1 for l in existing_levels] + [block['heading_line'] + 1],
                        content=heading,
                        context=f"Levels used: {sorted(set([l['level'] for l in existing_levels] + [level]))}",
                        similarity_score=0.8,
                        suggested_action="Standardize heading levels for consistent content",
                        is_legitimate=False,
                        confidence=0.8
                    )
                    issues.append(issue)

                heading_levels[heading].append({
                    'level': level,
                    'line': block['heading_line']
                })
            else:
                heading_levels[heading] = [{
                    'level': level,
                    'line': block['heading_line']
                }]

        return issues

    def _detect_broken_flow(self, blocks: List[Dict]) -> List[DuplicateIssue]:
        """Detect broken content flow indicating accidental duplication"""
        issues = []

        for i, block in enumerate(blocks[:-1]):
            next_block = blocks[i + 1]

            # Check for identical consecutive sections
            if (block['heading'] == next_block['heading'] and
                block['level'] == next_block['level']):

                content_similarity = self._calculate_content_similarity(
                    block['content'], next_block['content']
                )

                if content_similarity > 0.7:
                    issue = DuplicateIssue(
                        file_path="",
                        issue_type="broken_flow",
                        severity="critical",
                        line_numbers=[block['start_line'] + 1, next_block['start_line'] + 1],
                        content=f"Consecutive identical sections: {block['heading']}",
                        context=f"Content similarity: {content_similarity:.2%}",
                        similarity_score=content_similarity,
                        suggested_action="Remove duplicate consecutive section",
                        is_legitimate=False,
                        confidence=content_similarity
                    )
                    issues.append(issue)

        return issues

    def validate_document(self, file_path: str) -> ValidationReport:
        """Validate a single document for duplicate content issues"""
        start_time = datetime.now()

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')

            # Extract content blocks
            blocks = self._extract_content_blocks(lines)

            # Run all detection methods
            all_issues = []
            all_issues.extend(self._detect_exact_duplicates(blocks))
            all_issues.extend(self._detect_near_duplicates(blocks))
            all_issues.extend(self._detect_inconsistent_headings(blocks))
            all_issues.extend(self._detect_broken_flow(blocks))

            # Set file path for all issues
            for issue in all_issues:
                issue.file_path = file_path

            # Count issues by severity
            critical_count = sum(1 for issue in all_issues if issue.severity == 'critical')
            warning_count = sum(1 for issue in all_issues if issue.severity == 'warning')
            info_count = sum(1 for issue in all_issues if issue.severity == 'info')

            processing_time = (datetime.now() - start_time).total_seconds()

            report = ValidationReport(
                file_path=file_path,
                total_issues=len(all_issues),
                critical_issues=critical_count,
                warning_issues=warning_count,
                info_issues=info_count,
                issues=all_issues,
                processing_time=processing_time,
                timestamp=datetime.now().isoformat()
            )

            logger.info(f"Validated {file_path}: {len(all_issues)} issues found")
            return report

        except Exception as e:
            logger.error(f"Error validating {file_path}: {e}")
            return ValidationReport(
                file_path=file_path,
                total_issues=0,
                critical_issues=0,
                warning_issues=0,
                info_issues=0,
                issues=[],
                processing_time=0.0,
                timestamp=datetime.now().isoformat()
            )

    def batch_validate_directory(self, pattern: str = "*.md", exclude_patterns: List[str] = None) -> Dict:
        """Validate all Markdown files in the current directory"""
        if exclude_patterns is None:
            exclude_patterns = ['*_with_page_breaks.md', 'TASK_*.md', '*_SUMMARY.md']

        md_files = glob.glob(pattern)

        # Filter out excluded patterns
        filtered_files = []
        for file in md_files:
            should_exclude = False
            for exclude_pattern in exclude_patterns:
                if Path(file).match(exclude_pattern):
                    should_exclude = True
                    break
            if not should_exclude:
                filtered_files.append(file)

        print(f"=== INTELLIGENT DOCUMENT VALIDATION ===")
        print(f"Scanning {len(filtered_files)} Markdown files...")
        print()

        reports = []
        total_issues = 0
        critical_issues = 0

        for file_path in filtered_files:
            report = self.validate_document(file_path)
            reports.append(report)
            total_issues += report.total_issues
            critical_issues += report.critical_issues

            # Print summary for each file
            if report.total_issues > 0:
                print(f"📄 {file_path}")
                print(f"   Issues: {report.total_issues} (Critical: {report.critical_issues}, Warning: {report.warning_issues})")

                # Show top issues
                for issue in report.issues[:3]:  # Show first 3 issues
                    print(f"   • {issue.severity.upper()}: {issue.issue_type} - {issue.content[:60]}...")

                if len(report.issues) > 3:
                    print(f"   ... and {len(report.issues) - 3} more issues")
                print()
            else:
                print(f"✅ {file_path} - No issues found")

        # Generate comprehensive report
        batch_report = {
            'timestamp': datetime.now().isoformat(),
            'files_processed': len(filtered_files),
            'total_issues': total_issues,
            'critical_issues': critical_issues,
            'files_with_issues': len([r for r in reports if r.total_issues > 0]),
            'validation_reports': [asdict(report) for report in reports],
            'summary': {
                'clean_files': len([r for r in reports if r.total_issues == 0]),
                'files_needing_attention': len([r for r in reports if r.critical_issues > 0]),
                'average_processing_time': sum(r.processing_time for r in reports) / len(reports) if reports else 0
            }
        }

        print("=== VALIDATION SUMMARY ===")
        print(f"Files processed: {batch_report['files_processed']}")
        print(f"Total issues found: {batch_report['total_issues']}")
        print(f"Critical issues: {batch_report['critical_issues']}")
        print(f"Files needing attention: {batch_report['summary']['files_needing_attention']}")
        print(f"Clean files: {batch_report['summary']['clean_files']}")

        return batch_report

    def generate_detailed_report(self, batch_report: Dict, output_file: str = "validation_report.json") -> str:
        """Generate a detailed validation report"""

        # Save JSON report
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(batch_report, f, indent=2, ensure_ascii=False)

        # Generate human-readable report
        markdown_report = f"# Document Validation Report\n\n"
        markdown_report += f"**Generated:** {batch_report['timestamp']}\n\n"
        markdown_report += f"## Summary\n\n"
        markdown_report += f"- **Files Processed:** {batch_report['files_processed']}\n"
        markdown_report += f"- **Total Issues:** {batch_report['total_issues']}\n"
        markdown_report += f"- **Critical Issues:** {batch_report['critical_issues']}\n"
        markdown_report += f"- **Files Needing Attention:** {batch_report['summary']['files_needing_attention']}\n"
        markdown_report += f"- **Clean Files:** {batch_report['summary']['clean_files']}\n\n"

        # Detailed issues by file
        markdown_report += f"## Detailed Issues by File\n\n"

        for report_data in batch_report['validation_reports']:
            if report_data['total_issues'] > 0:
                markdown_report += f"### {report_data['file_path']}\n\n"
                markdown_report += f"**Issues Found:** {report_data['total_issues']} "
                markdown_report += f"(Critical: {report_data['critical_issues']}, "
                markdown_report += f"Warning: {report_data['warning_issues']})\n\n"

                for issue in report_data['issues']:
                    severity_emoji = {"critical": "🚨", "warning": "⚠️", "info": "ℹ️"}
                    markdown_report += f"#### {severity_emoji.get(issue['severity'], '•')} {issue['issue_type'].replace('_', ' ').title()}\n\n"
                    markdown_report += f"- **Lines:** {', '.join(map(str, issue['line_numbers']))}\n"
                    markdown_report += f"- **Content:** {issue['content'][:100]}...\n"
                    markdown_report += f"- **Context:** {issue['context']}\n"
                    markdown_report += f"- **Suggested Action:** {issue['suggested_action']}\n"
                    markdown_report += f"- **Confidence:** {issue['confidence']:.2%}\n\n"

        # Save markdown report
        markdown_file = output_file.replace('.json', '.md')
        with open(markdown_file, 'w', encoding='utf-8') as f:
            f.write(markdown_report)

        return markdown_file

    def auto_fix_critical_issues(self, file_path: str, backup: bool = True) -> Dict:
        """Automatically fix critical duplicate issues with user confirmation"""

        if backup:
            backup_path = f"{file_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            with open(file_path, 'r', encoding='utf-8') as src, open(backup_path, 'w', encoding='utf-8') as dst:
                dst.write(src.read())
            print(f"📋 Backup created: {backup_path}")

        # Validate document to get issues
        report = self.validate_document(file_path)
        critical_issues = [issue for issue in report.issues if issue.severity == 'critical']

        if not critical_issues:
            return {'status': 'no_critical_issues', 'fixes_applied': 0}

        print(f"🔧 Found {len(critical_issues)} critical issues in {file_path}")

        # Read file content
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        fixes_applied = []
        lines_to_remove = set()

        for issue in critical_issues:
            if issue.issue_type in ['exact_duplicate', 'broken_flow']:
                # For exact duplicates and broken flow, remove the later occurrence
                if len(issue.line_numbers) >= 2:
                    # Remove the second occurrence (keep the first)
                    remove_line = max(issue.line_numbers) - 1  # Convert to 0-based index

                    # Find the end of the section to remove
                    section_end = remove_line
                    for i in range(remove_line + 1, len(lines)):
                        if lines[i].startswith('#'):
                            break
                        section_end = i

                    # Mark lines for removal
                    for line_num in range(remove_line, section_end + 1):
                        lines_to_remove.add(line_num)

                    fixes_applied.append({
                        'issue_type': issue.issue_type,
                        'lines_removed': list(range(remove_line + 1, section_end + 2)),  # Convert back to 1-based
                        'content': issue.content
                    })

        # Apply fixes by removing marked lines
        if lines_to_remove:
            fixed_lines = [line for i, line in enumerate(lines) if i not in lines_to_remove]

            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(fixed_lines)

            print(f"✅ Applied {len(fixes_applied)} fixes to {file_path}")

            return {
                'status': 'fixes_applied',
                'fixes_applied': len(fixes_applied),
                'backup_path': backup_path if backup else None,
                'fixes_details': fixes_applied
            }
        else:
            return {'status': 'no_fixes_needed', 'fixes_applied': 0}

    def integrate_with_pdf_pipeline(self, pre_conversion_check: bool = True) -> Dict:
        """Integration point for the existing PDF conversion pipeline"""

        print("🔍 Running intelligent document validation before PDF conversion...")

        # Run validation
        batch_report = self.batch_validate_directory()

        # Generate reports
        report_file = self.generate_detailed_report(batch_report, "pre_conversion_validation.json")

        # Check if there are critical issues
        critical_files = [
            report for report in batch_report['validation_reports']
            if report['critical_issues'] > 0
        ]

        if critical_files and pre_conversion_check:
            print(f"\n⚠️  WARNING: {len(critical_files)} files have critical issues!")
            print("Files with critical issues:")
            for report in critical_files:
                print(f"  • {report['file_path']}: {report['critical_issues']} critical issues")

            print(f"\n📊 Detailed report saved to: {report_file}")

            # Ask for user decision
            response = input("\nProceed with PDF conversion? (y/n/fix): ").lower().strip()

            if response == 'fix':
                print("\n🔧 Auto-fixing critical issues...")
                for report in critical_files:
                    fix_result = self.auto_fix_critical_issues(report['file_path'])
                    print(f"  {report['file_path']}: {fix_result['status']}")

                # Re-validate after fixes
                print("\n🔍 Re-validating after fixes...")
                updated_report = self.batch_validate_directory()
                return {
                    'status': 'fixes_applied',
                    'proceed_with_conversion': True,
                    'validation_report': updated_report
                }

            elif response == 'y':
                return {
                    'status': 'proceed_with_issues',
                    'proceed_with_conversion': True,
                    'validation_report': batch_report
                }
            else:
                return {
                    'status': 'conversion_cancelled',
                    'proceed_with_conversion': False,
                    'validation_report': batch_report
                }
        else:
            print("✅ All documents passed validation!")
            return {
                'status': 'validation_passed',
                'proceed_with_conversion': True,
                'validation_report': batch_report
            }

def main():
    """Main function for testing the intelligent document validator"""
    validator = IntelligentDocumentValidator()

    # Run batch validation
    batch_report = validator.batch_validate_directory()

    # Generate detailed report
    report_file = validator.generate_detailed_report(batch_report)
    print(f"\n📊 Detailed report saved to: {report_file}")

    # Integration test
    integration_result = validator.integrate_with_pdf_pipeline(pre_conversion_check=False)
    print(f"\n🔗 Integration result: {integration_result['status']}")

if __name__ == "__main__":
    main()
