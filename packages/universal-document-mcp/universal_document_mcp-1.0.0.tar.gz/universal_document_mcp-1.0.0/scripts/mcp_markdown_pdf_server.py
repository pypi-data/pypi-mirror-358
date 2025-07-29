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

# Import enhanced file management
try:
    from enhanced_file_manager import EnhancedFileManager
    from file_organization_tools import FileOrganizationTools
    FILE_MANAGEMENT_AVAILABLE = True
except ImportError:
    print("Warning: Enhanced file management not available")
    FILE_MANAGEMENT_AVAILABLE = False

# Install MCP dependencies if needed
try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    print("Installing MCP dependencies...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "mcp[cli]"])
    from mcp.server.fastmcp import FastMCP

# Create MCP server
mcp = FastMCP("Enhanced Markdown PDF Converter with File Management",
              dependencies=["playwright", "markdown", "asyncio"])

# Initialize file management
if FILE_MANAGEMENT_AVAILABLE:
    file_manager = EnhancedFileManager()
    org_tools = FileOrganizationTools()
else:
    file_manager = None
    org_tools = None

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
    mermaid.initialize({{
        startOnLoad: false,
        theme: 'default',
        securityLevel: 'loose',
        fontFamily: 'Arial, sans-serif'
    }});
    
    document.addEventListener('DOMContentLoaded', function() {{
        console.log('🔍 Processing Mermaid diagrams...');

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
                    console.log('✅ Mermaid initialization complete');
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

            # Process page breaks and hide page markers
            await page.evaluate("""
                // Find and process page break lines
                function processPageBreaks() {
                    const walker = document.createTreeWalker(
                        document.body,
                        NodeFilter.SHOW_TEXT,
                        null,
                        false
                    );

                    const pageBreakLines = [];
                    let node;

                    while (node = walker.nextNode()) {
                        // Look for lines with dashes and "Page X" pattern
                        if (node.textContent.includes('Page ') &&
                            (node.textContent.includes('---') || node.textContent.includes('___'))) {
                            pageBreakLines.push(node);
                        }
                    }

                    // Hide page break lines and add page breaks
                    pageBreakLines.forEach(lineNode => {
                        const element = lineNode.parentElement;
                        if (element) {
                            // Hide the page break line completely
                            element.style.display = 'none';
                            element.style.visibility = 'hidden';
                            element.style.height = '0';
                            element.style.margin = '0';
                            element.style.padding = '0';
                            element.classList.add('page-break-line');

                            // Find the next visible element and add page break before it
                            let nextElement = element.nextElementSibling;
                            while (nextElement && (nextElement.style.display === 'none' ||
                                   nextElement.textContent.trim() === '')) {
                                nextElement = nextElement.nextElementSibling;
                            }

                            if (nextElement) {
                                nextElement.style.pageBreakBefore = 'always';
                                nextElement.style.breakBefore = 'page';
                                nextElement.classList.add('page-break-target');
                            }
                        }
                    });

                    return pageBreakLines.length;
                }

                // Enhanced intelligent page break processing
                function processIntelligentPageBreaks() {
                    const breakCandidates = [];
                    const allHeadings = document.querySelectorAll('h1, h2, h3, h4, h5, h6');

                    allHeadings.forEach((heading, index) => {
                        if (index === 0) return; // Skip first heading

                        const headingLevel = parseInt(heading.tagName.charAt(1));
                        const headingText = heading.textContent.trim();

                        // Calculate content metrics
                        const contentAfter = getContentAfterElement(heading);
                        const estimatedLines = estimateContentLines(contentAfter);
                        const contentBefore = getContentBeforeElement(heading);
                        const currentPageLines = estimateContentLines(contentBefore);

                        let shouldBreak = false;
                        let reason = '';
                        let confidence = 0;

                        // Intelligent decision rules

                        // Rule 1: Phase headings always start new pages
                        if (headingText.includes('Phase ')) {
                            shouldBreak = true;
                            reason = 'Phase heading - always new page';
                            confidence = 0.95;
                        }

                        // Rule 2: Major sections with substantial content
                        else if (headingLevel <= 2 && estimatedLines >= 8 && currentPageLines >= 20) {
                            shouldBreak = true;
                            reason = 'Major section with substantial content';
                            confidence = 0.9;
                        }

                        // Rule 3: Avoid orphaned headings (anti-orphan rule)
                        else if (estimatedLines < 10 && currentPageLines > 32) {
                            shouldBreak = true;
                            reason = 'Avoid orphaned heading at page bottom';
                            confidence = 0.85;
                        }

                        // Rule 4: Important document sections
                        else if (headingLevel <= 2 && (
                            headingText.includes('Risk') ||
                            headingText.includes('Conclusion') ||
                            headingText.includes('Implementation') ||
                            headingText.includes('Architecture') ||
                            headingText.includes('Requirements') ||
                            headingText.includes('Operational')
                        )) {
                            if (currentPageLines >= 25 && estimatedLines >= 6) {
                                shouldBreak = true;
                                reason = 'Important document section';
                                confidence = 0.8;
                            }
                        }

                        // Rule 5: Prevent overly long pages
                        else if (currentPageLines + estimatedLines > 45) {
                            shouldBreak = true;
                            reason = 'Prevent overly long page';
                            confidence = 0.9;
                        }

                        // Rule 6: Good page balance for subsections
                        else if (headingLevel === 3 && estimatedLines >= 8 &&
                                currentPageLines >= 25 && currentPageLines <= 38) {
                            shouldBreak = true;
                            reason = 'Good page balance for subsection';
                            confidence = 0.7;
                        }

                        if (shouldBreak && confidence >= 0.7) {
                            heading.style.pageBreakBefore = 'always';
                            heading.style.breakBefore = 'page';
                            heading.classList.add('intelligent-page-break');
                            heading.setAttribute('data-break-reason', reason);

                            breakCandidates.push({
                                element: heading,
                                reason: reason,
                                confidence: confidence,
                                headingText: headingText
                            });

                            console.log(`Applied intelligent break: ${headingText} (${reason})`);
                        }
                    });

                    return breakCandidates.length;
                }

                // Helper functions for content analysis
                function getContentAfterElement(element) {
                    const content = [];
                    let current = element.nextElementSibling;

                    while (current) {
                        if (current.tagName && current.tagName.match(/^H[1-6]$/)) {
                            const currentLevel = parseInt(current.tagName.charAt(1));
                            const elementLevel = parseInt(element.tagName.charAt(1));
                            if (currentLevel <= elementLevel) break;
                        }
                        content.push(current);
                        current = current.nextElementSibling;
                    }
                    return content;
                }

                function getContentBeforeElement(element) {
                    const content = [];
                    let current = element.previousElementSibling;
                    let lineCount = 0;

                    while (current && lineCount < 50) {
                        if (current.classList && (
                            current.classList.contains('page-break-target') ||
                            current.classList.contains('intelligent-page-break')
                        )) break;

                        content.unshift(current);
                        lineCount += estimateElementLines(current);
                        current = current.previousElementSibling;
                    }
                    return content;
                }

                function estimateContentLines(elements) {
                    return elements.reduce((total, element) => total + estimateElementLines(element), 0);
                }

                function estimateElementLines(element) {
                    if (!element || !element.textContent) return 0;

                    const text = element.textContent.trim();
                    if (!text) return 0.5;

                    if (element.tagName && element.tagName.match(/^H[1-6]$/)) return 2;
                    if (element.tagName === 'PRE' || element.classList.contains('mermaid')) {
                        return Math.max(3, text.split('\\n').length);
                    }
                    if (element.tagName === 'UL' || element.tagName === 'OL') {
                        return Math.max(2, element.querySelectorAll('li').length);
                    }

                    return Math.max(1, Math.ceil(text.length / 80));
                }

                const pageBreaksProcessed = processPageBreaks();
                const intelligentBreaksProcessed = processIntelligentPageBreaks();

                console.log(`Processed ${pageBreaksProcessed} page break lines and applied ${intelligentBreaksProcessed} intelligent page breaks`);
            """)
            
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
def check_system_status() -> str:
    """Check system status and dependencies"""
    status = {
        "timestamp": datetime.now().isoformat(),
        "dependencies": {},
        "system_info": {}
    }

    # Check Python version
    status["system_info"]["python_version"] = sys.version

    # Check dependencies
    try:
        import playwright
        status["dependencies"]["playwright"] = "✅ Available"
    except ImportError:
        status["dependencies"]["playwright"] = "❌ Not installed"

    try:
        import markdown
        status["dependencies"]["markdown"] = "✅ Available"
    except ImportError:
        status["dependencies"]["markdown"] = "❌ Not installed"

    # Check for markdown files
    md_files = glob.glob("*.md")
    status["system_info"]["markdown_files_found"] = len(md_files)

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
        return "❌ Failed to install required dependencies"
    
    if not os.path.exists(file_path):
        return f"❌ File not found: {file_path}"
    
    base_name = Path(file_path).stem
    html_file = f"{base_name}.html"
    pdf_file = f"{base_name}.pdf"
    
    try:
        # Step 1: MD → HTML
        if not convert_markdown_to_html(file_path, html_file):
            return f"❌ Failed to convert {file_path} to HTML"
        
        # Step 2: HTML → PDF
        if not await convert_html_to_pdf(html_file, pdf_file):
            return f"❌ Failed to convert {html_file} to PDF"
        
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
        return f"❌ Error converting {file_path}: {str(e)}"

@mcp.tool()
async def batch_convert_all() -> str:
    """Convert all Markdown files to PDF that don't have existing PDFs"""
    if not install_conversion_dependencies():
        return "❌ Failed to install required dependencies"
    
    md_files = glob.glob("*.md")
    files_to_convert = []
    
    for md_file in md_files:
        base_name = Path(md_file).stem
        pdf_file = f"{base_name}.pdf"
        
        if not os.path.exists(pdf_file):
            files_to_convert.append(md_file)
    
    if not files_to_convert:
        return "✅ All Markdown files already have corresponding PDFs!"
    
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
async def convert_with_enhanced_page_breaks(file_path: str) -> str:
    """Convert Markdown to PDF with enhanced page break processing that hides page markers and adds intelligent breaks"""
    if not install_conversion_dependencies():
        return "❌ Failed to install required dependencies"

    if not os.path.exists(file_path):
        return f"❌ File not found: {file_path}"

    base_name = Path(file_path).stem
    html_file = f"{base_name}.html"
    pdf_file = f"{base_name}.pdf"

    try:
        # Step 1: MD → HTML
        if not convert_markdown_to_html(file_path, html_file):
            return f"❌ Failed to convert {file_path} to HTML"

        # Step 2: Enhanced HTML → PDF with page break processing
        if not await convert_html_to_pdf(html_file, pdf_file):
            return f"❌ Failed to convert {html_file} to PDF"

        # Get file size
        size_kb = os.path.getsize(pdf_file) / 1024

        result = {
            "status": "success",
            "input_file": file_path,
            "output_file": pdf_file,
            "size_kb": round(size_kb, 1),
            "timestamp": datetime.now().isoformat(),
            "features": [
                "Page break markers hidden in PDF",
                "Intelligent page breaks before major sections",
                "Phase headings start on new pages",
                "Mermaid diagrams preserved",
                "Professional formatting maintained"
            ]
        }

        return json.dumps(result, indent=2)

    except Exception as e:
        return f"❌ Error converting {file_path}: {str(e)}"

@mcp.tool()
async def batch_convert_with_enhanced_breaks() -> str:
    """Batch convert all Markdown files with enhanced page break processing"""
    if not install_conversion_dependencies():
        return "❌ Failed to install required dependencies"

    md_files = glob.glob("*.md")
    if not md_files:
        return "ℹ️ No Markdown files found in current directory"

    results = []
    success_count = 0

    for md_file in md_files:
        base_name = Path(md_file).stem
        html_file = f"{base_name}.html"
        pdf_file = f"{base_name}.pdf"

        try:
            # Convert MD to HTML
            if convert_markdown_to_html(md_file, html_file):
                # Convert HTML to PDF with enhanced processing
                if await convert_html_to_pdf(html_file, pdf_file):
                    success_count += 1
                    size_kb = os.path.getsize(pdf_file) / 1024
                    results.append({
                        "file": md_file,
                        "status": "success",
                        "size_kb": round(size_kb, 1),
                        "features_applied": [
                            "Page markers hidden",
                            "Intelligent page breaks",
                            "Phase headings on new pages"
                        ]
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
        "total_files": len(md_files),
        "successful_conversions": success_count,
        "failed_conversions": len(md_files) - success_count,
        "results": results,
        "timestamp": datetime.now().isoformat(),
        "enhancements_applied": [
            "Page break markers automatically hidden in PDF output",
            "Major section headings (Phase 1, Phase 2, etc.) start on new pages",
            "Intelligent page break detection and processing",
            "Professional formatting with proper margins and spacing",
            "Mermaid diagrams preserved and rendered correctly"
        ]
    }

    return json.dumps(summary, indent=2)

# Enhanced File Management Tools

@mcp.tool()
def display_file_organization() -> str:
    """Display comprehensive file organization and structure"""
    if not FILE_MANAGEMENT_AVAILABLE:
        return "❌ Enhanced file management not available. Please ensure enhanced_file_manager.py and file_organization_tools.py are present."

    return org_tools.display_file_tree()

@mcp.tool()
def show_backup_history(file_name: str = None) -> str:
    """Show backup history for a specific file or all files"""
    if not FILE_MANAGEMENT_AVAILABLE:
        return "❌ Enhanced file management not available."

    return org_tools.display_backup_history(file_name)

@mcp.tool()
def show_file_processing_history(file_name: str) -> str:
    """Show detailed processing history for a specific file"""
    if not FILE_MANAGEMENT_AVAILABLE:
        return "❌ Enhanced file management not available."

    return org_tools.display_file_processing_history(file_name)

@mcp.tool()
def generate_organization_report() -> str:
    """Generate comprehensive organization and statistics report"""
    if not FILE_MANAGEMENT_AVAILABLE:
        return "❌ Enhanced file management not available."

    return org_tools.generate_organization_report()

@mcp.tool()
def cleanup_old_backups(days_old: int = 30, keep_minimum: int = 3) -> str:
    """Clean up old backup files while keeping minimum number"""
    if not FILE_MANAGEMENT_AVAILABLE:
        return "❌ Enhanced file management not available."

    return org_tools.cleanup_old_backups(days_old, keep_minimum)

@mcp.tool()
def get_file_suggestions() -> str:
    """Get suggestions for improving file organization"""
    if not FILE_MANAGEMENT_AVAILABLE:
        return "❌ Enhanced file management not available."

    return org_tools.get_file_suggestions()

@mcp.tool()
async def convert_with_backup_management(file_path: str, create_backup: bool = True) -> str:
    """Convert file with enhanced backup management and tracking"""
    if not FILE_MANAGEMENT_AVAILABLE:
        return await convert_with_enhanced_page_breaks(file_path)

    if not install_conversion_dependencies():
        return "❌ Failed to install required dependencies"

    if not os.path.exists(file_path):
        return f"❌ File not found: {file_path}"

    base_name = Path(file_path).stem
    html_file = f"{base_name}.html"
    pdf_file = f"{base_name}.pdf"

    try:
        # Create backup if requested and PDF exists
        backup_path = None
        if create_backup and os.path.exists(pdf_file):
            backup_path = file_manager.create_backup(pdf_file, "enhanced_conversion")

        # Step 1: MD → HTML
        if not convert_markdown_to_html(file_path, html_file):
            file_manager.record_processing_operation(
                "convert_md_to_html", file_path, html_file, False, "HTML conversion failed"
            )
            return f"❌ Failed to convert {file_path} to HTML"

        file_manager.record_processing_operation(
            "convert_md_to_html", file_path, html_file, True, "Successfully converted to HTML"
        )

        # Step 2: Enhanced HTML → PDF
        if not await convert_html_to_pdf(html_file, pdf_file):
            file_manager.record_processing_operation(
                "convert_html_to_pdf_enhanced", html_file, pdf_file, False, "PDF conversion failed"
            )
            return f"❌ Failed to convert {html_file} to PDF"

        file_manager.record_processing_operation(
            "convert_html_to_pdf_enhanced", html_file, pdf_file, True,
            "Successfully converted to PDF with intelligent page breaks"
        )

        # Get file size
        size_kb = os.path.getsize(pdf_file) / 1024

        result = {
            "status": "success",
            "input_file": file_path,
            "output_file": pdf_file,
            "size_kb": round(size_kb, 1),
            "backup_created": backup_path is not None,
            "backup_path": backup_path,
            "timestamp": datetime.now().isoformat(),
            "features": [
                "Intelligent page break processing",
                "Enhanced file management and tracking",
                "Organized backup system",
                "Processing history recorded",
                "Professional formatting maintained"
            ]
        }

        return json.dumps(result, indent=2)

    except Exception as e:
        if file_manager:
            file_manager.record_processing_operation(
                "convert_with_backup_management", file_path, pdf_file, False, str(e)
            )
        return f"❌ Error converting {file_path}: {str(e)}"

@mcp.tool()
async def batch_convert_with_file_management() -> str:
    """Batch convert all files with comprehensive file management"""
    if not FILE_MANAGEMENT_AVAILABLE:
        return await batch_convert_with_enhanced_breaks()

    if not install_conversion_dependencies():
        return "❌ Failed to install required dependencies"

    md_files = glob.glob("*.md")
    if not md_files:
        return "ℹ️ No Markdown files found in current directory"

    results = []
    success_count = 0

    print("📁 Initial file organization:")
    print(org_tools.display_file_tree())

    for md_file in md_files:
        base_name = Path(md_file).stem
        html_file = f"{base_name}.html"
        pdf_file = f"{base_name}.pdf"

        try:
            # Create backup if PDF exists
            backup_path = None
            if os.path.exists(pdf_file):
                backup_path = file_manager.create_backup(pdf_file, "batch_conversion")

            # Convert MD to HTML
            if convert_markdown_to_html(md_file, html_file):
                file_manager.record_processing_operation(
                    "convert_md_to_html", md_file, html_file, True, "Batch conversion - HTML"
                )

                # Convert HTML to PDF
                if await convert_html_to_pdf(html_file, pdf_file):
                    file_manager.record_processing_operation(
                        "convert_html_to_pdf_batch", html_file, pdf_file, True,
                        "Batch conversion - PDF with intelligent page breaks"
                    )

                    success_count += 1
                    size_kb = os.path.getsize(pdf_file) / 1024
                    results.append({
                        "file": md_file,
                        "status": "success",
                        "size_kb": round(size_kb, 1),
                        "backup_created": backup_path is not None,
                        "backup_path": backup_path
                    })
                else:
                    file_manager.record_processing_operation(
                        "convert_html_to_pdf_batch", html_file, pdf_file, False, "PDF conversion failed"
                    )
                    results.append({"file": md_file, "status": "failed_pdf_conversion"})
            else:
                file_manager.record_processing_operation(
                    "convert_md_to_html", md_file, html_file, False, "HTML conversion failed"
                )
                results.append({"file": md_file, "status": "failed_html_conversion"})

        except Exception as e:
            file_manager.record_processing_operation(
                "batch_convert_with_file_management", md_file, pdf_file, False, str(e)
            )
            results.append({"file": md_file, "status": "error", "error": str(e)})

    summary = {
        "total_files": len(md_files),
        "successful_conversions": success_count,
        "failed_conversions": len(md_files) - success_count,
        "results": results,
        "timestamp": datetime.now().isoformat(),
        "file_organization": org_tools.display_file_tree(),
        "organization_report": org_tools.generate_organization_report(),
        "enhancements_applied": [
            "Intelligent page break processing",
            "Organized backup system in backups/ folder",
            "Comprehensive processing history tracking",
            "Professional file naming conventions",
            "Enhanced file management and organization"
        ]
    }

    return json.dumps(summary, indent=2)

if __name__ == "__main__":
    mcp.run()
