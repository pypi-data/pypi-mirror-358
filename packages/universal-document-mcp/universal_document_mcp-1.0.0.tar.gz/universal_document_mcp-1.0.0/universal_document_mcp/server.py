#!/usr/bin/env python3
"""
Universal Document Converter MCP Server
Main server entry point for system-wide installation
"""

import sys
import os
import asyncio
import argparse
from pathlib import Path
from typing import Dict, Any, Optional

# Add the scripts directory to the path to import existing modules
current_dir = Path(__file__).parent.parent
scripts_dir = current_dir / "scripts"
sys.path.insert(0, str(scripts_dir))

try:
    # Import the existing enhanced MCP server
    from enhanced_mcp_server_main import EnhancedMCPServer, AIConfig
    from mcp_universal_document_converter import UniversalDocumentConverter
except ImportError as e:
    print(f"Error importing MCP server modules: {e}")
    print("Please ensure all dependencies are installed.")
    sys.exit(1)


def create_server(workspace: Optional[str] = None, ai_enabled: bool = False) -> EnhancedMCPServer:
    """
    Create and configure the MCP server instance
    
    Args:
        workspace: Optional workspace path (defaults to current directory)
        ai_enabled: Whether to enable AI features
        
    Returns:
        Configured EnhancedMCPServer instance
    """
    if workspace is None:
        workspace = os.getcwd()
    
    ai_config = AIConfig(enabled=ai_enabled)
    server = EnhancedMCPServer(workspace, ai_config)
    return server


def main():
    """Main entry point for the MCP server"""
    parser = argparse.ArgumentParser(
        description="Universal Document Converter MCP Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run MCP server (default mode)
  universal-document-mcp

  # Run with specific workspace
  universal-document-mcp --workspace /path/to/workspace

  # Enable AI features
  universal-document-mcp --ai-enabled

  # Quick conversion mode
  universal-document-mcp --convert document.md

  # Show version
  universal-document-mcp --version
        """
    )
    
    parser.add_argument("--workspace", 
                       help="Workspace directory path (default: current directory)")
    parser.add_argument("--ai-enabled", action="store_true",
                       help="Enable AI-powered features")
    parser.add_argument("--convert", metavar="FILE",
                       help="Quick conversion mode for specified markdown file")
    parser.add_argument("--version", action="version", 
                       version="Universal Document Converter MCP Server v1.0.0")
    parser.add_argument("--debug", action="store_true",
                       help="Enable debug logging")
    
    args = parser.parse_args()
    
    # Set up logging level
    if args.debug:
        import logging
        logging.basicConfig(level=logging.DEBUG)
    
    # Handle quick conversion mode
    if args.convert:
        converter = UniversalDocumentConverter()
        result = asyncio.run(converter.convert_document(args.convert))
        if result["success"]:
            print(f"✅ Conversion successful: {result['output_file']}")
            sys.exit(0)
        else:
            print(f"❌ Conversion failed: {result['error']}")
            sys.exit(1)
    
    # Create and run the MCP server
    try:
        server = create_server(
            workspace=args.workspace,
            ai_enabled=args.ai_enabled
        )
        print("🚀 Starting Universal Document Converter MCP Server...")
        print(f"📁 Workspace: {server.workspace_root}")
        print(f"🤖 AI Features: {'Enabled' if args.ai_enabled else 'Disabled'}")
        print("📡 Listening for MCP requests...")
        
        asyncio.run(server.run())
        
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Server error: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
