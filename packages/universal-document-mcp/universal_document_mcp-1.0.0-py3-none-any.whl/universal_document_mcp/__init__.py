"""
Universal Document Converter MCP Server
AI-powered markdown to PDF conversion with Mermaid diagram support
"""

__version__ = "1.0.0"
__author__ = "AUGMENT AI Assistant"
__email__ = "support@augment.ai"
__license__ = "MIT"

from .server import create_server, main

__all__ = ["create_server", "main", "__version__"]
