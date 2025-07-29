#!/usr/bin/env python3
"""
Document Formatter and Fixer
Automatically detects and fixes formatting issues in Markdown documents
"""

import re
import glob
from pathlib import Path
from typing import List, Dict, Tuple
import json
from datetime import datetime

class DocumentFormatterFixer:
    """Fixes common formatting issues in Markdown documents"""
    
    def __init__(self):
        self.fixes_applied = []
        self.issues_found = []
    
    def analyze_document(self, file_path: str) -> Dict:
        """Analyze a document for formatting issues"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
        
        issues = {
            'duplicate_sections': [],
            'broken_titles': [],
            'inconsistent_headings': [],
            'spacing_issues': []
        }
        
        # Check for duplicate sections
        section_counts = {}
        for i, line in enumerate(lines):
            if line.startswith('#'):
                section = line.strip()
                if section in section_counts:
                    issues['duplicate_sections'].append({
                        'line': i + 1,
                        'section': section,
                        'occurrence': section_counts[section] + 1
                    })
                    section_counts[section] += 1
                else:
                    section_counts[section] = 1
        
        # Check for broken titles
        for i in range(len(lines)-1):
            if (lines[i].strip() and not lines[i].startswith('#') and 
                lines[i+1].strip() and not lines[i+1].startswith('#') and
                len(lines[i]) < 50 and len(lines[i+1]) < 50):
                if any(word in lines[i+1] for word in ['Brief', 'Framework', 'Summary']):
                    issues['broken_titles'].append({
                        'lines': [i+1, i+2],
                        'content': [lines[i], lines[i+1]]
                    })
        
        # Check for inconsistent heading levels
        heading_groups = {}
        for i, line in enumerate(lines):
            if line.startswith('#'):
                # Extract the heading text without the # symbols
                heading_text = line.lstrip('#').strip()
                level = len(line) - len(line.lstrip('#'))
                
                if heading_text in heading_groups:
                    heading_groups[heading_text].append((i+1, level))
                else:
                    heading_groups[heading_text] = [(i+1, level)]
        
        for heading_text, occurrences in heading_groups.items():
            if len(occurrences) > 1:
                levels = [level for _, level in occurrences]
                if len(set(levels)) > 1:
                    issues['inconsistent_headings'].append({
                        'heading': heading_text,
                        'occurrences': occurrences,
                        'levels': levels
                    })
        
        return issues
    
    def fix_duplicate_sections(self, file_path: str) -> bool:
        """Remove duplicate sections, keeping only the first occurrence"""
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        seen_sections = set()
        fixed_lines = []
        sections_removed = []
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            if line.startswith('#'):
                section = line.strip()
                if section in seen_sections:
                    # This is a duplicate section - remove it and its content
                    sections_removed.append((i+1, section))
                    
                    # Skip this section and its content until the next section or end
                    i += 1
                    while i < len(lines) and not lines[i].startswith('#'):
                        i += 1
                    continue
                else:
                    seen_sections.add(section)
            
            fixed_lines.append(line)
            i += 1
        
        if sections_removed:
            # Write the fixed content back
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(fixed_lines)
            
            self.fixes_applied.append({
                'file': file_path,
                'type': 'duplicate_sections_removed',
                'count': len(sections_removed),
                'sections': sections_removed
            })
            return True
        
        return False
    
    def fix_broken_titles(self, file_path: str) -> bool:
        """Fix titles that are split across multiple lines"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
        
        fixed_lines = lines.copy()
        fixes_made = []
        
        i = 0
        while i < len(fixed_lines) - 1:
            line1 = fixed_lines[i].strip()
            line2 = fixed_lines[i+1].strip()
            
            # Check if this looks like a broken title
            if (line1 and not line1.startswith('#') and 
                line2 and not line2.startswith('#') and
                len(line1) < 50 and len(line2) < 50 and
                any(word in line2 for word in ['Brief', 'Framework', 'Summary'])):
                
                # Combine the lines
                combined = f"{line1} {line2}"
                fixed_lines[i] = combined
                fixed_lines.pop(i+1)  # Remove the second line
                
                fixes_made.append({
                    'lines': [i+1, i+2],
                    'original': [line1, line2],
                    'fixed': combined
                })
                
                continue
            
            i += 1
        
        if fixes_made:
            # Write the fixed content back
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(fixed_lines))
            
            self.fixes_applied.append({
                'file': file_path,
                'type': 'broken_titles_fixed',
                'count': len(fixes_made),
                'fixes': fixes_made
            })
            return True
        
        return False
    
    def fix_inconsistent_headings(self, file_path: str) -> bool:
        """Fix inconsistent heading levels for the same content"""
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Find heading groups and determine the most common level
        heading_groups = {}
        for i, line in enumerate(lines):
            if line.startswith('#'):
                heading_text = line.lstrip('#').strip()
                level = len(line) - len(line.lstrip('#'))
                
                if heading_text in heading_groups:
                    heading_groups[heading_text].append((i, level))
                else:
                    heading_groups[heading_text] = [(i, level)]
        
        fixes_made = []
        
        for heading_text, occurrences in heading_groups.items():
            if len(occurrences) > 1:
                levels = [level for _, level in occurrences]
                if len(set(levels)) > 1:
                    # Use the most common level, or the first one if tied
                    level_counts = {}
                    for level in levels:
                        level_counts[level] = level_counts.get(level, 0) + 1
                    
                    target_level = max(level_counts.keys(), key=lambda x: level_counts[x])
                    
                    # Fix all occurrences to use the target level
                    for line_idx, current_level in occurrences:
                        if current_level != target_level:
                            old_line = lines[line_idx]
                            new_line = '#' * target_level + ' ' + heading_text + '\n'
                            lines[line_idx] = new_line
                            
                            fixes_made.append({
                                'line': line_idx + 1,
                                'heading': heading_text,
                                'old_level': current_level,
                                'new_level': target_level
                            })
        
        if fixes_made:
            # Write the fixed content back
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            
            self.fixes_applied.append({
                'file': file_path,
                'type': 'inconsistent_headings_fixed',
                'count': len(fixes_made),
                'fixes': fixes_made
            })
            return True
        
        return False
    
    def fix_document(self, file_path: str) -> Dict:
        """Fix all formatting issues in a document"""
        print(f"Fixing document: {file_path}")
        
        # Analyze issues first
        issues = self.analyze_document(file_path)
        
        fixes_applied = []
        
        # Fix duplicate sections first
        if issues['duplicate_sections']:
            if self.fix_duplicate_sections(file_path):
                fixes_applied.append('duplicate_sections')
                print(f"  ✅ Removed {len(issues['duplicate_sections'])} duplicate sections")
        
        # Fix broken titles
        if issues['broken_titles']:
            if self.fix_broken_titles(file_path):
                fixes_applied.append('broken_titles')
                print(f"  ✅ Fixed {len(issues['broken_titles'])} broken titles")
        
        # Fix inconsistent headings
        if issues['inconsistent_headings']:
            if self.fix_inconsistent_headings(file_path):
                fixes_applied.append('inconsistent_headings')
                print(f"  ✅ Fixed {len(issues['inconsistent_headings'])} inconsistent headings")
        
        if not fixes_applied:
            print(f"  ✅ No issues found in {file_path}")
        
        return {
            'file': file_path,
            'issues_found': issues,
            'fixes_applied': fixes_applied
        }
    
    def batch_fix_directory(self, pattern: str = "*.md") -> Dict:
        """Fix all Markdown files in the current directory"""
        md_files = glob.glob(pattern)
        
        print(f"=== BATCH FIXING {len(md_files)} MARKDOWN FILES ===")
        print()
        
        results = []
        total_fixes = 0
        
        for md_file in md_files:
            # Skip generated files
            if ('_with_page_breaks' in md_file or 
                'TASK_COMPLETION_SUMMARY' in md_file):
                print(f"Skipping generated file: {md_file}")
                continue
            
            result = self.fix_document(md_file)
            results.append(result)
            
            if result['fixes_applied']:
                total_fixes += len(result['fixes_applied'])
        
        print()
        print(f"=== BATCH FIXING COMPLETE ===")
        print(f"Files processed: {len(results)}")
        print(f"Total fixes applied: {total_fixes}")
        
        # Generate report
        report = {
            'timestamp': datetime.now().isoformat(),
            'files_processed': len(results),
            'total_fixes': total_fixes,
            'results': results,
            'fixes_applied': self.fixes_applied
        }
        
        return report

def main():
    """Main function for testing the document formatter"""
    fixer = DocumentFormatterFixer()
    
    # Fix all documents
    report = fixer.batch_fix_directory()
    
    # Save report
    with open("document_formatting_fixes_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    
    print(f"Detailed report saved to: document_formatting_fixes_report.json")

if __name__ == "__main__":
    main()
