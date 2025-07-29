#!/usr/bin/env python3
"""
Enhanced File Manager for MCP Document Processing
Provides comprehensive file organization, backup management, and version tracking
"""

import os
import shutil
import json
import glob
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict

@dataclass
class FileRecord:
    """Represents a file and its processing history"""
    original_name: str
    current_name: str
    file_type: str  # 'markdown', 'html', 'pdf'
    created_date: str
    last_modified: str
    processing_history: List[Dict]
    backup_files: List[str]
    size_kb: float
    status: str  # 'original', 'processed', 'backup'

@dataclass
class ProcessingRecord:
    """Represents a single processing operation"""
    timestamp: str
    operation: str  # 'backup', 'convert_md_to_html', 'convert_html_to_pdf', 'apply_page_breaks'
    input_file: str
    output_file: str
    success: bool
    details: str

class EnhancedFileManager:
    """Enhanced file management system for document processing"""
    
    def __init__(self, base_directory: str = "."):
        self.base_dir = Path(base_directory)
        self.backups_dir = self.base_dir / "backups"
        self.metadata_file = self.base_dir / ".file_manager_metadata.json"
        self.file_records = {}
        
        # Create directory structure
        self._ensure_directory_structure()
        
        # Load existing metadata
        self._load_metadata()
    
    def _ensure_directory_structure(self):
        """Create necessary directories"""
        self.backups_dir.mkdir(exist_ok=True)
        
        # Create subdirectories for organization
        (self.backups_dir / "pdf").mkdir(exist_ok=True)
        (self.backups_dir / "html").mkdir(exist_ok=True)
        (self.backups_dir / "markdown").mkdir(exist_ok=True)
    
    def _load_metadata(self):
        """Load file metadata from disk"""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.file_records = {
                        name: FileRecord(**record) for name, record in data.items()
                    }
            except Exception as e:
                print(f"Warning: Could not load metadata: {e}")
                self.file_records = {}
    
    def _save_metadata(self):
        """Save file metadata to disk"""
        try:
            data = {
                name: asdict(record) for name, record in self.file_records.items()
            }
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save metadata: {e}")
    
    def create_backup(self, file_path: str, operation: str = "manual_backup") -> str:
        """Create a backup of a file with organized naming"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Determine file type and backup location
        file_ext = file_path.suffix.lower()
        if file_ext == '.pdf':
            backup_subdir = self.backups_dir / "pdf"
        elif file_ext == '.html':
            backup_subdir = self.backups_dir / "html"
        elif file_ext == '.md':
            backup_subdir = self.backups_dir / "markdown"
        else:
            backup_subdir = self.backups_dir
        
        # Generate backup filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{file_path.stem}_backup_{timestamp}{file_ext}"
        backup_path = backup_subdir / backup_name
        
        # Create backup
        shutil.copy2(file_path, backup_path)
        
        # Update metadata
        self._update_file_record(
            str(file_path),
            ProcessingRecord(
                timestamp=datetime.now().isoformat(),
                operation=f"backup_{operation}",
                input_file=str(file_path),
                output_file=str(backup_path),
                success=True,
                details=f"Backup created before {operation}"
            )
        )
        
        print(f"  📦 Backup created: {backup_path}")
        return str(backup_path)
    
    def _update_file_record(self, file_path: str, processing_record: ProcessingRecord):
        """Update file record with processing information"""
        file_path = Path(file_path)
        
        if file_path.name not in self.file_records:
            # Create new record
            self.file_records[file_path.name] = FileRecord(
                original_name=file_path.name,
                current_name=file_path.name,
                file_type=self._get_file_type(file_path),
                created_date=datetime.now().isoformat(),
                last_modified=datetime.now().isoformat(),
                processing_history=[],
                backup_files=[],
                size_kb=0.0,
                status='original'
            )
        
        record = self.file_records[file_path.name]
        
        # Update record
        record.last_modified = datetime.now().isoformat()
        record.processing_history.append(asdict(processing_record))
        
        if processing_record.operation.startswith('backup_'):
            record.backup_files.append(processing_record.output_file)
        
        if file_path.exists():
            record.size_kb = file_path.stat().st_size / 1024
        
        # Update status based on processing history
        if any('convert' in op['operation'] for op in record.processing_history):
            record.status = 'processed'
        
        self._save_metadata()
    
    def _get_file_type(self, file_path: Path) -> str:
        """Determine file type from extension"""
        ext = file_path.suffix.lower()
        if ext == '.md':
            return 'markdown'
        elif ext == '.html':
            return 'html'
        elif ext == '.pdf':
            return 'pdf'
        else:
            return 'other'
    
    def get_file_info(self, file_name: str) -> Optional[FileRecord]:
        """Get information about a file"""
        return self.file_records.get(file_name)
    
    def list_backups(self, file_name: str = None) -> List[Dict]:
        """List backup files, optionally filtered by original file"""
        backups = []
        
        if file_name:
            record = self.file_records.get(file_name)
            if record:
                for backup_path in record.backup_files:
                    if Path(backup_path).exists():
                        backups.append({
                            'original_file': file_name,
                            'backup_path': backup_path,
                            'created': Path(backup_path).stat().st_mtime,
                            'size_kb': Path(backup_path).stat().st_size / 1024
                        })
        else:
            # List all backups
            for record in self.file_records.values():
                for backup_path in record.backup_files:
                    if Path(backup_path).exists():
                        backups.append({
                            'original_file': record.original_name,
                            'backup_path': backup_path,
                            'created': Path(backup_path).stat().st_mtime,
                            'size_kb': Path(backup_path).stat().st_size / 1024
                        })
        
        return sorted(backups, key=lambda x: x['created'], reverse=True)
    
    def get_file_tree(self) -> Dict:
        """Generate a file tree showing organization"""
        tree = {
            'working_directory': {
                'markdown_files': [],
                'html_files': [],
                'pdf_files': []
            },
            'backups': {
                'pdf': [],
                'html': [],
                'markdown': []
            },
            'statistics': {
                'total_files': 0,
                'total_backups': 0,
                'total_size_kb': 0
            }
        }
        
        # Scan working directory
        for pattern, file_list in [
            ('*.md', tree['working_directory']['markdown_files']),
            ('*.html', tree['working_directory']['html_files']),
            ('*.pdf', tree['working_directory']['pdf_files'])
        ]:
            for file_path in self.base_dir.glob(pattern):
                if file_path.is_file():
                    file_info = {
                        'name': file_path.name,
                        'size_kb': file_path.stat().st_size / 1024,
                        'modified': datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
                        'has_backups': file_path.name in self.file_records and len(self.file_records[file_path.name].backup_files) > 0
                    }
                    file_list.append(file_info)
                    tree['statistics']['total_files'] += 1
                    tree['statistics']['total_size_kb'] += file_info['size_kb']
        
        # Scan backup directories
        for backup_type in ['pdf', 'html', 'markdown']:
            backup_dir = self.backups_dir / backup_type
            if backup_dir.exists():
                for file_path in backup_dir.iterdir():
                    if file_path.is_file():
                        file_info = {
                            'name': file_path.name,
                            'size_kb': file_path.stat().st_size / 1024,
                            'created': datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                        }
                        tree['backups'][backup_type].append(file_info)
                        tree['statistics']['total_backups'] += 1
        
        return tree
    
    def cleanup_old_backups(self, days_old: int = 30, keep_minimum: int = 3) -> List[str]:
        """Clean up old backup files while keeping minimum number"""
        removed_files = []
        cutoff_time = datetime.now().timestamp() - (days_old * 24 * 60 * 60)
        
        for record in self.file_records.values():
            # Sort backups by creation time (newest first)
            backup_info = []
            for backup_path in record.backup_files:
                path = Path(backup_path)
                if path.exists():
                    backup_info.append((backup_path, path.stat().st_mtime))
            
            backup_info.sort(key=lambda x: x[1], reverse=True)
            
            # Keep minimum number of backups, remove old ones beyond that
            for i, (backup_path, mtime) in enumerate(backup_info):
                if i >= keep_minimum and mtime < cutoff_time:
                    try:
                        Path(backup_path).unlink()
                        record.backup_files.remove(backup_path)
                        removed_files.append(backup_path)
                    except Exception as e:
                        print(f"Warning: Could not remove {backup_path}: {e}")
        
        if removed_files:
            self._save_metadata()
        
        return removed_files
    
    def record_processing_operation(self, operation: str, input_file: str, 
                                  output_file: str, success: bool, details: str = ""):
        """Record a processing operation in the metadata"""
        processing_record = ProcessingRecord(
            timestamp=datetime.now().isoformat(),
            operation=operation,
            input_file=input_file,
            output_file=output_file,
            success=success,
            details=details
        )
        
        self._update_file_record(input_file, processing_record)
        
        # Also update output file if different
        if input_file != output_file and Path(output_file).exists():
            self._update_file_record(output_file, processing_record)
