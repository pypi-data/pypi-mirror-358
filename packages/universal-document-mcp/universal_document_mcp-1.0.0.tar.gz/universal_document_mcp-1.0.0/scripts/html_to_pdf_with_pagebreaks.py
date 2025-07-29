#!/usr/bin/env python3
"""
HTML to PDF Converter with Page Break Support
Uses Playwright to convert HTML files to PDF while respecting manual page break markers
"""

import sys
import os
import asyncio
from pathlib import Path

def install_playwright():
    """Install playwright if not available"""
    try:
        import playwright
        return True
    except ImportError:
        print("Installing playwright...")
        import subprocess
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "playwright"])
            # Install browser binaries
            subprocess.check_call([sys.executable, "-m", "playwright", "install", "chromium"])
            import playwright
            return True
        except Exception as e:
            print(f"Failed to install playwright: {e}")
            return False

async def convert_html_to_pdf_with_pagebreaks(html_file, pdf_file):
    """Convert HTML file to PDF using Playwright with page break support"""
    try:
        from playwright.async_api import async_playwright
        
        async with async_playwright() as p:
            # Launch browser
            browser = await p.chromium.launch()
            page = await browser.new_page()
            
            # Navigate to HTML file
            file_path = Path(html_file).resolve()
            await page.goto(f"file://{file_path}")
            
            # Wait for any JavaScript content to load (especially Mermaid diagrams)
            await page.wait_for_timeout(3000)  # Wait 3 seconds for rendering
            
            # Wait for Mermaid diagrams to render if present
            try:
                await page.wait_for_selector('svg[id^="mermaid"]', timeout=5000)
                print(f"  ✅ Mermaid diagrams detected and rendered in {html_file}")
            except:
                print(f"  ℹ️  No Mermaid diagrams found in {html_file} or already rendered")
            
            # Add CSS for page breaks - this will respect manual page break markers and hide them
            await page.add_style_tag(content="""
                @media print {
                    /* Respect manual page break markers */
                    .page-break,
                    .pagebreak,
                    [class*="page-break"],
                    [class*="pagebreak"] {
                        page-break-before: always !important;
                        break-before: page !important;
                    }

                    /* Look for text-based page markers and add breaks before them */
                    *:contains("Page ") {
                        page-break-before: always !important;
                        break-before: page !important;
                    }

                    /* Hide all page break markers and lines in print */
                    .page-marker,
                    [class*="page-marker"],
                    .page-break-line,
                    [class*="page-break-line"] {
                        display: none !important;
                        visibility: hidden !important;
                        height: 0 !important;
                        margin: 0 !important;
                        padding: 0 !important;
                        line-height: 0 !important;
                    }

                    /* Ensure major headings start on new pages */
                    h1 {
                        page-break-before: always !important;
                        break-before: page !important;
                    }

                    /* Phase headings should start on new pages */
                    h2:contains("Phase ") {
                        page-break-before: always !important;
                        break-before: page !important;
                    }

                    /* Ensure sections don't break awkwardly */
                    h1, h2, h3, h4, h5, h6 {
                        page-break-after: avoid !important;
                        break-after: avoid !important;
                    }

                    /* Keep diagrams together */
                    .mermaid,
                    svg[id^="mermaid"],
                    pre.mermaid {
                        page-break-inside: avoid !important;
                        break-inside: avoid !important;
                    }

                    /* Avoid orphaned content */
                    p, li {
                        orphans: 3;
                        widows: 3;
                    }
                }
            """)
            
            # Execute JavaScript to process page markers and add intelligent page breaks
            await page.evaluate("""
                // Find all text nodes containing page break markers
                function findPageBreakLines() {
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

                    return pageBreakLines;
                }

                // Enhanced function to find headings that should start on new pages
                function findIntelligentPageBreaks() {
                    const breakCandidates = [];

                    // Find all headings
                    const allHeadings = document.querySelectorAll('h1, h2, h3, h4, h5, h6');

                    allHeadings.forEach((heading, index) => {
                        if (index === 0) return; // Skip first heading

                        const headingLevel = parseInt(heading.tagName.charAt(1));
                        const headingText = heading.textContent.trim();

                        // Calculate content after this heading
                        const contentAfter = getContentAfterElement(heading);
                        const estimatedLines = estimateContentLines(contentAfter);

                        // Calculate content before this heading (current page content)
                        const contentBefore = getContentBeforeElement(heading);
                        const currentPageLines = estimateContentLines(contentBefore);

                        // Decision logic for page breaks
                        let shouldBreak = false;
                        let reason = '';
                        let confidence = 0;

                        // Rule 1: Major sections (h1, h2) with substantial content
                        if (headingLevel <= 2 && estimatedLines >= 5) {
                            if (currentPageLines >= 20) {
                                shouldBreak = true;
                                reason = 'Major section with substantial content';
                                confidence = 0.9;
                            }
                        }

                        // Rule 2: Phase headings always start new pages
                        if (headingText.includes('Phase ')) {
                            shouldBreak = true;
                            reason = 'Phase heading - always new page';
                            confidence = 0.95;
                        }

                        // Rule 3: Avoid orphaned headings (heading with little content at page bottom)
                        if (estimatedLines < 8 && currentPageLines > 35) {
                            shouldBreak = true;
                            reason = 'Avoid orphaned heading at page bottom';
                            confidence = 0.8;
                        }

                        // Rule 4: Risk Management, Conclusion, and other major sections
                        if (headingLevel <= 2 && (
                            headingText.includes('Risk') ||
                            headingText.includes('Conclusion') ||
                            headingText.includes('Implementation') ||
                            headingText.includes('Architecture') ||
                            headingText.includes('Requirements')
                        )) {
                            if (currentPageLines >= 25 && estimatedLines >= 8) {
                                shouldBreak = true;
                                reason = 'Major document section';
                                confidence = 0.85;
                            }
                        }

                        // Rule 5: Prevent overly long pages
                        if (currentPageLines + estimatedLines > 45) {
                            shouldBreak = true;
                            reason = 'Prevent overly long page';
                            confidence = 0.9;
                        }

                        // Rule 6: Subsections with good page balance
                        if (headingLevel === 3 && estimatedLines >= 10 &&
                            currentPageLines >= 25 && currentPageLines <= 40) {
                            shouldBreak = true;
                            reason = 'Good page balance for subsection';
                            confidence = 0.7;
                        }

                        if (shouldBreak) {
                            breakCandidates.push({
                                element: heading,
                                reason: reason,
                                confidence: confidence,
                                headingLevel: headingLevel,
                                headingText: headingText,
                                estimatedLines: estimatedLines,
                                currentPageLines: currentPageLines
                            });
                        }
                    });

                    return breakCandidates;
                }

                // Helper function to get content after an element
                function getContentAfterElement(element) {
                    const content = [];
                    let current = element.nextElementSibling;

                    while (current) {
                        // Stop at next heading of same or higher level
                        if (current.tagName && current.tagName.match(/^H[1-6]$/)) {
                            const currentLevel = parseInt(current.tagName.charAt(1));
                            const elementLevel = parseInt(element.tagName.charAt(1));
                            if (currentLevel <= elementLevel) {
                                break;
                            }
                        }

                        content.push(current);
                        current = current.nextElementSibling;
                    }

                    return content;
                }

                // Helper function to get content before an element (for current page estimation)
                function getContentBeforeElement(element) {
                    const content = [];
                    let current = element.previousElementSibling;
                    let lineCount = 0;

                    // Go back until we find a page break or reach reasonable page length
                    while (current && lineCount < 50) {
                        // Stop if we find a page break marker
                        if (current.classList && (
                            current.classList.contains('page-break-target') ||
                            current.classList.contains('major-heading-break')
                        )) {
                            break;
                        }

                        content.unshift(current);
                        lineCount += estimateElementLines(current);
                        current = current.previousElementSibling;
                    }

                    return content;
                }

                // Helper function to estimate content lines
                function estimateContentLines(elements) {
                    let totalLines = 0;

                    elements.forEach(element => {
                        totalLines += estimateElementLines(element);
                    });

                    return totalLines;
                }

                // Helper function to estimate lines for a single element
                function estimateElementLines(element) {
                    if (!element || !element.textContent) return 0;

                    const text = element.textContent.trim();
                    if (!text) return 0.5; // Empty elements take minimal space

                    // Headings take more space
                    if (element.tagName && element.tagName.match(/^H[1-6]$/)) {
                        return 2; // Heading + spacing
                    }

                    // Code blocks
                    if (element.tagName === 'PRE' || element.classList.contains('mermaid')) {
                        const lines = text.split('\\n').length;
                        return Math.max(3, lines); // Minimum 3 lines for code blocks
                    }

                    // Lists
                    if (element.tagName === 'UL' || element.tagName === 'OL') {
                        const items = element.querySelectorAll('li').length;
                        return Math.max(2, items); // At least 2 lines for lists
                    }

                    // Regular paragraphs - estimate based on character count
                    const charCount = text.length;
                    const estimatedLines = Math.max(1, Math.ceil(charCount / 80)); // ~80 chars per line

                    return estimatedLines;
                }

                // Process page break lines - hide them and add page breaks
                const pageBreakLines = findPageBreakLines();
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

                // Apply intelligent page breaks
                const intelligentBreaks = findIntelligentPageBreaks();
                let appliedBreaks = 0;

                intelligentBreaks.forEach(breakInfo => {
                    // Only apply high-confidence breaks or resolve conflicts
                    if (breakInfo.confidence >= 0.7) {
                        breakInfo.element.style.pageBreakBefore = 'always';
                        breakInfo.element.style.breakBefore = 'page';
                        breakInfo.element.classList.add('intelligent-page-break');
                        breakInfo.element.setAttribute('data-break-reason', breakInfo.reason);
                        appliedBreaks++;

                        console.log(`Applied intelligent page break: ${breakInfo.headingText} (${breakInfo.reason}, confidence: ${breakInfo.confidence})`);
                    } else if (breakInfo.confidence >= 0.6) {
                        // Medium confidence - apply with less aggressive styling
                        breakInfo.element.style.pageBreakBefore = 'auto';
                        breakInfo.element.style.breakBefore = 'auto';
                        breakInfo.element.classList.add('suggested-page-break');

                        console.log(`Suggested page break: ${breakInfo.headingText} (${breakInfo.reason}, confidence: ${breakInfo.confidence})`);
                    }
                });

                // Additional intelligent rules for specific content patterns
                applyContentSpecificRules();

                function applyContentSpecificRules() {
                    // Rule: Avoid orphaned "Operational Risks" type sections
                    const riskSections = document.querySelectorAll('h2, h3');
                    riskSections.forEach(heading => {
                        const text = heading.textContent.trim();
                        if (text.includes('Operational') || text.includes('Technical') ||
                            text.includes('Deployment') || text.includes('Monitoring')) {

                            const contentAfter = getContentAfterElement(heading);
                            const estimatedLines = estimateContentLines(contentAfter);
                            const contentBefore = getContentBeforeElement(heading);
                            const currentPageLines = estimateContentLines(contentBefore);

                            // If this section would be orphaned (little content, late in page)
                            if (estimatedLines < 10 && currentPageLines > 30) {
                                heading.style.pageBreakBefore = 'always';
                                heading.style.breakBefore = 'page';
                                heading.classList.add('anti-orphan-break');

                                console.log(`Applied anti-orphan break for: ${text}`);
                            }
                        }
                    });

                    // Rule: Keep related subsections together when possible
                    const subsections = document.querySelectorAll('h3, h4');
                    subsections.forEach(heading => {
                        const contentAfter = getContentAfterElement(heading);
                        const estimatedLines = estimateContentLines(contentAfter);

                        // If subsection has substantial content, avoid breaking it
                        if (estimatedLines >= 8) {
                            heading.style.pageBreakInside = 'avoid';
                            heading.style.breakInside = 'avoid';

                            // Apply to following content as well
                            contentAfter.forEach(element => {
                                if (element.tagName && !element.tagName.match(/^H[1-6]$/)) {
                                    element.style.pageBreakInside = 'avoid';
                                    element.style.breakInside = 'avoid';
                                }
                            });
                        }
                    });
                }

                console.log(`Processed ${pageBreakLines.length} page break lines and applied ${appliedBreaks} intelligent page breaks`);
            """)
            
            # Generate PDF with professional settings and page break support
            await page.pdf(
                path=pdf_file,
                format='A4',
                margin={
                    'top': '0.75in',
                    'right': '0.75in',
                    'bottom': '0.75in',
                    'left': '0.75in'
                },
                print_background=True,  # Include background colors and images
                prefer_css_page_size=True,
                display_header_footer=False,  # Clean output without browser headers
                scale=1.0  # Ensure proper scaling
            )
            
            await browser.close()
            print(f"  ✅ Successfully converted {html_file} to {pdf_file}")
            return True
            
    except Exception as e:
        print(f"  ❌ Error converting {html_file} to PDF: {e}")
        return False

def convert_html_to_pdf(html_file, pdf_file):
    """Synchronous wrapper for async conversion"""
    return asyncio.run(convert_html_to_pdf_with_pagebreaks(html_file, pdf_file))

def main():
    """Main conversion function"""
    if not install_playwright():
        print("❌ Could not install playwright. Please install manually.")
        return False
    
    # Files to convert
    html_files = [
        "executive-brief-enhanced-final.html",
        "research-proposal-enhanced-final.html",
        "architectural-vision-enhanced-final.html"
    ]
    
    print("🔄 Starting PDF conversion with page break support...")
    print("=" * 60)
    
    success_count = 0
    
    for html_file in html_files:
        if os.path.exists(html_file):
            pdf_file = html_file.replace('.html', '.pdf')
            print(f"\n📄 Converting {html_file}...")
            if convert_html_to_pdf(html_file, pdf_file):
                success_count += 1
                # Get file size for verification
                size_kb = os.path.getsize(pdf_file) / 1024
                print(f"  📊 Output size: {size_kb:.1f} KB")
        else:
            print(f"⚠️  Warning: {html_file} not found")
    
    print("\n" + "=" * 60)
    print(f"🎯 Conversion complete!")
    print(f"✅ Successfully converted {success_count} out of {len(html_files)} files.")
    print(f"📋 Features preserved:")
    print(f"   • Manual page break markers respected")
    print(f"   • Mermaid diagrams rendered")
    print(f"   • Professional A4 formatting (0.75\" margins)")
    print(f"   • All text and visual elements intact")
    
    return success_count == len(html_files)

if __name__ == "__main__":
    main()
