#!/usr/bin/env python3
"""
Final solution: Create HTML with inline Mermaid.js that renders properly in browsers,
then use browser print-to-PDF functionality for best results.
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
    page_break_replacement = '<div class="page-break"></div>'
    
    processed_html = re.sub(page_break_pattern, page_break_replacement, html_content, flags=re.IGNORECASE | re.MULTILINE)
    
    return processed_html

def extract_mermaid_diagrams(html_content):
    """Extract and replace Mermaid code blocks with proper Mermaid.js divs."""

    # Pattern to match Mermaid code blocks in HTML (both formats)
    mermaid_pattern1 = r'<pre><code class="language-mermaid">(.*?)</code></pre>'
    mermaid_pattern2 = r'<div class="codehilite"><pre><span></span><code><span class="n">flowchart</span>(.*?)</code></pre></div>'

    def replace_mermaid1(match):
        diagram_content = match.group(1).strip()

        # Create proper Mermaid.js div
        mermaid_div = f'''
        <div class="mermaid-container">
            <div class="mermaid">
{diagram_content}
            </div>
        </div>
        '''
        return mermaid_div

    def replace_mermaid2(match):
        # Extract the flowchart content and clean it up
        diagram_content = "flowchart" + match.group(1)

        # Remove HTML span tags and decode entities
        diagram_content = re.sub(r'<span[^>]*>', '', diagram_content)
        diagram_content = re.sub(r'</span>', '', diagram_content)
        diagram_content = diagram_content.replace('&quot;', '"')
        diagram_content = diagram_content.replace('&gt;', '>')
        diagram_content = diagram_content.replace('&lt;', '<')
        diagram_content = diagram_content.replace('&amp;', '&')

        # Create proper Mermaid.js div
        mermaid_div = f'''
        <div class="mermaid-container">
            <div class="mermaid">
{diagram_content}
            </div>
        </div>
        '''
        return mermaid_div

    # Apply both patterns
    processed_html = re.sub(mermaid_pattern1, replace_mermaid1, html_content, flags=re.DOTALL)
    processed_html = re.sub(mermaid_pattern2, replace_mermaid2, processed_html, flags=re.DOTALL)

    return processed_html

def create_html_with_mermaid(content):
    """Create a complete HTML document with Mermaid.js integration."""
    
    html_template = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>A Four-Tiered Cognitive Architecture for Advanced AI Reasoning</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10.6.1/dist/mermaid.min.js"></script>
    <style>
        @page {{
            size: A4;
            margin: 0.75in;
        }}
        
        @media print {{
            .page-break {{
                page-break-before: always !important;
                break-before: page !important;
                height: 0 !important;
                margin: 0 !important;
                padding: 0 !important;
                border: none !important;
                display: block !important;
            }}
            
            .mermaid-container {{
                page-break-inside: avoid !important;
                break-inside: avoid !important;
                margin: 1em 0 !important;
            }}
            
            .mermaid {{
                text-align: center !important;
                background: white !important;
                padding: 20px !important;
                border: 1px solid #ddd !important;
                border-radius: 8px !important;
                margin: 0 auto !important;
                max-width: 100% !important;
            }}
            
            .mermaid svg {{
                max-width: 100% !important;
                height: auto !important;
            }}
        }}
        
        body {{
            font-family: 'Times New Roman', serif;
            font-size: 11pt;
            line-height: 1.4;
            color: #000;
            background: white;
            max-width: none;
            margin: 0;
            padding: 0;
        }}
        
        h1, h2, h3, h4, h5, h6 {{
            page-break-after: avoid;
            break-after: avoid;
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
        
        .page-break {{
            page-break-before: always;
            break-before: page;
            height: 0;
            margin: 0;
            padding: 0;
            border: none;
            display: block;
        }}
        
        .mermaid-container {{
            page-break-inside: avoid;
            break-inside: avoid;
            margin: 1.5em 0;
            text-align: center;
        }}
        
        .mermaid {{
            display: inline-block;
            text-align: center;
            background: white;
            padding: 20px;
            border: 1px solid #ddd;
            border-radius: 8px;
            margin: 0 auto;
            max-width: 100%;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        .mermaid svg {{
            max-width: 100%;
            height: auto;
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
            break-inside: avoid;
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
        pre:not(.mermaid) {{
            background: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 4px;
            padding: 12px;
            font-size: 9pt;
            overflow-x: auto;
            page-break-inside: avoid;
        }}
        
        code {{
            background: #f8f9fa;
            padding: 2px 4px;
            border-radius: 3px;
            font-size: 10pt;
        }}
        
        /* Print instructions */
        .print-instructions {{
            background: #e3f2fd;
            border: 2px solid #1976d2;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
            font-size: 12pt;
        }}
        
        @media print {{
            .print-instructions {{
                display: none !important;
            }}
        }}
    </style>
</head>
<body>
    <div class="print-instructions">
        <h3>📄 Print Instructions</h3>
        <p><strong>To convert this document to PDF:</strong></p>
        <ol>
            <li>Press <kbd>Ctrl+P</kbd> (or <kbd>Cmd+P</kbd> on Mac)</li>
            <li>Select "Save as PDF" as the destination</li>
            <li>Set paper size to A4</li>
            <li>Set margins to 0.75 inches (or 19mm)</li>
            <li>Ensure "Background graphics" is enabled</li>
            <li>Click "Save" or "Print"</li>
        </ol>
        <p><em>This instruction box will not appear in the printed PDF.</em></p>
    </div>

{content}

    <script>
        // Initialize Mermaid
        mermaid.initialize({{
            startOnLoad: true,
            theme: 'default',
            flowchart: {{
                useMaxWidth: true,
                htmlLabels: true,
                curve: 'basis'
            }},
            themeVariables: {{
                primaryColor: '#e1f5fe',
                primaryTextColor: '#000',
                primaryBorderColor: '#1976d2',
                lineColor: '#1976d2',
                secondaryColor: '#f3e5f5',
                tertiaryColor: '#e8f5e8'
            }}
        }});
        
        // Ensure diagrams are rendered before printing
        window.addEventListener('beforeprint', function() {{
            // Small delay to ensure all diagrams are rendered
            setTimeout(function() {{
                console.log('Ready for printing');
            }}, 1000);
        }});
        
        // Auto-render after page load
        window.addEventListener('load', function() {{
            setTimeout(function() {{
                mermaid.init();
                console.log('Mermaid diagrams initialized');
            }}, 500);
        }});
    </script>
</body>
</html>"""
    
    return html_template

def convert_md_to_printable_html(input_file, output_file=None):
    """Convert markdown to HTML with working Mermaid diagrams for browser printing."""
    
    input_path = Path(input_file)
    if not input_path.exists():
        print(f"Error: Input file {input_file} not found")
        return False
    
    if output_file is None:
        output_file = input_path.stem + '_printable.html'
    
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
        html_content = extract_mermaid_diagrams(html_content)
        
        # Create complete HTML document with Mermaid.js
        full_html = create_html_with_mermaid(html_content)
        
        # Save HTML file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(full_html)
        
        print(f"✅ HTML file created: {output_path}")
        print("\n📄 NEXT STEPS:")
        print(f"1. Open {output_path} in your browser")
        print("2. Wait for diagrams to load (should see flowcharts)")
        print("3. Press Ctrl+P (or Cmd+P on Mac)")
        print("4. Select 'Save as PDF'")
        print("5. Set paper size to A4, margins to 0.75 inches")
        print("6. Enable 'Background graphics'")
        print("7. Save as PDF")
        print("\n🎯 This will give you a PDF with properly rendered Mermaid diagrams!")
        
        return True
        
    except Exception as e:
        print(f"Error during conversion: {e}")
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python final_mermaid_pdf_solution.py <input.md> [output.html]")
        print("\nThis creates an HTML file with working Mermaid diagrams.")
        print("Use your browser's print-to-PDF feature for best results.")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    success = convert_md_to_printable_html(input_file, output_file)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
