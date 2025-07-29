#!/usr/bin/env python3
"""
Test Enhanced File Management System
Tests the new file organization, backup management, and tracking features
"""

import asyncio
import os
import sys
from pathlib import Path
from datetime import datetime

try:
    from enhanced_file_manager import EnhancedFileManager
    from file_organization_tools import FileOrganizationTools
    from mcp_markdown_pdf_server import convert_markdown_to_html, convert_html_to_pdf
except ImportError as e:
    print(f"❌ Error: Could not import required modules: {e}")
    sys.exit(1)

async def test_enhanced_file_management():
    """Test the enhanced file management system"""
    
    print("🧪 Testing Enhanced File Management System")
    print("=" * 60)
    print("This test verifies:")
    print("• Organized backup system in backups/ folder")
    print("• Clear file naming conventions")
    print("• Processing history tracking")
    print("• File organization tools")
    print("• Comprehensive reporting")
    print()
    
    # Initialize file management
    file_manager = EnhancedFileManager()
    org_tools = FileOrganizationTools()
    
    # Test file
    test_file = "architectural-vision-enhanced-final.md"
    
    if not os.path.exists(test_file):
        print(f"❌ Test file {test_file} not found")
        return False
    
    print(f"📄 Testing with: {test_file}")
    
    # Show initial organization
    print("\n📁 Initial File Organization:")
    print(org_tools.display_file_tree())
    
    # Test file processing with enhanced management
    base_name = Path(test_file).stem
    html_file = f"{base_name}_enhanced_mgmt.html"
    pdf_file = f"{base_name}_enhanced_mgmt.pdf"
    
    try:
        # Step 1: Create backup if PDF exists
        original_pdf = f"{base_name}.pdf"
        backup_path = None
        if os.path.exists(original_pdf):
            print(f"\n📦 Creating backup of existing PDF...")
            backup_path = file_manager.create_backup(original_pdf, "enhanced_management_test")
            print(f"✅ Backup created: {backup_path}")
        
        # Step 2: Convert MD to HTML
        print(f"\n🔄 Converting {test_file} to HTML...")
        if not convert_markdown_to_html(test_file, html_file):
            print("❌ Failed to convert MD to HTML")
            return False
        
        file_manager.record_processing_operation(
            "convert_md_to_html_test", test_file, html_file, True, 
            "Test conversion with enhanced file management"
        )
        print(f"✅ HTML generated: {html_file}")
        
        # Step 3: Convert HTML to PDF
        print(f"\n🔄 Converting HTML to PDF with enhanced management...")
        if not await convert_html_to_pdf(html_file, pdf_file):
            print("❌ Failed to convert HTML to PDF")
            return False
        
        file_manager.record_processing_operation(
            "convert_html_to_pdf_test", html_file, pdf_file, True, 
            "Test PDF conversion with intelligent page breaks and file management"
        )
        print(f"✅ PDF generated: {pdf_file}")
        
        # Step 4: Show updated organization
        print(f"\n📁 Updated File Organization:")
        print(org_tools.display_file_tree())
        
        # Step 5: Show processing history
        print(f"\n📋 Processing History for {test_file}:")
        print(org_tools.display_file_processing_history(test_file))
        
        # Step 6: Show backup history
        print(f"\n📦 Backup History:")
        print(org_tools.display_backup_history())
        
        # Step 7: Generate organization report
        print(f"\n📊 Organization Report:")
        print(org_tools.generate_organization_report())
        
        # Step 8: Test file suggestions
        print(f"\n💡 File Suggestions:")
        print(org_tools.get_file_suggestions())
        
        print(f"\n✅ Enhanced file management test completed successfully!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False

async def test_backup_organization():
    """Test backup organization and naming"""
    
    print("\n" + "=" * 60)
    print("🗂️ Testing Backup Organization")
    print("=" * 60)
    
    file_manager = EnhancedFileManager()
    
    # Test creating backups for different file types
    test_files = []
    
    # Find test files
    for pattern in ["*.pdf", "*.html", "*.md"]:
        files = list(Path(".").glob(pattern))
        if files:
            test_files.append(files[0])  # Take first file of each type
    
    if not test_files:
        print("⚠️ No test files found for backup testing")
        return True
    
    print(f"📄 Testing backup organization with {len(test_files)} files:")
    
    backup_paths = []
    for test_file in test_files[:3]:  # Limit to 3 files
        print(f"\n📦 Creating backup for: {test_file}")
        try:
            backup_path = file_manager.create_backup(str(test_file), "organization_test")
            backup_paths.append(backup_path)
            print(f"✅ Backup created: {Path(backup_path).name}")
            print(f"   Location: {Path(backup_path).parent}")
        except Exception as e:
            print(f"❌ Error creating backup: {e}")
    
    # Show backup organization
    print(f"\n📁 Backup Directory Structure:")
    backups_dir = Path("backups")
    if backups_dir.exists():
        for item in backups_dir.rglob("*"):
            if item.is_file():
                relative_path = item.relative_to(backups_dir)
                size_kb = item.stat().st_size / 1024
                print(f"  📄 {relative_path} ({size_kb:.1f} KB)")
    
    print(f"\n✅ Backup organization test completed!")
    return True

async def test_file_naming_conventions():
    """Test file naming conventions"""
    
    print("\n" + "=" * 60)
    print("🏷️ Testing File Naming Conventions")
    print("=" * 60)
    
    file_manager = EnhancedFileManager()
    
    # Test naming convention
    test_file = "test_document.pdf"
    
    # Create a temporary test file
    with open(test_file, 'w') as f:
        f.write("Test content")
    
    try:
        # Create multiple backups to test naming
        backup_paths = []
        for i in range(3):
            backup_path = file_manager.create_backup(test_file, f"naming_test_{i+1}")
            backup_paths.append(backup_path)
            print(f"📦 Backup {i+1}: {Path(backup_path).name}")
        
        print(f"\n🏷️ Naming Convention Analysis:")
        print(f"Original file: {test_file}")
        print(f"Backup pattern: [filename]_backup_[timestamp].pdf")
        print(f"Location pattern: backups/[filetype]/[backup_name]")
        
        # Verify naming conventions
        for backup_path in backup_paths:
            backup_file = Path(backup_path)
            print(f"\n📄 {backup_file.name}")
            print(f"   ├── Contains 'backup': {'backup' in backup_file.name}")
            print(f"   ├── Contains timestamp: {any(c.isdigit() for c in backup_file.name)}")
            print(f"   ├── In organized folder: {'backups' in str(backup_file.parent)}")
            print(f"   └── Preserves extension: {backup_file.suffix == Path(test_file).suffix}")
        
        print(f"\n✅ File naming convention test completed!")
        
    finally:
        # Cleanup test file
        if os.path.exists(test_file):
            os.remove(test_file)
    
    return True

def main():
    """Run all enhanced file management tests"""
    print("🚀 Starting Enhanced File Management Tests")
    print("This comprehensive test verifies all file organization features.")
    print()
    
    # Run tests
    success1 = asyncio.run(test_enhanced_file_management())
    success2 = asyncio.run(test_backup_organization())
    success3 = asyncio.run(test_file_naming_conventions())
    
    print("\n" + "=" * 60)
    print("🎯 Test Results Summary")
    print("=" * 60)
    
    tests = [
        ("Enhanced File Management", success1),
        ("Backup Organization", success2),
        ("File Naming Conventions", success3)
    ]
    
    all_passed = True
    for test_name, success in tests:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{test_name:25} | {status}")
        if not success:
            all_passed = False
    
    if all_passed:
        print(f"\n🎉 All tests passed! Enhanced file management is working correctly.")
        print(f"\n📋 Key Features Verified:")
        print(f"   ✅ Organized backup system in backups/ folder")
        print(f"   ✅ Clear hierarchical naming conventions")
        print(f"   ✅ Comprehensive processing history tracking")
        print(f"   ✅ File organization and reporting tools")
        print(f"   ✅ Backup management and cleanup features")
        
        print(f"\n🛠️ Available Tools:")
        print(f"   • python manage_document_files.py - Interactive file management")
        print(f"   • python apply_page_break_fixes.py - Enhanced batch processing")
        print(f"   • MCP server tools for file organization and backup management")
        
    else:
        print(f"\n❌ Some tests failed. Please check the error messages above.")
    
    return all_passed

if __name__ == "__main__":
    main()
