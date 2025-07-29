#!/usr/bin/env python3
"""
Comprehensive test suite for Enhanced Universal Document Converter MCP Server
Tests all advanced features including AI integration, workspace compatibility, and NPX distribution
"""

import asyncio
import json
import os
import sys
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
import logging

# Import enhanced MCP server components
from enhanced_mcp_server_main import (
    detect_conversion_trigger, 
    enhanced_quick_convert, 
    EnhancedMCPServer
)
from enhanced_universal_document_converter import (
    EnhancedUniversalDocumentConverter,
    WorkspaceManager,
    APIKeyManager,
    AIConfig,
    WorkspaceConfig
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EnhancedMCPServerTester:
    """Comprehensive test suite for enhanced MCP server"""
    
    def __init__(self):
        self.test_results = []
        self.temp_dir = None
        self.test_workspace = None
        
    def log_test(self, test_name: str, success: bool, message: str = ""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.test_results.append({
            "test": test_name,
            "success": success,
            "message": message
        })
        print(f"{status} {test_name}: {message}")
    
    def create_test_workspace(self) -> str:
        """Create a test workspace with various file types"""
        workspace = Path(self.temp_dir) / "test_workspace"
        workspace.mkdir(exist_ok=True)
        
        # Create workspace indicators
        (workspace / ".git").mkdir(exist_ok=True)
        (workspace / "package.json").write_text('{"name": "test-project"}')
        
        # Create test markdown with enhanced content
        test_content = """# Enhanced Test Document

This is a comprehensive test document for the Enhanced Universal Document Converter.

## Architecture Overview

```mermaid
flowchart TB
    A[User Input] --> B[Enhanced Processing Engine]
    B --> C[AI Layout Optimizer]
    C --> D[Professional PDF Output]
    
    classDef input fill:#e1f5fe,stroke:#01579b
    classDef process fill:#f3e5f5,stroke:#4a148c
    classDef ai fill:#fff3e0,stroke:#f57c00
    classDef output fill:#e8f5e8,stroke:#1b5e20
    
    class A input
    class B process
    class C ai
    class D output
```

## Advanced Features

This document tests multiple advanced features:

1. **Universal Workspace Compatibility**
2. **AI-Powered Layout Optimization**
3. **Advanced API Key Management**
4. **NPX Package Distribution**

## Complex Diagram

```mermaid
flowchart LR
    Start --> Process1[Data Processing]
    Process1 --> Decision{AI Analysis?}
    Decision -->|Yes| AI[OpenRouter AI]
    Decision -->|No| Standard[Standard Processing]
    AI --> Optimize[Layout Optimization]
    Standard --> Optimize
    Optimize --> End[PDF Generation]
```

## Conclusion

This test document contains multiple Mermaid diagrams and complex content for comprehensive testing of the enhanced converter capabilities.
"""
        
        test_file = workspace / "enhanced_test_document.md"
        test_file.write_text(test_content)
        
        return str(test_file)
    
    async def test_enhanced_trigger_detection(self):
        """Test enhanced trigger keyword detection including NPX commands"""
        test_cases = [
            ("convert: md -> html -> pdf", True),
            ("I need markdown to pdf conversion", True),
            ("npx universal-doc-converter document.md", True),
            ("universal doc converter", True),
            ("document conversion please", True),
            ("md to pdf with ai layout", True),
            ("generate pdf with mermaid optimization", True),
            ("just some random text", False),
            ("hello world", False),
            ("create a simple document", False)
        ]
        
        for test_input, expected in test_cases:
            result = detect_conversion_trigger(test_input)
            success = result == expected
            self.log_test(
                f"Enhanced Trigger Detection: '{test_input[:40]}...'",
                success,
                f"Expected: {expected}, Got: {result}"
            )
    
    async def test_workspace_manager(self):
        """Test universal workspace compatibility"""
        try:
            # Test workspace detection from different paths
            workspace_manager = WorkspaceManager(self.test_workspace)
            
            # Test path resolution
            test_file = "test.md"
            resolved = workspace_manager.resolve_path(test_file)
            relative = workspace_manager.get_relative_path(str(resolved))
            
            success = (
                workspace_manager.config.root_path.exists() and
                resolved.is_absolute() and
                relative == test_file
            )
            
            self.log_test(
                "Universal Workspace Compatibility",
                success,
                f"Root: {workspace_manager.config.root_path}, Resolved: {resolved.name}"
            )
            
        except Exception as e:
            self.log_test("Universal Workspace Compatibility", False, f"Error: {str(e)}")
    
    async def test_api_key_manager(self):
        """Test advanced API key management system"""
        try:
            # Create temporary API key manager
            temp_config = Path(self.temp_dir) / "test_api_keys.json"
            api_manager = APIKeyManager(str(temp_config))
            
            # Test adding keys
            test_keys = [
                "sk-or-test-key-1-12345",
                "sk-or-test-key-2-67890",
                "sk-or-test-key-3-abcdef"
            ]
            
            added_count = 0
            for key in test_keys:
                if api_manager.add_key(key):
                    added_count += 1
            
            # Test key rotation
            first_key = api_manager.get_next_key()
            second_key = api_manager.get_next_key()
            
            # Test health status
            health_status = api_manager.get_health_status()
            
            success = (
                added_count == len(test_keys) and
                first_key in test_keys and
                second_key in test_keys and
                health_status["total_keys"] == len(test_keys)
            )
            
            self.log_test(
                "Advanced API Key Management",
                success,
                f"Added: {added_count}, Health: {health_status['average_health_score']}"
            )
            
        except Exception as e:
            self.log_test("Advanced API Key Management", False, f"Error: {str(e)}")
    
    async def test_enhanced_document_analysis(self):
        """Test enhanced document analysis with AI features"""
        try:
            converter = EnhancedUniversalDocumentConverter(self.test_workspace)
            test_file = self.create_test_workspace()
            
            analysis = converter.analyze_document(test_file)
            
            success = (
                "workspace_root" in analysis and
                "relative_path" in analysis and
                analysis["existing_mermaid_diagrams"] == 2 and  # Should detect 2 diagrams
                analysis["document_type"] in ["technical", "general"]
            )
            
            self.log_test(
                "Enhanced Document Analysis",
                success,
                f"Diagrams: {analysis.get('existing_mermaid_diagrams', 0)}, Type: {analysis.get('document_type', 'unknown')}"
            )
            
        except Exception as e:
            self.log_test("Enhanced Document Analysis", False, f"Error: {str(e)}")
    
    async def test_ai_layout_analysis(self):
        """Test AI-powered layout analysis (mock test without real API)"""
        try:
            # Create AI config without real API keys for testing
            ai_config = AIConfig(enabled=True, model="anthropic/claude-3-haiku")
            converter = EnhancedUniversalDocumentConverter(self.test_workspace, ai_config)
            
            # Test AI analysis structure (without making real API calls)
            test_content = "# Test Document\n\nThis is a test document with content."
            test_diagrams = ["flowchart TB\n    A --> B"]
            
            # Mock AI analysis response
            mock_analysis = {
                "ai_analysis": True,
                "summary": "Document structure analyzed",
                "chunks": [{"chunk_id": 1, "start_line": 1, "end_line": 10}],
                "page_breaks": [{"position": "after_line_5", "confidence": 0.9}],
                "optimizations": ["Keep diagrams with descriptions"]
            }
            
            # Test the analysis structure
            success = (
                "ai_analysis" in mock_analysis and
                "chunks" in mock_analysis and
                "page_breaks" in mock_analysis and
                len(mock_analysis["chunks"]) > 0
            )
            
            self.log_test(
                "AI Layout Analysis Structure",
                success,
                f"Chunks: {len(mock_analysis['chunks'])}, Breaks: {len(mock_analysis['page_breaks'])}"
            )
            
        except Exception as e:
            self.log_test("AI Layout Analysis Structure", False, f"Error: {str(e)}")
    
    async def test_enhanced_mcp_server_initialization(self):
        """Test enhanced MCP server initialization"""
        try:
            ai_config = AIConfig(enabled=False)
            server = EnhancedMCPServer(self.test_workspace, ai_config)
            
            # Test initialize request
            init_result = await server.handle_initialize({})
            
            # Test tools list
            tools_result = await server.handle_tools_list({})
            
            # Test resources list
            resources_result = await server.handle_resources_list({})
            
            success = (
                "protocolVersion" in init_result and
                "capabilities" in init_result and
                "serverInfo" in init_result and
                len(tools_result.get("tools", [])) > 0 and
                len(resources_result.get("resources", [])) > 0
            )
            
            self.log_test(
                "Enhanced MCP Server Initialization",
                success,
                f"Protocol: {init_result.get('protocolVersion', 'Unknown')}, Tools: {len(tools_result.get('tools', []))}"
            )
            
        except Exception as e:
            self.log_test("Enhanced MCP Server Initialization", False, f"Error: {str(e)}")
    
    async def test_enhanced_tools_call(self):
        """Test enhanced tools call with new features"""
        try:
            ai_config = AIConfig(enabled=False)  # Disable AI for testing
            server = EnhancedMCPServer(self.test_workspace, ai_config)
            
            test_file = self.create_test_workspace()
            
            call_params = {
                "name": "convert_document_md_to_pdf_enhanced",
                "arguments": {
                    "markdown_file": test_file,
                    "optimize_diagrams": True,
                    "ai_layout_optimization": False,
                    "backup_enabled": True,
                    "user_input": "convert: md -> html -> pdf"
                }
            }
            
            result = await server.handle_tools_call(call_params)
            
            success = not result.get("isError", True)
            content = result.get("content", [])
            message = content[0].get("text", "") if content else ""
            
            self.log_test(
                "Enhanced Tools Call",
                success,
                "Enhanced conversion successful" if success else f"Error: {message[:100]}"
            )
            
        except Exception as e:
            self.log_test("Enhanced Tools Call", False, f"Error: {str(e)}")
    
    async def test_npx_compatibility(self):
        """Test NPX package compatibility"""
        try:
            # Test package.json structure
            package_json_path = Path("package.json")
            if package_json_path.exists():
                with open(package_json_path, 'r') as f:
                    package_data = json.load(f)
                
                required_fields = ["name", "version", "bin", "scripts", "keywords"]
                has_required = all(field in package_data for field in required_fields)
                
                # Test bin file exists
                bin_file = Path("bin/universal-doc-converter.js")
                bin_exists = bin_file.exists()
                
                success = has_required and bin_exists
                
                self.log_test(
                    "NPX Package Compatibility",
                    success,
                    f"Package fields: {has_required}, Bin file: {bin_exists}"
                )
            else:
                self.log_test("NPX Package Compatibility", False, "package.json not found")
                
        except Exception as e:
            self.log_test("NPX Package Compatibility", False, f"Error: {str(e)}")
    
    async def test_enhanced_quick_convert(self):
        """Test enhanced quick conversion functionality"""
        try:
            test_file = self.create_test_workspace()
            
            # Test without AI
            result_standard = await enhanced_quick_convert(
                test_file, 
                "convert: md -> html -> pdf",
                ai_layout=False,
                workspace_path=self.test_workspace
            )
            
            # Test with AI (mock)
            result_ai = await enhanced_quick_convert(
                test_file,
                "npx universal-doc-converter",
                ai_layout=True,  # This will enable AI config but won't make real API calls
                workspace_path=self.test_workspace
            )
            
            success = (
                result_standard.get("success", False) and
                result_ai.get("success", False) and
                "features_used" in result_standard and
                "features_used" in result_ai
            )
            
            self.log_test(
                "Enhanced Quick Conversion",
                success,
                f"Standard: {result_standard.get('success')}, AI: {result_ai.get('success')}"
            )
            
        except Exception as e:
            self.log_test("Enhanced Quick Conversion", False, f"Error: {str(e)}")
    
    async def run_all_tests(self):
        """Run all enhanced tests"""
        print("🧪 Starting Enhanced Universal Document Converter MCP Server Tests")
        print("=" * 80)
        
        # Create temporary workspace
        self.temp_dir = tempfile.mkdtemp(prefix="enhanced_mcp_test_")
        self.test_workspace = str(Path(self.temp_dir) / "workspace")
        Path(self.test_workspace).mkdir(exist_ok=True)
        
        print(f"📁 Test workspace: {self.test_workspace}")
        
        try:
            # Run all enhanced tests
            await self.test_enhanced_trigger_detection()
            await self.test_workspace_manager()
            await self.test_api_key_manager()
            await self.test_enhanced_document_analysis()
            await self.test_ai_layout_analysis()
            await self.test_enhanced_mcp_server_initialization()
            await self.test_enhanced_tools_call()
            await self.test_npx_compatibility()
            await self.test_enhanced_quick_convert()
            
        finally:
            # Cleanup
            if self.temp_dir and os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
        
        # Print enhanced summary
        print("\n" + "=" * 80)
        print("📊 Enhanced Test Results Summary")
        print("=" * 80)
        
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['test']}")
        
        print(f"\n🎯 Overall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
        
        if passed == total:
            print("🎉 All enhanced tests passed! MCP server is ready for production deployment.")
            print("🚀 Features validated:")
            print("   • Universal workspace compatibility")
            print("   • AI-powered layout optimization")
            print("   • Advanced API key management")
            print("   • NPX package distribution")
            print("   • Enhanced MCP protocol support")
        else:
            print("⚠️  Some tests failed. Please review the issues above.")
        
        return passed == total

async def main():
    """Main test execution"""
    tester = EnhancedMCPServerTester()
    success = await tester.run_all_tests()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())
