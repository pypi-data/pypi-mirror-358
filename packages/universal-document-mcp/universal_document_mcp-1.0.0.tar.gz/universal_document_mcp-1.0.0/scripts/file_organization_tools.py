#!/usr/bin/env python3
"""
File Organization Tools for MCP Document Processing
Provides comprehensive file management, backup viewing, and organization utilities
"""

import os
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List
from enhanced_file_manager import EnhancedFileManager

class FileOrganizationTools:
    """Tools for managing and organizing document processing files"""
    
    def __init__(self, base_directory: str = "."):
        self.file_manager = EnhancedFileManager(base_directory)
    
    def display_file_tree(self) -> str:
        """Display a comprehensive file tree"""
        tree = self.file_manager.get_file_tree()
        
        output = []
        output.append("📁 Document Processing File Tree")
        output.append("=" * 50)
        
        # Working Directory
        output.append("\n📂 Working Directory")
        output.append("├── 📄 Markdown Files:")
        for file_info in tree['working_directory']['markdown_files']:
            backup_indicator = " 📦" if file_info['has_backups'] else ""
            output.append(f"│   ├── {file_info['name']} ({file_info['size_kb']:.1f} KB){backup_indicator}")
        
        output.append("├── 🌐 HTML Files:")
        for file_info in tree['working_directory']['html_files']:
            backup_indicator = " 📦" if file_info['has_backups'] else ""
            output.append(f"│   ├── {file_info['name']} ({file_info['size_kb']:.1f} KB){backup_indicator}")
        
        output.append("└── 📋 PDF Files:")
        for file_info in tree['working_directory']['pdf_files']:
            backup_indicator = " 📦" if file_info['has_backups'] else ""
            output.append(f"    ├── {file_info['name']} ({file_info['size_kb']:.1f} KB){backup_indicator}")
        
        # Backup Directory
        output.append("\n📦 Backups Directory")
        output.append("├── 📋 PDF Backups:")
        for backup in tree['backups']['pdf']:
            output.append(f"│   ├── {backup['name']} ({backup['size_kb']:.1f} KB)")
        
        output.append("├── 🌐 HTML Backups:")
        for backup in tree['backups']['html']:
            output.append(f"│   ├── {backup['name']} ({backup['size_kb']:.1f} KB)")
        
        output.append("└── 📄 Markdown Backups:")
        for backup in tree['backups']['markdown']:
            output.append(f"    ├── {backup['name']} ({backup['size_kb']:.1f} KB)")
        
        # Statistics
        stats = tree['statistics']
        output.append(f"\n📊 Statistics")
        output.append(f"├── Total Files: {stats['total_files']}")
        output.append(f"├── Total Backups: {stats['total_backups']}")
        output.append(f"└── Total Size: {stats['total_size_kb']:.1f} KB")
        
        return "\n".join(output)
    
    def display_backup_history(self, file_name: str = None) -> str:
        """Display backup history for a file or all files"""
        backups = self.file_manager.list_backups(file_name)
        
        if not backups:
            return f"No backups found{' for ' + file_name if file_name else ''}."
        
        output = []
        if file_name:
            output.append(f"📦 Backup History for: {file_name}")
        else:
            output.append("📦 All Backup Files")
        output.append("=" * 50)
        
        current_file = None
        for backup in backups:
            if backup['original_file'] != current_file:
                current_file = backup['original_file']
                output.append(f"\n📄 {current_file}")
            
            created_date = datetime.fromtimestamp(backup['created']).strftime("%Y-%m-%d %H:%M:%S")
            backup_name = Path(backup['backup_path']).name
            output.append(f"  ├── {backup_name}")
            output.append(f"  │   ├── Created: {created_date}")
            output.append(f"  │   └── Size: {backup['size_kb']:.1f} KB")
        
        return "\n".join(output)
    
    def display_file_processing_history(self, file_name: str) -> str:
        """Display processing history for a specific file"""
        record = self.file_manager.get_file_info(file_name)
        
        if not record:
            return f"No processing history found for: {file_name}"
        
        output = []
        output.append(f"📋 Processing History: {file_name}")
        output.append("=" * 50)
        output.append(f"Original Name: {record.original_name}")
        output.append(f"Current Name: {record.current_name}")
        output.append(f"File Type: {record.file_type}")
        output.append(f"Status: {record.status}")
        output.append(f"Size: {record.size_kb:.1f} KB")
        output.append(f"Created: {record.created_date}")
        output.append(f"Last Modified: {record.last_modified}")
        
        if record.processing_history:
            output.append(f"\n🔄 Processing Operations:")
            for i, operation in enumerate(record.processing_history, 1):
                timestamp = datetime.fromisoformat(operation['timestamp']).strftime("%Y-%m-%d %H:%M:%S")
                status = "✅" if operation['success'] else "❌"
                output.append(f"  {i}. {status} {operation['operation']} ({timestamp})")
                output.append(f"     Input: {Path(operation['input_file']).name}")
                output.append(f"     Output: {Path(operation['output_file']).name}")
                if operation['details']:
                    output.append(f"     Details: {operation['details']}")
        
        if record.backup_files:
            output.append(f"\n📦 Backup Files ({len(record.backup_files)}):")
            for backup_path in record.backup_files:
                if Path(backup_path).exists():
                    backup_name = Path(backup_path).name
                    size_kb = Path(backup_path).stat().st_size / 1024
                    output.append(f"  ├── {backup_name} ({size_kb:.1f} KB)")
                else:
                    output.append(f"  ├── {Path(backup_path).name} (missing)")
        
        return "\n".join(output)
    
    def generate_organization_report(self) -> str:
        """Generate a comprehensive organization report"""
        tree = self.file_manager.get_file_tree()
        
        output = []
        output.append("📊 Document Processing Organization Report")
        output.append("=" * 60)
        output.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Summary Statistics
        stats = tree['statistics']
        output.append(f"\n📈 Summary Statistics")
        output.append(f"├── Working Files: {stats['total_files']}")
        output.append(f"├── Backup Files: {stats['total_backups']}")
        output.append(f"├── Total Storage: {stats['total_size_kb']:.1f} KB")
        output.append(f"└── Backup Ratio: {stats['total_backups'] / max(stats['total_files'], 1):.1f} backups per file")
        
        # File Type Breakdown
        output.append(f"\n📁 File Type Breakdown")
        md_count = len(tree['working_directory']['markdown_files'])
        html_count = len(tree['working_directory']['html_files'])
        pdf_count = len(tree['working_directory']['pdf_files'])
        
        output.append(f"├── Markdown Files: {md_count}")
        output.append(f"├── HTML Files: {html_count}")
        output.append(f"└── PDF Files: {pdf_count}")
        
        # Backup Status
        output.append(f"\n📦 Backup Status")
        files_with_backups = 0
        for file_list in tree['working_directory'].values():
            files_with_backups += sum(1 for f in file_list if f['has_backups'])
        
        backup_coverage = files_with_backups / max(stats['total_files'], 1) * 100
        output.append(f"├── Files with Backups: {files_with_backups}/{stats['total_files']}")
        output.append(f"├── Backup Coverage: {backup_coverage:.1f}%")
        
        # Recommendations
        output.append(f"\n💡 Recommendations")
        if backup_coverage < 50:
            output.append("├── ⚠️  Low backup coverage - consider backing up more files")
        else:
            output.append("├── ✅ Good backup coverage")
        
        if stats['total_backups'] > stats['total_files'] * 5:
            output.append("├── ⚠️  Many backup files - consider cleanup")
        else:
            output.append("├── ✅ Reasonable backup count")
        
        # Recent Activity
        all_records = [record for record in self.file_manager.file_records.values() 
                      if record.processing_history]
        
        if all_records:
            recent_operations = []
            for record in all_records:
                for op in record.processing_history[-3:]:  # Last 3 operations
                    recent_operations.append((record.original_name, op))
            
            recent_operations.sort(key=lambda x: x[1]['timestamp'], reverse=True)
            
            output.append(f"\n🕒 Recent Activity (Last 5 operations)")
            for i, (file_name, op) in enumerate(recent_operations[:5]):
                timestamp = datetime.fromisoformat(op['timestamp']).strftime("%m-%d %H:%M")
                status = "✅" if op['success'] else "❌"
                output.append(f"├── {status} {op['operation']} on {file_name} ({timestamp})")
        
        return "\n".join(output)
    
    def cleanup_old_backups(self, days_old: int = 30, keep_minimum: int = 3) -> str:
        """Clean up old backup files"""
        removed_files = self.file_manager.cleanup_old_backups(days_old, keep_minimum)
        
        if not removed_files:
            return f"No backup files older than {days_old} days found for cleanup."
        
        output = []
        output.append(f"🧹 Backup Cleanup Complete")
        output.append("=" * 40)
        output.append(f"Removed {len(removed_files)} old backup files:")
        
        for file_path in removed_files:
            output.append(f"  ├── {Path(file_path).name}")
        
        output.append(f"\nCleanup criteria:")
        output.append(f"├── Older than: {days_old} days")
        output.append(f"└── Kept minimum: {keep_minimum} backups per file")
        
        return "\n".join(output)
    
    def get_file_suggestions(self) -> str:
        """Provide suggestions for file organization"""
        tree = self.file_manager.get_file_tree()
        suggestions = []
        
        # Check for files without backups
        files_without_backups = []
        for file_list in tree['working_directory'].values():
            for file_info in file_list:
                if not file_info['has_backups']:
                    files_without_backups.append(file_info['name'])
        
        if files_without_backups:
            suggestions.append(f"📦 Consider backing up {len(files_without_backups)} files without backups")
        
        # Check for large files
        large_files = []
        for file_list in tree['working_directory'].values():
            for file_info in file_list:
                if file_info['size_kb'] > 1000:  # > 1MB
                    large_files.append(file_info['name'])
        
        if large_files:
            suggestions.append(f"📊 {len(large_files)} large files detected - monitor storage usage")
        
        # Check backup count
        if tree['statistics']['total_backups'] > tree['statistics']['total_files'] * 10:
            suggestions.append("🧹 Consider cleaning up old backups to save space")
        
        if not suggestions:
            suggestions.append("✅ File organization looks good!")
        
        return "\n".join(suggestions)
