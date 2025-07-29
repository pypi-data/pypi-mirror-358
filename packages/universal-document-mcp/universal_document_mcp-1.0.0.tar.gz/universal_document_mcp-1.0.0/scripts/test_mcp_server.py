#!/usr/bin/env python3
"""
Test script for Universal Document Converter MCP Server
Validates all functionality and integration points
"""

import asyncio
import json
import os
import sys
from pathlib import Path
import tempfile
import shutil

# Import our MCP server components
from mcp_server_main import detect_conversion_trigger, quick_convert, MCPServer
from mcp_universal_document_converter import UniversalDocumentConverter

class MCPServerTester:
    """Comprehensive test suite for MCP server"""
    
    def __init__(self):
        self.test_results = []
        self.temp_dir = None
        
    def log_test(self, test_name: str, success: bool, message: str = ""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.test_results.append({
            "test": test_name,
            "success": success,
            "message": message
        })
        print(f"{status} {test_name}: {message}")
    
    def create_test_markdown(self) -> str:
        """Create a test markdown file with Mermaid diagrams"""
        test_content = """# Test Document

This is a test document for the Universal Document Converter.

## Architecture Overview

```mermaid
flowchart TB
    A[User Input] --> B[Processing Engine]
    B --> C[Output Generator]
    C --> D[Final Result]
    
    classDef input fill:#e1f5fe,stroke:#01579b
    classDef process fill:#f3e5f5,stroke:#4a148c
    classDef output fill:#e8f5e8,stroke:#1b5e20
    
    class A input
    class B process
    class C,D output
```

## Process Flow

This diagram shows the basic process flow.

```mermaid
flowchart LR
    Start --> Process --> End
```

## Conclusion

This test document contains multiple Mermaid diagrams for testing optimization.
"""
        
        test_file = os.path.join(self.temp_dir, "test_document.md")
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_content)
        
        return test_file
    
    async def test_trigger_detection(self):
        """Test trigger keyword detection"""
        test_cases = [
            ("convert: md -> html -> pdf", True),
            ("I need markdown to pdf conversion", True),
            ("document conversion please", True),
            ("md to pdf", True),
            ("convert markdown", True),
            ("generate pdf", True),
            ("mermaid pdf", True),
            ("just some random text", False),
            ("hello world", False),
            ("create a document", False)
        ]
        
        for test_input, expected in test_cases:
            result = detect_conversion_trigger(test_input)
            success = result == expected
            self.log_test(
                f"Trigger Detection: '{test_input[:30]}...'",
                success,
                f"Expected: {expected}, Got: {result}"
            )
    
    async def test_document_analysis(self):
        """Test document analysis functionality"""
        converter = UniversalDocumentConverter()
        test_file = self.create_test_markdown()
        
        try:
            analysis = converter.analyze_document(test_file)
            
            # Check analysis results
            success = (
                "file_size" in analysis and
                "existing_mermaid_diagrams" in analysis and
                "document_type" in analysis and
                analysis["existing_mermaid_diagrams"] == 2  # Should detect 2 diagrams
            )
            
            self.log_test(
                "Document Analysis",
                success,
                f"Detected {analysis.get('existing_mermaid_diagrams', 0)} diagrams"
            )
            
        except Exception as e:
            self.log_test("Document Analysis", False, f"Error: {str(e)}")
    
    async def test_diagram_optimization(self):
        """Test Mermaid diagram optimization"""
        converter = UniversalDocumentConverter()
        
        # Test content with long labels
        test_content = '''```mermaid
flowchart TB
    A["Very Long Label That Should Be Shortened For Better Rendering"] --> B["Another Extremely Long Label That Needs Optimization"]
    B --> C["Short Label"]
```'''
        
        try:
            optimized = converter.optimize_mermaid_diagrams(test_content)
            
            # Check if optimization occurred
            success = len(optimized) < len(test_content) or "..." in optimized
            
            self.log_test(
                "Diagram Optimization",
                success,
                f"Original: {len(test_content)} chars, Optimized: {len(optimized)} chars"
            )
            
        except Exception as e:
            self.log_test("Diagram Optimization", False, f"Error: {str(e)}")
    
    async def test_backup_creation(self):
        """Test backup file creation"""
        converter = UniversalDocumentConverter()
        test_file = self.create_test_markdown()
        
        try:
            backup_path = converter.create_backup(test_file)
            success = os.path.exists(backup_path) if backup_path else False
            
            self.log_test(
                "Backup Creation",
                success,
                f"Backup created: {backup_path}" if success else "No backup created"
            )
            
        except Exception as e:
            self.log_test("Backup Creation", False, f"Error: {str(e)}")
    
    async def test_quick_conversion(self):
        """Test quick conversion functionality"""
        test_file = self.create_test_markdown()
        
        try:
            result = await quick_convert(test_file, "convert: md -> html -> pdf")
            
            success = result.get("success", False)
            output_file = result.get("output_file", "")
            
            # Check if PDF was created
            if success and output_file:
                pdf_exists = os.path.exists(output_file)
                success = success and pdf_exists
            
            self.log_test(
                "Quick Conversion",
                success,
                f"PDF created: {output_file}" if success else result.get("error", "Unknown error")
            )
            
        except Exception as e:
            self.log_test("Quick Conversion", False, f"Error: {str(e)}")
    
    async def test_mcp_server_initialization(self):
        """Test MCP server initialization"""
        try:
            server = MCPServer()
            
            # Test initialize request
            init_result = await server.handle_initialize({})
            
            success = (
                "protocolVersion" in init_result and
                "capabilities" in init_result and
                "serverInfo" in init_result
            )
            
            self.log_test(
                "MCP Server Initialization",
                success,
                f"Protocol version: {init_result.get('protocolVersion', 'Unknown')}"
            )
            
        except Exception as e:
            self.log_test("MCP Server Initialization", False, f"Error: {str(e)}")
    
    async def test_tools_list(self):
        """Test tools list functionality"""
        try:
            server = MCPServer()
            tools_result = await server.handle_tools_list({})
            
            tools = tools_result.get("tools", [])
            success = len(tools) > 0 and any(
                tool.get("name") == "convert_document_md_to_pdf" 
                for tool in tools
            )
            
            self.log_test(
                "Tools List",
                success,
                f"Found {len(tools)} tools"
            )
            
        except Exception as e:
            self.log_test("Tools List", False, f"Error: {str(e)}")
    
    async def test_tools_call(self):
        """Test tools call functionality"""
        test_file = self.create_test_markdown()
        
        try:
            server = MCPServer()
            
            call_params = {
                "name": "convert_document_md_to_pdf",
                "arguments": {
                    "markdown_file": test_file,
                    "optimize_diagrams": True,
                    "user_input": "convert: md -> html -> pdf"
                }
            }
            
            result = await server.handle_tools_call(call_params)
            
            success = not result.get("isError", True)
            content = result.get("content", [])
            message = content[0].get("text", "") if content else ""
            
            self.log_test(
                "Tools Call",
                success,
                "Conversion successful" if success else f"Error: {message}"
            )
            
        except Exception as e:
            self.log_test("Tools Call", False, f"Error: {str(e)}")
    
    async def run_all_tests(self):
        """Run all tests"""
        print("🧪 Starting Universal Document Converter MCP Server Tests")
        print("=" * 60)
        
        # Create temporary directory for tests
        self.temp_dir = tempfile.mkdtemp(prefix="mcp_test_")
        print(f"📁 Test directory: {self.temp_dir}")
        
        try:
            # Run all tests
            await self.test_trigger_detection()
            await self.test_document_analysis()
            await self.test_diagram_optimization()
            await self.test_backup_creation()
            await self.test_quick_conversion()
            await self.test_mcp_server_initialization()
            await self.test_tools_list()
            await self.test_tools_call()
            
        finally:
            # Cleanup
            if self.temp_dir and os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 Test Results Summary")
        print("=" * 60)
        
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['test']}")
        
        print(f"\n🎯 Overall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
        
        if passed == total:
            print("🎉 All tests passed! MCP server is ready for integration.")
        else:
            print("⚠️  Some tests failed. Please review the issues above.")
        
        return passed == total

async def main():
    """Main test execution"""
    tester = MCPServerTester()
    success = await tester.run_all_tests()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())
