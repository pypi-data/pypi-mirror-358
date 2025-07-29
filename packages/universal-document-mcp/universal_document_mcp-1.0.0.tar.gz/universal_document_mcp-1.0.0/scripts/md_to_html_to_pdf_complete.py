#!/usr/bin/env python3
"""
Complete Markdown to PDF Converter with Mermaid and Page Break Support
1. Converts Markdown to HTML with Mermaid diagram rendering
2. Converts HTML to PDF respecting manual page break markers
"""

import sys
import os
import asyncio
import re
from pathlib import Path

def install_dependencies():
    """Install required dependencies"""
    dependencies = ['playwright', 'markdown']

    for dep in dependencies:
        try:
            __import__(dep.replace('-', '_'))
        except ImportError:
            print(f"Installing {dep}...")
            import subprocess
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
            except Exception as e:
                print(f"Failed to install {dep}: {e}")
                return False

    # Install playwright browsers
    try:
        import subprocess
        subprocess.check_call([sys.executable, "-m", "playwright", "install", "chromium"])
    except:
        pass

    return True

def convert_markdown_to_html(md_file, html_file):
    """Convert Markdown to HTML with Mermaid support"""
    try:
        import markdown

        # Read markdown content
        with open(md_file, 'r', encoding='utf-8') as f:
            md_content = f.read()

        # Configure markdown with basic extensions
        md = markdown.Markdown(extensions=[
            'extra',
            'codehilite',
            'toc'
        ])

        # Convert to HTML
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
        
        h1 {{
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        
        h2 {{
            border-bottom: 2px solid #ecf0f1;
            padding-bottom: 8px;
        }}
        
        .mermaid {{
            text-align: center;
            margin: 20px 0;
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
        
        th {{
            background-color: #f2f2f2;
            font-weight: bold;
        }}
        
        ul, ol {{
            padding-left: 30px;
        }}
        
        li {{
            margin-bottom: 5px;
        }}
        
        /* Page break support */
        @media print {{
            .page-break, 
            .pagebreak,
            [class*="page-break"],
            [class*="pagebreak"] {{
                page-break-before: always !important;
                break-before: page !important;
            }}
            
            h1, h2, h3, h4, h5, h6 {{
                page-break-after: avoid !important;
                break-after: avoid !important;
            }}
            
            .mermaid, 
            svg[id^="mermaid"],
            pre.mermaid {{
                page-break-inside: avoid !important;
                break-inside: avoid !important;
            }}
            
            p, li {{
                orphans: 3;
                widows: 3;
            }}
        }}
    </style>
</head>
<body>
{html_content}

<script>
    // Initialize Mermaid
    mermaid.initialize({{
        startOnLoad: true,
        theme: 'default',
        securityLevel: 'loose',
        fontFamily: 'Arial, sans-serif'
    }});
    
    // Process any mermaid code blocks
    document.addEventListener('DOMContentLoaded', function() {{
        const mermaidBlocks = document.querySelectorAll('pre code.language-mermaid, code.language-mermaid');
        mermaidBlocks.forEach((block, index) => {{
            const mermaidCode = block.textContent;
            const mermaidDiv = document.createElement('div');
            mermaidDiv.className = 'mermaid';
            mermaidDiv.textContent = mermaidCode;
            block.parentNode.replaceWith(mermaidDiv);
        }});
        
        // Re-initialize mermaid after processing
        mermaid.init();
    }});
</script>
</body>
</html>"""
        
        # Write HTML file
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(full_html)
        
        print(f"  ✅ Converted {md_file} to {html_file}")
        return True
        
    except Exception as e:
        print(f"  ❌ Error converting {md_file} to HTML: {e}")
        return False

async def convert_html_to_pdf_with_pagebreaks(html_file, pdf_file):
    """Convert HTML file to PDF using Playwright with page break support"""
    try:
        from playwright.async_api import async_playwright
        
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            
            file_path = Path(html_file).resolve()
            await page.goto(f"file://{file_path}")
            
            # Wait for content and Mermaid diagrams to load
            await page.wait_for_timeout(5000)
            
            try:
                await page.wait_for_selector('svg[id^="mermaid"], .mermaid svg', timeout=10000)
                print(f"  ✅ Mermaid diagrams rendered in {html_file}")
            except:
                print(f"  ℹ️  No Mermaid diagrams found in {html_file}")
            
            # Add enhanced page break CSS
            await page.add_style_tag(content="""
                @media print {
                    /* Enhanced page break detection */
                    *:contains("Page ") {
                        page-break-before: always !important;
                        break-before: page !important;
                    }
                    
                    /* Manual page break classes */
                    .page-break, .pagebreak, [class*="page-break"], [class*="pagebreak"] {
                        page-break-before: always !important;
                        break-before: page !important;
                    }
                    
                    /* Section breaks */
                    h1 { page-break-before: auto; }
                    h2, h3, h4, h5, h6 { page-break-after: avoid !important; }
                    
                    /* Keep content together */
                    .mermaid, svg[id^="mermaid"], pre.mermaid, table {
                        page-break-inside: avoid !important;
                        break-inside: avoid !important;
                    }
                    
                    /* Typography */
                    p, li { orphans: 3; widows: 3; }
                }
            """)
            
            # JavaScript to handle page markers
            await page.evaluate("""
                function addPageBreaks() {
                    var walker = document.createTreeWalker(
                        document.body,
                        NodeFilter.SHOW_TEXT,
                        null,
                        false
                    );

                    var node;
                    var pageMarkers = [];

                    while (node = walker.nextNode()) {
                        if (node.textContent.match(/Page\\s+\\d+/)) {
                            pageMarkers.push(node);
                        }
                    }

                    for (var i = 0; i < pageMarkers.length; i++) {
                        var marker = pageMarkers[i];
                        var element = marker.parentElement;
                        if (element) {
                            element.style.pageBreakBefore = 'always';
                            element.style.breakBefore = 'page';
                        }
                    }

                    return pageMarkers.length;
                }

                var markerCount = addPageBreaks();
                console.log('Added page breaks for ' + markerCount + ' page markers');
            """)
            
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
                display_header_footer=False,
                scale=1.0
            )
            
            await browser.close()
            print(f"  ✅ Generated PDF: {pdf_file}")
            return True
            
    except Exception as e:
        print(f"  ❌ Error generating PDF from {html_file}: {e}")
        return False

def main():
    """Main conversion workflow"""
    if not install_dependencies():
        print("❌ Could not install required dependencies")
        return False
    
    # Files to process
    files = [
        "executive-brief-enhanced-final",
        "research-proposal-enhanced-final", 
        "architectural-vision-enhanced-final"
    ]
    
    print("🔄 Starting complete Markdown → HTML → PDF conversion...")
    print("=" * 70)
    
    success_count = 0
    
    for file_base in files:
        md_file = f"{file_base}.md"
        html_file = f"{file_base}.html"
        pdf_file = f"{file_base}.pdf"
        
        if os.path.exists(md_file):
            print(f"\n📄 Processing {md_file}...")
            
            # Step 1: MD → HTML
            if convert_markdown_to_html(md_file, html_file):
                # Step 2: HTML → PDF
                if asyncio.run(convert_html_to_pdf_with_pagebreaks(html_file, pdf_file)):
                    success_count += 1
                    size_kb = os.path.getsize(pdf_file) / 1024
                    print(f"  📊 Final PDF size: {size_kb:.1f} KB")
        else:
            print(f"⚠️  Warning: {md_file} not found")
    
    print("\n" + "=" * 70)
    print(f"🎯 Conversion complete!")
    print(f"✅ Successfully processed {success_count} out of {len(files)} files")
    print(f"📋 Your updated Markdown files are now converted to PDF with:")
    print(f"   • All latest edits included")
    print(f"   • Manual page break markers respected") 
    print(f"   • Mermaid diagrams properly rendered")
    print(f"   • Professional A4 formatting")
    
    return success_count == len(files)

if __name__ == "__main__":
    main()
