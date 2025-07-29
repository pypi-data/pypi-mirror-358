#!/usr/bin/env python3
"""
MCP Server Main Entry Point for Universal Document Converter
Compatible with VS Code Insiders Extension: AUGMENT
"""

import asyncio
import json
import sys
from typing import Any, Dict, List
import logging
from mcp_universal_document_converter import (
    UniversalDocumentConverter, 
    mcp_tool_convert_document, 
    mcp_handle_convert_document
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MCPServer:
    """MCP Server implementation for document conversion"""
    
    def __init__(self):
        self.converter = UniversalDocumentConverter()
        self.tools = [mcp_tool_convert_document()]
        
    async def handle_initialize(self, params: Dict) -> Dict:
        """Handle MCP initialize request"""
        return {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {
                    "listChanged": True
                }
            },
            "serverInfo": {
                "name": "universal-document-converter",
                "version": "1.0.0"
            }
        }
    
    async def handle_tools_list(self, params: Dict) -> Dict:
        """Handle tools/list request"""
        return {
            "tools": self.tools
        }
    
    async def handle_tools_call(self, params: Dict) -> Dict:
        """Handle tools/call request"""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        if tool_name == "convert_document_md_to_pdf":
            try:
                result = await mcp_handle_convert_document(arguments)
                
                if result.get("success"):
                    return {
                        "content": [
                            {
                                "type": "text",
                                "text": result.get("message", "Conversion completed successfully!")
                            }
                        ],
                        "isError": False
                    }
                else:
                    return {
                        "content": [
                            {
                                "type": "text", 
                                "text": f"❌ Conversion failed: {result.get('error', 'Unknown error')}"
                            }
                        ],
                        "isError": True
                    }
                    
            except Exception as e:
                logger.error(f"Tool execution error: {e}")
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": f"❌ Tool execution failed: {str(e)}"
                        }
                    ],
                    "isError": True
                }
        else:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"❌ Unknown tool: {tool_name}"
                    }
                ],
                "isError": True
            }
    
    async def handle_request(self, request: Dict) -> Dict:
        """Handle incoming MCP requests"""
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id")
        
        try:
            if method == "initialize":
                result = await self.handle_initialize(params)
            elif method == "tools/list":
                result = await self.handle_tools_list(params)
            elif method == "tools/call":
                result = await self.handle_tools_call(params)
            else:
                result = {
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                }
            
            response = {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": result
            }
            
        except Exception as e:
            logger.error(f"Request handling error: {e}")
            response = {
                "jsonrpc": "2.0", 
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }
        
        return response
    
    async def run(self):
        """Run the MCP server"""
        logger.info("🚀 Universal Document Converter MCP Server starting...")
        logger.info("📋 Available triggers:")
        for trigger in self.converter.supported_triggers:
            logger.info(f"   • {trigger}")
        
        try:
            while True:
                # Read JSON-RPC request from stdin
                line = await asyncio.get_event_loop().run_in_executor(
                    None, sys.stdin.readline
                )
                
                if not line:
                    break
                
                try:
                    request = json.loads(line.strip())
                    response = await self.handle_request(request)
                    
                    # Write JSON-RPC response to stdout
                    print(json.dumps(response))
                    sys.stdout.flush()
                    
                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON received: {e}")
                    error_response = {
                        "jsonrpc": "2.0",
                        "id": None,
                        "error": {
                            "code": -32700,
                            "message": "Parse error"
                        }
                    }
                    print(json.dumps(error_response))
                    sys.stdout.flush()
                    
        except KeyboardInterrupt:
            logger.info("🛑 Server stopped by user")
        except Exception as e:
            logger.error(f"Server error: {e}")

# Standalone trigger detection function for AUGMENT integration
def detect_conversion_trigger(user_input: str) -> bool:
    """
    Standalone function to detect if user input should trigger document conversion
    This can be called by AUGMENT extension to determine if this MCP server should be activated
    """
    converter = UniversalDocumentConverter()
    return converter.detect_trigger(user_input)

# Quick conversion function for direct integration
async def quick_convert(markdown_file: str, user_input: str = "") -> Dict:
    """
    Quick conversion function for direct integration with AUGMENT
    """
    converter = UniversalDocumentConverter()
    
    # Check trigger if user input provided
    if user_input and not converter.detect_trigger(user_input):
        return {
            "success": False,
            "error": "Input does not contain conversion trigger keywords"
        }
    
    # Install dependencies
    if not converter.install_dependencies():
        return {"success": False, "error": "Failed to install dependencies"}
    
    # Convert document
    return await converter.convert_document(markdown_file, optimize_diagrams=True)

if __name__ == "__main__":
    # Check if running in test mode
    if len(sys.argv) > 1:
        if sys.argv[1] == "--test-trigger":
            test_input = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else ""
            detected = detect_conversion_trigger(test_input)
            print(f"Trigger detected: {detected}")
            print(f"Input: '{test_input}'")
        elif sys.argv[1] == "--quick-convert":
            if len(sys.argv) > 2:
                md_file = sys.argv[2]
                user_input = " ".join(sys.argv[3:]) if len(sys.argv) > 3 else ""
                result = asyncio.run(quick_convert(md_file, user_input))
                print(json.dumps(result, indent=2))
            else:
                print("Usage: --quick-convert <markdown_file> [user_input]")
        else:
            print("Usage:")
            print("  python mcp_server_main.py                    # Run MCP server")
            print("  python mcp_server_main.py --test-trigger <text>  # Test trigger detection")
            print("  python mcp_server_main.py --quick-convert <file> [input]  # Quick conversion")
    else:
        # Run MCP server
        server = MCPServer()
        asyncio.run(server.run())
