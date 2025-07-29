#!/usr/bin/env python3
"""
Enhanced MCP Server with Intelligent Document Validation
Integrates the intelligent document validator with the existing MCP markdown-to-PDF server
"""

import asyncio
import json
import glob
from typing import Dict, List, Optional, Any
from pathlib import Path
import logging

# Import existing MCP server functions
from mcp_markdown_pdf_server_clean import (
    batch_convert_all,
    convert_single_file,
    detect_mermaid_diagrams,
    check_system_status
)

# Import new validation components
from mcp_document_validator_integration import (
    MCPDocumentValidatorIntegration,
    mcp_validate_documents,
    mcp_auto_fix_and_convert,
    mcp_generate_validation_report,
    mcp_health_check
)

logger = logging.getLogger(__name__)

class EnhancedMCPServer:
    """Enhanced MCP Server with intelligent document validation capabilities"""
    
    def __init__(self):
        self.validator_integration = MCPDocumentValidatorIntegration()
        self.server_info = {
            "name": "Enhanced MCP Markdown-PDF Server with Validation",
            "version": "2.0.0",
            "description": "Advanced document processing with intelligent duplicate detection",
            "capabilities": [
                "markdown_to_pdf_conversion",
                "mermaid_diagram_rendering", 
                "intelligent_duplicate_detection",
                "automatic_content_fixing",
                "batch_document_processing",
                "validation_reporting",
                "document_health_monitoring"
            ]
        }
    
    # Enhanced Resources with Validation
    async def get_resources(self) -> List[Dict[str, Any]]:
        """Get available resources including validation capabilities"""
        return [
            {
                "uri": "markdown://files",
                "name": "Markdown Files",
                "description": "List and analyze Markdown files in the current directory",
                "mimeType": "application/json"
            },
            {
                "uri": "validation://status", 
                "name": "Validation Status",
                "description": "Current validation status of all documents",
                "mimeType": "application/json"
            },
            {
                "uri": "conversion://status",
                "name": "Conversion Status", 
                "description": "Status of PDF conversion operations",
                "mimeType": "application/json"
            },
            {
                "uri": "validation://reports",
                "name": "Validation Reports",
                "description": "Historical validation reports and analysis",
                "mimeType": "application/json"
            }
        ]
    
    async def read_resource(self, uri: str) -> Dict[str, Any]:
        """Read resource content with validation integration"""
        
        if uri == "markdown://files":
            md_files = glob.glob("*.md")
            file_info = []
            
            for file_path in md_files:
                # Quick validation check
                report = self.validator_integration.validator.validate_document(file_path)
                
                file_info.append({
                    "path": file_path,
                    "size": Path(file_path).stat().st_size,
                    "validation_status": "clean" if report.total_issues == 0 else "issues_found",
                    "critical_issues": report.critical_issues,
                    "total_issues": report.total_issues
                })
            
            return {
                "contents": [{
                    "uri": uri,
                    "mimeType": "application/json",
                    "text": json.dumps({
                        "files": file_info,
                        "total_files": len(md_files),
                        "files_with_issues": len([f for f in file_info if f["total_issues"] > 0])
                    }, indent=2)
                }]
            }
        
        elif uri == "validation://status":
            # Get current validation status
            batch_report = self.validator_integration.validator.batch_validate_directory()
            
            return {
                "contents": [{
                    "uri": uri,
                    "mimeType": "application/json", 
                    "text": json.dumps({
                        "overall_status": "clean" if batch_report["critical_issues"] == 0 else "issues_found",
                        "summary": batch_report,
                        "last_check": batch_report.get("timestamp")
                    }, indent=2)
                }]
            }
        
        elif uri == "conversion://status":
            # Get conversion status
            system_status = await check_system_status()
            
            return {
                "contents": [{
                    "uri": uri,
                    "mimeType": "application/json",
                    "text": json.dumps({
                        "system_ready": True,
                        "dependencies": system_status,
                        "pdf_files": len(glob.glob("*.pdf")),
                        "markdown_files": len(glob.glob("*.md"))
                    }, indent=2)
                }]
            }
        
        elif uri == "validation://reports":
            # Get validation history
            history = self.validator_integration.get_validation_history()
            
            return {
                "contents": [{
                    "uri": uri,
                    "mimeType": "application/json",
                    "text": json.dumps({
                        "validation_runs": len(history),
                        "recent_reports": history[-5:] if history else [],
                        "trends": self._analyze_validation_trends(history)
                    }, indent=2)
                }]
            }
        
        else:
            raise ValueError(f"Unknown resource URI: {uri}")
    
    def _analyze_validation_trends(self, history: List[Dict]) -> Dict:
        """Analyze trends in validation history"""
        if not history:
            return {"status": "no_data"}
        
        recent = history[-5:] if len(history) >= 5 else history
        
        total_issues_trend = [report["total_issues"] for report in recent]
        critical_issues_trend = [report["critical_issues"] for report in recent]
        
        return {
            "total_issues_trend": total_issues_trend,
            "critical_issues_trend": critical_issues_trend,
            "improving": len(recent) > 1 and recent[-1]["total_issues"] < recent[0]["total_issues"],
            "latest_status": "clean" if recent[-1]["critical_issues"] == 0 else "needs_attention"
        }
    
    # Enhanced Tools with Validation
    async def get_tools(self) -> List[Dict[str, Any]]:
        """Get available tools including validation capabilities"""
        return [
            {
                "name": "validate_documents",
                "description": "Intelligently validate documents for duplicate content and formatting issues",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "files": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Optional list of specific files to validate"
                        },
                        "auto_fix": {
                            "type": "boolean", 
                            "description": "Whether to automatically fix critical issues",
                            "default": False
                        }
                    }
                }
            },
            {
                "name": "convert_with_validation",
                "description": "Convert documents to PDF with pre-conversion validation",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "files": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Optional list of specific files to convert"
                        },
                        "skip_validation": {
                            "type": "boolean",
                            "description": "Skip validation and convert directly",
                            "default": False
                        },
                        "auto_fix": {
                            "type": "boolean",
                            "description": "Automatically fix issues before conversion", 
                            "default": False
                        }
                    }
                }
            },
            {
                "name": "generate_validation_report",
                "description": "Generate comprehensive validation report",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "format": {
                            "type": "string",
                            "enum": ["json", "markdown", "both"],
                            "description": "Output format for the report",
                            "default": "both"
                        }
                    }
                }
            },
            {
                "name": "health_check",
                "description": "Perform system health check including validation capabilities",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "batch_convert_all",
                "description": "Convert all Markdown files to PDF (legacy function)",
                "inputSchema": {
                    "type": "object", 
                    "properties": {}
                }
            },
            {
                "name": "detect_mermaid_diagrams",
                "description": "Detect Mermaid diagrams in a file",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Path to the Markdown file"
                        }
                    },
                    "required": ["file_path"]
                }
            }
        ]
    
    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute tool with validation integration"""
        
        try:
            if name == "validate_documents":
                files = arguments.get("files")
                auto_fix = arguments.get("auto_fix", False)
                
                if auto_fix:
                    result = await self.validator_integration.auto_fix_and_convert(files)
                else:
                    result = await self.validator_integration.validate_before_conversion(files)
                
                return {
                    "content": [{
                        "type": "text",
                        "text": json.dumps(result, indent=2)
                    }]
                }
            
            elif name == "convert_with_validation":
                files = arguments.get("files")
                skip_validation = arguments.get("skip_validation", False)
                auto_fix = arguments.get("auto_fix", False)
                
                if skip_validation:
                    # Direct conversion without validation
                    if files:
                        results = []
                        for file_path in files:
                            result = await convert_single_file(file_path)
                            results.append(result)
                        return {
                            "content": [{
                                "type": "text", 
                                "text": json.dumps({"results": results}, indent=2)
                            }]
                        }
                    else:
                        result = await batch_convert_all()
                        return {
                            "content": [{
                                "type": "text",
                                "text": result
                            }]
                        }
                else:
                    # Conversion with validation
                    if auto_fix:
                        result = await self.validator_integration.auto_fix_and_convert(files)
                    else:
                        # Validate first, then convert if safe
                        validation_result = await self.validator_integration.validate_before_conversion(files)
                        
                        if validation_result["proceed_with_conversion"]:
                            if files:
                                conversion_results = []
                                for file_path in files:
                                    conv_result = await convert_single_file(file_path)
                                    conversion_results.append(conv_result)
                                result = {
                                    "validation": validation_result,
                                    "conversion": {"results": conversion_results}
                                }
                            else:
                                conv_result = await batch_convert_all()
                                result = {
                                    "validation": validation_result,
                                    "conversion": json.loads(conv_result) if isinstance(conv_result, str) else conv_result
                                }
                        else:
                            result = {
                                "validation": validation_result,
                                "conversion": {"status": "skipped", "reason": "validation_failed"}
                            }
                    
                    return {
                        "content": [{
                            "type": "text",
                            "text": json.dumps(result, indent=2)
                        }]
                    }
            
            elif name == "generate_validation_report":
                format_type = arguments.get("format", "both")
                result = await self.validator_integration.generate_validation_report(format_type)
                
                return {
                    "content": [{
                        "type": "text",
                        "text": json.dumps(result, indent=2)
                    }]
                }
            
            elif name == "health_check":
                # Combined health check
                validation_health = await self.validator_integration.health_check()
                system_status = await check_system_status()
                
                result = {
                    "validation_system": validation_health,
                    "conversion_system": system_status,
                    "overall_status": "healthy" if validation_health["status"] == "healthy" else "warning"
                }
                
                return {
                    "content": [{
                        "type": "text",
                        "text": json.dumps(result, indent=2)
                    }]
                }
            
            elif name == "batch_convert_all":
                # Legacy function
                result = await batch_convert_all()
                return {
                    "content": [{
                        "type": "text",
                        "text": result
                    }]
                }
            
            elif name == "detect_mermaid_diagrams":
                file_path = arguments["file_path"]
                result = detect_mermaid_diagrams(file_path)
                return {
                    "content": [{
                        "type": "text",
                        "text": result
                    }]
                }
            
            else:
                raise ValueError(f"Unknown tool: {name}")
                
        except Exception as e:
            logger.error(f"Error executing tool {name}: {e}")
            return {
                "content": [{
                    "type": "text",
                    "text": json.dumps({
                        "error": str(e),
                        "tool": name,
                        "arguments": arguments
                    }, indent=2)
                }],
                "isError": True
            }
    
    async def get_server_info(self) -> Dict[str, Any]:
        """Get enhanced server information"""
        return self.server_info

# Main server instance
enhanced_server = EnhancedMCPServer()

# Export functions for MCP integration
async def get_resources() -> List[Dict[str, Any]]:
    return await enhanced_server.get_resources()

async def read_resource(uri: str) -> Dict[str, Any]:
    return await enhanced_server.read_resource(uri)

async def get_tools() -> List[Dict[str, Any]]:
    return await enhanced_server.get_tools()

async def call_tool(name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    return await enhanced_server.call_tool(name, arguments)

async def get_server_info() -> Dict[str, Any]:
    return await enhanced_server.get_server_info()

async def main():
    """Test the enhanced server"""
    print("🚀 Enhanced MCP Server with Intelligent Document Validation")
    print("=" * 60)
    
    # Test server info
    info = await get_server_info()
    print(f"Server: {info['name']} v{info['version']}")
    print(f"Capabilities: {', '.join(info['capabilities'])}")
    print()
    
    # Test health check
    health_result = await call_tool("health_check", {})
    print("Health Check Results:")
    print(health_result["content"][0]["text"])

if __name__ == "__main__":
    asyncio.run(main())
