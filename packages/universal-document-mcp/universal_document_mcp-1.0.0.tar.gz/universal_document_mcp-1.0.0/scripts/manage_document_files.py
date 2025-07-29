#!/usr/bin/env python3
"""
Document File Management Tool
Standalone tool for managing document processing files, backups, and organization
"""

import sys
import os
from pathlib import Path
from datetime import datetime

try:
    from enhanced_file_manager import EnhancedFileManager
    from file_organization_tools import FileOrganizationTools
except ImportError as e:
    print(f"❌ Error: Could not import required modules: {e}")
    print("Make sure these files are in the current directory:")
    print("  - enhanced_file_manager.py")
    print("  - file_organization_tools.py")
    sys.exit(1)

class DocumentFileManager:
    """Interactive document file management interface"""
    
    def __init__(self):
        self.file_manager = EnhancedFileManager()
        self.org_tools = FileOrganizationTools()
    
    def show_main_menu(self):
        """Display main menu options"""
        print("\n📁 Document File Management Tool")
        print("=" * 40)
        print("1. 📊 Show File Organization")
        print("2. 📦 View Backup History")
        print("3. 📋 Show File Processing History")
        print("4. 📈 Generate Organization Report")
        print("5. 🧹 Cleanup Old Backups")
        print("6. 💡 Get File Suggestions")
        print("7. 🔍 Search Files")
        print("8. 📦 Create Manual Backup")
        print("9. ❌ Exit")
        print()
    
    def handle_file_organization(self):
        """Handle file organization display"""
        print("\n📊 Current File Organization:")
        print("=" * 50)
        print(self.org_tools.display_file_tree())
    
    def handle_backup_history(self):
        """Handle backup history viewing"""
        print("\nBackup History Options:")
        print("1. Show all backups")
        print("2. Show backups for specific file")
        
        choice = input("Enter choice (1-2): ").strip()
        
        if choice == "1":
            print("\n📦 All Backup Files:")
            print("=" * 40)
            print(self.org_tools.display_backup_history())
        elif choice == "2":
            file_name = input("Enter file name: ").strip()
            if file_name:
                print(f"\n📦 Backup History for {file_name}:")
                print("=" * 40)
                print(self.org_tools.display_backup_history(file_name))
            else:
                print("❌ No file name provided")
        else:
            print("❌ Invalid choice")
    
    def handle_processing_history(self):
        """Handle processing history viewing"""
        file_name = input("Enter file name to view processing history: ").strip()
        if file_name:
            print(f"\n📋 Processing History for {file_name}:")
            print("=" * 50)
            print(self.org_tools.display_file_processing_history(file_name))
        else:
            print("❌ No file name provided")
    
    def handle_organization_report(self):
        """Handle organization report generation"""
        print("\n📈 Organization Report:")
        print("=" * 50)
        print(self.org_tools.generate_organization_report())
    
    def handle_cleanup_backups(self):
        """Handle backup cleanup"""
        print("\nBackup Cleanup Options:")
        print("Current defaults: Keep minimum 3 backups, remove files older than 30 days")
        
        use_defaults = input("Use default settings? (y/N): ").strip().lower()
        
        if use_defaults in ['y', 'yes']:
            days_old = 30
            keep_minimum = 3
        else:
            try:
                days_old = int(input("Days old to remove (default 30): ") or "30")
                keep_minimum = int(input("Minimum backups to keep (default 3): ") or "3")
            except ValueError:
                print("❌ Invalid input, using defaults")
                days_old = 30
                keep_minimum = 3
        
        print(f"\n🧹 Cleaning up backups older than {days_old} days (keeping minimum {keep_minimum})...")
        result = self.org_tools.cleanup_old_backups(days_old, keep_minimum)
        print(result)
    
    def handle_file_suggestions(self):
        """Handle file suggestions"""
        print("\n💡 File Organization Suggestions:")
        print("=" * 40)
        print(self.org_tools.get_file_suggestions())
    
    def handle_search_files(self):
        """Handle file searching"""
        print("\nFile Search Options:")
        print("1. List all markdown files")
        print("2. List all PDF files")
        print("3. List all HTML files")
        print("4. List files without backups")
        print("5. List large files (>1MB)")
        
        choice = input("Enter choice (1-5): ").strip()
        
        tree = self.file_manager.get_file_tree()
        
        if choice == "1":
            print("\n📄 Markdown Files:")
            for file_info in tree['working_directory']['markdown_files']:
                backup_status = " 📦" if file_info['has_backups'] else " ⚠️"
                print(f"  ├── {file_info['name']} ({file_info['size_kb']:.1f} KB){backup_status}")
        
        elif choice == "2":
            print("\n📋 PDF Files:")
            for file_info in tree['working_directory']['pdf_files']:
                backup_status = " 📦" if file_info['has_backups'] else " ⚠️"
                print(f"  ├── {file_info['name']} ({file_info['size_kb']:.1f} KB){backup_status}")
        
        elif choice == "3":
            print("\n🌐 HTML Files:")
            for file_info in tree['working_directory']['html_files']:
                backup_status = " 📦" if file_info['has_backups'] else " ⚠️"
                print(f"  ├── {file_info['name']} ({file_info['size_kb']:.1f} KB){backup_status}")
        
        elif choice == "4":
            print("\n⚠️ Files Without Backups:")
            found_any = False
            for file_list in tree['working_directory'].values():
                for file_info in file_list:
                    if not file_info['has_backups']:
                        print(f"  ├── {file_info['name']} ({file_info['size_kb']:.1f} KB)")
                        found_any = True
            if not found_any:
                print("  ✅ All files have backups!")
        
        elif choice == "5":
            print("\n📊 Large Files (>1MB):")
            found_any = False
            for file_list in tree['working_directory'].values():
                for file_info in file_list:
                    if file_info['size_kb'] > 1024:
                        print(f"  ├── {file_info['name']} ({file_info['size_kb']:.1f} KB)")
                        found_any = True
            if not found_any:
                print("  ✅ No large files found!")
        
        else:
            print("❌ Invalid choice")
    
    def handle_manual_backup(self):
        """Handle manual backup creation"""
        file_name = input("Enter file name to backup: ").strip()
        if not file_name:
            print("❌ No file name provided")
            return
        
        if not os.path.exists(file_name):
            print(f"❌ File not found: {file_name}")
            return
        
        try:
            backup_path = self.file_manager.create_backup(file_name, "manual_backup")
            print(f"✅ Backup created successfully!")
            print(f"   Original: {file_name}")
            print(f"   Backup: {backup_path}")
        except Exception as e:
            print(f"❌ Error creating backup: {e}")
    
    def run(self):
        """Run the interactive file management tool"""
        print("🚀 Document File Management Tool")
        print("Manage your document processing files, backups, and organization")
        
        while True:
            self.show_main_menu()
            choice = input("Enter your choice (1-9): ").strip()
            
            if choice == "1":
                self.handle_file_organization()
            elif choice == "2":
                self.handle_backup_history()
            elif choice == "3":
                self.handle_processing_history()
            elif choice == "4":
                self.handle_organization_report()
            elif choice == "5":
                self.handle_cleanup_backups()
            elif choice == "6":
                self.handle_file_suggestions()
            elif choice == "7":
                self.handle_search_files()
            elif choice == "8":
                self.handle_manual_backup()
            elif choice == "9":
                print("\n👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please enter a number from 1-9.")
            
            input("\nPress Enter to continue...")

def main():
    """Main function"""
    try:
        manager = DocumentFileManager()
        manager.run()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()
