#!/usr/bin/env python3
"""
Apply Mermaid Diagram Fix to Existing Documents
Fixes the rendering issue where Mermaid diagrams appear as syntax-highlighted code instead of actual diagrams
"""

import sys
import os
import asyncio
import subprocess
import glob
from pathlib import Path
from datetime import datetime

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

def convert_markdown_to_html_with_mermaid_fix(md_file, html_file):
    """Convert Markdown to HTML with enhanced Mermaid support"""
    try:
        import markdown
        
        # Read markdown content
        with open(md_file, 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        # Basic markdown conversion
        md = markdown.Markdown(extensions=['extra', 'codehilite', 'toc'])
        html_content = md.convert(md_content)
        
        # Create full HTML document with ENHANCED Mermaid support
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
            margin: 20px 0;
            background: white;
            border: 1px solid #e1e8ed;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
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
            /* Hide page break markers and lines */
            .page-marker,
            [class*="page-marker"],
            .page-break-line,
            [class*="page-break-line"] {{
                display: none !important;
                visibility: hidden !important;
                height: 0 !important;
                margin: 0 !important;
                padding: 0 !important;
                line-height: 0 !important;
            }}

            /* Major headings start on new pages (except first h1) */
            h1:not(:first-of-type) {{
                page-break-before: always !important;
                break-before: page !important;
            }}

            /* Phase headings start on new pages */
            h2 {{
                page-break-before: auto !important;
                break-before: auto !important;
            }}

            /* Avoid breaking after headings */
            h1, h2, h3, h4, h5, h6 {{
                page-break-after: avoid !important;
                break-after: avoid !important;
            }}

            /* Keep content together */
            .mermaid, svg, pre, table {{
                page-break-inside: avoid !important;
                break-inside: avoid !important;
            }}

            /* Orphan and widow control */
            p, li {{ orphans: 3; widows: 3; }}
        }}
    </style>
</head>
<body>
{html_content}

<script>
    // Enhanced Mermaid initialization
    mermaid.initialize({{
        startOnLoad: false,
        theme: 'default',
        securityLevel: 'loose',
        fontFamily: 'Arial, sans-serif',
        flowchart: {{
            useMaxWidth: true,
            htmlLabels: true
        }},
        sequence: {{
            useMaxWidth: true
        }},
        gantt: {{
            useMaxWidth: true
        }}
    }});
    
    document.addEventListener('DOMContentLoaded', function() {{
        console.log('🔍 Applying Mermaid diagram fix...');
        
        // Enhanced detection for syntax-highlighted code blocks
        const codeBlocks = document.querySelectorAll('div.codehilite pre code, pre code');
        let mermaidCount = 0;
        
        codeBlocks.forEach((codeBlock) => {{
            // Get the text content, removing HTML tags from syntax highlighting
            let codeText = codeBlock.textContent || codeBlock.innerText;
            
            // Enhanced Mermaid detection patterns
            if (codeText.includes('flowchart') || codeText.includes('graph') || 
                codeText.includes('sequenceDiagram') || codeText.includes('classDiagram') ||
                codeText.includes('gantt') || codeText.includes('pie') ||
                codeText.includes('subgraph') || codeText.includes('classDef') ||
                codeText.includes('stateDiagram') || codeText.includes('journey') ||
                codeText.includes('gitgraph') || codeText.includes('erDiagram')) {{
                
                console.log('✅ Found Mermaid diagram:', codeText.substring(0, 50) + '...');
                
                // Create a new div for the Mermaid diagram
                const mermaidDiv = document.createElement('div');
                mermaidDiv.className = 'mermaid';
                mermaidDiv.textContent = codeText;
                
                // Replace the entire code block structure with the Mermaid div
                const preElement = codeBlock.closest('pre');
                const codeHiliteDiv = preElement ? preElement.closest('div.codehilite') : null;
                const targetElement = codeHiliteDiv || preElement;
                
                if (targetElement) {{
                    targetElement.parentNode.replaceChild(mermaidDiv, targetElement);
                    mermaidCount++;
                }}
            }}
        }});
        
        console.log(`🎯 Converted ${{mermaidCount}} code blocks to Mermaid diagrams`);
        
        // Initialize Mermaid after processing with enhanced error handling
        if (mermaidCount > 0) {{
            setTimeout(() => {{
                try {{
                    mermaid.init();
                    console.log('✅ Mermaid initialization complete - diagrams should now be visible!');
                }} catch (error) {{
                    console.error('❌ Mermaid initialization error:', error);
                }}
            }}, 500);
        }} else {{
            console.log('ℹ️ No Mermaid diagrams found to process');
        }}
    }});
</script>
</body>
</html>"""
        
        # Write HTML file
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(full_html)
        
        print(f"  ✅ Applied Mermaid fix to {html_file}")
        return True
        
    except Exception as e:
        print(f"  ❌ Error applying Mermaid fix to {md_file}: {e}")
        return False

async def convert_html_to_pdf_with_mermaid_wait(html_file, pdf_file):
    """Convert HTML to PDF with proper Mermaid rendering wait"""
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
            
            # Enhanced Mermaid diagram detection and rendering wait
            try:
                mermaid_count = await page.evaluate("document.querySelectorAll('.mermaid').length")
                if mermaid_count > 0:
                    print(f"  🔍 Found {mermaid_count} Mermaid diagram(s), waiting for rendering...")
                    
                    # Wait for SVG elements to appear (Mermaid renders as SVG)
                    await page.wait_for_selector('svg[id^="mermaid"], .mermaid svg', timeout=15000)
                    
                    # Additional wait to ensure all diagrams are fully rendered
                    await page.wait_for_timeout(2000)
                    
                    # Verify all diagrams have rendered successfully
                    rendered_count = await page.evaluate("document.querySelectorAll('.mermaid svg').length")
                    print(f"  ✅ Successfully rendered {rendered_count}/{mermaid_count} Mermaid diagrams")
                    
                    if rendered_count < mermaid_count:
                        print(f"  ⚠️ Warning: {mermaid_count - rendered_count} diagrams may not have rendered properly")
                else:
                    print(f"  ℹ️ No Mermaid diagrams detected")
            except Exception as e:
                print(f"  ⚠️ Mermaid rendering issue: {e}")
                # Continue with PDF generation even if Mermaid fails
            
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
            print(f"  ✅ Generated PDF with fixed Mermaid diagrams: {pdf_file}")
            return True
            
    except Exception as e:
        print(f"  ❌ Error generating PDF: {e}")
        return False

def main():
    """Apply Mermaid fix to all Markdown files"""
    if not install_dependencies():
        print("❌ Could not install required dependencies")
        return False
    
    # Find all Markdown files
    md_files = glob.glob("*.md")
    
    if not md_files:
        print("❌ No Markdown files found in current directory")
        return False
    
    print("🔧 APPLYING MERMAID DIAGRAM FIX")
    print("=" * 50)
    print(f"Found {len(md_files)} Markdown files to process")
    print()
    
    success_count = 0
    
    for md_file in md_files:
        # Skip only certain generated files, but process page break files
        if ('TASK_COMPLETION_SUMMARY' in md_file or
            md_file.startswith('.')):
            print(f"⏭️ Skipping generated file: {md_file}")
            continue
        
        base_name = Path(md_file).stem
        html_file = f"{base_name}.html"
        pdf_file = f"{base_name}.pdf"
        
        print(f"📄 Processing {md_file}...")
        
        # Step 1: Apply Mermaid fix to HTML
        if convert_markdown_to_html_with_mermaid_fix(md_file, html_file):
            # Step 2: Generate PDF with proper Mermaid rendering
            if asyncio.run(convert_html_to_pdf_with_mermaid_wait(html_file, pdf_file)):
                success_count += 1
                size_kb = os.path.getsize(pdf_file) / 1024
                print(f"  📊 PDF size: {size_kb:.1f} KB")
        
        print()
    
    print("=" * 50)
    print(f"🎯 MERMAID FIX COMPLETE!")
    processed_files = [f for f in md_files if not ('TASK_COMPLETION_SUMMARY' in f or f.startswith('.'))]
    print(f"✅ Successfully processed {success_count}/{len(processed_files)} files")
    print()
    print("🔧 FIXES APPLIED:")
    print("   • Enhanced Mermaid diagram detection")
    print("   • Syntax-highlighted code block conversion")
    print("   • Proper SVG rendering in PDFs")
    print("   • Professional styling and formatting")
    print("   • Page break preservation")
    print()
    print("📋 Your Mermaid diagrams should now render properly as visual diagrams!")
    
    return success_count > 0

if __name__ == "__main__":
    main()
