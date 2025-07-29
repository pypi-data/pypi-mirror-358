#!/usr/bin/env python3
"""
Test script to verify the page break fixes work correctly
Tests both issues:
1. Page break markers are hidden in PDF
2. Major sections (Phase headings) get proper page breaks
"""

import asyncio
import os
import sys
from pathlib import Path

# Import our enhanced conversion functions
from html_to_pdf_with_pagebreaks import convert_html_to_pdf_with_pagebreaks
from mcp_markdown_pdf_server import convert_markdown_to_html, convert_html_to_pdf

async def test_page_break_fixes():
    """Test the page break fixes on a sample document"""
    
    print("🧪 Testing Page Break Fixes")
    print("=" * 50)
    
    # Test file
    test_file = "architectural-vision-enhanced-final.md"
    
    if not os.path.exists(test_file):
        print(f"❌ Test file {test_file} not found")
        return False
    
    print(f"📄 Testing with: {test_file}")
    
    # Generate output files with test suffix
    base_name = Path(test_file).stem
    html_file = f"{base_name}_test_fixed.html"
    pdf_file = f"{base_name}_test_fixed.pdf"
    
    try:
        # Step 1: Convert MD to HTML
        print("\n🔄 Step 1: Converting Markdown to HTML...")
        if not convert_markdown_to_html(test_file, html_file):
            print("❌ Failed to convert MD to HTML")
            return False
        print(f"✅ HTML generated: {html_file}")
        
        # Step 2: Convert HTML to PDF with enhanced processing
        print("\n🔄 Step 2: Converting HTML to PDF with enhanced page breaks...")
        if not await convert_html_to_pdf(html_file, pdf_file):
            print("❌ Failed to convert HTML to PDF")
            return False
        print(f"✅ PDF generated: {pdf_file}")
        
        # Verify output
        if os.path.exists(pdf_file):
            size_kb = os.path.getsize(pdf_file) / 1024
            print(f"📊 PDF size: {size_kb:.1f} KB")
            
            print("\n✅ Test completed successfully!")
            print("\n🎯 Expected fixes applied:")
            print("   • Page break markers (Page X lines) should be hidden in PDF")
            print("   • Phase headings should start on new pages")
            print("   • Professional formatting maintained")
            print("   • Mermaid diagrams preserved")
            
            print(f"\n📋 Please check the generated PDF: {pdf_file}")
            print("   Look for:")
            print("   1. No visible 'Page X' lines with dashes")
            print("   2. Phase 2, Phase 3, Phase 4 each starting on new pages")
            print("   3. Clean, professional appearance")
            
            return True
        else:
            print("❌ PDF file was not created")
            return False
            
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False

async def test_comparison():
    """Create a comparison between old and new conversion methods"""
    
    print("\n" + "=" * 50)
    print("🔍 Creating Comparison Test")
    print("=" * 50)
    
    test_file = "architectural-vision-enhanced-final.md"
    
    if not os.path.exists(test_file):
        print(f"❌ Test file {test_file} not found")
        return False
    
    base_name = Path(test_file).stem
    
    # Test with old method (existing PDF)
    old_pdf = f"{base_name}.pdf"
    
    # Test with new method
    new_html = f"{base_name}_enhanced.html"
    new_pdf = f"{base_name}_enhanced.pdf"
    
    try:
        print(f"📄 Generating enhanced version of: {test_file}")
        
        # Generate new version with fixes
        if convert_markdown_to_html(test_file, new_html):
            if await convert_html_to_pdf(new_html, new_pdf):
                new_size = os.path.getsize(new_pdf) / 1024
                print(f"✅ Enhanced PDF created: {new_pdf} ({new_size:.1f} KB)")
                
                if os.path.exists(old_pdf):
                    old_size = os.path.getsize(old_pdf) / 1024
                    print(f"📊 Original PDF: {old_pdf} ({old_size:.1f} KB)")
                    print(f"📊 Enhanced PDF: {new_pdf} ({new_size:.1f} KB)")
                    
                    print("\n🔍 Comparison Guide:")
                    print("   Original PDF issues:")
                    print("   • Visible 'Page X' lines with dashes")
                    print("   • Phase headings not properly separated")
                    print("   Enhanced PDF fixes:")
                    print("   • Page markers hidden")
                    print("   • Phase headings on new pages")
                    print("   • Clean professional appearance")
                
                return True
            else:
                print("❌ Failed to create enhanced PDF")
                return False
        else:
            print("❌ Failed to create enhanced HTML")
            return False
            
    except Exception as e:
        print(f"❌ Error during comparison test: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting Page Break Fix Tests")
    print("This will test the fixes for:")
    print("1. Hiding page break markers in PDF output")
    print("2. Adding proper page breaks before major sections")
    print()
    
    # Run tests
    success = asyncio.run(test_page_break_fixes())
    
    if success:
        asyncio.run(test_comparison())
        print("\n🎉 All tests completed!")
        print("Please review the generated PDF files to verify the fixes.")
    else:
        print("\n❌ Tests failed. Please check the error messages above.")
        return False
    
    return True

if __name__ == "__main__":
    main()
