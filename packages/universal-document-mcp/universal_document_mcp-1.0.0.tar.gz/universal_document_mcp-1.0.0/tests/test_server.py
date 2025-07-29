"""
Tests for the MCP server functionality
"""

import pytest
import asyncio
from unittest.mock import Mock, patch
from universal_document_mcp.server import create_server, main


class TestMCPServer:
    """Test cases for MCP server functionality"""
    
    def test_create_server_default(self):
        """Test creating server with default parameters"""
        server = create_server()
        assert server is not None
        assert hasattr(server, 'workspace_root')
    
    def test_create_server_with_workspace(self):
        """Test creating server with custom workspace"""
        workspace = "/test/workspace"
        server = create_server(workspace=workspace)
        assert server is not None
    
    def test_create_server_with_ai_enabled(self):
        """Test creating server with AI features enabled"""
        server = create_server(ai_enabled=True)
        assert server is not None
    
    @patch('sys.argv', ['universal-document-mcp', '--version'])
    def test_main_version(self):
        """Test main function with version argument"""
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 0
    
    @patch('sys.argv', ['universal-document-mcp', '--convert', 'test.md'])
    @patch('universal_document_mcp.server.UniversalDocumentConverter')
    @patch('universal_document_mcp.server.asyncio.run')
    def test_main_convert_mode(self, mock_asyncio_run, mock_converter_class):
        """Test main function in convert mode"""
        # Mock the converter
        mock_converter = Mock()
        mock_converter.convert_document.return_value = {
            "success": True,
            "output_file": "test.pdf"
        }
        mock_converter_class.return_value = mock_converter
        
        # Mock asyncio.run to return the result directly
        mock_asyncio_run.return_value = {
            "success": True,
            "output_file": "test.pdf"
        }
        
        with pytest.raises(SystemExit) as exc_info:
            main()
        
        assert exc_info.value.code == 0
        mock_converter_class.assert_called_once()
    
    @patch('sys.argv', ['universal-document-mcp', '--convert', 'test.md'])
    @patch('universal_document_mcp.server.UniversalDocumentConverter')
    @patch('universal_document_mcp.server.asyncio.run')
    def test_main_convert_mode_failure(self, mock_asyncio_run, mock_converter_class):
        """Test main function in convert mode with failure"""
        # Mock the converter to return failure
        mock_converter = Mock()
        mock_converter_class.return_value = mock_converter
        
        # Mock asyncio.run to return failure result
        mock_asyncio_run.return_value = {
            "success": False,
            "error": "Test error"
        }
        
        with pytest.raises(SystemExit) as exc_info:
            main()
        
        assert exc_info.value.code == 1
    
    @patch('sys.argv', ['universal-document-mcp'])
    @patch('universal_document_mcp.server.create_server')
    @patch('universal_document_mcp.server.asyncio.run')
    def test_main_server_mode(self, mock_asyncio_run, mock_create_server):
        """Test main function in server mode"""
        # Mock the server
        mock_server = Mock()
        mock_server.workspace_root = "/test"
        mock_create_server.return_value = mock_server
        
        # Mock KeyboardInterrupt to simulate user stopping server
        mock_asyncio_run.side_effect = KeyboardInterrupt()
        
        with pytest.raises(SystemExit) as exc_info:
            main()
        
        assert exc_info.value.code == 0
        mock_create_server.assert_called_once()
    
    @patch('sys.argv', ['universal-document-mcp', '--debug'])
    @patch('universal_document_mcp.server.logging.basicConfig')
    @patch('universal_document_mcp.server.create_server')
    @patch('universal_document_mcp.server.asyncio.run')
    def test_main_debug_mode(self, mock_asyncio_run, mock_create_server, mock_logging):
        """Test main function with debug logging enabled"""
        # Mock the server
        mock_server = Mock()
        mock_server.workspace_root = "/test"
        mock_create_server.return_value = mock_server
        
        # Mock KeyboardInterrupt to simulate user stopping server
        mock_asyncio_run.side_effect = KeyboardInterrupt()
        
        with pytest.raises(SystemExit) as exc_info:
            main()
        
        assert exc_info.value.code == 0
        # Verify debug logging was configured
        mock_logging.assert_called_once()


class TestServerIntegration:
    """Integration tests for server functionality"""
    
    @pytest.mark.asyncio
    async def test_server_creation_and_basic_functionality(self):
        """Test that server can be created and has basic functionality"""
        server = create_server()
        
        # Check that server has required attributes
        assert hasattr(server, 'workspace_root')
        assert hasattr(server, 'run')
        
        # Check that server can be configured
        assert server is not None


if __name__ == "__main__":
    pytest.main([__file__])
