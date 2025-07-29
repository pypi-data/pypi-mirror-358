#!/usr/bin/env python3
"""
Comprehensive Testing and Validation System for AI-Enhanced Document Processing
Tests the enhanced system against existing documents and validates improvements.
"""

import os
import json
import asyncio
import time
from pathlib import Path
from typing import List, Dict, Any, Tuple
from datetime import datetime

# Import both old and new systems for comparison
from mcp_markdown_pdf_server import convert_markdown_to_html, convert_html_to_pdf
from ai_enhanced_mcp_server import ai_enhanced_conversion, ai_analyze_document_structure, ai_generate_smart_page_breaks
from ai_content_parser import AIContentParser
from smart_page_break_engine import SmartPageBreakEngine

class SystemValidator:
    """Validates the AI-enhanced system against the original system"""
    
    def __init__(self):
        self.test_results = []
        self.ai_parser = AIContentParser()
        self.page_break_engine = SmartPageBreakEngine()
        
    async def run_comprehensive_tests(self, test_files: List[str]) -> Dict[str, Any]:
        """Run comprehensive tests on multiple files"""
        print("🧪 Starting Comprehensive AI-Enhanced System Testing...")
        print("=" * 70)
        
        overall_results = {
            "test_timestamp": datetime.now().isoformat(),
            "total_files_tested": len(test_files),
            "individual_results": [],
            "summary_metrics": {},
            "system_comparison": {},
            "validation_status": "pending"
        }
        
        for test_file in test_files:
            if os.path.exists(test_file):
                print(f"\n📄 Testing {test_file}...")
                result = await self.test_single_file(test_file)
                overall_results["individual_results"].append(result)
            else:
                print(f"⚠️  Warning: {test_file} not found, skipping...")
        
        # Calculate summary metrics
        overall_results["summary_metrics"] = self.calculate_summary_metrics(overall_results["individual_results"])
        
        # System comparison
        overall_results["system_comparison"] = self.compare_systems(overall_results["individual_results"])
        
        # Validation status
        overall_results["validation_status"] = self.determine_validation_status(overall_results)
        
        return overall_results
    
    async def test_single_file(self, file_path: str) -> Dict[str, Any]:
        """Test a single file with both systems"""
        base_name = Path(file_path).stem
        
        test_result = {
            "file": file_path,
            "timestamp": datetime.now().isoformat(),
            "original_system": {},
            "ai_enhanced_system": {},
            "ai_analysis": {},
            "improvements": [],
            "issues": [],
            "overall_score": 0.0
        }
        
        try:
            # Test 1: AI Analysis
            print("  🔍 Running AI content analysis...")
            ai_analysis_result = await ai_analyze_document_structure(file_path)
            ai_analysis = json.loads(ai_analysis_result)
            test_result["ai_analysis"] = ai_analysis
            
            if ai_analysis.get("status") == "success":
                print(f"    ✅ Analyzed {ai_analysis['structure_analysis']['total_blocks']} content blocks")
                print(f"    ✅ Found {ai_analysis['structure_analysis']['content_relationships']} relationships")
            
            # Test 2: Smart Page Break Generation
            print("  🎯 Generating smart page breaks...")
            page_breaks_result = await ai_generate_smart_page_breaks(file_path)
            page_breaks = json.loads(page_breaks_result)
            
            if page_breaks.get("status") == "success":
                print(f"    ✅ Generated {page_breaks['page_break_analysis']['total_decisions']} page break decisions")
                print(f"    ✅ {page_breaks['page_break_analysis']['high_confidence']} high-confidence breaks")
            
            # Test 3: Original System Conversion
            print("  📄 Testing original system conversion...")
            original_start = time.time()
            
            # Use existing system
            html_file_orig = f"{base_name}_original.html"
            pdf_file_orig = f"{base_name}_original.pdf"
            
            if convert_markdown_to_html(file_path, html_file_orig):
                if await convert_html_to_pdf(html_file_orig, pdf_file_orig):
                    original_time = time.time() - original_start
                    original_size = os.path.getsize(pdf_file_orig) / 1024
                    
                    test_result["original_system"] = {
                        "status": "success",
                        "conversion_time": round(original_time, 2),
                        "output_file": pdf_file_orig,
                        "size_kb": round(original_size, 1),
                        "features": ["Basic page breaks", "Mermaid support", "Professional formatting"]
                    }
                    print(f"    ✅ Original conversion: {original_size:.1f} KB in {original_time:.2f}s")
                else:
                    test_result["original_system"] = {"status": "failed", "error": "PDF generation failed"}
            else:
                test_result["original_system"] = {"status": "failed", "error": "HTML conversion failed"}
            
            # Test 4: AI-Enhanced System Conversion
            print("  🤖 Testing AI-enhanced system conversion...")
            ai_start = time.time()
            
            ai_result_json = await ai_enhanced_conversion(file_path, use_ai_page_breaks=True)
            ai_result = json.loads(ai_result_json)
            ai_time = time.time() - ai_start
            
            if ai_result.get("status") == "success":
                ai_size = ai_result.get("size_kb", 0)
                test_result["ai_enhanced_system"] = {
                    "status": "success",
                    "conversion_time": round(ai_time, 2),
                    "output_file": ai_result.get("output_file"),
                    "size_kb": ai_size,
                    "features": ai_result.get("features", []),
                    "ai_analysis": ai_result.get("ai_analysis")
                }
                print(f"    ✅ AI-enhanced conversion: {ai_size:.1f} KB in {ai_time:.2f}s")
            else:
                test_result["ai_enhanced_system"] = {"status": "failed", "error": ai_result.get("error")}
            
            # Test 5: Quality Analysis
            test_result["improvements"] = self.analyze_improvements(test_result)
            test_result["issues"] = self.identify_issues(test_result)
            test_result["overall_score"] = self.calculate_quality_score(test_result)
            
            print(f"    📊 Overall quality score: {test_result['overall_score']:.2f}/10")
            
        except Exception as e:
            test_result["error"] = str(e)
            print(f"    ❌ Test failed: {e}")
        
        return test_result
    
    def analyze_improvements(self, test_result: Dict[str, Any]) -> List[str]:
        """Analyze improvements in the AI-enhanced system"""
        improvements = []
        
        original = test_result.get("original_system", {})
        ai_enhanced = test_result.get("ai_enhanced_system", {})
        ai_analysis = test_result.get("ai_analysis", {})
        
        # Check if both systems succeeded
        if original.get("status") == "success" and ai_enhanced.get("status") == "success":
            
            # AI-specific improvements
            if ai_analysis.get("status") == "success":
                structure = ai_analysis.get("structure_analysis", {})
                if structure.get("content_relationships", 0) > 0:
                    improvements.append(f"Identified {structure['content_relationships']} content relationships for better layout")
                
                if structure.get("content_clusters", 0) > 0:
                    improvements.append(f"Created {structure['content_clusters']} content clusters for logical grouping")
                
                if len(ai_analysis.get("high_priority_groups", [])) > 0:
                    improvements.append(f"Identified {len(ai_analysis['high_priority_groups'])} high-priority content groups")
            
            # Page break improvements
            ai_stats = ai_enhanced.get("ai_analysis", {})
            if ai_stats and ai_stats.get("high_confidence_breaks", 0) > 0:
                improvements.append(f"Applied {ai_stats['high_confidence_breaks']} intelligent page breaks")
            
            # Performance comparison
            orig_time = original.get("conversion_time", 0)
            ai_time = ai_enhanced.get("conversion_time", 0)
            if ai_time > 0 and orig_time > 0:
                if ai_time < orig_time * 1.5:  # Within 50% of original time
                    improvements.append("Maintained reasonable conversion performance")
                elif ai_time > orig_time * 2:
                    improvements.append("Note: AI processing adds conversion time for enhanced quality")
            
            # Feature improvements
            ai_features = set(ai_enhanced.get("features", []))
            orig_features = set(original.get("features", []))
            new_features = ai_features - orig_features
            if new_features:
                improvements.append(f"Added new features: {', '.join(new_features)}")
        
        return improvements
    
    def identify_issues(self, test_result: Dict[str, Any]) -> List[str]:
        """Identify potential issues with the AI-enhanced system"""
        issues = []
        
        original = test_result.get("original_system", {})
        ai_enhanced = test_result.get("ai_enhanced_system", {})
        
        # Check for failures
        if original.get("status") == "success" and ai_enhanced.get("status") != "success":
            issues.append("AI-enhanced system failed while original system succeeded")
        
        # Check for significant performance degradation
        orig_time = original.get("conversion_time", 0)
        ai_time = ai_enhanced.get("conversion_time", 0)
        if ai_time > orig_time * 3:  # More than 3x slower
            issues.append(f"Significant performance degradation: {ai_time:.2f}s vs {orig_time:.2f}s")
        
        # Check for file size issues
        orig_size = original.get("size_kb", 0)
        ai_size = ai_enhanced.get("size_kb", 0)
        if ai_size > orig_size * 1.5:  # More than 50% larger
            issues.append(f"Significant file size increase: {ai_size:.1f} KB vs {orig_size:.1f} KB")
        
        # Check AI analysis issues
        ai_analysis = test_result.get("ai_analysis", {})
        if ai_analysis.get("status") != "success":
            issues.append("AI content analysis failed")
        
        return issues
    
    def calculate_quality_score(self, test_result: Dict[str, Any]) -> float:
        """Calculate overall quality score (0-10)"""
        score = 5.0  # Base score
        
        # Success bonus
        if test_result.get("ai_enhanced_system", {}).get("status") == "success":
            score += 2.0
        
        # AI analysis bonus
        if test_result.get("ai_analysis", {}).get("status") == "success":
            score += 1.0
        
        # Improvements bonus
        improvements = len(test_result.get("improvements", []))
        score += min(2.0, improvements * 0.3)
        
        # Issues penalty
        issues = len(test_result.get("issues", []))
        score -= min(3.0, issues * 0.5)
        
        return max(0.0, min(10.0, score))
    
    def calculate_summary_metrics(self, individual_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate summary metrics across all tests"""
        total_tests = len(individual_results)
        successful_tests = len([r for r in individual_results if r.get("ai_enhanced_system", {}).get("status") == "success"])
        
        avg_score = sum(r.get("overall_score", 0) for r in individual_results) / total_tests if total_tests > 0 else 0
        
        total_improvements = sum(len(r.get("improvements", [])) for r in individual_results)
        total_issues = sum(len(r.get("issues", [])) for r in individual_results)
        
        return {
            "success_rate": round(successful_tests / total_tests * 100, 1) if total_tests > 0 else 0,
            "average_quality_score": round(avg_score, 2),
            "total_improvements_identified": total_improvements,
            "total_issues_identified": total_issues,
            "improvement_to_issue_ratio": round(total_improvements / max(1, total_issues), 2)
        }
    
    def compare_systems(self, individual_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Compare original vs AI-enhanced systems"""
        original_successes = len([r for r in individual_results if r.get("original_system", {}).get("status") == "success"])
        ai_successes = len([r for r in individual_results if r.get("ai_enhanced_system", {}).get("status") == "success"])
        
        # Average conversion times
        orig_times = [r.get("original_system", {}).get("conversion_time", 0) for r in individual_results if r.get("original_system", {}).get("conversion_time")]
        ai_times = [r.get("ai_enhanced_system", {}).get("conversion_time", 0) for r in individual_results if r.get("ai_enhanced_system", {}).get("conversion_time")]
        
        avg_orig_time = sum(orig_times) / len(orig_times) if orig_times else 0
        avg_ai_time = sum(ai_times) / len(ai_times) if ai_times else 0
        
        return {
            "original_system_success_rate": round(original_successes / len(individual_results) * 100, 1),
            "ai_enhanced_success_rate": round(ai_successes / len(individual_results) * 100, 1),
            "average_original_conversion_time": round(avg_orig_time, 2),
            "average_ai_enhanced_conversion_time": round(avg_ai_time, 2),
            "performance_overhead": round((avg_ai_time - avg_orig_time) / max(avg_orig_time, 0.1) * 100, 1) if avg_orig_time > 0 else 0
        }
    
    def determine_validation_status(self, overall_results: Dict[str, Any]) -> str:
        """Determine overall validation status"""
        metrics = overall_results.get("summary_metrics", {})
        comparison = overall_results.get("system_comparison", {})
        
        success_rate = metrics.get("success_rate", 0)
        avg_score = metrics.get("average_quality_score", 0)
        improvement_ratio = metrics.get("improvement_to_issue_ratio", 0)
        
        if success_rate >= 90 and avg_score >= 7.0 and improvement_ratio >= 2.0:
            return "EXCELLENT - System significantly improved"
        elif success_rate >= 80 and avg_score >= 6.0 and improvement_ratio >= 1.5:
            return "GOOD - System shows clear improvements"
        elif success_rate >= 70 and avg_score >= 5.0 and improvement_ratio >= 1.0:
            return "ACCEPTABLE - System maintains quality with some improvements"
        elif success_rate >= 50:
            return "NEEDS_IMPROVEMENT - System has issues that need addressing"
        else:
            return "FAILED - System has significant problems"

    def export_test_results(self, results: Dict[str, Any], output_file: str):
        """Export test results to JSON file"""
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

    def print_test_summary(self, results: Dict[str, Any]):
        """Print a comprehensive test summary"""
        print("\n" + "=" * 70)
        print("🎯 AI-ENHANCED SYSTEM VALIDATION SUMMARY")
        print("=" * 70)

        metrics = results.get("summary_metrics", {})
        comparison = results.get("system_comparison", {})

        print(f"\n📊 Overall Results:")
        print(f"   • Files tested: {results['total_files_tested']}")
        print(f"   • Success rate: {metrics.get('success_rate', 0)}%")
        print(f"   • Average quality score: {metrics.get('average_quality_score', 0)}/10")
        print(f"   • Validation status: {results.get('validation_status', 'Unknown')}")

        print(f"\n🔄 System Comparison:")
        print(f"   • Original system success rate: {comparison.get('original_system_success_rate', 0)}%")
        print(f"   • AI-enhanced success rate: {comparison.get('ai_enhanced_success_rate', 0)}%")
        print(f"   • Performance overhead: {comparison.get('performance_overhead', 0)}%")

        print(f"\n✨ Improvements vs Issues:")
        print(f"   • Total improvements identified: {metrics.get('total_improvements_identified', 0)}")
        print(f"   • Total issues identified: {metrics.get('total_issues_identified', 0)}")
        print(f"   • Improvement-to-issue ratio: {metrics.get('improvement_to_issue_ratio', 0)}")

        # Show individual file results
        print(f"\n📄 Individual File Results:")
        for result in results.get("individual_results", []):
            file_name = Path(result["file"]).name
            score = result.get("overall_score", 0)
            status = result.get("ai_enhanced_system", {}).get("status", "unknown")
            improvements = len(result.get("improvements", []))
            issues = len(result.get("issues", []))

            status_icon = "✅" if status == "success" else "❌"
            print(f"   {status_icon} {file_name}: {score:.1f}/10 ({improvements} improvements, {issues} issues)")

        print("\n" + "=" * 70)

async def main():
    """Main testing function"""
    validator = SystemValidator()

    # Define test files (existing markdown files in the directory)
    test_files = [
        "blueprint-ceo.md",
        "COMPLETE_SOLUTION_SUMMARY.md",
        "CRITICAL_PAGE_BREAK_FIXES_COMPLETE.md",
        "INTELLIGENT_PAGE_BREAKS_SOLUTION.md",
        "PAGE_BREAK_FIXES_SUMMARY.md"
    ]

    # Filter to only existing files
    existing_files = [f for f in test_files if os.path.exists(f)]

    if not existing_files:
        print("❌ No test files found! Please ensure markdown files are available.")
        return

    print(f"🧪 Testing AI-Enhanced System with {len(existing_files)} files:")
    for file in existing_files:
        print(f"   • {file}")

    # Run comprehensive tests
    results = await validator.run_comprehensive_tests(existing_files)

    # Export results
    results_file = f"ai_system_validation_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    validator.export_test_results(results, results_file)

    # Print summary
    validator.print_test_summary(results)

    print(f"\n💾 Detailed results exported to: {results_file}")

    # Provide recommendations based on results
    validation_status = results.get("validation_status", "")
    if "EXCELLENT" in validation_status or "GOOD" in validation_status:
        print("\n🎉 RECOMMENDATION: The AI-enhanced system is ready for production use!")
        print("   The system shows significant improvements over the original implementation.")
    elif "ACCEPTABLE" in validation_status:
        print("\n⚠️  RECOMMENDATION: The AI-enhanced system is functional but could be improved.")
        print("   Consider addressing identified issues before full deployment.")
    else:
        print("\n🚨 RECOMMENDATION: The AI-enhanced system needs significant work.")
        print("   Review and fix critical issues before considering deployment.")

if __name__ == "__main__":
    asyncio.run(main())
