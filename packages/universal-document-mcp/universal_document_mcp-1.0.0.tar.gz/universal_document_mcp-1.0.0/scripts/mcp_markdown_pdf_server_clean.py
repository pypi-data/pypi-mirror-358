#!/usr/bin/env python3
"""
MCP Server for Automated Markdown to PDF Conversion with Mermaid Support
Provides tools for detecting, converting, and managing Markdown files with diagrams
"""

import sys
import os
import asyncio
import subprocess
import glob
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

# Install MCP dependencies if needed
try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    print("Installing MCP dependencies...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "mcp[cli]"])
    from mcp.server.fastmcp import FastMCP

# Create MCP server
mcp = FastMCP("Markdown PDF Converter", 
              dependencies=["playwright", "markdown", "asyncio"])

def install_conversion_dependencies():
    """Install required dependencies for conversion"""
    try:
        import playwright
        import markdown
        return True
    except ImportError:
        print("Installing conversion dependencies...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "playwright", "markdown"])
            subprocess.check_call([sys.executable, "-m", "playwright", "install", "chromium"])
            return True
        except Exception as e:
            print(f"Failed to install dependencies: {e}")
            return False

def convert_markdown_to_html(md_file: str, html_file: str) -> bool:
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
            margin: 20px 0;
            background: white;
            border: 1px solid #e1e8ed;
            border-radius: 8px;
            padding: 20px;
        }}
        
        pre {{
            background-color: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 4px;
            padding: 15px;
            overflow-x: auto;
        }}
        
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
        startOnLoad: false,
        theme: 'default',
        securityLevel: 'loose',
        fontFamily: 'Arial, sans-serif'
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
        
        # Write HTML file
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(full_html)
        
        return True
        
    except Exception as e:
        print(f"Error converting {md_file}: {e}")
        return False

async def convert_html_to_pdf(html_file: str, pdf_file: str) -> bool:
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
                    # Wait for SVG elements to appear (Mermaid renders as SVG)
                    await page.wait_for_selector('svg[id^="mermaid"], .mermaid svg', timeout=15000)
                    # Additional wait to ensure all diagrams are fully rendered
                    await page.wait_for_timeout(2000)
            except Exception as e:
                print(f"Mermaid rendering issue: {e}")
            
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
            return True
            
    except Exception as e:
        print(f"Error generating PDF: {e}")
        return False

@mcp.resource("markdown://files")
def list_markdown_files() -> str:
    """List all Markdown files in the current directory"""
    md_files = glob.glob("*.md")
    files_info = []
    
    for md_file in md_files:
        base_name = Path(md_file).stem
        pdf_file = f"{base_name}.pdf"
        html_file = f"{base_name}.html"
        
        file_info = {
            "markdown": md_file,
            "pdf_exists": os.path.exists(pdf_file),
            "html_exists": os.path.exists(html_file),
            "size_kb": round(os.path.getsize(md_file) / 1024, 1),
            "modified": datetime.fromtimestamp(os.path.getmtime(md_file)).isoformat()
        }
        files_info.append(file_info)
    
    return json.dumps(files_info, indent=2)

@mcp.resource("conversion://status")
def conversion_status() -> str:
    """Get conversion status for all Markdown files"""
    md_files = glob.glob("*.md")
    status = {
        "total_markdown_files": len(md_files),
        "converted_to_pdf": 0,
        "needs_conversion": [],
        "last_check": datetime.now().isoformat()
    }
    
    for md_file in md_files:
        base_name = Path(md_file).stem
        pdf_file = f"{base_name}.pdf"
        
        if os.path.exists(pdf_file):
            status["converted_to_pdf"] += 1
        else:
            status["needs_conversion"].append(md_file)
    
    return json.dumps(status, indent=2)

@mcp.tool()
def detect_mermaid_diagrams(file_path: str) -> str:
    """Detect Mermaid diagrams in a Markdown file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        mermaid_keywords = ['flowchart', 'graph', 'sequenceDiagram', 'classDiagram', 
                           'gantt', 'pie', 'subgraph', 'classDef']
        
        found_diagrams = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            for keyword in mermaid_keywords:
                if keyword in line:
                    found_diagrams.append({
                        "line": i + 1,
                        "type": keyword,
                        "content": line.strip()
                    })
        
        result = {
            "file": file_path,
            "mermaid_diagrams_found": len(found_diagrams),
            "diagrams": found_diagrams
        }
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        return f"Error analyzing {file_path}: {str(e)}"

@mcp.tool()
async def convert_single_file(file_path: str) -> str:
    """Convert a single Markdown file to PDF with Mermaid support"""
    if not install_conversion_dependencies():
        return "ERROR: Failed to install required dependencies"

    if not os.path.exists(file_path):
        return f"ERROR: File not found: {file_path}"

    base_name = Path(file_path).stem
    html_file = f"{base_name}.html"
    pdf_file = f"{base_name}.pdf"

    try:
        # Step 1: MD to HTML
        if not convert_markdown_to_html(file_path, html_file):
            return f"ERROR: Failed to convert {file_path} to HTML"

        # Step 2: HTML to PDF
        if not await convert_html_to_pdf(html_file, pdf_file):
            return f"ERROR: Failed to convert {html_file} to PDF"

        # Get file size
        size_kb = os.path.getsize(pdf_file) / 1024

        result = {
            "status": "success",
            "input_file": file_path,
            "output_file": pdf_file,
            "size_kb": round(size_kb, 1),
            "timestamp": datetime.now().isoformat()
        }

        return json.dumps(result, indent=2)

    except Exception as e:
        return f"ERROR: Error converting {file_path}: {str(e)}"

@mcp.tool()
async def batch_convert_all() -> str:
    """Convert all Markdown files to PDF that don't have existing PDFs"""
    if not install_conversion_dependencies():
        return "ERROR: Failed to install required dependencies"

    md_files = glob.glob("*.md")
    files_to_convert = []

    for md_file in md_files:
        base_name = Path(md_file).stem
        pdf_file = f"{base_name}.pdf"

        if not os.path.exists(pdf_file):
            files_to_convert.append(md_file)

    if not files_to_convert:
        return "SUCCESS: All Markdown files already have corresponding PDFs!"

    results = []
    success_count = 0

    for md_file in files_to_convert:
        base_name = Path(md_file).stem
        html_file = f"{base_name}.html"
        pdf_file = f"{base_name}.pdf"

        try:
            # Convert MD to HTML
            if convert_markdown_to_html(md_file, html_file):
                # Convert HTML to PDF
                if await convert_html_to_pdf(html_file, pdf_file):
                    success_count += 1
                    size_kb = os.path.getsize(pdf_file) / 1024
                    results.append({
                        "file": md_file,
                        "status": "success",
                        "size_kb": round(size_kb, 1)
                    })
                else:
                    results.append({
                        "file": md_file,
                        "status": "failed_pdf_conversion"
                    })
            else:
                results.append({
                    "file": md_file,
                    "status": "failed_html_conversion"
                })
        except Exception as e:
            results.append({
                "file": md_file,
                "status": "error",
                "error": str(e)
            })

    summary = {
        "total_files": len(files_to_convert),
        "successful_conversions": success_count,
        "failed_conversions": len(files_to_convert) - success_count,
        "results": results,
        "timestamp": datetime.now().isoformat()
    }

    return json.dumps(summary, indent=2)

@mcp.tool()
def check_system_status() -> str:
    """Check system status and dependencies"""
    status = {
        "python_version": sys.version,
        "current_directory": os.getcwd(),
        "markdown_files_count": len(glob.glob("*.md")),
        "pdf_files_count": len(glob.glob("*.pdf")),
        "html_files_count": len(glob.glob("*.html")),
        "dependencies": {}
    }

    # Check dependencies
    try:
        import playwright
        status["dependencies"]["playwright"] = "installed"
    except ImportError:
        status["dependencies"]["playwright"] = "not_installed"

    try:
        import markdown
        status["dependencies"]["markdown"] = "installed"
    except ImportError:
        status["dependencies"]["markdown"] = "not_installed"

    try:
        from mcp.server.fastmcp import FastMCP
        status["dependencies"]["mcp"] = "installed"
    except ImportError:
        status["dependencies"]["mcp"] = "not_installed"

    return json.dumps(status, indent=2)

if __name__ == "__main__":
    mcp.run()
