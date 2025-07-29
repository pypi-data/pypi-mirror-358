#!/usr/bin/env python3
"""
Automated HTML to PDF converter using Playwright for perfect Mermaid rendering.
"""

import asyncio
import sys
from pathlib import Path
from playwright.async_api import async_playwright

async def convert_html_to_pdf(html_file, output_pdf=None):
    """Convert HTML file with Mermaid diagrams to PDF using Playwright."""
    
    html_path = Path(html_file)
    if not html_path.exists():
        print(f"Error: HTML file {html_file} not found")
        return False
    
    if output_pdf is None:
        output_pdf = html_path.with_suffix('.pdf')
    
    output_path = Path(output_pdf)
    
    print(f"Converting {html_file} to {output_pdf}")
    
    try:
        async with async_playwright() as p:
            # Launch browser
            browser = await p.chromium.launch()
            page = await browser.new_page()
            
            # Navigate to HTML file
            file_url = f"file://{html_path.absolute()}"
            await page.goto(file_url)
            
            # Wait for Mermaid diagrams to render
            print("Waiting for Mermaid diagrams to render...")
            await page.wait_for_timeout(3000)  # Wait 3 seconds for diagrams
            
            # Check if Mermaid diagrams are present
            mermaid_elements = await page.query_selector_all('.mermaid svg')
            print(f"Found {len(mermaid_elements)} rendered Mermaid diagrams")
            
            # Generate PDF with proper settings
            print("Generating PDF...")
            await page.pdf(
                path=str(output_path),
                format='A4',
                margin={
                    'top': '0.75in',
                    'right': '0.75in',
                    'bottom': '0.75in',
                    'left': '0.75in'
                },
                print_background=True,
                prefer_css_page_size=True
            )
            
            await browser.close()
            
            print(f"✅ PDF successfully created: {output_path}")
            return True
            
    except Exception as e:
        print(f"Error during conversion: {e}")
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python auto_html_to_pdf.py <input.html> [output.pdf]")
        print("\nConverts HTML with Mermaid diagrams to PDF using browser rendering.")
        sys.exit(1)
    
    html_file = sys.argv[1]
    output_pdf = sys.argv[2] if len(sys.argv) > 2 else None
    
    success = asyncio.run(convert_html_to_pdf(html_file, output_pdf))
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
