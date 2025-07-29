#!/usr/bin/env python3
"""
Validate Page Break Fixes
This script validates that the page break fixes have been applied correctly by:
1. Checking if page break markers are properly hidden
2. Verifying that major sections have proper page breaks
3. Generating a validation report
"""

import os
import glob
import json
from pathlib import Path
from datetime import datetime

def analyze_markdown_file(md_file: str) -> dict:
    """Analyze a markdown file for page break patterns"""
    
    analysis = {
        "file": md_file,
        "page_break_markers": [],
        "phase_headings": [],
        "issues_found": [],
        "recommendations": []
    }
    
    try:
        with open(md_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        for i, line in enumerate(lines, 1):
            line_stripped = line.strip()
            
            # Check for page break markers
            if 'Page ' in line and ('---' in line or '___' in line):
                analysis["page_break_markers"].append({
                    "line_number": i,
                    "content": line_stripped,
                    "type": "page_marker"
                })
            
            # Check for Phase headings
            if line_stripped.startswith('##') and 'Phase ' in line:
                analysis["phase_headings"].append({
                    "line_number": i,
                    "content": line_stripped,
                    "phase": line_stripped
                })
        
        # Analyze issues
        if analysis["page_break_markers"]:
            analysis["issues_found"].append({
                "type": "visible_page_markers",
                "count": len(analysis["page_break_markers"]),
                "description": "Page break markers found that should be hidden in PDF"
            })
            analysis["recommendations"].append(
                "Apply page break fixes to hide page markers in PDF output"
            )
        
        if analysis["phase_headings"]:
            # Check if phase headings are properly spaced
            phase_issues = []
            for i, phase in enumerate(analysis["phase_headings"]):
                if i > 0:  # Skip first phase
                    prev_phase = analysis["phase_headings"][i-1]
                    line_gap = phase["line_number"] - prev_phase["line_number"]
                    if line_gap < 5:  # Phases too close together
                        phase_issues.append(phase)
            
            if phase_issues:
                analysis["issues_found"].append({
                    "type": "phase_spacing",
                    "count": len(phase_issues),
                    "description": "Phase headings may not have proper page breaks"
                })
                analysis["recommendations"].append(
                    "Apply enhanced page break processing for proper phase separation"
                )
        
        analysis["status"] = "analyzed"
        
    except Exception as e:
        analysis["status"] = "error"
        analysis["error"] = str(e)
    
    return analysis

def check_pdf_exists_and_size(md_file: str) -> dict:
    """Check if corresponding PDF exists and get its properties"""
    
    base_name = Path(md_file).stem
    pdf_file = f"{base_name}.pdf"
    
    pdf_info = {
        "pdf_exists": False,
        "pdf_file": pdf_file,
        "size_kb": 0,
        "last_modified": None
    }
    
    if os.path.exists(pdf_file):
        pdf_info["pdf_exists"] = True
        pdf_info["size_kb"] = round(os.path.getsize(pdf_file) / 1024, 1)
        pdf_info["last_modified"] = datetime.fromtimestamp(
            os.path.getmtime(pdf_file)
        ).isoformat()
    
    return pdf_info

def generate_validation_report():
    """Generate a comprehensive validation report"""
    
    print("🔍 Validating Page Break Fixes")
    print("=" * 50)
    
    # Find all markdown files
    md_files = glob.glob("*.md")
    
    if not md_files:
        print("ℹ️ No markdown files found in current directory")
        return
    
    print(f"📄 Found {len(md_files)} markdown files to analyze")
    
    validation_results = {
        "timestamp": datetime.now().isoformat(),
        "total_files": len(md_files),
        "files_analyzed": 0,
        "files_with_issues": 0,
        "files_with_pdfs": 0,
        "total_page_markers": 0,
        "total_phase_headings": 0,
        "file_analyses": [],
        "summary": {},
        "recommendations": []
    }
    
    print("\n🔄 Analyzing files...")
    
    for md_file in md_files:
        print(f"   📄 Analyzing {md_file}...")
        
        # Analyze markdown content
        analysis = analyze_markdown_file(md_file)
        
        # Check PDF status
        pdf_info = check_pdf_exists_and_size(md_file)
        analysis.update(pdf_info)
        
        validation_results["file_analyses"].append(analysis)
        
        if analysis["status"] == "analyzed":
            validation_results["files_analyzed"] += 1
            
            if analysis["issues_found"]:
                validation_results["files_with_issues"] += 1
            
            if pdf_info["pdf_exists"]:
                validation_results["files_with_pdfs"] += 1
            
            validation_results["total_page_markers"] += len(analysis["page_break_markers"])
            validation_results["total_phase_headings"] += len(analysis["phase_headings"])
    
    # Generate summary
    validation_results["summary"] = {
        "files_needing_fixes": validation_results["files_with_issues"],
        "files_without_pdfs": validation_results["files_analyzed"] - validation_results["files_with_pdfs"],
        "total_issues": sum(len(f["issues_found"]) for f in validation_results["file_analyses"]),
        "fix_success_rate": round(
            (validation_results["files_analyzed"] - validation_results["files_with_issues"]) / 
            max(validation_results["files_analyzed"], 1) * 100, 1
        ) if validation_results["files_analyzed"] > 0 else 0
    }
    
    # Generate recommendations
    if validation_results["files_with_issues"] > 0:
        validation_results["recommendations"].extend([
            f"Apply page break fixes to {validation_results['files_with_issues']} files with issues",
            "Use the enhanced MCP conversion tools to regenerate PDFs",
            "Run apply_page_break_fixes.py to fix all documents at once"
        ])
    
    if validation_results["summary"]["files_without_pdfs"] > 0:
        validation_results["recommendations"].append(
            f"Generate PDFs for {validation_results['summary']['files_without_pdfs']} markdown files"
        )
    
    # Print results
    print("\n" + "=" * 50)
    print("📊 VALIDATION RESULTS")
    print("=" * 50)
    
    print(f"Total files analyzed: {validation_results['files_analyzed']}")
    print(f"Files with PDFs: {validation_results['files_with_pdfs']}")
    print(f"Files with issues: {validation_results['files_with_issues']}")
    print(f"Total page markers found: {validation_results['total_page_markers']}")
    print(f"Total phase headings found: {validation_results['total_phase_headings']}")
    print(f"Fix success rate: {validation_results['summary']['fix_success_rate']}%")
    
    # Show files with issues
    if validation_results["files_with_issues"] > 0:
        print(f"\n⚠️ Files needing fixes:")
        for analysis in validation_results["file_analyses"]:
            if analysis["issues_found"]:
                print(f"   📄 {analysis['file']}:")
                for issue in analysis["issues_found"]:
                    print(f"      • {issue['description']} ({issue['count']} found)")
    
    # Show recommendations
    if validation_results["recommendations"]:
        print(f"\n💡 Recommendations:")
        for i, rec in enumerate(validation_results["recommendations"], 1):
            print(f"   {i}. {rec}")
    
    # Save detailed report
    report_file = f"page_break_validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(validation_results, f, indent=2)
    
    print(f"\n📋 Detailed report saved to: {report_file}")
    
    # Final status
    if validation_results["files_with_issues"] == 0:
        print("\n✅ All files appear to be properly configured!")
        print("   Page break fixes should be working correctly.")
    else:
        print(f"\n⚠️ {validation_results['files_with_issues']} files need attention.")
        print("   Run apply_page_break_fixes.py to fix all issues.")
    
    return validation_results

def main():
    """Main function"""
    print("🔍 Page Break Fix Validation Tool")
    print("This tool validates that page break fixes are working correctly.")
    print()
    
    try:
        results = generate_validation_report()
        return results is not None
    except Exception as e:
        print(f"❌ Error during validation: {e}")
        return False

if __name__ == "__main__":
    main()
