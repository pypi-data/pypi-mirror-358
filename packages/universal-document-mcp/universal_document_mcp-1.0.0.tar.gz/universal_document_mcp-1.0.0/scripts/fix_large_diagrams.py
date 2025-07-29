#!/usr/bin/env python3
"""
Fix large Mermaid diagrams that don't fit on a single page.
This script modifies the HTML to add better size constraints and page handling.
"""

import re
import sys
from pathlib import Path

def fix_large_diagrams(html_content):
    """Add size constraints and better page handling for large Mermaid diagrams."""
    
    # Enhanced CSS for better diagram sizing
    enhanced_css = """
        /* Enhanced Mermaid diagram sizing */
        .mermaid-container {
            page-break-inside: avoid !important;
            break-inside: avoid !important;
            margin: 1.5em 0;
            text-align: center;
            max-height: 90vh;
            overflow: visible;
        }
        
        .mermaid {
            display: inline-block;
            text-align: center;
            background: white;
            padding: 15px;
            border: 1px solid #ddd;
            border-radius: 8px;
            margin: 0 auto;
            max-width: 95% !important;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            transform-origin: top center;
        }
        
        /* Large diagram scaling */
        .mermaid.large-diagram {
            transform: scale(0.75);
            transform-origin: top center;
            margin-bottom: 2em;
        }
        
        .mermaid svg {
            max-width: 100% !important;
            max-height: 85vh !important;
            height: auto !important;
            width: auto !important;
        }
        
        /* Print-specific adjustments */
        @media print {
            .mermaid-container {
                page-break-inside: avoid !important;
                break-inside: avoid !important;
                margin: 1em 0 !important;
                max-height: none !important;
            }
            
            .mermaid {
                max-width: 90% !important;
                padding: 10px !important;
                transform: scale(0.8) !important;
                transform-origin: top center !important;
            }
            
            .mermaid.large-diagram {
                transform: scale(0.65) !important;
                margin-bottom: 3em !important;
            }
            
            .mermaid svg {
                max-width: 100% !important;
                max-height: 22cm !important;
                height: auto !important;
                width: auto !important;
            }
        }
    """
    
    # Find and replace the existing mermaid CSS
    css_pattern = r'(\.mermaid-container\s*{[^}]*}.*?\.mermaid svg\s*{[^}]*})'
    
    if re.search(css_pattern, html_content, re.DOTALL):
        html_content = re.sub(css_pattern, enhanced_css, html_content, flags=re.DOTALL)
    else:
        # If pattern not found, insert before closing </style>
        html_content = html_content.replace('</style>', enhanced_css + '\n    </style>')
    
    return html_content

def identify_large_diagrams(html_content):
    """Identify and mark large diagrams for special handling."""
    
    # Pattern to find mermaid containers
    mermaid_pattern = r'(<div class="mermaid-container">\s*<div class="mermaid">\s*flowchart[^<]*(?:<[^>]*>[^<]*</[^>]*>|[^<])*?</div>\s*</div>)'
    
    def mark_large_diagram(match):
        diagram_content = match.group(1)
        
        # Count the number of nodes and connections to estimate complexity
        node_count = len(re.findall(r'\w+\[', diagram_content))
        connection_count = len(re.findall(r'-->', diagram_content))
        
        # If diagram is complex, mark it as large
        if node_count > 8 or connection_count > 10:
            # Add large-diagram class
            modified_content = diagram_content.replace(
                '<div class="mermaid">',
                '<div class="mermaid large-diagram">'
            )
            return modified_content
        
        return diagram_content
    
    processed_html = re.sub(mermaid_pattern, mark_large_diagram, html_content, flags=re.DOTALL)
    
    return processed_html

def enhance_mermaid_config(html_content):
    """Enhance Mermaid configuration for better rendering of large diagrams."""
    
    enhanced_config = """
        // Enhanced Mermaid configuration for large diagrams
        mermaid.initialize({
            startOnLoad: true,
            theme: 'default',
            flowchart: {
                useMaxWidth: true,
                htmlLabels: true,
                curve: 'basis',
                nodeSpacing: 30,
                rankSpacing: 40,
                padding: 15
            },
            themeVariables: {
                primaryColor: '#e1f5fe',
                primaryTextColor: '#000',
                primaryBorderColor: '#1976d2',
                lineColor: '#1976d2',
                secondaryColor: '#f3e5f5',
                tertiaryColor: '#e8f5e8',
                fontSize: '12px'
            },
            maxTextSize: 90000,
            maxEdges: 200
        });
    """
    
    # Replace the existing mermaid.initialize call
    config_pattern = r'mermaid\.initialize\({[^}]*(?:{[^}]*}[^}]*)*}\);'
    
    if re.search(config_pattern, html_content, re.DOTALL):
        html_content = re.sub(config_pattern, enhanced_config, html_content, flags=re.DOTALL)
    
    return html_content

def fix_html_file(input_file, output_file=None):
    """Fix large diagrams in HTML file."""
    
    input_path = Path(input_file)
    if not input_path.exists():
        print(f"Error: Input file {input_file} not found")
        return False
    
    if output_file is None:
        output_file = input_path.stem + '_fixed_large.html'
    
    output_path = Path(output_file)
    
    print(f"Fixing large diagrams in {input_file}")
    
    try:
        # Read HTML content
        with open(input_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Apply fixes
        print("1. Enhancing CSS for large diagrams...")
        html_content = fix_large_diagrams(html_content)
        
        print("2. Identifying and marking large diagrams...")
        html_content = identify_large_diagrams(html_content)
        
        print("3. Enhancing Mermaid configuration...")
        html_content = enhance_mermaid_config(html_content)
        
        # Save fixed HTML file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ Fixed HTML file created: {output_path}")
        print("\n📄 NEXT STEPS:")
        print(f"1. Open {output_path} in your browser")
        print("2. Verify that large diagrams are properly scaled")
        print("3. Use browser print-to-PDF or run auto_html_to_pdf.py")
        
        return True
        
    except Exception as e:
        print(f"Error during processing: {e}")
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python fix_large_diagrams.py <input.html> [output.html]")
        print("\nFixes large Mermaid diagrams that don't fit on a single page.")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    success = fix_html_file(input_file, output_file)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
