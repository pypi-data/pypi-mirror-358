#!/usr/bin/env python3
"""
Simple Markdown to PDF Converter
Converts updated Markdown files to HTML then PDF with Mermaid support
"""

import sys
import os
import asyncio
import subprocess
from pathlib import Path

def install_playwright():
    """Install playwright if needed"""
    try:
        import playwright
        return True
    except ImportError:
        print("Installing playwright...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "playwright"])
            subprocess.check_call([sys.executable, "-m", "playwright", "install", "chromium"])
            return True
        except Exception as e:
            print(f"Failed to install playwright: {e}")
            return False

def install_markdown():
    """Install markdown if needed"""
    try:
        import markdown
        return True
    except ImportError:
        print("Installing markdown...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "markdown"])
            return True
        except Exception as e:
            print(f"Failed to install markdown: {e}")
            return False

def convert_markdown_to_html(md_file, html_file):
    """Convert Markdown to HTML with Mermaid support"""
    try:
        import markdown
        
        # Read markdown content
        with open(md_file, 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        # Basic markdown conversion
        md = markdown.Markdown(extensions=['extra', 'codehilite', 'toc'])
        html_content = md.convert(md_content)
        
        # Create full HTML document with Mermaid support
        full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{Path(md_file).stem}</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10.9.1/dist/mermaid.min.js"></script>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            color: #333;
        }}
        
        h1, h2, h3, h4, h5, h6 {{
            color: #2c3e50;
            margin-top: 2em;
            margin-bottom: 1em;
        }}
        
        h1 {{ border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
        h2 {{ border-bottom: 2px solid #ecf0f1; padding-bottom: 8px; }}
        
        .mermaid {{ text-align: center; margin: 20px 0; }}
        
        pre {{
            background-color: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 4px;
            padding: 15px;
            overflow-x: auto;
        }}
        
        code {{
            background-color: #f8f9fa;
            padding: 2px 4px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
        }}
        
        blockquote {{
            border-left: 4px solid #3498db;
            margin: 0;
            padding-left: 20px;
            color: #7f8c8d;
        }}
        
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
        }}
        
        th, td {{
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }}
        
        th {{ background-color: #f2f2f2; font-weight: bold; }}
        
        @media print {{
            h1, h2, h3, h4, h5, h6 {{ page-break-after: avoid !important; }}
            .mermaid, svg, pre, table {{ page-break-inside: avoid !important; }}
            p, li {{ orphans: 3; widows: 3; }}
        }}
    </style>
</head>
<body>
{html_content}

<script>
    mermaid.initialize({{
        startOnLoad: true,
        theme: 'default',
        securityLevel: 'loose'
    }});
    
    document.addEventListener('DOMContentLoaded', function() {{
        // Convert mermaid code blocks to diagrams
        const mermaidBlocks = document.querySelectorAll('pre code.language-mermaid, code.language-mermaid, pre code:contains("flowchart"), pre code:contains("graph"), pre code:contains("sequenceDiagram")');

        // Also look for code blocks that contain mermaid syntax
        const allCodeBlocks = document.querySelectorAll('pre code');
        allCodeBlocks.forEach((block) => {{
            const code = block.textContent.trim();
            if (code.includes('flowchart') || code.includes('graph') || code.includes('sequenceDiagram') ||
                code.includes('classDiagram') || code.includes('gantt') || code.includes('pie')) {{
                const mermaidDiv = document.createElement('div');
                mermaidDiv.className = 'mermaid';
                mermaidDiv.textContent = code;
                block.parentNode.replaceWith(mermaidDiv);
            }}
        }});

        // Process explicitly marked mermaid blocks
        mermaidBlocks.forEach((block) => {{
            const mermaidCode = block.textContent;
            const mermaidDiv = document.createElement('div');
            mermaidDiv.className = 'mermaid';
            mermaidDiv.textContent = mermaidCode;
            block.parentNode.replaceWith(mermaidDiv);
        }});

        // Initialize mermaid after processing
        setTimeout(() => {{
            mermaid.init();
        }}, 100);
    }});
</script>
</body>
</html>"""
        
        # Write HTML file
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(full_html)
        
        print(f"  ✅ Converted {md_file} to HTML")
        return True
        
    except Exception as e:
        print(f"  ❌ Error converting {md_file}: {e}")
        return False

async def convert_html_to_pdf(html_file, pdf_file):
    """Convert HTML to PDF using Playwright"""
    try:
        from playwright.async_api import async_playwright
        
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            
            # Load HTML file
            file_path = Path(html_file).resolve()
            await page.goto(f"file://{file_path}")
            
            # Wait for content to load and Mermaid to process
            await page.wait_for_timeout(3000)

            # Check for Mermaid diagrams and wait for them to render
            try:
                # First check if there are mermaid divs
                mermaid_count = await page.evaluate("document.querySelectorAll('.mermaid').length")
                if mermaid_count > 0:
                    print(f"  🔍 Found {mermaid_count} Mermaid diagram(s), waiting for rendering...")
                    # Wait for SVG elements to appear
                    await page.wait_for_selector('svg[id^="mermaid"], .mermaid svg', timeout=10000)
                    print(f"  ✅ Mermaid diagrams rendered successfully")
                else:
                    print(f"  ℹ️  No Mermaid diagrams detected")
            except Exception as e:
                print(f"  ⚠️  Mermaid rendering timeout or error: {e}")
            
            # Generate PDF
            await page.pdf(
                path=pdf_file,
                format='A4',
                margin={
                    'top': '0.75in',
                    'right': '0.75in',
                    'bottom': '0.75in',
                    'left': '0.75in'
                },
                print_background=True,
                prefer_css_page_size=True,
                display_header_footer=False
            )
            
            await browser.close()
            print(f"  ✅ Generated PDF: {pdf_file}")
            return True
            
    except Exception as e:
        print(f"  ❌ Error generating PDF: {e}")
        return False

def main():
    """Main conversion process"""
    if not install_playwright() or not install_markdown():
        print("❌ Could not install required dependencies")
        return False
    
    files = [
        "executive-brief-enhanced-final",
        "research-proposal-enhanced-final",
        "architectural-vision-enhanced-final"
    ]
    
    print("🔄 Converting updated Markdown files to PDF...")
    print("=" * 60)
    
    success_count = 0
    
    for file_base in files:
        md_file = f"{file_base}.md"
        html_file = f"{file_base}.html"
        pdf_file = f"{file_base}.pdf"
        
        if os.path.exists(md_file):
            print(f"\n📄 Processing {md_file}...")
            
            # Convert MD to HTML
            if convert_markdown_to_html(md_file, html_file):
                # Convert HTML to PDF
                if asyncio.run(convert_html_to_pdf(html_file, pdf_file)):
                    success_count += 1
                    size_kb = os.path.getsize(pdf_file) / 1024
                    print(f"  📊 PDF size: {size_kb:.1f} KB")
        else:
            print(f"⚠️  {md_file} not found")
    
    print("\n" + "=" * 60)
    print(f"🎯 Conversion complete!")
    print(f"✅ Successfully converted {success_count}/{len(files)} files")
    print(f"📋 Your updated Markdown edits are now in PDF format!")
    
    return success_count > 0

if __name__ == "__main__":
    main()
