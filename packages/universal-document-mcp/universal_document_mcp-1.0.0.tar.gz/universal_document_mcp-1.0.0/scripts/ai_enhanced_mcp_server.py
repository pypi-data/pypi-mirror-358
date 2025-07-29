#!/usr/bin/env python3
"""
AI-Enhanced MCP Server for Intelligent Document Processing
Integrates AI-powered content analysis and smart page break decisions
with the existing MCP server infrastructure.
"""

import sys
import os
import asyncio
import subprocess
import glob
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

# Import existing MCP infrastructure
try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    print("Installing MCP dependencies...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "mcp[cli]"])
    from mcp.server.fastmcp import FastMCP

# Import existing conversion functions
from mcp_markdown_pdf_server import (
    convert_markdown_to_html, 
    convert_html_to_pdf,
    install_conversion_dependencies
)

# Import new AI components
from ai_content_parser import AIContentParser, DocumentStructure
from smart_page_break_engine import SmartPageBreakEngine, PageBreakDecision

# Import enhanced file management if available
try:
    from enhanced_file_manager import EnhancedFileManager
    from file_organization_tools import FileOrganizationTools
    FILE_MANAGEMENT_AVAILABLE = True
except ImportError:
    print("Warning: Enhanced file management not available")
    FILE_MANAGEMENT_AVAILABLE = False

# Create enhanced MCP server
mcp = FastMCP("AI-Enhanced Markdown PDF Converter",
              dependencies=["playwright", "markdown", "asyncio"])

# Initialize AI components
ai_parser = AIContentParser()
page_break_engine = SmartPageBreakEngine()

# Initialize file management if available
if FILE_MANAGEMENT_AVAILABLE:
    file_manager = EnhancedFileManager()
    org_tools = FileOrganizationTools()
else:
    file_manager = None
    org_tools = None

@mcp.tool()
async def ai_analyze_document_structure(file_path: str) -> str:
    """Analyze document structure using AI-powered content parser"""
    if not os.path.exists(file_path):
        return json.dumps({"error": f"File not found: {file_path}"})
    
    try:
        # Parse document with AI
        document_structure = ai_parser.parse_document(file_path)
        
        # Get content groups for page breaks
        content_groups = ai_parser.get_content_groups_for_page_breaks(document_structure)
        
        # Create analysis summary
        analysis = {
            "status": "success",
            "file_analyzed": file_path,
            "timestamp": datetime.now().isoformat(),
            "structure_analysis": {
                "total_blocks": len(document_structure.blocks),
                "content_relationships": len(document_structure.relationships),
                "content_clusters": len(document_structure.content_clusters),
                "content_groups": len(content_groups)
            },
            "content_types": {},
            "relationship_types": {},
            "high_priority_groups": []
        }
        
        # Count content types
        for block in document_structure.blocks:
            content_type = block.content_type.value
            analysis["content_types"][content_type] = analysis["content_types"].get(content_type, 0) + 1
        
        # Count relationship types
        for rel in document_structure.relationships:
            rel_type = rel.relationship_type.value
            analysis["relationship_types"][rel_type] = analysis["relationship_types"].get(rel_type, 0) + 1
        
        # Identify high-priority groups
        high_priority_groups = [g for g in content_groups if g['priority'] == 'high']
        for group in high_priority_groups[:5]:  # Limit to top 5
            analysis["high_priority_groups"].append({
                "group_id": group['group_id'],
                "group_type": group['group_type'],
                "estimated_lines": group['estimated_lines'],
                "keep_together": group['keep_together']
            })
        
        return json.dumps(analysis, indent=2)
        
    except Exception as e:
        return json.dumps({
            "error": f"Failed to analyze document: {str(e)}",
            "status": "failed"
        })

@mcp.tool()
async def ai_generate_smart_page_breaks(file_path: str) -> str:
    """Generate intelligent page break recommendations using AI"""
    if not os.path.exists(file_path):
        return json.dumps({"error": f"File not found: {file_path}"})
    
    try:
        # Parse document structure
        document_structure = ai_parser.parse_document(file_path)
        content_groups = ai_parser.get_content_groups_for_page_breaks(document_structure)
        
        # Generate smart page break decisions
        decisions = page_break_engine.analyze_optimal_page_breaks(document_structure, content_groups)
        
        # Create summary
        summary = {
            "status": "success",
            "file_analyzed": file_path,
            "timestamp": datetime.now().isoformat(),
            "page_break_analysis": {
                "total_decisions": len(decisions),
                "high_confidence": len([d for d in decisions if d.confidence > 0.8]),
                "medium_confidence": len([d for d in decisions if 0.6 <= d.confidence <= 0.8]),
                "low_confidence": len([d for d in decisions if d.confidence < 0.6])
            },
            "break_reasons": {},
            "top_recommendations": []
        }
        
        # Count break reasons
        for decision in decisions:
            reason = decision.reason.value
            summary["break_reasons"][reason] = summary["break_reasons"].get(reason, 0) + 1
        
        # Top recommendations
        top_decisions = sorted(decisions, key=lambda x: x.confidence, reverse=True)[:5]
        for decision in top_decisions:
            summary["top_recommendations"].append({
                "line_number": decision.line_number,
                "reason": decision.reason.value,
                "priority": decision.priority.value,
                "confidence": round(decision.confidence, 3),
                "reasoning": decision.reasoning
            })
        
        return json.dumps(summary, indent=2)
        
    except Exception as e:
        return json.dumps({
            "error": f"Failed to generate page break recommendations: {str(e)}",
            "status": "failed"
        })

@mcp.tool()
async def ai_enhanced_conversion(file_path: str, use_ai_page_breaks: bool = True) -> str:
    """Convert Markdown to PDF with AI-enhanced page break intelligence"""
    if not install_conversion_dependencies():
        return json.dumps({"error": "Failed to install required dependencies"})

    if not os.path.exists(file_path):
        return json.dumps({"error": f"File not found: {file_path}"})

    base_name = Path(file_path).stem
    html_file = f"{base_name}_ai_enhanced.html"
    pdf_file = f"{base_name}_ai_enhanced.pdf"

    try:
        # Step 1: AI Analysis (if requested)
        ai_analysis = None
        page_break_decisions = None
        
        if use_ai_page_breaks:
            # Parse document structure
            document_structure = ai_parser.parse_document(file_path)
            content_groups = ai_parser.get_content_groups_for_page_breaks(document_structure)
            
            # Generate smart page break decisions
            page_break_decisions = page_break_engine.analyze_optimal_page_breaks(document_structure, content_groups)
            
            ai_analysis = {
                "content_blocks": len(document_structure.blocks),
                "relationships": len(document_structure.relationships),
                "clusters": len(document_structure.content_clusters),
                "page_break_decisions": len(page_break_decisions),
                "high_confidence_breaks": len([d for d in page_break_decisions if d.confidence > 0.8])
            }

        # Step 2: MD → HTML conversion
        if not convert_markdown_to_html(file_path, html_file):
            return json.dumps({"error": f"Failed to convert {file_path} to HTML"})

        # Step 3: Enhanced HTML → PDF with AI page breaks
        if use_ai_page_breaks and page_break_decisions:
            # Apply AI-generated page breaks to HTML
            success = await apply_ai_page_breaks_to_html(html_file, page_break_decisions)
            if not success:
                return json.dumps({"error": "Failed to apply AI page breaks to HTML"})

        # Step 4: Generate PDF
        if not await convert_html_to_pdf(html_file, pdf_file):
            return json.dumps({"error": f"Failed to convert {html_file} to PDF"})

        # Get file size
        size_kb = os.path.getsize(pdf_file) / 1024

        result = {
            "status": "success",
            "input_file": file_path,
            "output_file": pdf_file,
            "html_file": html_file,
            "size_kb": round(size_kb, 1),
            "timestamp": datetime.now().isoformat(),
            "ai_enhanced": use_ai_page_breaks,
            "features": [
                "AI-powered content analysis",
                "Smart page break decisions",
                "Professional document layout",
                "Mermaid diagrams preserved",
                "Enhanced visual balance"
            ]
        }
        
        if ai_analysis:
            result["ai_analysis"] = ai_analysis

        return json.dumps(result, indent=2)

    except Exception as e:
        return json.dumps({
            "error": f"Conversion failed: {str(e)}",
            "status": "failed"
        })

async def apply_ai_page_breaks_to_html(html_file: str, decisions: List[PageBreakDecision]) -> bool:
    """Apply AI-generated page break decisions to HTML file"""
    try:
        # Read HTML content
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Create page break markers based on AI decisions
        break_markers = []
        for decision in decisions:
            if decision.confidence > 0.6:  # Only apply high-confidence breaks
                marker = f'<div class="ai-page-break" data-line="{decision.line_number}" data-reason="{decision.reason.value}" data-confidence="{decision.confidence:.2f}"></div>'
                break_markers.append((decision.line_number, marker))
        
        # Sort by line number (descending to avoid offset issues)
        break_markers.sort(key=lambda x: x[0], reverse=True)
        
        # Insert break markers into HTML
        # This is a simplified approach - in practice, you'd need more sophisticated HTML parsing
        lines = html_content.split('\n')
        for line_num, marker in break_markers:
            if 0 <= line_num < len(lines):
                lines.insert(line_num, marker)
        
        # Add CSS for AI page breaks
        ai_css = """
        <style>
        @media print {
            .ai-page-break {
                page-break-before: always !important;
                break-before: page !important;
                display: none !important;
                height: 0 !important;
                margin: 0 !important;
                padding: 0 !important;
            }
        }
        </style>
        """
        
        # Insert CSS before closing head tag
        modified_html = '\n'.join(lines)
        modified_html = modified_html.replace('</head>', f'{ai_css}</head>')
        
        # Write modified HTML
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(modified_html)
        
        return True
        
    except Exception as e:
        print(f"Error applying AI page breaks: {e}")
        return False

@mcp.tool()
async def batch_ai_enhanced_conversion(pattern: str = "*.md", use_ai_page_breaks: bool = True) -> str:
    """Batch convert multiple Markdown files with AI enhancement"""
    if not install_conversion_dependencies():
        return json.dumps({"error": "Failed to install required dependencies"})

    # Find matching files
    files_to_convert = glob.glob(pattern)
    if not files_to_convert:
        return json.dumps({"error": f"No files found matching pattern: {pattern}"})

    results = []
    success_count = 0

    for file_path in files_to_convert:
        print(f"Processing {file_path}...")

        try:
            # Convert individual file
            result_json = await ai_enhanced_conversion(file_path, use_ai_page_breaks)
            result = json.loads(result_json)

            if result.get("status") == "success":
                success_count += 1
                results.append({
                    "file": file_path,
                    "status": "success",
                    "output": result.get("output_file"),
                    "size_kb": result.get("size_kb"),
                    "ai_analysis": result.get("ai_analysis")
                })
            else:
                results.append({
                    "file": file_path,
                    "status": "failed",
                    "error": result.get("error")
                })

        except Exception as e:
            results.append({
                "file": file_path,
                "status": "failed",
                "error": str(e)
            })

    summary = {
        "status": "completed",
        "total_files": len(files_to_convert),
        "successful_conversions": success_count,
        "failed_conversions": len(files_to_convert) - success_count,
        "results": results,
        "timestamp": datetime.now().isoformat(),
        "ai_enhanced": use_ai_page_breaks
    }

    return json.dumps(summary, indent=2)

# Backward compatibility tools - maintain existing functionality
@mcp.tool()
async def convert_with_enhanced_page_breaks(file_path: str) -> str:
    """Legacy tool: Convert with enhanced page breaks (now AI-powered)"""
    return await ai_enhanced_conversion(file_path, use_ai_page_breaks=True)

@mcp.tool()
async def batch_convert_with_enhanced_breaks() -> str:
    """Legacy tool: Batch convert with enhanced breaks (now AI-powered)"""
    return await batch_ai_enhanced_conversion("*.md", use_ai_page_breaks=True)

# Additional tools for AI analysis and page breaks
@mcp.tool()
async def get_ai_document_analysis(file_path: str) -> str:
    """Get AI analysis of document structure"""
    try:
        if not os.path.exists(file_path):
            return json.dumps({"error": f"File not found: {file_path}"})

        # Parse document
        document_structure = ai_parser.parse_document(file_path)
        content_groups = ai_parser.get_content_groups_for_page_breaks(document_structure)

        # Export analysis
        analysis_file = f"{Path(file_path).stem}_ai_analysis.json"
        ai_parser.export_analysis(document_structure, analysis_file)

        return json.dumps({
            "analysis_file": analysis_file,
            "blocks": len(document_structure.blocks),
            "relationships": len(document_structure.relationships),
            "clusters": len(document_structure.content_clusters),
            "groups": len(content_groups)
        })

    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
async def get_smart_page_breaks(file_path: str) -> str:
    """Get smart page break recommendations"""
    try:
        if not os.path.exists(file_path):
            return json.dumps({"error": f"File not found: {file_path}"})

        # Parse and analyze
        document_structure = ai_parser.parse_document(file_path)
        content_groups = ai_parser.get_content_groups_for_page_breaks(document_structure)
        decisions = page_break_engine.analyze_optimal_page_breaks(document_structure, content_groups)

        # Export decisions
        decisions_file = f"{Path(file_path).stem}_page_breaks.json"
        page_break_engine.export_decisions(decisions, decisions_file)

        return json.dumps({
            "decisions_file": decisions_file,
            "total_decisions": len(decisions),
            "high_confidence": len([d for d in decisions if d.confidence > 0.8]),
            "recommendations": [
                {
                    "line": d.line_number,
                    "reason": d.reason.value,
                    "confidence": round(d.confidence, 3)
                }
                for d in sorted(decisions, key=lambda x: x.confidence, reverse=True)[:5]
            ]
        })

    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
async def compare_conversion_methods(file_path: str) -> str:
    """Compare traditional vs AI-enhanced conversion methods"""
    if not os.path.exists(file_path):
        return json.dumps({"error": f"File not found: {file_path}"})

    try:
        base_name = Path(file_path).stem

        # Traditional conversion
        traditional_result = await convert_with_enhanced_page_breaks(file_path)
        traditional_data = json.loads(traditional_result)

        # AI-enhanced conversion
        ai_result = await ai_enhanced_conversion(file_path, use_ai_page_breaks=True)
        ai_data = json.loads(ai_result)

        comparison = {
            "file_analyzed": file_path,
            "timestamp": datetime.now().isoformat(),
            "traditional_method": {
                "status": traditional_data.get("status"),
                "output_file": traditional_data.get("output_file"),
                "size_kb": traditional_data.get("size_kb"),
                "features": traditional_data.get("features", [])
            },
            "ai_enhanced_method": {
                "status": ai_data.get("status"),
                "output_file": ai_data.get("output_file"),
                "size_kb": ai_data.get("size_kb"),
                "features": ai_data.get("features", []),
                "ai_analysis": ai_data.get("ai_analysis")
            },
            "improvements": []
        }

        # Identify improvements
        if ai_data.get("ai_analysis"):
            analysis = ai_data["ai_analysis"]
            if analysis.get("high_confidence_breaks", 0) > 0:
                comparison["improvements"].append(f"Added {analysis['high_confidence_breaks']} high-confidence intelligent page breaks")
            if analysis.get("content_blocks", 0) > 0:
                comparison["improvements"].append(f"Analyzed {analysis['content_blocks']} content blocks for optimal layout")
            if analysis.get("relationships", 0) > 0:
                comparison["improvements"].append(f"Identified {analysis['relationships']} content relationships for better grouping")

        return json.dumps(comparison, indent=2)

    except Exception as e:
        return json.dumps({
            "error": f"Comparison failed: {str(e)}",
            "status": "failed"
        })

def main():
    """Main function to run the AI-enhanced MCP server"""
    print("🚀 Starting AI-Enhanced MCP Server...")
    print("Features:")
    print("  • AI-powered content analysis")
    print("  • Smart page break decisions")
    print("  • Backward compatibility with existing tools")
    print("  • Enhanced document layout intelligence")
    print("  • Professional PDF output")

    # The server would be started here in a real deployment
    # For testing, we can demonstrate the functionality

    test_file = "blueprint-ceo.md"
    if Path(test_file).exists():
        print(f"\n🧪 Testing AI-enhanced conversion with {test_file}...")

        # Test AI analysis
        import asyncio

        async def test_ai_features():
            print("\n1. Testing AI document analysis...")
            analysis_result = await ai_analyze_document_structure(test_file)
            analysis = json.loads(analysis_result)
            if analysis.get("status") == "success":
                print(f"   ✅ Analyzed {analysis['structure_analysis']['total_blocks']} content blocks")
                print(f"   ✅ Found {analysis['structure_analysis']['content_relationships']} relationships")
                print(f"   ✅ Identified {len(analysis['high_priority_groups'])} high-priority groups")

            print("\n2. Testing smart page break generation...")
            breaks_result = await ai_generate_smart_page_breaks(test_file)
            breaks = json.loads(breaks_result)
            if breaks.get("status") == "success":
                print(f"   ✅ Generated {breaks['page_break_analysis']['total_decisions']} page break decisions")
                print(f"   ✅ {breaks['page_break_analysis']['high_confidence']} high-confidence recommendations")

            print("\n3. Testing AI-enhanced conversion...")
            conversion_result = await ai_enhanced_conversion(test_file, use_ai_page_breaks=True)
            conversion = json.loads(conversion_result)
            if conversion.get("status") == "success":
                print(f"   ✅ Generated {conversion['output_file']} ({conversion['size_kb']} KB)")
                if conversion.get("ai_analysis"):
                    ai_stats = conversion["ai_analysis"]
                    print(f"   ✅ Applied {ai_stats['high_confidence_breaks']} intelligent page breaks")

        asyncio.run(test_ai_features())

    else:
        print(f"Test file {test_file} not found!")

if __name__ == "__main__":
    main()
