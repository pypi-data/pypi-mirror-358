#!/usr/bin/env python3
"""
Validate Mermaid Diagrams
Tests all Mermaid diagrams to ensure they render without syntax errors
"""

import re
import os
import glob
import asyncio
import subprocess
import sys
from pathlib import Path

def install_dependencies():
    """Install required dependencies"""
    try:
        import playwright
        return True
    except ImportError:
        print("Installing Playwright...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "playwright"])
            subprocess.check_call([sys.executable, "-m", "playwright", "install", "chromium"])
            return True
        except Exception as e:
            print(f"Failed to install dependencies: {e}")
            return False

def extract_mermaid_diagrams(md_file):
    """Extract all Mermaid diagrams from a Markdown file"""
    try:
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find all Mermaid code blocks
        mermaid_pattern = r'```mermaid\n(.*?)\n```'
        diagrams = re.findall(mermaid_pattern, content, re.DOTALL)
        
        return diagrams
    except Exception as e:
        print(f"Error reading {md_file}: {e}")
        return []

def create_test_html(diagrams):
    """Create a test HTML file with all diagrams"""
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mermaid Diagram Validation</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10.9.1/dist/mermaid.min.js"></script>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }
        .diagram-container {
            background: white;
            margin: 20px 0;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .diagram-title {
            font-weight: bold;
            margin-bottom: 10px;
            color: #333;
        }
        .mermaid {
            text-align: center;
            margin: 20px 0;
        }
        .error {
            color: red;
            background: #ffe6e6;
            padding: 10px;
            border-radius: 4px;
            margin: 10px 0;
        }
        .success {
            color: green;
            background: #e6ffe6;
            padding: 10px;
            border-radius: 4px;
            margin: 10px 0;
        }
    </style>
</head>
<body>
    <h1>🔍 Mermaid Diagram Validation Test</h1>
    <div id="status">Loading diagrams...</div>
"""
    
    for i, diagram in enumerate(diagrams, 1):
        html_content += f"""
    <div class="diagram-container">
        <div class="diagram-title">Diagram {i}</div>
        <div class="mermaid" id="diagram-{i}">
{diagram}
        </div>
        <div id="status-{i}">Rendering...</div>
    </div>
"""
    
    html_content += """
<script>
    mermaid.initialize({
        startOnLoad: false,
        theme: 'default',
        securityLevel: 'loose',
        fontFamily: 'Arial, sans-serif',
        flowchart: {
            useMaxWidth: true,
            htmlLabels: true
        },
        sequence: {
            useMaxWidth: true
        },
        gantt: {
            useMaxWidth: true
        }
    });
    
    document.addEventListener('DOMContentLoaded', function() {
        console.log('🔍 Starting Mermaid diagram validation...');
        
        const diagrams = document.querySelectorAll('.mermaid');
        let successCount = 0;
        let errorCount = 0;
        
        diagrams.forEach((diagram, index) => {
            const statusDiv = document.getElementById(`status-${index + 1}`);
            
            try {
                // Try to render the diagram
                mermaid.init(undefined, diagram);
                
                // Check if SVG was created
                setTimeout(() => {
                    const svg = diagram.querySelector('svg');
                    if (svg) {
                        statusDiv.innerHTML = '<div class="success">✅ Rendered successfully</div>';
                        successCount++;
                    } else {
                        statusDiv.innerHTML = '<div class="error">❌ No SVG generated</div>';
                        errorCount++;
                    }
                    
                    // Update overall status
                    if (index === diagrams.length - 1) {
                        setTimeout(() => {
                            document.getElementById('status').innerHTML = 
                                `<div class="success">✅ Validation complete: ${successCount} successful, ${errorCount} errors</div>`;
                        }, 1000);
                    }
                }, 2000);
                
            } catch (error) {
                console.error(`Error rendering diagram ${index + 1}:`, error);
                statusDiv.innerHTML = `<div class="error">❌ Syntax error: ${error.message}</div>`;
                errorCount++;
            }
        });
    });
</script>
</body>
</html>"""
    
    return html_content

async def validate_diagrams_in_browser(html_file):
    """Validate diagrams using Playwright browser automation"""
    try:
        from playwright.async_api import async_playwright
        
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            
            # Enable console logging
            page.on("console", lambda msg: print(f"Browser: {msg.text}"))
            
            # Load HTML file
            file_path = Path(html_file).resolve()
            await page.goto(f"file://{file_path}")
            
            # Wait for validation to complete
            await page.wait_for_timeout(10000)  # Wait 10 seconds for all diagrams to render
            
            # Get validation results
            status_text = await page.text_content('#status')
            print(f"Validation Result: {status_text}")
            
            # Count successful renders
            svg_count = await page.evaluate("document.querySelectorAll('.mermaid svg').length")
            total_diagrams = await page.evaluate("document.querySelectorAll('.mermaid').length")
            
            await browser.close()
            
            return svg_count, total_diagrams
            
    except Exception as e:
        print(f"Browser validation error: {e}")
        return 0, 0

def main():
    """Validate all Mermaid diagrams in Markdown files"""
    if not install_dependencies():
        print("❌ Could not install required dependencies")
        return False
    
    print("🔍 MERMAID DIAGRAM VALIDATION")
    print("=" * 50)
    
    # Find all Markdown files
    md_files = glob.glob("*.md")
    
    if not md_files:
        print("❌ No Markdown files found in current directory")
        return False
    
    all_diagrams = []
    file_diagram_counts = {}
    
    # Extract diagrams from all files
    for md_file in md_files:
        if ('TASK_COMPLETION_SUMMARY' in md_file or md_file.startswith('.')):
            continue
        
        print(f"📄 Extracting diagrams from {md_file}...")
        diagrams = extract_mermaid_diagrams(md_file)
        
        if diagrams:
            print(f"  ✅ Found {len(diagrams)} Mermaid diagram(s)")
            all_diagrams.extend(diagrams)
            file_diagram_counts[md_file] = len(diagrams)
        else:
            print(f"  ℹ️ No Mermaid diagrams found")
    
    if not all_diagrams:
        print("❌ No Mermaid diagrams found in any files")
        return False
    
    print(f"\n🎯 Total diagrams to validate: {len(all_diagrams)}")
    print()
    
    # Create test HTML file
    print("📝 Creating validation test file...")
    html_content = create_test_html(all_diagrams)
    test_file = "mermaid_validation_test.html"
    
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"  ✅ Created {test_file}")
    
    # Validate in browser
    print("\n🌐 Running browser validation...")
    svg_count, total_diagrams = asyncio.run(validate_diagrams_in_browser(test_file))
    
    print("\n" + "=" * 50)
    print("🎯 VALIDATION RESULTS")
    print("=" * 50)
    
    for md_file, count in file_diagram_counts.items():
        print(f"📄 {md_file}: {count} diagram(s)")
    
    print(f"\n📊 Overall Results:")
    print(f"   • Total diagrams: {total_diagrams}")
    print(f"   • Successfully rendered: {svg_count}")
    print(f"   • Failed to render: {total_diagrams - svg_count}")
    
    if svg_count == total_diagrams:
        print(f"\n✅ ALL DIAGRAMS VALIDATED SUCCESSFULLY!")
        print(f"🎉 No syntax errors found - all Mermaid diagrams are rendering correctly!")
    else:
        print(f"\n⚠️ Some diagrams failed validation")
        print(f"📋 Check {test_file} in your browser for detailed error information")
    
    # Clean up
    try:
        os.remove(test_file)
        print(f"\n🧹 Cleaned up {test_file}")
    except:
        pass
    
    return svg_count == total_diagrams

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
