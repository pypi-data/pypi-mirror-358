# Changelog

All notable changes to the Universal Document Converter MCP Server will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-01-26

### Added

#### Core Features
- Universal document conversion: Markdown → HTML → PDF
- Intelligent Mermaid diagram optimization for PDF rendering
- AI-powered layout optimization with intelligent page breaks
- Cross-platform support (Windows, macOS, Linux)

#### MCP Integration
- Full MCP (Model Context Protocol) server implementation
- Support for Claude Desktop, Cline, Roo, Continue, and Zed Editor
- Automatic configuration generation for all supported applications
- Real-time document conversion through MCP tools

#### Installation & Setup
- Multiple installation methods: Python (pip) and Node.js (npm)
- Interactive setup wizard for guided installation
- Cross-platform installation scripts (PowerShell for Windows, Bash for Unix)
- Automatic dependency management and Playwright browser installation

#### Configuration Management
- Auto-detection and configuration of MCP-compatible applications
- Manual configuration options for advanced users
- Environment variable support for customization
- Workspace-aware operation with relative path support

#### Command Line Interface
- Comprehensive CLI with multiple operation modes
- Quick conversion mode for standalone document processing
- Configuration management and status checking
- Debug and logging capabilities

#### Developer Features
- Modular architecture with clean separation of concerns
- Comprehensive error handling and logging
- Development mode installation support
- Extensible plugin architecture for future enhancements

### Technical Details

#### Dependencies
- Python 3.8+ support with backward compatibility
- Playwright for reliable PDF generation
- Markdown processing with extension support
- MCP protocol implementation
- Cross-spawn for cross-platform process management

#### Architecture
- Async/await pattern for non-blocking operations
- JSON-RPC 2.0 protocol compliance
- Modular converter system with pluggable components
- Resource management for workspace file access

#### Security
- Workspace sandboxing for file operations
- Input validation and sanitization
- Safe subprocess execution
- Environment variable isolation

### Configuration Files Generated

- `claude-desktop.json` - Claude Desktop MCP configuration
- `cline-vscode.json` - Cline VS Code extension configuration
- `roo.json` - Roo application configuration
- `continue.json` - Continue extension configuration
- `zed.json` - Zed Editor configuration
- `generic-mcp.json` - Generic MCP client configuration

### Installation Scripts

- `install.sh` - Unix/Linux/macOS installation script
- `install.ps1` - Windows PowerShell installation script
- `setup-wizard.js` - Interactive Node.js setup wizard
- `generate-mcp-configs.js` - Configuration file generator
- `show-config.js` - System status and configuration viewer

### Package Management

#### Python Package
- `setup.py` - Traditional setuptools configuration
- `pyproject.toml` - Modern Python packaging configuration
- `requirements-mcp.txt` - MCP-specific dependencies
- Entry points for command-line tools
- Optional dependencies for AI features and development

#### Node.js Package
- `package.json` - npm package configuration with global installation support
- Binary wrappers for cross-platform execution
- Automatic Python package installation
- Development and production dependency management

### Documentation

- Comprehensive README with quick start guide
- Detailed installation instructions (INSTALL.md)
- Configuration examples for all supported applications
- Troubleshooting guide with common issues and solutions
- API documentation for developers

### Known Issues

- None at initial release

### Migration Notes

This is the initial release, so no migration is required.

### Contributors

- AUGMENT AI Assistant - Initial development and architecture

### Acknowledgments

- MCP Protocol team for the Model Context Protocol specification
- Playwright team for reliable PDF generation capabilities
- Mermaid.js team for diagram rendering support
- Open source community for various dependencies and tools

---

## Release Notes

### v1.0.0 Release Highlights

This initial release establishes the Universal Document Converter MCP Server as a comprehensive solution for AI-powered document conversion. Key highlights include:

1. **Universal Compatibility**: Works seamlessly with all major MCP-compatible applications
2. **Intelligent Processing**: AI-powered optimization for professional document output
3. **Easy Installation**: Multiple installation methods with automated setup
4. **Cross-Platform**: Native support for Windows, macOS, and Linux
5. **Developer Friendly**: Clean architecture and comprehensive documentation

### Future Roadmap

Planned features for upcoming releases:
- Additional output formats (DOCX, HTML, etc.)
- Enhanced AI features with more model options
- Plugin system for custom converters
- Web interface for browser-based usage
- Batch processing capabilities
- Template system for consistent formatting
- Integration with cloud storage services

### Support

For support, bug reports, or feature requests:
- GitHub Issues: https://github.com/augment-ai/universal-document-mcp/issues
- GitHub Discussions: https://github.com/augment-ai/universal-document-mcp/discussions
- Documentation: https://github.com/augment-ai/universal-document-mcp/wiki
