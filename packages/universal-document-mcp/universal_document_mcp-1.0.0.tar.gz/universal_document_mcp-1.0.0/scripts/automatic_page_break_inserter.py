#!/usr/bin/env python3
"""
Automatic Page Break Inserter
Applies learned page break patterns to automatically insert optimal page breaks in Markdown documents
"""

import re
import json
from pathlib import Path
from typing import List, Dict, Tuple
from intelligent_page_break_detector import IntelligentPageBreakDetector, ContentBlock
from datetime import datetime

class AutomaticPageBreakInserter:
    """Automatically inserts page breaks based on learned patterns"""
    
    def __init__(self, training_file: str = None):
        self.detector = IntelligentPageBreakDetector()
        self.learned_patterns = {}
        self.page_break_template = "\n\n-------------------------------------------------------------------------------- Page {page_num}\n\n"
        
        if training_file and Path(training_file).exists():
            self.train_from_file(training_file)
    
    def train_from_file(self, training_file: str):
        """Train the system using patterns from an existing file"""
        print(f"Training from {training_file}...")
        
        # Analyze patterns in the training file
        patterns = self.detector.analyze_manual_breaks(training_file)
        
        # Extract pattern statistics
        pattern_stats = {}
        for pattern in patterns:
            pattern_type = pattern.pattern_type
            if pattern_type not in pattern_stats:
                pattern_stats[pattern_type] = {
                    'count': 0,
                    'avg_confidence': 0,
                    'avg_lines_since_last': 0,
                    'contexts': []
                }
            
            stats = pattern_stats[pattern_type]
            stats['count'] += 1
            stats['avg_confidence'] += pattern.confidence
            stats['avg_lines_since_last'] += pattern.context.get('lines_since_last_break', 0)
            stats['contexts'].append(pattern.context)
        
        # Calculate averages
        for pattern_type, stats in pattern_stats.items():
            if stats['count'] > 0:
                stats['avg_confidence'] /= stats['count']
                stats['avg_lines_since_last'] /= stats['count']
        
        self.learned_patterns = pattern_stats
        print(f"Learned {len(pattern_stats)} pattern types from {len(patterns)} examples")
    
    def insert_page_breaks(self, input_file: str, output_file: str = None) -> str:
        """Insert page breaks into a Markdown file"""
        if not output_file:
            output_file = input_file.replace('.md', '_with_page_breaks.md')
        
        # Read the input file
        with open(input_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Remove any existing page break markers
        cleaned_lines = []
        for line in lines:
            if not (re.search(r'Page \d+', line) and '---' in line):
                cleaned_lines.append(line)
        
        # Get suggestions for page breaks
        suggestions = self.detector.suggest_page_breaks(input_file)
        
        # Filter and sort suggestions by confidence
        high_confidence_suggestions = [
            s for s in suggestions 
            if s['confidence'] >= 0.6 and s['page_length'] >= 20
        ]
        high_confidence_suggestions.sort(key=lambda x: x['line_number'])
        
        # Insert page breaks
        output_lines = []
        page_number = 1
        last_break_line = 0
        
        for i, line in enumerate(cleaned_lines):
            # Check if we should insert a page break before this line
            should_break = False
            break_reason = ""
            
            for suggestion in high_confidence_suggestions:
                # Adjust for any lines we've already added
                adjusted_line = suggestion['line_number'] - (len(output_lines) - i)
                
                if i == adjusted_line and i > last_break_line + 15:  # Minimum 15 lines between breaks
                    should_break = True
                    break_reason = suggestion['reason']
                    break
            
            if should_break and i > 0:
                page_number += 1
                page_break = self.page_break_template.format(page_num=page_number)
                output_lines.append(page_break)
                last_break_line = i
                print(f"Inserted page break at line {i+1}: {break_reason}")
            
            output_lines.append(line)
        
        # Write the output file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.writelines(output_lines)
        
        print(f"Page breaks inserted. Output saved to: {output_file}")
        return output_file
    
    def create_document_template(self, document_type: str = "technical") -> Dict:
        """Create a document template with page break guidelines"""
        templates = {
            "technical": {
                "name": "Technical Document Template",
                "description": "For technical specifications, architecture documents, and research papers",
                "rules": {
                    "min_lines_per_page": 25,
                    "max_lines_per_page": 50,
                    "preferred_lines_per_page": 40,
                    "break_before_major_headings": True,
                    "break_before_diagrams": True,
                    "break_after_sections": True,
                    "avoid_orphan_lines": 3,
                    "avoid_widow_lines": 2
                },
                "patterns": {
                    "before_major_heading": {"weight": 0.9, "min_page_length": 20},
                    "before_section_heading": {"weight": 0.8, "min_page_length": 25},
                    "before_subsection_heading": {"weight": 0.6, "min_page_length": 30},
                    "after_code_block": {"weight": 0.7, "min_page_length": 25},
                    "after_section_end": {"weight": 0.6, "min_page_length": 30}
                }
            },
            "business": {
                "name": "Business Document Template",
                "description": "For business plans, proposals, and executive summaries",
                "rules": {
                    "min_lines_per_page": 20,
                    "max_lines_per_page": 45,
                    "preferred_lines_per_page": 35,
                    "break_before_major_headings": True,
                    "break_before_diagrams": False,
                    "break_after_sections": True,
                    "avoid_orphan_lines": 2,
                    "avoid_widow_lines": 2
                },
                "patterns": {
                    "before_major_heading": {"weight": 0.9, "min_page_length": 15},
                    "before_section_heading": {"weight": 0.7, "min_page_length": 20},
                    "before_subsection_heading": {"weight": 0.5, "min_page_length": 25},
                    "after_section_end": {"weight": 0.8, "min_page_length": 20}
                }
            },
            "academic": {
                "name": "Academic Paper Template",
                "description": "For research papers, theses, and academic publications",
                "rules": {
                    "min_lines_per_page": 30,
                    "max_lines_per_page": 55,
                    "preferred_lines_per_page": 45,
                    "break_before_major_headings": True,
                    "break_before_diagrams": True,
                    "break_after_sections": False,
                    "avoid_orphan_lines": 4,
                    "avoid_widow_lines": 3
                },
                "patterns": {
                    "before_major_heading": {"weight": 0.95, "min_page_length": 25},
                    "before_section_heading": {"weight": 0.8, "min_page_length": 30},
                    "before_subsection_heading": {"weight": 0.6, "min_page_length": 35},
                    "after_code_block": {"weight": 0.8, "min_page_length": 30}
                }
            }
        }
        
        return templates.get(document_type, templates["technical"])
    
    def apply_template(self, template: Dict):
        """Apply a document template to the page break rules"""
        if "rules" in template:
            self.detector.page_break_rules.update(template["rules"])
        
        print(f"Applied template: {template.get('name', 'Unknown')}")
        print(f"Description: {template.get('description', 'No description')}")
    
    def batch_process_directory(self, directory: str, pattern: str = "*.md", template_type: str = "technical"):
        """Process all Markdown files in a directory"""
        directory_path = Path(directory)
        if not directory_path.exists():
            print(f"Directory {directory} does not exist!")
            return
        
        # Apply template
        template = self.create_document_template(template_type)
        self.apply_template(template)
        
        # Find all matching files
        md_files = list(directory_path.glob(pattern))
        
        if not md_files:
            print(f"No files matching {pattern} found in {directory}")
            return
        
        print(f"Processing {len(md_files)} files with {template_type} template...")
        
        results = []
        for md_file in md_files:
            try:
                # Skip files that already have page breaks
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if 'Page ' in content and '---' in content:
                    print(f"Skipping {md_file.name} (already has page breaks)")
                    continue
                
                output_file = self.insert_page_breaks(str(md_file))
                results.append({
                    "input_file": str(md_file),
                    "output_file": output_file,
                    "status": "success"
                })
                
            except Exception as e:
                print(f"Error processing {md_file.name}: {e}")
                results.append({
                    "input_file": str(md_file),
                    "output_file": None,
                    "status": "error",
                    "error": str(e)
                })
        
        # Save batch processing report
        report = {
            "timestamp": datetime.now().isoformat(),
            "directory": directory,
            "pattern": pattern,
            "template_type": template_type,
            "files_processed": len(results),
            "successful": len([r for r in results if r["status"] == "success"]),
            "failed": len([r for r in results if r["status"] == "error"]),
            "results": results
        }
        
        report_file = directory_path / "page_break_batch_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        
        print(f"Batch processing complete! Report saved to: {report_file}")
        return results
    
    def generate_summary_report(self) -> Dict:
        """Generate a summary of the learned patterns and capabilities"""
        return {
            "system_info": {
                "name": "Automatic Page Break Inserter",
                "version": "1.0",
                "timestamp": datetime.now().isoformat()
            },
            "learned_patterns": self.learned_patterns,
            "current_rules": self.detector.page_break_rules,
            "available_templates": ["technical", "business", "academic"],
            "capabilities": [
                "Pattern learning from existing documents",
                "Automatic page break insertion",
                "Multiple document templates",
                "Batch processing",
                "Confidence-based filtering",
                "Customizable rules"
            ]
        }

def main():
    """Main function for testing the automatic page break inserter"""
    inserter = AutomaticPageBreakInserter()
    
    # Train from the architectural vision document
    training_file = "architectural-vision-enhanced-final.md"
    if Path(training_file).exists():
        inserter.train_from_file(training_file)
    
    # Test on other documents that don't have page breaks
    test_files = [
        "blueprint-ceo.md",
        "blueprint-new.md",
        "blueprint-complete-with-diagrams.md"
    ]
    
    print("\nTesting automatic page break insertion...")
    for test_file in test_files:
        if Path(test_file).exists():
            print(f"\nProcessing {test_file}...")
            try:
                output_file = inserter.insert_page_breaks(test_file)
                print(f"Success! Output: {output_file}")
            except Exception as e:
                print(f"Error processing {test_file}: {e}")
        else:
            print(f"File {test_file} not found, skipping...")
    
    # Generate summary report
    summary = inserter.generate_summary_report()
    with open("page_break_system_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    
    print(f"\nSystem summary saved to: page_break_system_summary.json")

if __name__ == "__main__":
    main()
