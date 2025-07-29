#!/usr/bin/env python3
"""
Apply Page Break Fixes to All Documents
This script applies the page break fixes to all markdown documents in the current directory.
It will regenerate PDFs with:
1. Hidden page break markers
2. Proper page breaks for major sections (Phase headings)
"""

import asyncio
import os
import glob
import sys
from pathlib import Path
from datetime import datetime

# Import our enhanced conversion functions
try:
    from mcp_markdown_pdf_server import convert_markdown_to_html, convert_html_to_pdf
    from enhanced_file_manager import EnhancedFileManager
    from file_organization_tools import FileOrganizationTools
except ImportError as e:
    print(f"❌ Error: Could not import required modules: {e}")
    print("Make sure all required files are in the current directory:")
    print("  - mcp_markdown_pdf_server.py")
    print("  - enhanced_file_manager.py")
    print("  - file_organization_tools.py")
    sys.exit(1)

async def apply_fixes_to_file(md_file: str, file_manager: EnhancedFileManager, backup_existing: bool = True) -> dict:
    """Apply page break fixes to a single markdown file with enhanced file management"""

    base_name = Path(md_file).stem
    html_file = f"{base_name}.html"
    pdf_file = f"{base_name}.pdf"

    result = {
        "file": md_file,
        "status": "unknown",
        "size_kb": 0,
        "backup_created": False,
        "backup_path": None
    }

    try:
        # Create backup using enhanced file manager
        if backup_existing and os.path.exists(pdf_file):
            backup_path = file_manager.create_backup(pdf_file, "intelligent_page_break_fix")
            result["backup_created"] = True
            result["backup_path"] = backup_path
        
        # Convert MD to HTML
        print(f"  🔄 Converting {md_file} to HTML...")
        if not convert_markdown_to_html(md_file, html_file):
            result["status"] = "failed_html_conversion"
            file_manager.record_processing_operation(
                "convert_md_to_html", md_file, html_file, False, "HTML conversion failed"
            )
            return result

        file_manager.record_processing_operation(
            "convert_md_to_html", md_file, html_file, True, "Successfully converted to HTML"
        )

        # Convert HTML to PDF with enhanced processing
        print(f"  🔄 Converting {html_file} to PDF with intelligent page breaks...")
        if not await convert_html_to_pdf(html_file, pdf_file):
            result["status"] = "failed_pdf_conversion"
            file_manager.record_processing_operation(
                "convert_html_to_pdf_intelligent", html_file, pdf_file, False, "PDF conversion failed"
            )
            return result

        file_manager.record_processing_operation(
            "convert_html_to_pdf_intelligent", html_file, pdf_file, True,
            "Successfully converted to PDF with intelligent page breaks"
        )

        # Get file size
        if os.path.exists(pdf_file):
            size_kb = os.path.getsize(pdf_file) / 1024
            result["size_kb"] = round(size_kb, 1)
            result["status"] = "success"
            print(f"  ✅ Generated fixed PDF: {pdf_file} ({size_kb:.1f} KB)")
        else:
            result["status"] = "pdf_not_created"

        return result
        
    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)
        print(f"  ❌ Error processing {md_file}: {e}")
        return result

async def apply_fixes_to_all_documents():
    """Apply page break fixes to all markdown documents with enhanced file management"""

    # Initialize enhanced file management
    file_manager = EnhancedFileManager()
    org_tools = FileOrganizationTools()

    print("🔧 Applying Intelligent Page Break Fixes to All Documents")
    print("=" * 60)
    print("This will fix:")
    print("• Hide page break markers in PDF output")
    print("• Add intelligent page breaks based on content context")
    print("• Prevent orphaned sections (like 'Operational Risks')")
    print("• Optimize visual balance and readability")
    print("• Maintain professional formatting with smart decisions")
    print("• Organize backups in dedicated folders with clear naming")
    print()

    # Show current file organization
    print("📁 Current File Organization:")
    print(org_tools.display_file_tree())
    print()
    
    # Find all markdown files
    md_files = glob.glob("*.md")
    
    if not md_files:
        print("ℹ️ No markdown files found in current directory")
        return
    
    print(f"📄 Found {len(md_files)} markdown files:")
    for md_file in md_files:
        print(f"   • {md_file}")
    print()
    
    # Ask for confirmation
    response = input("Do you want to proceed? This will regenerate all PDFs. (y/N): ")
    if response.lower() not in ['y', 'yes']:
        print("❌ Operation cancelled by user")
        return
    
    print("\n🚀 Starting conversion process...")
    print("=" * 60)
    
    results = []
    success_count = 0
    
    for i, md_file in enumerate(md_files, 1):
        print(f"\n📄 Processing {i}/{len(md_files)}: {md_file}")

        result = await apply_fixes_to_file(md_file, file_manager, backup_existing=True)
        results.append(result)

        if result["status"] == "success":
            success_count += 1
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 CONVERSION SUMMARY")
    print("=" * 60)
    print(f"Total files processed: {len(md_files)}")
    print(f"Successful conversions: {success_count}")
    print(f"Failed conversions: {len(md_files) - success_count}")
    
    if success_count > 0:
        print(f"\n✅ Successfully applied fixes to {success_count} documents!")
        print("\n🎯 Intelligent fixes applied:")
        print("   • Page break markers are now hidden in PDF output")
        print("   • Intelligent page breaks based on content context")
        print("   • Anti-orphan logic prevents awkward section placement")
        print("   • Visual balance optimized for readability")
        print("   • Professional formatting maintained")
        print("   • Mermaid diagrams preserved")
    
    # Show detailed results
    print(f"\n📋 Detailed Results:")
    for result in results:
        status_icon = "✅" if result["status"] == "success" else "❌"
        print(f"   {status_icon} {result['file']}: {result['status']}")
        if result["status"] == "success":
            print(f"      Size: {result['size_kb']} KB")
        if result.get("backup_created"):
            backup_name = Path(result.get('backup_path', '')).name if result.get('backup_path') else 'Created'
            print(f"      Backup: {backup_name}")
        if result.get("error"):
            print(f"      Error: {result['error']}")

    # Show updated file organization
    print(f"\n📁 Updated File Organization:")
    print(org_tools.display_file_tree())

    # Show organization report
    print(f"\n📊 Organization Report:")
    print(org_tools.generate_organization_report())

    print(f"\n🎉 Process completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\n💡 File Management Tips:")
    print(f"   • Backups are organized in the 'backups/' folder")
    print(f"   • Use 'python file_organization_tools.py' to view file status")
    print(f"   • Processing history is tracked for all operations")

def main():
    """Main function"""
    print("🚀 Page Break Fix Application Tool")
    print("This tool will apply the page break fixes to all your markdown documents.")
    print()
    
    # Check if we're in the right directory
    if not os.path.exists("mcp_markdown_pdf_server.py"):
        print("❌ Error: mcp_markdown_pdf_server.py not found in current directory")
        print("Please run this script from the directory containing the MCP server files")
        return False
    
    try:
        asyncio.run(apply_fixes_to_all_documents())
        return True
    except KeyboardInterrupt:
        print("\n❌ Operation cancelled by user")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    main()
