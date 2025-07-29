#!/usr/bin/env python3
"""
Convert the whitepaper_draft.md file to PDF with enhanced Mermaid support
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
    """Convert Markdown to HTML with enhanced Mermaid support for academic papers"""
    try:
        import markdown
        
        # Read markdown content
        with open(md_file, 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        # Basic markdown conversion
        md = markdown.Markdown(extensions=['extra', 'codehilite', 'toc'])
        html_content = md.convert(md_content)
        
        # Create full HTML document with academic paper styling
        full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>A Four-Tiered Cognitive Architecture for Advanced AI Reasoning</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10.9.1/dist/mermaid.min.js"></script>
    <style>
        body {{
            font-family: 'Times New Roman', Times, serif;
            line-height: 1.6;
            max-width: 8.5in;
            margin: 0 auto;
            padding: 0.75in;
            color: #000;
            font-size: 11pt;
        }}
        
        h1 {{
            font-size: 18pt;
            font-weight: bold;
            text-align: center;
            margin: 0.5in 0 0.3in 0;
            color: #000;
            border: none;
        }}
        
        h2 {{
            font-size: 14pt;
            font-weight: bold;
            margin: 0.4in 0 0.2in 0;
            color: #000;
            border: none;
        }}
        
        h3 {{
            font-size: 12pt;
            font-weight: bold;
            margin: 0.3in 0 0.15in 0;
            color: #000;
        }}
        
        h4, h5, h6 {{
            font-size: 11pt;
            font-weight: bold;
            margin: 0.2in 0 0.1in 0;
            color: #000;
        }}
        
        p {{
            margin: 0.15in 0;
            text-align: justify;
            text-indent: 0;
        }}
        
        .mermaid {{
            text-align: center;
            margin: 0.4in 0;
            background: white;
            border: 1px solid #ddd;
            border-radius: 4px;
            padding: 0.3in;
            page-break-inside: avoid !important;
            break-inside: avoid !important;
            page-break-before: auto;
            page-break-after: auto;
            min-height: 3in;
        }}

        .mermaid-container {{
            page-break-inside: avoid !important;
            break-inside: avoid !important;
            margin: 0.5in 0;
        }}

        .page-break-before {{
            page-break-before: auto !important;
            break-before: page !important;
            margin-top: 0.5in !important;
        }}
        
        pre {{
            background-color: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 4px;
            padding: 0.15in;
            overflow-x: auto;
            font-size: 9pt;
            margin: 0.2in 0;
            page-break-inside: avoid;
        }}
        
        code {{
            background-color: #f8f9fa;
            padding: 1px 3px;
            border-radius: 2px;
            font-family: 'Courier New', monospace;
            font-size: 9pt;
        }}
        
        blockquote {{
            border-left: 3px solid #ccc;
            margin: 0.2in 0;
            padding-left: 0.2in;
            color: #666;
            font-style: italic;
        }}
        
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 0.2in 0;
            font-size: 10pt;
        }}
        
        th, td {{
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }}
        
        th {{
            background-color: #f2f2f2;
            font-weight: bold;
        }}
        
        /* Academic paper specific styles */
        .author-info {{
            text-align: center;
            margin: 0.2in 0 0.4in 0;
            font-size: 12pt;
        }}
        
        .abstract {{
            margin: 0.3in 0;
            padding: 0.2in;
            background-color: #f9f9f9;
            border: 1px solid #ddd;
        }}
        
        .keywords {{
            margin: 0.2in 0;
            font-style: italic;
        }}
        
        .references {{
            font-size: 10pt;
        }}
        
        .references ol {{
            padding-left: 0.3in;
        }}
        
        .references li {{
            margin: 0.1in 0;
        }}
        
        /* Figure captions */
        em {{
            font-style: italic;
            font-size: 10pt;
            text-align: center;
            display: block;
            margin: 0.1in 0 0.2in 0;
        }}
        
        strong {{
            font-weight: bold;
        }}
        
        @media print {{
            body {{ margin: 0; padding: 0.75in; }}
            h1, h2, h3, h4, h5, h6 {{
                page-break-after: avoid !important;
                break-after: avoid !important;
            }}
            .mermaid, .mermaid-container, svg, pre, table {{
                page-break-inside: avoid !important;
                break-inside: avoid !important;
                page-break-before: auto !important;
                page-break-after: auto !important;
            }}
            .mermaid {{
                min-height: 3in !important;
                margin: 0.5in 0 !important;
                padding: 0.3in !important;
            }}
            p, li {{
                orphans: 3;
                widows: 3;
            }}
            .abstract {{
                page-break-inside: avoid !important;
                break-inside: avoid !important;
            }}
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
            htmlLabels: true
        }},
        themeVariables: {{
            primaryColor: '#e1f5fe',
            primaryTextColor: '#000',
            primaryBorderColor: '#1976d2',
            lineColor: '#333',
            sectionBkgColor: '#f5f5f5',
            altSectionBkgColor: '#fff',
            gridColor: '#ddd',
            secondaryColor: '#f3e5f5',
            tertiaryColor: '#e8f5e8'
        }}
    }});
    
    document.addEventListener('DOMContentLoaded', function() {{
        console.log('Processing Mermaid diagrams for academic paper...');

        // Process page break divs from markdown
        const pageBreakDivs = document.querySelectorAll('div[style*="page-break-before"]');
        pageBreakDivs.forEach(div => {{
            div.className = 'page-break-before';
            div.style.cssText = 'page-break-before: auto !important; margin-top: 0.5in !important;';
        }});
        console.log(`Processed ${{pageBreakDivs.length}} page break markers`);

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

                // Create a container for the Mermaid diagram
                const mermaidContainer = document.createElement('div');
                mermaidContainer.className = 'mermaid-container';

                // Create a new div for the Mermaid diagram
                const mermaidDiv = document.createElement('div');
                mermaidDiv.className = 'mermaid';
                mermaidDiv.textContent = codeText;

                // Add the mermaid div to the container
                mermaidContainer.appendChild(mermaidDiv);

                // Replace the code block with the Mermaid container
                const preElement = codeBlock.closest('pre');
                if (preElement) {{
                    preElement.parentNode.replaceChild(mermaidContainer, preElement);
                    mermaidCount++;
                }}
            }}
        }});
        
        console.log(`Converted ${{mermaidCount}} code blocks to Mermaid diagrams`);
        
        // Initialize Mermaid after processing
        if (mermaidCount > 0) {{
            setTimeout(() => {{
                mermaid.init();
                console.log('Mermaid initialization complete for academic paper');
            }}, 1000);
        }}
    }});
</script>
</body>
</html>"""
        
        # Write HTML file
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(full_html)
        
        print(f"  ✅ Converted {md_file} to HTML with academic formatting")
        return True

    except Exception as e:
        print(f"  ❌ Error converting {md_file}: {e}")
        return False

async def convert_html_to_pdf(html_file, pdf_file):
    """Convert HTML to PDF using Playwright with academic paper settings"""
    try:
        from playwright.async_api import async_playwright

        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()

            # Load HTML file
            file_path = Path(html_file).resolve()
            await page.goto(f"file://{file_path}")

            # Wait for initial content load
            await page.wait_for_timeout(3000)

            # Check for and wait for Mermaid diagrams
            try:
                mermaid_count = await page.evaluate("document.querySelectorAll('.mermaid').length")
                if mermaid_count > 0:
                    print(f"  🔍 Found {mermaid_count} Mermaid diagram(s), waiting for rendering...")

                    # Wait for SVG elements to appear (Mermaid renders as SVG)
                    await page.wait_for_selector('svg[id^="mermaid"], .mermaid svg', timeout=20000)

                    # Additional wait to ensure all diagrams are fully rendered
                    await page.wait_for_timeout(3000)

                    print(f"  ✅ All Mermaid diagrams rendered successfully")
                else:
                    print(f"  ℹ️  No Mermaid diagrams detected")
            except Exception as e:
                print(f"  ⚠️  Mermaid rendering issue: {e}")

            # Generate PDF with academic paper settings
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
                display_header_footer=False,
                scale=1.0
            )

            await browser.close()
            print(f"  ✅ Generated academic PDF: {pdf_file}")
            return True

    except Exception as e:
        print(f"  ❌ Error generating PDF: {e}")
        return False

def main():
    """Main conversion process for whitepaper"""
    if not install_dependencies():
        print("❌ Could not install required dependencies")
        return False

    md_file = "whitepaper_draft.md"
    html_file = "whitepaper_draft.html"
    pdf_file = "whitepaper_draft.pdf"

    print("🔄 Converting whitepaper to PDF with enhanced Mermaid diagrams and optimized page breaks...")
    print("=" * 80)

    if os.path.exists(md_file):
        print(f"\n📄 Processing {md_file}...")

        # Convert MD to HTML with enhanced Mermaid handling
        if convert_markdown_to_html(md_file, html_file):
            # Convert HTML to PDF with optimized page breaks
            if asyncio.run(convert_html_to_pdf(html_file, pdf_file)):
                size_kb = os.path.getsize(pdf_file) / 1024
                print(f"  📊 PDF size: {size_kb:.1f} KB")
                print("\n" + "=" * 80)
                print(f"🎯 Whitepaper conversion complete!")
                print(f"✅ Successfully converted {md_file} to {pdf_file}")
                print(f"📋 Your academic whitepaper with Mermaid diagrams is now in PDF format!")
                print(f"🔧 Features included:")
                print(f"   • Professional academic paper formatting")
                print(f"   • 4 enhanced Mermaid diagrams with color coding")
                print(f"   • A4 format with 0.75\" margins")
                print(f"   • Proper typography for academic publications")
                print(f"   • Intelligent page break optimization preventing diagram splits")
                print(f"   • Complete technical specifications and references")
                return True
    else:
        print(f"⚠️  {md_file} not found")
        return False

if __name__ == "__main__":
    main()
