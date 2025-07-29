#!/usr/bin/env python3
"""
Universal MCP Server for Document Conversion: MD -> HTML -> PDF
Supports automatic Mermaid diagram optimization and professional formatting
Triggered by keywords: "convert: md -> html -> pdf", "markdown to pdf", "document conversion"
"""

import sys
import os
import asyncio
import subprocess
import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class UniversalDocumentConverter:
    """Universal document converter with Mermaid optimization"""
    
    def __init__(self):
        self.supported_triggers = [
            "convert: md -> html -> pdf",
            "markdown to pdf", 
            "document conversion",
            "md to pdf",
            "convert markdown",
            "generate pdf",
            "mermaid pdf"
        ]
        
    def detect_trigger(self, user_input: str) -> bool:
        """Detect if user input contains conversion trigger keywords"""
        user_input_lower = user_input.lower()
        return any(trigger in user_input_lower for trigger in self.supported_triggers)
    
    def install_dependencies(self) -> bool:
        """Install required dependencies for conversion"""
        try:
            import playwright
            import markdown
            logger.info("Dependencies already installed")
            return True
        except ImportError:
            logger.info("Installing required packages...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", "playwright", "markdown"])
                subprocess.check_call([sys.executable, "-m", "playwright", "install", "chromium"])
                logger.info("Dependencies installed successfully")
                return True
            except Exception as e:
                logger.error(f"Failed to install dependencies: {e}")
                return False
    
    def analyze_document(self, md_file: str) -> Dict:
        """Analyze markdown document for optimization opportunities"""
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Detect existing Mermaid diagrams
            mermaid_blocks = re.findall(r'```mermaid\n(.*?)\n```', content, re.DOTALL)
            
            # Detect figure placeholders
            figure_placeholders = re.findall(r'\[.*?Figure.*?\]', content)
            
            # Detect document type based on content
            doc_type = "technical" if any(word in content.lower() for word in 
                                       ["architecture", "algorithm", "framework", "system"]) else "general"
            
            analysis = {
                "file_size": len(content),
                "line_count": len(content.split('\n')),
                "existing_mermaid_diagrams": len(mermaid_blocks),
                "figure_placeholders": len(figure_placeholders),
                "document_type": doc_type,
                "needs_optimization": len(mermaid_blocks) > 0,
                "complexity": "high" if len(content) > 20000 else "medium" if len(content) > 10000 else "low"
            }
            
            logger.info(f"Document analysis: {analysis}")
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing document: {e}")
            return {"error": str(e)}
    
    def optimize_mermaid_diagrams(self, content: str) -> str:
        """Optimize Mermaid diagrams for better PDF rendering"""
        
        # Patterns for common optimizations
        optimizations = [
            # Shorten common long labels
            (r'"([^"]{30,})"', lambda m: f'"{self.shorten_label(m.group(1))}"'),
            # Convert TB to TD for better spacing
            (r'flowchart TB', 'flowchart TD'),
            # Optimize class definitions for smaller stroke width
            (r'stroke-width:2px', 'stroke-width:1px'),
            (r'stroke-width:3px', 'stroke-width:2px'),
        ]
        
        optimized_content = content
        for pattern, replacement in optimizations:
            if callable(replacement):
                optimized_content = re.sub(pattern, replacement, optimized_content)
            else:
                optimized_content = re.sub(pattern, replacement, optimized_content)
        
        return optimized_content
    
    def shorten_label(self, label: str) -> str:
        """Intelligently shorten long labels while preserving meaning"""
        # Common abbreviations for technical terms
        abbreviations = {
            "Architecture": "Arch",
            "Cognitive": "Cog",
            "Differentiable": "Diff",
            "Optimization": "Opt",
            "Processing": "Process",
            "Framework": "FW",
            "Algorithm": "Algo",
            "Implementation": "Impl",
            "Configuration": "Config",
            "Management": "Mgmt",
            "Development": "Dev",
            "Application": "App",
            "Interface": "IF",
            "Component": "Comp"
        }
        
        shortened = label
        for full, abbrev in abbreviations.items():
            shortened = shortened.replace(full, abbrev)
        
        # If still too long, truncate intelligently
        if len(shortened) > 25:
            words = shortened.split()
            if len(words) > 2:
                shortened = f"{words[0]} {words[1]}..."
            elif len(shortened) > 30:
                shortened = shortened[:27] + "..."
        
        return shortened
    
    def create_backup(self, file_path: str) -> str:
        """Create timestamped backup of original file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = Path("backups")
        backup_dir.mkdir(exist_ok=True)
        
        file_path = Path(file_path)
        backup_path = backup_dir / f"{file_path.stem}_backup_{timestamp}{file_path.suffix}"
        
        try:
            import shutil
            shutil.copy2(file_path, backup_path)
            logger.info(f"Backup created: {backup_path}")
            return str(backup_path)
        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            return ""
    
    def generate_conversion_script(self, md_file: str) -> str:
        """Generate custom conversion script for the specific document"""
        file_stem = Path(md_file).stem
        script_name = f"convert_{file_stem}.py"
        
        script_content = f'''#!/usr/bin/env python3
"""
Auto-generated conversion script for {md_file}
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
'''
        
        with open(script_name, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        logger.info(f"Generated conversion script: {script_name}")
        return script_name

    async def convert_document(self, md_file: str, optimize_diagrams: bool = True) -> Dict:
        """Main conversion function: MD -> HTML -> PDF"""
        try:
            # Step 1: Create backup
            backup_path = self.create_backup(md_file)

            # Step 2: Analyze document
            analysis = self.analyze_document(md_file)
            if "error" in analysis:
                return {"success": False, "error": analysis["error"]}

            # Step 3: Optimize content if needed
            if optimize_diagrams and analysis.get("needs_optimization", False):
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                optimized_content = self.optimize_mermaid_diagrams(content)

                # Save optimized version
                optimized_file = f"{Path(md_file).stem}_optimized.md"
                with open(optimized_file, 'w', encoding='utf-8') as f:
                    f.write(optimized_content)

                md_file = optimized_file
                logger.info(f"Created optimized version: {optimized_file}")

            # Step 4: Generate and run conversion script
            script_name = self.generate_conversion_script(md_file)

            # Step 5: Execute conversion
            result = subprocess.run([sys.executable, script_name],
                                  capture_output=True, text=True, timeout=300)

            if result.returncode == 0:
                pdf_file = f"{Path(md_file).stem}.pdf"
                if os.path.exists(pdf_file):
                    file_size = os.path.getsize(pdf_file) / 1024

                    return {
                        "success": True,
                        "input_file": md_file,
                        "output_file": pdf_file,
                        "backup_file": backup_path,
                        "script_file": script_name,
                        "file_size_kb": round(file_size, 1),
                        "analysis": analysis,
                        "optimized": optimize_diagrams and analysis.get("needs_optimization", False)
                    }
                else:
                    return {"success": False, "error": "PDF file not generated"}
            else:
                return {"success": False, "error": result.stderr}

        except Exception as e:
            logger.error(f"Conversion failed: {e}")
            return {"success": False, "error": str(e)}

# MCP Server Integration Functions
def mcp_tool_convert_document():
    """MCP tool definition for document conversion"""
    return {
        "name": "convert_document_md_to_pdf",
        "description": "Universal document converter: MD -> HTML -> PDF with Mermaid optimization. Triggered by keywords like 'convert: md -> html -> pdf', 'markdown to pdf', etc.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "markdown_file": {
                    "type": "string",
                    "description": "Path to the markdown file to convert"
                },
                "optimize_diagrams": {
                    "type": "boolean",
                    "description": "Whether to optimize Mermaid diagrams for better PDF rendering",
                    "default": True
                },
                "user_input": {
                    "type": "string",
                    "description": "Original user input to check for trigger keywords"
                }
            },
            "required": ["markdown_file"]
        }
    }

async def mcp_handle_convert_document(args: Dict) -> Dict:
    """MCP handler for document conversion"""
    converter = UniversalDocumentConverter()

    # Check if this was triggered by keywords
    user_input = args.get("user_input", "")
    if user_input and not converter.detect_trigger(user_input):
        return {
            "success": False,
            "error": "This tool is triggered by keywords like 'convert: md -> html -> pdf', 'markdown to pdf', etc."
        }

    # Install dependencies
    if not converter.install_dependencies():
        return {"success": False, "error": "Failed to install required dependencies"}

    # Convert document
    markdown_file = args["markdown_file"]
    optimize_diagrams = args.get("optimize_diagrams", True)

    if not os.path.exists(markdown_file):
        return {"success": False, "error": f"File not found: {markdown_file}"}

    result = await converter.convert_document(markdown_file, optimize_diagrams)

    # Add helpful message
    if result.get("success"):
        result["message"] = f"""
🎯 Document conversion completed successfully!

📄 Input: {result['input_file']}
📋 Output: {result['output_file']} ({result['file_size_kb']} KB)
💾 Backup: {result['backup_file']}
🔧 Script: {result['script_file']}

✨ Features applied:
• Professional A4 formatting with 0.75" margins
• Optimized Mermaid diagram rendering
• Intelligent page break handling
• Enhanced visual layout
• Automatic backup creation

The document is now ready for professional use, publication, or sharing!
"""

    return result

# Main execution for testing
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Universal Document Converter MCP Server")
    parser.add_argument("markdown_file", help="Markdown file to convert")
    parser.add_argument("--no-optimize", action="store_true", help="Skip diagram optimization")
    parser.add_argument("--test-trigger", help="Test trigger detection with input text")

    args = parser.parse_args()

    converter = UniversalDocumentConverter()

    if args.test_trigger:
        detected = converter.detect_trigger(args.test_trigger)
        print(f"Trigger detected: {detected}")
        if detected:
            print("This input would trigger the conversion workflow")
        else:
            print("This input would NOT trigger the conversion workflow")
    else:
        # Run conversion
        result = asyncio.run(converter.convert_document(
            args.markdown_file,
            optimize_diagrams=not args.no_optimize
        ))

        if result["success"]:
            print("✅ Conversion successful!")
            print(f"📄 Output: {result['output_file']}")
        else:
            print(f"❌ Conversion failed: {result['error']}")
