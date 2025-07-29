#!/usr/bin/env python3
"""
Convert the Cipher_Cognitive_Architecture_2025.md file to PDF with Mermaid support
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
            print(f"Failed to install dependencies: {e}")
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
        
        # Create full HTML document with enhanced Mermaid support
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
{html_content}

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
        console.log('Processing Mermaid diagrams...');
        
        // Find all code blocks that contain Mermaid syntax
        const codeBlocks = document.querySelectorAll('div.codehilite pre code, pre code');
        let mermaidCount = 0;
        
        codeBlocks.forEach((codeBlock) => {{
            // Get the text content, removing HTML tags
            let codeText = codeBlock.textContent || codeBlock.innerText;
            
            // Check if this looks like a Mermaid diagram
            if (codeText.includes('flowchart') || codeText.includes('graph') || 
                codeText.includes('sequenceDiagram') || codeText.includes('classDiagram') ||
                codeText.includes('gantt') || codeText.includes('pie') ||
                codeText.includes('subgraph') || codeText.includes('classDef')) {{
                
                console.log('Found Mermaid diagram:', codeText.substring(0, 50) + '...');
                
                // Create a new div for the Mermaid diagram
                const mermaidDiv = document.createElement('div');
                mermaidDiv.className = 'mermaid';
                mermaidDiv.textContent = codeText;
                
                // Replace the code block with the Mermaid div
                const preElement = codeBlock.closest('pre');
                if (preElement) {{
                    preElement.parentNode.replaceChild(mermaidDiv, preElement);
                    mermaidCount++;
                }}
            }}
        }});
        
        console.log(`Converted ${{mermaidCount}} code blocks to Mermaid diagrams`);
        
        // Initialize Mermaid after processing
        if (mermaidCount > 0) {{
            setTimeout(() => {{
                mermaid.init();
                console.log('Mermaid initialization complete');
            }}, 500);
        }}
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
            
            # Wait for initial content load
            await page.wait_for_timeout(2000)
            
            # Check for and wait for Mermaid diagrams
            try:
                mermaid_count = await page.evaluate("document.querySelectorAll('.mermaid').length")
                if mermaid_count > 0:
                    print(f"  🔍 Found {mermaid_count} Mermaid diagram(s), waiting for rendering...")
                    
                    # Wait for SVG elements to appear (Mermaid renders as SVG)
                    await page.wait_for_selector('svg[id^="mermaid"], .mermaid svg', timeout=15000)
                    
                    # Additional wait to ensure all diagrams are fully rendered
                    await page.wait_for_timeout(2000)
                    
                    print(f"  ✅ All Mermaid diagrams rendered successfully")
                else:
                    print(f"  ℹ️  No Mermaid diagrams detected")
            except Exception as e:
                print(f"  ⚠️  Mermaid rendering issue: {e}")
            
            # Generate PDF with page break support
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
    if not install_dependencies():
        print("❌ Could not install required dependencies")
        return False
    
    md_file = "Cipher_Cognitive_Architecture_2025.md"
    html_file = "Cipher_Cognitive_Architecture_2025.html"
    pdf_file = "Cipher_Cognitive_Architecture_2025.pdf"
    
    print("🔄 Converting Cipher Cognitive Architecture 2025 document to PDF with Mermaid diagrams...")
    print("=" * 80)
    
    if os.path.exists(md_file):
        print(f"\n📄 Processing {md_file}...")
        
        # Convert MD to HTML
        if convert_markdown_to_html(md_file, html_file):
            # Convert HTML to PDF
            if asyncio.run(convert_html_to_pdf(html_file, pdf_file)):
                size_kb = os.path.getsize(pdf_file) / 1024
                print(f"  📊 PDF size: {size_kb:.1f} KB")
                print("\n" + "=" * 80)
                print(f"🎯 Conversion complete!")
                print(f"✅ Successfully converted {md_file} to {pdf_file}")
                print(f"📋 Your Cipher Cognitive Architecture document with Mermaid diagrams is now in PDF format!")
                print(f"🔧 Features included:")
                print(f"   • Four-tiered cognitive architecture diagrams")
                print(f"   • Properly rendered Mermaid flowcharts")
                print(f"   • Professional A4 formatting with 0.75\" margins")
                print(f"   • Enhanced visual layout for technical content")
                return True
    else:
        print(f"⚠️  {md_file} not found")
        return False

if __name__ == "__main__":
    main()
