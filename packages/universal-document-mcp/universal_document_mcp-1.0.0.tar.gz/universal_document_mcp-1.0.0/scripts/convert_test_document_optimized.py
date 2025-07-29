#!/usr/bin/env python3
"""
Auto-generated conversion script for """ + md_file + """
Created by Universal MCP Document Converter
"""

import sys
import os
import asyncio
import subprocess
from pathlib import Path

def install_dependencies():
    """Install required dependencies"""
    try:
        import playwright
        import markdown
        return True
    except ImportError:
        print("Installing required packages...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "playwright", "markdown"])
            subprocess.check_call([sys.executable, "-m", "playwright", "install", "chromium"])
            return True
        except Exception as e:
            print(f"Failed to install dependencies: {{e}}")
            return False

def convert_markdown_to_html(md_file, html_file):
    """Convert Markdown to HTML with optimized Mermaid support"""
    try:
        import markdown
        
        with open(md_file, 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        md = markdown.Markdown(extensions=['extra', 'codehilite', 'toc'])
        html_content = md.convert(md_content)
        
        # Enhanced HTML template with optimized Mermaid rendering
        html_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
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

        .mermaid {{
            text-align: center;
            margin: 15px 0;
            background: white;
            border: 1px solid #e1e8ed;
            border-radius: 8px;
            padding: 15px;
            max-width: 100%;
            max-height: 400px;
            overflow: hidden;
        }}

        .mermaid svg {{
            max-width: 100% !important;
            max-height: 380px !important;
            height: auto !important;
        }}

        @media print {{
            h1, h2, h3, h4, h5, h6 {{ page-break-after: avoid !important; }}
            .mermaid, svg, pre, table {{
                page-break-inside: avoid !important;
                max-height: 350px !important;
            }}
            .mermaid svg {{
                max-height: 330px !important;
                transform: scale(0.85);
                transform-origin: center top;
            }}
            p, li {{ orphans: 3; widows: 3; }}
        }}
    </style>
</head>
<body>
{content}

<script>
    mermaid.initialize({{
        startOnLoad: false,
        theme: 'default',
        securityLevel: 'loose',
        fontFamily: 'Arial, sans-serif',
        flowchart: {{
            useMaxWidth: true,
            htmlLabels: true,
            curve: 'basis'
        }},
        themeVariables: {{
            fontSize: '14px',
            fontSizeFactor: 0.9
        }}
    }});
    
    document.addEventListener('DOMContentLoaded', function() {{
        const codeBlocks = document.querySelectorAll('div.codehilite pre code, pre code');
        let mermaidCount = 0;

        codeBlocks.forEach((codeBlock) => {{
            let codeText = codeBlock.textContent || codeBlock.innerText;

            if (codeText.includes('flowchart') || codeText.includes('graph') ||
                codeText.includes('sequenceDiagram') || codeText.includes('classDiagram') ||
                codeText.includes('gantt') || codeText.includes('pie') ||
                codeText.includes('subgraph') || codeText.includes('classDef')) {{

                const mermaidDiv = document.createElement('div');
                mermaidDiv.className = 'mermaid';
                mermaidDiv.textContent = codeText;

                const preElement = codeBlock.closest('pre');
                if (preElement) {{
                    preElement.parentNode.replaceChild(mermaidDiv, preElement);
                    mermaidCount++;
                }}
            }}
        }});

        if (mermaidCount > 0) {{
            setTimeout(() => {{
                mermaid.init();
            }}, 500);
        }}
    }});
</script>
</body>
</html>"""

        # Format the template with actual values
        full_html = html_template.format(
            title=Path(md_file).stem,
            content=html_content
        )

        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(full_html)
        
        print(f"  ✅ Converted {md_file} to HTML")
        return True

    except Exception as e:
        print(f"  ❌ Error converting {md_file}: {e}")
        return False

async def convert_html_to_pdf(html_file, pdf_file):
    """Convert HTML to PDF using Playwright with optimized settings"""
    try:
        from playwright.async_api import async_playwright
        
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            
            file_path = Path(html_file).resolve()
            await page.goto(f"file://{file_path}")
            await page.wait_for_timeout(2000)

            try:
                mermaid_count = await page.evaluate("document.querySelectorAll('.mermaid').length")
                if mermaid_count > 0:
                    print(f"  🔍 Found {mermaid_count} Mermaid diagram(s), optimizing...")
                    await page.wait_for_selector('svg[id^="mermaid"], .mermaid svg', timeout=15000)
                    await page.wait_for_timeout(2000)
                    print(f"  ✅ All diagrams optimized and rendered")
            except Exception as e:
                print(f"  ⚠️  Mermaid rendering issue: {e}")

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
            print(f"  ✅ Generated optimized PDF: {pdf_file}")
            return True

    except Exception as e:
        print(f"  ❌ Error generating PDF: {e}")
        return False

def main():
    """Main conversion process"""
    if not install_dependencies():
        print("❌ Could not install required dependencies")
        return False
    
    md_file = "{md_file}"
    html_file = "{file_stem}.html"
    pdf_file = "{file_stem}.pdf"
    
    print("🔄 Universal Document Converter - MD → HTML → PDF")
    print("=" * 60)
    print(f"📄 Processing {md_file}...")

    if os.path.exists(md_file):
        if convert_markdown_to_html(md_file, html_file):
            if asyncio.run(convert_html_to_pdf(html_file, pdf_file)):
                size_kb = os.path.getsize(pdf_file) / 1024
                print(f"📊 PDF size: {size_kb:.1f} KB")
                print("🎯 Conversion complete!")
                print(f"✅ {md_file} → {pdf_file}")
                return True
    else:
        print(f"⚠️  {md_file} not found")
        return False

if __name__ == "__main__":
    main()
