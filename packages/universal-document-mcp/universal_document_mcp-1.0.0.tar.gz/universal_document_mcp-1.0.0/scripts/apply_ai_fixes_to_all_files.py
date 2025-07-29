#!/usr/bin/env python3
"""
Apply AI-Enhanced Fixes to All Existing Markdown Files
Processes all markdown files in the directory with the new AI-enhanced system
"""

import os
import glob
import asyncio
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# Import the AI-enhanced system
from ai_enhanced_mcp_server import batch_ai_enhanced_conversion, ai_enhanced_conversion

class BatchAIProcessor:
    """Batch processor for applying AI fixes to all markdown files"""
    
    def __init__(self):
        self.processed_files = []
        self.failed_files = []
        self.start_time = None
        
    async def process_all_markdown_files(self) -> Dict[str, Any]:
        """Process all markdown files in the directory with AI enhancements"""
        
        print("🚀 Starting AI-Enhanced Batch Processing of All Markdown Files")
        print("=" * 80)
        
        self.start_time = datetime.now()
        
        # Find all markdown files
        markdown_files = self._find_all_markdown_files()
        
        if not markdown_files:
            return {
                "status": "no_files",
                "message": "No markdown files found to process"
            }
        
        print(f"📄 Found {len(markdown_files)} markdown files to process:")
        for i, file in enumerate(markdown_files, 1):
            print(f"   {i:2d}. {file}")
        
        print(f"\n🤖 Processing with AI-Enhanced System...")
        print("-" * 80)
        
        # Process each file
        results = []
        for i, file_path in enumerate(markdown_files, 1):
            print(f"\n📄 Processing {i}/{len(markdown_files)}: {file_path}")
            result = await self._process_single_file(file_path)
            results.append(result)
            
            if result["status"] == "success":
                self.processed_files.append(file_path)
                print(f"   ✅ Success: {result['output_file']} ({result['size_kb']} KB)")
                if result.get("ai_analysis"):
                    ai_stats = result["ai_analysis"]
                    print(f"   🧠 AI Analysis: {ai_stats.get('content_blocks', 0)} blocks, {ai_stats.get('relationships', 0)} relationships")
            else:
                self.failed_files.append(file_path)
                print(f"   ❌ Failed: {result.get('error', 'Unknown error')}")
        
        # Generate summary
        summary = self._generate_summary(results)
        
        # Export detailed results
        self._export_results(results, summary)
        
        # Print final summary
        self._print_final_summary(summary)
        
        return summary
    
    def _find_all_markdown_files(self) -> List[str]:
        """Find all markdown files in the current directory"""
        
        # Get all .md files in current directory
        md_files = glob.glob("*.md")
        
        # Filter out temporary and backup files
        filtered_files = []
        exclude_patterns = [
            "_backup_",
            "_temp_",
            "_test_",
            "AI_ENHANCED_",
            "AI_SYSTEM_",
            "PROJECT_COMPLETION_"
        ]
        
        for file in md_files:
            # Skip if file matches exclude patterns
            if any(pattern in file for pattern in exclude_patterns):
                continue
            
            # Skip if file is in INFO directory
            if file.startswith("INFO"):
                continue
                
            filtered_files.append(file)
        
        return sorted(filtered_files)
    
    async def _process_single_file(self, file_path: str) -> Dict[str, Any]:
        """Process a single markdown file with AI enhancements"""
        
        try:
            # Use AI-enhanced conversion
            result_json = await ai_enhanced_conversion(file_path, use_ai_page_breaks=True)
            result = json.loads(result_json)
            
            # Add processing metadata
            result["processed_at"] = datetime.now().isoformat()
            result["original_file"] = file_path
            
            return result
            
        except Exception as e:
            return {
                "status": "failed",
                "original_file": file_path,
                "error": str(e),
                "processed_at": datetime.now().isoformat()
            }
    
    def _generate_summary(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate processing summary"""
        
        total_files = len(results)
        successful = len([r for r in results if r.get("status") == "success"])
        failed = total_files - successful
        
        # Calculate total processing time
        end_time = datetime.now()
        total_time = (end_time - self.start_time).total_seconds()
        
        # Calculate total output size
        total_size_kb = sum(r.get("size_kb", 0) for r in results if r.get("status") == "success")
        
        # AI analysis statistics
        total_blocks = sum(r.get("ai_analysis", {}).get("content_blocks", 0) for r in results if r.get("ai_analysis"))
        total_relationships = sum(r.get("ai_analysis", {}).get("relationships", 0) for r in results if r.get("ai_analysis"))
        total_clusters = sum(r.get("ai_analysis", {}).get("clusters", 0) for r in results if r.get("ai_analysis"))
        total_decisions = sum(r.get("ai_analysis", {}).get("page_break_decisions", 0) for r in results if r.get("ai_analysis"))
        
        return {
            "batch_processing_summary": {
                "start_time": self.start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "total_processing_time_seconds": round(total_time, 2),
                "total_files_processed": total_files,
                "successful_conversions": successful,
                "failed_conversions": failed,
                "success_rate_percent": round((successful / total_files * 100), 1) if total_files > 0 else 0,
                "total_output_size_kb": round(total_size_kb, 1)
            },
            "ai_analysis_summary": {
                "total_content_blocks_analyzed": total_blocks,
                "total_relationships_identified": total_relationships,
                "total_content_clusters_created": total_clusters,
                "total_page_break_decisions": total_decisions,
                "average_blocks_per_document": round(total_blocks / successful, 1) if successful > 0 else 0,
                "average_relationships_per_document": round(total_relationships / successful, 1) if successful > 0 else 0
            },
            "file_results": results,
            "processed_files": self.processed_files,
            "failed_files": self.failed_files
        }
    
    def _export_results(self, results: List[Dict[str, Any]], summary: Dict[str, Any]):
        """Export detailed results to JSON file"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"ai_batch_processing_results_{timestamp}.json"
        
        export_data = {
            "batch_processing_metadata": {
                "processed_at": datetime.now().isoformat(),
                "system_version": "AI-Enhanced Document Processing v1.0",
                "processing_mode": "AI-Enhanced with Smart Page Breaks"
            },
            "summary": summary,
            "detailed_results": results
        }
        
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Detailed results exported to: {results_file}")
    
    def _print_final_summary(self, summary: Dict[str, Any]):
        """Print comprehensive final summary"""
        
        batch_summary = summary["batch_processing_summary"]
        ai_summary = summary["ai_analysis_summary"]
        
        print("\n" + "=" * 80)
        print("🎯 AI-ENHANCED BATCH PROCESSING COMPLETE")
        print("=" * 80)
        
        print(f"\n📊 Processing Summary:")
        print(f"   • Total files processed: {batch_summary['total_files_processed']}")
        print(f"   • Successful conversions: {batch_summary['successful_conversions']}")
        print(f"   • Failed conversions: {batch_summary['failed_conversions']}")
        print(f"   • Success rate: {batch_summary['success_rate_percent']}%")
        print(f"   • Total processing time: {batch_summary['total_processing_time_seconds']}s")
        print(f"   • Total output size: {batch_summary['total_output_size_kb']} KB")
        
        print(f"\n🧠 AI Analysis Summary:")
        print(f"   • Content blocks analyzed: {ai_summary['total_content_blocks_analyzed']}")
        print(f"   • Relationships identified: {ai_summary['total_relationships_identified']}")
        print(f"   • Content clusters created: {ai_summary['total_content_clusters_created']}")
        print(f"   • Page break decisions: {ai_summary['total_page_break_decisions']}")
        print(f"   • Avg blocks per document: {ai_summary['average_blocks_per_document']}")
        print(f"   • Avg relationships per document: {ai_summary['average_relationships_per_document']}")
        
        if self.processed_files:
            print(f"\n✅ Successfully Processed Files:")
            for file in self.processed_files:
                output_file = f"{Path(file).stem}_ai_enhanced.pdf"
                print(f"   • {file} → {output_file}")
        
        if self.failed_files:
            print(f"\n❌ Failed Files:")
            for file in self.failed_files:
                print(f"   • {file}")
        
        print("\n" + "=" * 80)
        
        # Final recommendation
        success_rate = batch_summary['success_rate_percent']
        if success_rate >= 95:
            print("🎉 EXCELLENT: All files processed successfully with AI enhancements!")
        elif success_rate >= 80:
            print("✅ GOOD: Most files processed successfully. Review failed files if any.")
        else:
            print("⚠️  WARNING: Some files failed processing. Review errors and retry.")
        
        print("🚀 AI-enhanced PDFs are ready for use!")

async def main():
    """Main function to process all markdown files"""
    
    processor = BatchAIProcessor()
    
    print("🤖 AI-Enhanced Document Processing System")
    print("Applying intelligent fixes to ALL existing markdown files...")
    print()
    
    # Process all files
    summary = await processor.process_all_markdown_files()
    
    # Check if we should continue
    if summary.get("status") == "no_files":
        print("❌ No markdown files found to process!")
        return
    
    # Success message
    batch_summary = summary["batch_processing_summary"]
    if batch_summary["success_rate_percent"] >= 95:
        print(f"\n🎉 SUCCESS: AI fixes applied to {batch_summary['successful_conversions']} files!")
        print("All documents now have intelligent page breaks and enhanced layout.")
    else:
        print(f"\n⚠️  PARTIAL SUCCESS: {batch_summary['successful_conversions']} files processed successfully.")
        print("Some files may need manual review.")

if __name__ == "__main__":
    asyncio.run(main())
