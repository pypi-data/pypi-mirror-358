#!/usr/bin/env python3
"""
Custom PDF conversion script that handles manual page break markers.
Converts markdown to HTML, processes manual page breaks, then to PDF.
"""

import re
import subprocess
import sys
import os
from pathlib import Path

def process_manual_breaks(html_content):
    """Convert manual page break markers to proper CSS page breaks."""
    
    # Pattern to match our manual page break markers
    page_break_pattern = r'<hr\s*/?>[\s\n]*<p><strong>PAGE BREAK</strong></p>[\s\n]*<hr\s*/?>'
    
    # Replace with proper CSS page break
    page_break_replacement = '<div style="page-break-before: always; height: 0; margin: 0; padding: 0;"></div>'
    
    processed_html = re.sub(page_break_pattern, page_break_replacement, html_content, flags=re.IGNORECASE | re.MULTILINE)
    
    return processed_html

def add_pdf_styles(html_content):
    """Add comprehensive PDF-specific CSS styles."""
    
    pdf_styles = """
    <style>
    @page {
        size: A4;
        margin: 0.75in;
    }
    
    body {
        font-family: 'Times New Roman', serif;
        font-size: 11pt;
        line-height: 1.4;
        color: #000;
        background: white;
    }
    
    h1, h2, h3, h4, h5, h6 {
        page-break-after: avoid;
        margin-top: 1.2em;
        margin-bottom: 0.6em;
    }
    
    h1 {
        font-size: 18pt;
        font-weight: bold;
        text-align: center;
        margin-bottom: 1em;
    }
    
    h2 {
        font-size: 14pt;
        font-weight: bold;
        margin-top: 1.5em;
    }
    
    h3 {
        font-size: 12pt;
        font-weight: bold;
    }
    
    p {
        margin-bottom: 0.8em;
        text-align: justify;
        orphans: 2;
        widows: 2;
    }
    
    .mermaid {
        page-break-inside: avoid;
        margin: 1em 0;
        text-align: center;
    }
    
    .mermaid svg {
        max-width: 100%;
        height: auto;
    }
    
    figure {
        page-break-inside: avoid;
        margin: 1em 0;
        text-align: center;
    }
    
    figcaption {
        font-size: 10pt;
        font-style: italic;
        margin-top: 0.5em;
    }
    
    /* Force page breaks */
    div[style*="page-break-before: always"] {
        page-break-before: always !important;
        height: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
        border: none !important;
    }
    
    /* Prevent orphaned content */
    blockquote, pre, code {
        page-break-inside: avoid;
    }
    
    /* Abstract and keywords styling */
    .abstract {
        margin: 1.5em 0;
        padding: 1em;
        border-left: 3px solid #ccc;
        background-color: #f9f9f9;
    }
    
    .keywords {
        font-style: italic;
        margin-top: 1em;
    }
    </style>
    """
    
    # Insert styles after <head> tag or create head if it doesn't exist
    if '<head>' in html_content:
        html_content = html_content.replace('<head>', f'<head>{pdf_styles}')
    else:
        # If no head tag, add it
        if '<html>' in html_content:
            html_content = html_content.replace('<html>', f'<html><head>{pdf_styles}</head>')
        else:
            html_content = f'<html><head>{pdf_styles}</head><body>{html_content}</body></html>'
    
    return html_content

def convert_md_to_pdf(input_file, output_file=None):
    """Convert markdown to PDF with manual page break processing."""
    
    input_path = Path(input_file)
    if not input_path.exists():
        print(f"Error: Input file {input_file} not found")
        return False
    
    if output_file is None:
        output_file = input_path.with_suffix('.pdf')
    
    output_path = Path(output_file)
    
    print(f"Converting {input_file} to {output_file}")
    
    try:
        # Step 1: Convert markdown to HTML using pandoc
        print("Step 1: Converting markdown to HTML...")
        html_result = subprocess.run([
            'pandoc',
            str(input_path),
            '-f', 'markdown',
            '-t', 'html',
            '--standalone',
            '--mathjax'
        ], capture_output=True, text=True, encoding='utf-8', check=True)

        html_content = html_result.stdout

        if not html_content:
            print("Error: No HTML content generated from pandoc")
            return False
        
        # Step 2: Process manual page breaks
        print("Step 2: Processing manual page breaks...")
        html_content = process_manual_breaks(html_content)
        
        # Step 3: Add PDF-specific styles
        print("Step 3: Adding PDF styles...")
        html_content = add_pdf_styles(html_content)
        
        # Step 4: Save processed HTML to temporary file
        temp_html = input_path.with_suffix('.temp.html')
        with open(temp_html, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # Step 5: Convert HTML to PDF using wkhtmltopdf
        print("Step 4: Converting HTML to PDF...")
        subprocess.run([
            'wkhtmltopdf',
            '--page-size', 'A4',
            '--margin-top', '0.75in',
            '--margin-right', '0.75in',
            '--margin-bottom', '0.75in',
            '--margin-left', '0.75in',
            '--enable-local-file-access',
            '--print-media-type',
            '--encoding', 'utf-8',
            str(temp_html),
            str(output_path)
        ], check=True, encoding='utf-8')
        
        # Clean up temporary file
        temp_html.unlink()
        
        print(f"Successfully converted to {output_path}")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"Error during conversion: {e}")
        if hasattr(e, 'stderr') and e.stderr:
            print(f"Error details: {e.stderr}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python convert_with_manual_breaks.py <input.md> [output.pdf]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    success = convert_md_to_pdf(input_file, output_file)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
