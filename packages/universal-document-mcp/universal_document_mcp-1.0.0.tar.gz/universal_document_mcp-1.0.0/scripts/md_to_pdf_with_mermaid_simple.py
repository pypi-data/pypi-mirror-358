#!/usr/bin/env python3
"""
Simple markdown to PDF converter that preserves Mermaid diagrams as code blocks
with proper styling and page breaks.
"""

import markdown
import re
import sys
from pathlib import Path

def process_manual_breaks(html_content):
    """Convert manual page break markers to proper CSS page breaks."""
    
    # Pattern to match our manual page break markers
    page_break_pattern = r'<hr\s*/?>[\s\n]*<p><strong>PAGE BREAK</strong></p>[\s\n]*<hr\s*/?>'
    
    # Replace with proper CSS page break
    page_break_replacement = '<div style="page-break-before: always; height: 0; margin: 0; padding: 0;"></div>'
    
    processed_html = re.sub(page_break_pattern, page_break_replacement, html_content, flags=re.IGNORECASE | re.MULTILINE)
    
    return processed_html

def process_mermaid_diagrams(html_content):
    """Convert Mermaid code blocks to styled diagram representations."""
    
    # Pattern to match Mermaid code blocks in HTML
    mermaid_pattern = r'<pre><code class="language-mermaid">(.*?)</code></pre>'
    
    def replace_mermaid(match):
        diagram_content = match.group(1)
        
        # Create a styled representation of the Mermaid diagram
        styled_diagram = f'''
        <div class="mermaid-diagram-container">
            <div class="mermaid-diagram-title">Mermaid Diagram</div>
            <div class="mermaid-diagram-content">
                <pre class="mermaid-code">{diagram_content}</pre>
            </div>
            <div class="mermaid-note">Note: This diagram would be interactive in the original document</div>
        </div>
        '''
        return styled_diagram
    
    processed_html = re.sub(mermaid_pattern, replace_mermaid, html_content, flags=re.DOTALL)
    
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
        .mermaid-diagram-container {{
            page-break-inside: avoid;
            margin: 1.5em 0;
            border: 2px solid #2563eb;
            border-radius: 8px;
            background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
            padding: 0;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}
        
        .mermaid-diagram-title {{
            background: #2563eb;
            color: white;
            padding: 12px 20px;
            font-weight: bold;
            font-size: 12pt;
            margin: 0;
            border-radius: 6px 6px 0 0;
        }}
        
        .mermaid-diagram-content {{
            padding: 20px;
        }}
        
        .mermaid-code {{
            font-family: 'Courier New', monospace;
            font-size: 9pt;
            line-height: 1.3;
            background: white;
            border: 1px solid #cbd5e1;
            border-radius: 4px;
            padding: 15px;
            margin: 0;
            white-space: pre-wrap;
            color: #1e293b;
            overflow-x: auto;
        }}
        
        .mermaid-note {{
            background: #fef3c7;
            border: 1px solid #f59e0b;
            border-radius: 4px;
            padding: 8px 12px;
            margin-top: 15px;
            font-size: 9pt;
            font-style: italic;
            color: #92400e;
        }}
        
        /* Figure captions */
        .figure-caption {{
            font-size: 10pt;
            font-style: italic;
            margin-top: 0.5em;
            text-align: center;
            font-weight: bold;
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
        
        /* Regular code blocks */
        pre:not(.mermaid-code) {{
            background: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 4px;
            padding: 12px;
            font-size: 9pt;
            overflow-x: auto;
        }}
        
        code {{
            background: #f8f9fa;
            padding: 2px 4px;
            border-radius: 3px;
            font-size: 10pt;
        }}
    </style>
</head>
<body>
{content}
</body>
</html>"""
    
    return html_template

def convert_md_to_pdf(input_file, output_file=None):
    """Convert markdown to PDF with styled Mermaid diagram representations."""
    
    input_path = Path(input_file)
    if not input_path.exists():
        print(f"Error: Input file {input_file} not found")
        return False
    
    if output_file is None:
        output_file = input_path.with_suffix('.pdf')
    
    output_path = Path(output_file)
    
    print(f"Converting {input_file} to {output_file}")
    
    try:
        # Read markdown content
        with open(input_path, 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        # Convert markdown to HTML
        md = markdown.Markdown(extensions=['codehilite', 'fenced_code', 'tables'])
        html_content = md.convert(md_content)
        
        # Process manual page breaks
        html_content = process_manual_breaks(html_content)
        
        # Process Mermaid diagrams
        html_content = process_mermaid_diagrams(html_content)
        
        # Create complete HTML document
        full_html = create_html_template(html_content)
        
        # Save HTML file for inspection
        html_file = input_path.stem + '_styled.html'
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
        print("Usage: python md_to_pdf_with_mermaid_simple.py <input.md> [output.pdf]")
        print("\nRequirements:")
        print("  pip install weasyprint markdown")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    success = convert_md_to_pdf(input_file, output_file)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
