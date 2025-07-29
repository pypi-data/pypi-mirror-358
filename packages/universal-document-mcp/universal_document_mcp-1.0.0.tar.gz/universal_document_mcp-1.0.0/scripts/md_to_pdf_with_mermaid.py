#!/usr/bin/env python3
"""
Enhanced markdown to PDF converter that properly renders Mermaid diagrams.
Uses mermaid-cli to convert diagrams to images before PDF generation.
"""

import markdown
import re
import sys
import subprocess
import tempfile
import os
from pathlib import Path
import json

def extract_mermaid_diagrams(md_content):
    """Extract Mermaid diagrams from markdown content."""
    
    # Pattern to match Mermaid code blocks
    mermaid_pattern = r'```mermaid\n(.*?)\n```'
    
    diagrams = []
    matches = re.finditer(mermaid_pattern, md_content, flags=re.DOTALL)
    
    for i, match in enumerate(matches):
        diagram_content = match.group(1).strip()
        diagrams.append({
            'index': i,
            'content': diagram_content,
            'full_match': match.group(0)
        })
    
    return diagrams

def render_mermaid_to_svg(diagram_content, output_path):
    """Render a single Mermaid diagram to SVG using mermaid-cli."""
    
    try:
        # Create temporary mermaid file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.mmd', delete=False) as f:
            f.write(diagram_content)
            temp_mmd = f.name
        
        # Run mermaid-cli to generate SVG
        cmd = ['mmdc', '-i', temp_mmd, '-o', str(output_path), '-f']
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Clean up temp file
        os.unlink(temp_mmd)
        
        if result.returncode == 0:
            return True
        else:
            print(f"Mermaid rendering failed: {result.stderr}")
            return False
            
    except FileNotFoundError:
        print("mermaid-cli (mmdc) not found. Please install it with: npm install -g @mermaid-js/mermaid-cli")
        return False
    except Exception as e:
        print(f"Error rendering Mermaid diagram: {e}")
        return False

def process_mermaid_diagrams(md_content, temp_dir):
    """Process all Mermaid diagrams and replace with image references."""
    
    diagrams = extract_mermaid_diagrams(md_content)
    processed_content = md_content
    
    # Process diagrams in reverse order to maintain string positions
    for diagram in reversed(diagrams):
        svg_filename = f"diagram_{diagram['index']}.svg"
        svg_path = temp_dir / svg_filename
        
        # Try to render the diagram
        if render_mermaid_to_svg(diagram['content'], svg_path):
            # Replace with image reference
            img_tag = f'<div class="mermaid-diagram"><img src="{svg_path}" alt="Mermaid Diagram {diagram["index"]}" /></div>'
            processed_content = processed_content.replace(diagram['full_match'], img_tag)
        else:
            # Fallback to placeholder if rendering fails
            placeholder = f'<div class="mermaid-placeholder">[Mermaid Diagram {diagram["index"]} - Rendering Failed]<br><pre>{diagram["content"]}</pre></div>'
            processed_content = processed_content.replace(diagram['full_match'], placeholder)
    
    return processed_content

def process_manual_breaks(html_content):
    """Convert manual page break markers to proper CSS page breaks."""
    
    # Pattern to match our manual page break markers
    page_break_pattern = r'<hr\s*/?>[\s\n]*<p><strong>PAGE BREAK</strong></p>[\s\n]*<hr\s*/?>'
    
    # Replace with proper CSS page break
    page_break_replacement = '<div style="page-break-before: always; height: 0; margin: 0; padding: 0;"></div>'
    
    processed_html = re.sub(page_break_pattern, page_break_replacement, html_content, flags=re.IGNORECASE | re.MULTILINE)
    
    return processed_html

def create_html_template(content):
    """Create a complete HTML document with PDF-optimized CSS."""
    
    html_template = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>A Four-Tiered Cognitive Architecture for Advanced AI Reasoning</title>
    <style>
        @page {{
            size: A4;
            margin: 0.75in;
        }}
        
        body {{
            font-family: 'Times New Roman', serif;
            font-size: 11pt;
            line-height: 1.4;
            color: #000;
            background: white;
            max-width: none;
        }}
        
        h1, h2, h3, h4, h5, h6 {{
            page-break-after: avoid;
            margin-top: 1.2em;
            margin-bottom: 0.6em;
        }}
        
        h1 {{
            font-size: 18pt;
            font-weight: bold;
            text-align: center;
            margin-bottom: 1em;
        }}
        
        h2 {{
            font-size: 14pt;
            font-weight: bold;
            margin-top: 1.5em;
        }}
        
        h3 {{
            font-size: 12pt;
            font-weight: bold;
        }}
        
        p {{
            margin-bottom: 0.8em;
            text-align: justify;
            orphans: 2;
            widows: 2;
        }}
        
        /* Force page breaks */
        div[style*="page-break-before: always"] {{
            page-break-before: always !important;
            height: 0 !important;
            margin: 0 !important;
            padding: 0 !important;
            border: none !important;
        }}
        
        /* Mermaid diagram styling */
        .mermaid-diagram {{
            page-break-inside: avoid;
            margin: 1em 0;
            text-align: center;
        }}
        
        .mermaid-diagram img {{
            max-width: 100%;
            height: auto;
            border: 1px solid #ddd;
            padding: 10px;
            background: white;
        }}
        
        /* Mermaid placeholder styling */
        .mermaid-placeholder {{
            page-break-inside: avoid;
            margin: 1em 0;
            text-align: center;
            padding: 2em;
            border: 2px dashed #ccc;
            background-color: #f9f9f9;
            font-style: italic;
            color: #666;
        }}
        
        .mermaid-placeholder pre {{
            font-size: 9pt;
            text-align: left;
            margin-top: 1em;
            background: #f0f0f0;
            padding: 10px;
            border-radius: 4px;
        }}
        
        /* Figure captions */
        .figure-caption {{
            font-size: 10pt;
            font-style: italic;
            margin-top: 0.5em;
            text-align: center;
        }}
        
        /* Prevent orphaned content */
        blockquote, pre, code {{
            page-break-inside: avoid;
        }}
        
        /* Abstract and keywords styling */
        .abstract {{
            margin: 1.5em 0;
            padding: 1em;
            border-left: 3px solid #ccc;
            background-color: #f9f9f9;
        }}
        
        .keywords {{
            font-style: italic;
            margin-top: 1em;
        }}
    </style>
</head>
<body>
{content}
</body>
</html>"""
    
    return html_template

def convert_md_to_pdf_with_mermaid(input_file, output_file=None):
    """Convert markdown to PDF with proper Mermaid diagram rendering."""
    
    input_path = Path(input_file)
    if not input_path.exists():
        print(f"Error: Input file {input_file} not found")
        return False
    
    if output_file is None:
        output_file = input_path.with_suffix('.pdf')
    
    output_path = Path(output_file)
    
    print(f"Converting {input_file} to {output_file}")
    
    try:
        # Create temporary directory for SVG files
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Read markdown content
            with open(input_path, 'r', encoding='utf-8') as f:
                md_content = f.read()
            
            print("Processing Mermaid diagrams...")
            # Process Mermaid diagrams first
            md_content = process_mermaid_diagrams(md_content, temp_path)
            
            # Convert markdown to HTML
            md = markdown.Markdown(extensions=['codehilite', 'fenced_code', 'tables'])
            html_content = md.convert(md_content)
            
            # Process manual page breaks
            html_content = process_manual_breaks(html_content)
            
            # Create complete HTML document
            full_html = create_html_template(html_content)
            
            # Save HTML file for inspection
            html_file = input_path.with_suffix('_with_diagrams.html')
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(full_html)
            
            print(f"HTML file saved as: {html_file}")
            
            # Convert HTML to PDF using WeasyPrint
            try:
                import weasyprint
                print("Converting HTML to PDF using WeasyPrint...")
                weasyprint.HTML(filename=str(html_file)).write_pdf(str(output_path))
                print(f"PDF successfully created: {output_path}")
                return True
            except ImportError:
                print("WeasyPrint not available. Install with: pip install weasyprint")
                return False
            except Exception as e:
                print(f"WeasyPrint conversion failed: {e}")
                return False
        
    except Exception as e:
        print(f"Error during conversion: {e}")
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python md_to_pdf_with_mermaid.py <input.md> [output.pdf]")
        print("\nRequirements:")
        print("  pip install weasyprint markdown")
        print("  npm install -g @mermaid-js/mermaid-cli")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    success = convert_md_to_pdf_with_mermaid(input_file, output_file)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
