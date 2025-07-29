#!/usr/bin/env python3
"""
MCP Document Validator Integration
Integrates the intelligent document validator with the existing MCP server and PDF conversion pipeline
"""

import asyncio
import json
from typing import Dict, List, Optional
from pathlib import Path
import logging
from datetime import datetime

from intelligent_document_validator import IntelligentDocumentValidator, ValidationReport
from mcp_markdown_pdf_server_clean import batch_convert_all, convert_single_file

logger = logging.getLogger(__name__)

class MCPDocumentValidatorIntegration:
    """Integration layer between document validator and MCP server"""
    
    def __init__(self):
        self.validator = IntelligentDocumentValidator()
        self.validation_history = []
        
    async def validate_before_conversion(self, files: Optional[List[str]] = None) -> Dict:
        """
        Validate documents before PDF conversion
        
        Args:
            files: Optional list of specific files to validate. If None, validates all .md files
            
        Returns:
            Dict with validation results and conversion recommendations
        """
        
        print("🔍 INTELLIGENT DOCUMENT VALIDATION")
        print("=" * 50)
        
        # Run validation
        if files:
            # Validate specific files
            reports = []
            for file_path in files:
                if Path(file_path).exists():
                    report = self.validator.validate_document(file_path)
                    reports.append(report)
                else:
                    logger.warning(f"File not found: {file_path}")
            
            # Create batch report structure
            batch_report = {
                'timestamp': datetime.now().isoformat(),
                'files_processed': len(reports),
                'total_issues': sum(r.total_issues for r in reports),
                'critical_issues': sum(r.critical_issues for r in reports),
                'files_with_issues': len([r for r in reports if r.total_issues > 0]),
                'validation_reports': [self._report_to_dict(r) for r in reports]
            }
        else:
            # Validate all markdown files
            batch_report = self.validator.batch_validate_directory()
        
        # Store validation history
        self.validation_history.append(batch_report)
        
        # Analyze results and provide recommendations
        recommendations = self._analyze_validation_results(batch_report)
        
        return {
            'validation_report': batch_report,
            'recommendations': recommendations,
            'proceed_with_conversion': recommendations['safe_to_proceed'],
            'files_needing_attention': recommendations['critical_files']
        }
    
    def _report_to_dict(self, report: ValidationReport) -> Dict:
        """Convert ValidationReport to dictionary"""
        return {
            'file_path': report.file_path,
            'total_issues': report.total_issues,
            'critical_issues': report.critical_issues,
            'warning_issues': report.warning_issues,
            'info_issues': report.info_issues,
            'issues': [self._issue_to_dict(issue) for issue in report.issues],
            'processing_time': report.processing_time,
            'timestamp': report.timestamp
        }
    
    def _issue_to_dict(self, issue) -> Dict:
        """Convert DuplicateIssue to dictionary"""
        return {
            'file_path': issue.file_path,
            'issue_type': issue.issue_type,
            'severity': issue.severity,
            'line_numbers': issue.line_numbers,
            'content': issue.content,
            'context': issue.context,
            'similarity_score': issue.similarity_score,
            'suggested_action': issue.suggested_action,
            'is_legitimate': issue.is_legitimate,
            'confidence': issue.confidence
        }
    
    def _analyze_validation_results(self, batch_report: Dict) -> Dict:
        """Analyze validation results and provide recommendations"""
        
        critical_files = []
        warning_files = []
        clean_files = []
        
        for report in batch_report['validation_reports']:
            if report['critical_issues'] > 0:
                critical_files.append({
                    'file': report['file_path'],
                    'critical_issues': report['critical_issues'],
                    'total_issues': report['total_issues']
                })
            elif report['warning_issues'] > 0:
                warning_files.append({
                    'file': report['file_path'],
                    'warning_issues': report['warning_issues'],
                    'total_issues': report['total_issues']
                })
            else:
                clean_files.append(report['file_path'])
        
        # Determine if it's safe to proceed
        safe_to_proceed = len(critical_files) == 0
        
        recommendations = {
            'safe_to_proceed': safe_to_proceed,
            'critical_files': critical_files,
            'warning_files': warning_files,
            'clean_files': clean_files,
            'summary': {
                'total_files': batch_report['files_processed'],
                'files_with_critical_issues': len(critical_files),
                'files_with_warnings': len(warning_files),
                'clean_files_count': len(clean_files)
            }
        }
        
        if not safe_to_proceed:
            recommendations['action_required'] = "Critical issues found. Review and fix before PDF conversion."
        elif warning_files:
            recommendations['action_suggested'] = "Warning issues found. Consider reviewing before conversion."
        else:
            recommendations['status'] = "All files passed validation. Safe to proceed with PDF conversion."
        
        return recommendations
    
    async def auto_fix_and_convert(self, files: Optional[List[str]] = None, 
                                 backup: bool = True) -> Dict:
        """
        Auto-fix critical issues and then convert to PDF
        
        Args:
            files: Optional list of specific files to process
            backup: Whether to create backups before fixing
            
        Returns:
            Dict with fix results and conversion results
        """
        
        print("🔧 AUTO-FIX AND CONVERT WORKFLOW")
        print("=" * 40)
        
        # Step 1: Validate documents
        validation_result = await self.validate_before_conversion(files)
        
        if not validation_result['files_needing_attention']:
            print("✅ No critical issues found. Proceeding with conversion...")
            conversion_result = await batch_convert_all()
            return {
                'status': 'success',
                'validation_passed': True,
                'fixes_applied': 0,
                'conversion_result': json.loads(conversion_result) if isinstance(conversion_result, str) else conversion_result
            }
        
        # Step 2: Auto-fix critical issues
        print(f"🔧 Fixing {len(validation_result['files_needing_attention'])} files with critical issues...")
        
        fix_results = []
        for file_info in validation_result['files_needing_attention']:
            file_path = file_info['file']
            print(f"  Fixing: {file_path}")
            
            fix_result = self.validator.auto_fix_critical_issues(file_path, backup=backup)
            fix_results.append({
                'file': file_path,
                'result': fix_result
            })
            
            if fix_result['fixes_applied'] > 0:
                print(f"    ✅ Applied {fix_result['fixes_applied']} fixes")
            else:
                print(f"    ℹ️  No fixes needed")
        
        # Step 3: Re-validate after fixes
        print("\n🔍 Re-validating after fixes...")
        post_fix_validation = await self.validate_before_conversion(files)
        
        # Step 4: Convert to PDF
        if post_fix_validation['proceed_with_conversion']:
            print("\n📄 Converting to PDF...")
            conversion_result = await batch_convert_all()
            
            return {
                'status': 'success',
                'validation_passed': True,
                'fixes_applied': sum(r['result']['fixes_applied'] for r in fix_results),
                'fix_details': fix_results,
                'post_fix_validation': post_fix_validation,
                'conversion_result': json.loads(conversion_result) if isinstance(conversion_result, str) else conversion_result
            }
        else:
            return {
                'status': 'validation_failed',
                'validation_passed': False,
                'fixes_applied': sum(r['result']['fixes_applied'] for r in fix_results),
                'fix_details': fix_results,
                'post_fix_validation': post_fix_validation,
                'message': "Critical issues remain after auto-fix. Manual review required."
            }
    
    async def generate_validation_report(self, output_format: str = 'both') -> Dict:
        """
        Generate comprehensive validation report
        
        Args:
            output_format: 'json', 'markdown', or 'both'
            
        Returns:
            Dict with report file paths and summary
        """
        
        # Run fresh validation
        batch_report = self.validator.batch_validate_directory()
        
        report_files = []
        
        if output_format in ['json', 'both']:
            json_file = f"document_validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(batch_report, f, indent=2, ensure_ascii=False)
            report_files.append(json_file)
        
        if output_format in ['markdown', 'both']:
            markdown_file = self.validator.generate_detailed_report(
                batch_report, 
                f"document_validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )
            report_files.append(markdown_file)
        
        return {
            'report_files': report_files,
            'summary': batch_report,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_validation_history(self) -> List[Dict]:
        """Get history of all validation runs"""
        return self.validation_history
    
    async def health_check(self) -> Dict:
        """Perform a health check of the validation system"""
        
        try:
            # Test validation on a simple document
            test_content = """# Test Document
            
## Section 1
Content here.

## Section 1
Duplicate content here.
"""
            
            test_file = "test_validation.md"
            with open(test_file, 'w', encoding='utf-8') as f:
                f.write(test_content)
            
            # Run validation
            report = self.validator.validate_document(test_file)
            
            # Clean up
            Path(test_file).unlink()
            
            # Check if validation detected the duplicate
            has_duplicates = any(issue.issue_type == 'exact_duplicate' for issue in report.issues)
            
            return {
                'status': 'healthy' if has_duplicates else 'warning',
                'validator_working': has_duplicates,
                'test_issues_found': report.total_issues,
                'message': 'Validation system is working correctly' if has_duplicates else 'Validation may not be detecting duplicates properly'
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'validator_working': False,
                'error': str(e),
                'message': 'Validation system health check failed'
            }

# MCP Server Integration Functions
async def mcp_validate_documents(files: Optional[List[str]] = None) -> str:
    """MCP server function to validate documents"""
    integration = MCPDocumentValidatorIntegration()
    result = await integration.validate_before_conversion(files)
    return json.dumps(result, indent=2)

async def mcp_auto_fix_and_convert(files: Optional[List[str]] = None) -> str:
    """MCP server function to auto-fix and convert documents"""
    integration = MCPDocumentValidatorIntegration()
    result = await integration.auto_fix_and_convert(files)
    return json.dumps(result, indent=2)

async def mcp_generate_validation_report(output_format: str = 'both') -> str:
    """MCP server function to generate validation report"""
    integration = MCPDocumentValidatorIntegration()
    result = await integration.generate_validation_report(output_format)
    return json.dumps(result, indent=2)

async def mcp_health_check() -> str:
    """MCP server function for health check"""
    integration = MCPDocumentValidatorIntegration()
    result = await integration.health_check()
    return json.dumps(result, indent=2)

async def main():
    """Test the integration"""
    integration = MCPDocumentValidatorIntegration()
    
    # Health check
    health = await integration.health_check()
    print(f"Health check: {health['status']}")
    
    # Validation test
    result = await integration.validate_before_conversion()
    print(f"Validation completed: {result['proceed_with_conversion']}")

if __name__ == "__main__":
    asyncio.run(main())
