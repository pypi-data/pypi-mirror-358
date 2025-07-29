#!/usr/bin/env python3
"""
Advanced markdown to PDF converter that renders Mermaid diagrams using Playwright.
Creates actual visual diagrams in the PDF output.
"""

import markdown
import re
import sys
import asyncio
import tempfile
import base64
from pathlib import Path
from playwright.async_api import async_playwright

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

async def render_mermaid_to_image(diagram_content, output_path):
    """Render a Mermaid diagram to PNG using Playwright."""
    
    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
        <style>
            body {{
                margin: 0;
                padding: 20px;
                background: white;
                font-family: Arial, sans-serif;
            }}
            .mermaid {{
                text-align: center;
            }}
        </style>
    </head>
    <body>
        <div class="mermaid">
{diagram_content}
        </div>
        <script>
            mermaid.initialize({{
                startOnLoad: true,
                theme: 'default',
                flowchart: {{
                    useMaxWidth: true,
                    htmlLabels: true
                }}
            }});
        </script>
    </body>
    </html>
    """
    
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            
            # Set content and wait for Mermaid to render
            await page.set_content(html_template)
            await page.wait_for_timeout(2000)  # Wait for Mermaid to render
            
            # Find the SVG element and take screenshot
            svg_element = await page.query_selector('.mermaid svg')
            if svg_element:
                await svg_element.screenshot(path=str(output_path))
                await browser.close()
                return True
            else:
                print(f"Could not find rendered SVG for diagram")
                await browser.close()
                return False
                
    except Exception as e:
        print(f"Error rendering Mermaid diagram: {e}")
        return False

async def process_mermaid_diagrams(md_content, temp_dir):
    """Process all Mermaid diagrams and replace with image references."""
    
    diagrams = extract_mermaid_diagrams(md_content)
    processed_content = md_content
    
    # Process diagrams in reverse order to maintain string positions
    for diagram in reversed(diagrams):
        png_filename = f"diagram_{diagram['index']}.png"
        png_path = temp_dir / png_filename
        
        print(f"Rendering diagram {diagram['index']}...")
        
        # Try to render the diagram
        if await render_mermaid_to_image(diagram['content'], png_path):
            # Convert image to base64 for embedding
            with open(png_path, 'rb') as img_file:
                img_data = base64.b64encode(img_file.read()).decode()
            
            # Replace with embedded image
            img_tag = f'''
            <div class="mermaid-diagram">
                <img src="data:image/png;base64,{img_data}" alt="Mermaid Diagram {diagram['index']}" />
            </div>
            '''
            processed_content = processed_content.replace(diagram['full_match'], img_tag)
        else:
            # Fallback to styled code block if rendering fails
            styled_fallback = f'''
            <div class="mermaid-fallback">
                <div class="mermaid-fallback-title">Diagram {diagram['index']} (Rendering Failed)</div>
                <pre class="mermaid-code">{diagram['content']}</pre>
            </div>
            '''
            processed_content = processed_content.replace(diagram['full_match'], styled_fallback)
    
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
            margin: 1.5em 0;
            text-align: center;
        }}
        
        .mermaid-diagram img {{
            max-width: 100%;
            height: auto;
            border: 1px solid #ddd;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            background: white;
            padding: 10px;
        }}
        
        /* Fallback styling */
        .mermaid-fallback {{
            page-break-inside: avoid;
            margin: 1.5em 0;
            border: 2px solid #dc2626;
            border-radius: 8px;
            background: #fef2f2;
            padding: 0;
        }}
        
        .mermaid-fallback-title {{
            background: #dc2626;
            color: white;
            padding: 12px 20px;
            font-weight: bold;
            font-size: 12pt;
            margin: 0;
            border-radius: 6px 6px 0 0;
        }}
        
        .mermaid-code {{
            font-family: 'Courier New', monospace;
            font-size: 9pt;
            line-height: 1.3;
            background: white;
            border: none;
            border-radius: 0 0 6px 6px;
            padding: 15px 20px;
            margin: 0;
            white-space: pre-wrap;
            color: #1e293b;
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
    </style>
</head>
<body>
{content}
</body>
</html>"""
    
    return html_template

async def convert_md_to_pdf_with_rendered_mermaid(input_file, output_file=None):
    """Convert markdown to PDF with rendered Mermaid diagrams."""
    
    input_path = Path(input_file)
    if not input_path.exists():
        print(f"Error: Input file {input_file} not found")
        return False
    
    if output_file is None:
        output_file = input_path.with_suffix('.pdf')
    
    output_path = Path(output_file)
    
    print(f"Converting {input_file} to {output_file}")
    
    try:
        # Create temporary directory for images
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Read markdown content
            with open(input_path, 'r', encoding='utf-8') as f:
                md_content = f.read()
            
            print("Processing Mermaid diagrams...")
            # Process Mermaid diagrams first
            md_content = await process_mermaid_diagrams(md_content, temp_path)
            
            # Convert markdown to HTML
            md = markdown.Markdown(extensions=['codehilite', 'fenced_code', 'tables'])
            html_content = md.convert(md_content)
            
            # Process manual page breaks
            html_content = process_manual_breaks(html_content)
            
            # Create complete HTML document
            full_html = create_html_template(html_content)
            
            # Save HTML file for inspection
            html_file = input_path.stem + '_rendered.html'
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
        print("Usage: python md_to_pdf_with_rendered_mermaid.py <input.md> [output.pdf]")
        print("\nRequirements:")
        print("  pip install weasyprint markdown playwright")
        print("  playwright install chromium")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    success = asyncio.run(convert_md_to_pdf_with_rendered_mermaid(input_file, output_file))
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
