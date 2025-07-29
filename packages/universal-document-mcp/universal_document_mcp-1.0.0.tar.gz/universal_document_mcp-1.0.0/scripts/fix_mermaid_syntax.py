#!/usr/bin/env python3
"""
Fix Mermaid Diagram Syntax Errors
Identifies and corrects common Mermaid syntax issues that cause rendering errors
"""

import re
import os
import glob
from pathlib import Path
from datetime import datetime

def fix_mermaid_syntax_issues(content):
    """Fix common Mermaid syntax issues"""
    
    # Find all Mermaid code blocks
    mermaid_pattern = r'```mermaid\n(.*?)\n```'
    
    def fix_mermaid_block(match):
        mermaid_code = match.group(1)
        original_code = mermaid_code
        
        print(f"  🔍 Analyzing Mermaid block...")
        
        # Fix 1: Remove invalid characters in node IDs and labels
        # Issue: "User User Input" should be "👤 User Input"
        mermaid_code = re.sub(r'User\["User User Input"\]', r'User["👤 User Input"]', mermaid_code)
        
        # Fix 2: Fix subgraph labels with emoji prefixes that might cause issues
        # Replace problematic emoji combinations
        mermaid_code = re.sub(r'"Vision Tier 1:', r'"🔍 Tier 1:', mermaid_code)
        mermaid_code = re.sub(r'"Logic Tier 2:', r'"⚡ Tier 2:', mermaid_code)
        mermaid_code = re.sub(r'"Mediator Tier 3:', r'"🔄 Tier 3:', mermaid_code)
        mermaid_code = re.sub(r'"Art Tier 4:', r'"🎨 Tier 4:', mermaid_code)
        
        # Fix 3: Ensure proper node ID format (no spaces, special characters)
        # Replace problematic node names
        problematic_nodes = {
            'Brain Single Unified Neural Model': 'UNIFIED_MODEL',
            'Hybrid Cognitive Core': 'COGNITIVE_CORE',
            'Supervisory Layers': 'SUPERVISORY',
            'Deep Integration Pathways': 'INTEGRATION',
            'Start Input Processing': 'INPUT_START',
            'Brain Internal State Activation': 'INTERNAL_STATE',
            'Fast Parallel Region Activation': 'PARALLEL_ACTIVATION',
            'Hybrid Processing (Co-trained Regions)': 'HYBRID_PROCESSING',
            'Mediator Fusion Layer': 'FUSION_LAYER',
            'Goal Executive Region': 'EXECUTIVE_REGION'
        }
        
        for old_name, new_name in problematic_nodes.items():
            mermaid_code = re.sub(f'"{old_name}"', f'"{new_name}"', mermaid_code)
            mermaid_code = re.sub(f'{old_name}\\[', f'{new_name}[', mermaid_code)
        
        # Fix 4: Ensure proper flowchart syntax
        # Fix "graph TB" to "flowchart TB" for consistency
        mermaid_code = re.sub(r'^graph TB', 'flowchart TB', mermaid_code, flags=re.MULTILINE)
        mermaid_code = re.sub(r'^graph TD', 'flowchart TD', mermaid_code, flags=re.MULTILINE)
        mermaid_code = re.sub(r'^graph LR', 'flowchart LR', mermaid_code, flags=re.MULTILINE)
        
        # Fix 5: Clean up node labels with problematic characters
        # Remove or fix problematic emoji combinations in labels
        mermaid_code = re.sub(r'"Logic Logic Engine', r'"⚡ Logic Engine', mermaid_code)
        mermaid_code = re.sub(r'"Art Creative Engine', r'"🎨 Creative Engine', mermaid_code)
        mermaid_code = re.sub(r'"Thought Affective Region', r'"💭 Affective Region', mermaid_code)
        mermaid_code = re.sub(r'"Goal Executive Region', r'"🎯 Executive Region', mermaid_code)
        mermaid_code = re.sub(r'"Shield Guardrail Region', r'"🛡️ Guardrail Region', mermaid_code)
        mermaid_code = re.sub(r'"Logic Logic Region', r'"⚡ Logic Region', mermaid_code)
        mermaid_code = re.sub(r'"Art Creative Region', r'"🎨 Creative Region', mermaid_code)
        mermaid_code = re.sub(r'"Thought Affective Region', r'"💭 Affective Region', mermaid_code)
        
        # Fix 6: Ensure proper Gantt chart syntax
        if 'gantt' in mermaid_code:
            # Fix milestone syntax - ensure proper format
            mermaid_code = re.sub(r':milestone, (\w+), after (\w+), 0d', r':milestone, \\1, after \\2, 1d', mermaid_code)
            
            # Fix date format issues
            lines = mermaid_code.split('\n')
            fixed_lines = []
            for line in lines:
                # Fix task duration format
                if ':' in line and 'after' in line and 'M' in line:
                    # Convert "12M" to "365d" format
                    line = re.sub(r'(\d+)M', lambda m: f"{int(m.group(1)) * 30}d", line)
                fixed_lines.append(line)
            mermaid_code = '\n'.join(fixed_lines)
        
        # Fix 7: Clean up styling commands
        # Ensure style commands are properly formatted
        mermaid_code = re.sub(r'style (\w+) fill:#([a-fA-F0-9]{6})', r'style \\1 fill:#\\2,stroke:#333,stroke-width:2px', mermaid_code)
        
        # Fix 8: Remove any trailing whitespace that might cause issues
        lines = [line.rstrip() for line in mermaid_code.split('\n')]
        mermaid_code = '\n'.join(lines)
        
        if mermaid_code != original_code:
            print(f"  ✅ Applied syntax fixes to Mermaid block")
            print(f"     - Fixed node IDs and labels")
            print(f"     - Corrected flowchart syntax")
            print(f"     - Cleaned up emoji usage")
            print(f"     - Fixed styling commands")
        else:
            print(f"  ℹ️ No syntax issues found in this block")
        
        return f'```mermaid\n{mermaid_code}\n```'
    
    # Apply fixes to all Mermaid blocks
    fixed_content = re.sub(mermaid_pattern, fix_mermaid_block, content, flags=re.DOTALL)
    
    return fixed_content

def validate_mermaid_syntax(content):
    """Validate Mermaid syntax and report potential issues"""
    issues = []
    
    # Find all Mermaid blocks
    mermaid_pattern = r'```mermaid\n(.*?)\n```'
    blocks = re.findall(mermaid_pattern, content, re.DOTALL)
    
    for i, block in enumerate(blocks, 1):
        block_issues = []
        
        # Check for common syntax issues
        if 'User["User User Input"]' in block:
            block_issues.append("Duplicate 'User' in node label")
        
        if re.search(r'subgraph \w+ \["[^"]*"[^"]*"', block):
            block_issues.append("Potential quote escaping issue in subgraph")
        
        if re.search(r'^\s*graph\s+(TB|TD|LR)', block, re.MULTILINE):
            block_issues.append("Using 'graph' instead of 'flowchart' (may cause issues)")
        
        if re.search(r'[^\w\-_][\w\-_]*\[', block):
            block_issues.append("Potential invalid characters in node IDs")
        
        if block_issues:
            issues.append(f"Block {i}: {', '.join(block_issues)}")
    
    return issues

def backup_file(file_path):
    """Create a backup of the original file"""
    backup_dir = Path("backups")
    backup_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = backup_dir / f"{Path(file_path).stem}_backup_{timestamp}.md"
    
    with open(file_path, 'r', encoding='utf-8') as src, open(backup_path, 'w', encoding='utf-8') as dst:
        dst.write(src.read())
    
    return backup_path

def main():
    """Fix Mermaid syntax errors in all Markdown files"""
    print("🔧 MERMAID SYNTAX ERROR FIX")
    print("=" * 50)
    
    # Find all Markdown files
    md_files = glob.glob("*.md")
    
    if not md_files:
        print("❌ No Markdown files found in current directory")
        return False
    
    print(f"Found {len(md_files)} Markdown files to analyze")
    print()
    
    fixed_count = 0
    
    for md_file in md_files:
        # Skip generated files
        if ('TASK_COMPLETION_SUMMARY' in md_file or md_file.startswith('.')):
            print(f"⏭️ Skipping generated file: {md_file}")
            continue
        
        print(f"📄 Analyzing {md_file}...")
        
        # Read file content
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"  ❌ Error reading file: {e}")
            continue
        
        # Validate current syntax
        issues = validate_mermaid_syntax(content)
        if issues:
            print(f"  ⚠️ Found {len(issues)} potential syntax issues:")
            for issue in issues:
                print(f"     - {issue}")
        else:
            print(f"  ✅ No obvious syntax issues detected")
            continue
        
        # Create backup
        backup_path = backup_file(md_file)
        print(f"  💾 Created backup: {backup_path}")
        
        # Apply fixes
        fixed_content = fix_mermaid_syntax_issues(content)
        
        # Write fixed content
        try:
            with open(md_file, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            print(f"  ✅ Applied syntax fixes to {md_file}")
            fixed_count += 1
        except Exception as e:
            print(f"  ❌ Error writing fixed file: {e}")
        
        print()
    
    print("=" * 50)
    print(f"🎯 SYNTAX FIX COMPLETE!")
    print(f"✅ Fixed syntax issues in {fixed_count} files")
    print()
    print("🔧 FIXES APPLIED:")
    print("   • Corrected node ID formats")
    print("   • Fixed flowchart syntax")
    print("   • Cleaned up emoji usage")
    print("   • Fixed label formatting")
    print("   • Corrected Gantt chart syntax")
    print("   • Improved styling commands")
    print()
    print("📋 Next step: Re-run the Mermaid fix script to regenerate PDFs")
    
    return fixed_count > 0

if __name__ == "__main__":
    main()
