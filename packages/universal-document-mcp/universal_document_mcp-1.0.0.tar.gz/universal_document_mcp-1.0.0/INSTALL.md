# Installation Guide

This guide provides detailed installation instructions for the Universal Document Converter MCP Server.

## Prerequisites

### System Requirements

- **Python**: 3.8 or higher
- **Node.js**: 18.0 or higher (optional, for npm installation)
- **Operating System**: Windows 10+, macOS 10.14+, or Linux

### Required Tools

- Git (for development installation)
- pip (Python package manager)
- npm (Node.js package manager, optional)

## Installation Methods

### Method 1: Interactive Setup (Recommended)

The interactive setup wizard will guide you through the entire installation process:

```bash
# Using npm (recommended)
npx universal-document-mcp --setup

# Or using Python
pip install universal-document-mcp
python -m universal_document_mcp.server --setup
```

The setup wizard will:
1. Check your system requirements
2. Install the MCP server package
3. Install required dependencies (Playwright browsers)
4. Generate configuration files for detected applications
5. Test the installation

### Method 2: Python Installation

#### Step 1: Install the Package

```bash
pip install universal-document-mcp
```

#### Step 2: Install Playwright Browsers

```bash
python -m playwright install chromium
```

#### Step 3: Generate Configuration Files

```bash
universal-document-mcp --generate-configs
```

### Method 3: Node.js Installation

#### Step 1: Install Globally

```bash
npm install -g universal-document-mcp
```

#### Step 2: Run Setup

```bash
universal-document-mcp --setup
```

### Method 4: Development Installation

For developers who want to contribute or modify the code:

```bash
# Clone the repository
git clone https://github.com/augment-ai/universal-document-mcp.git
cd universal-document-mcp

# Install in development mode
pip install -e .

# Install development dependencies
pip install -e .[dev]

# Install Playwright browsers
python -m playwright install chromium
```

## Platform-Specific Instructions

### Windows

#### Using PowerShell (Recommended)

```powershell
# Download and run the installation script
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/augment-ai/universal-document-mcp/main/scripts/install.ps1" -OutFile "install.ps1"
.\install.ps1
```

#### Manual Installation

```powershell
# Install Python package
pip install universal-document-mcp

# Install Playwright browsers
python -m playwright install chromium

# Generate configurations
universal-document-mcp --generate-configs
```

### macOS

#### Using Homebrew (if you have it)

```bash
# Ensure Python 3.8+ is installed
brew install python@3.11

# Install the package
pip3 install universal-document-mcp

# Run setup
universal-document-mcp --setup
```

#### Using the Installation Script

```bash
# Download and run the installation script
curl -sSL https://raw.githubusercontent.com/augment-ai/universal-document-mcp/main/scripts/install.sh | bash
```

### Linux

#### Ubuntu/Debian

```bash
# Install Python and pip if not already installed
sudo apt update
sudo apt install python3 python3-pip

# Install the package
pip3 install universal-document-mcp

# Run setup
universal-document-mcp --setup
```

#### CentOS/RHEL/Fedora

```bash
# Install Python and pip if not already installed
sudo dnf install python3 python3-pip

# Install the package
pip3 install universal-document-mcp

# Run setup
universal-document-mcp --setup
```

#### Using the Installation Script

```bash
# Download and run the installation script
curl -sSL https://raw.githubusercontent.com/augment-ai/universal-document-mcp/main/scripts/install.sh | bash
```

## Post-Installation Configuration

### Verify Installation

```bash
# Check installation status
universal-document-mcp --config

# Test with a sample conversion
echo "# Test Document" > test.md
universal-document-mcp --convert test.md
```

### Configure Applications

The installation process automatically generates configuration files for supported applications. You may need to:

1. **Restart your MCP-compatible applications** (Claude Desktop, VS Code with Cline, etc.)
2. **Copy configuration files** to the correct locations if auto-detection failed
3. **Verify the server is detected** in your application's MCP server list

### Manual Configuration

If automatic configuration doesn't work, you can manually configure each application:

#### Claude Desktop

1. Locate your Claude Desktop configuration file:
   - **macOS**: `~/Library/Application Support/Claude/claude-desktop.json`
   - **Windows**: `%APPDATA%/Claude/claude-desktop.json`
   - **Linux**: `~/.config/claude/claude-desktop.json`

2. Add the MCP server configuration:
   ```json
   {
     "mcpServers": {
       "universal-document-converter": {
         "command": "python",
         "args": ["-m", "universal_document_mcp.server"],
         "env": {
           "PYTHONPATH": ".",
           "LOG_LEVEL": "INFO"
         }
       }
     }
   }
   ```

3. Restart Claude Desktop

#### Cline (VS Code)

1. Open VS Code settings (Ctrl/Cmd + ,)
2. Search for "Cline MCP"
3. Add the server configuration or edit the JSON settings directly

## Troubleshooting

### Common Issues

#### "Command not found" Error

If you get a "command not found" error:

1. **Check if the package is installed**: `pip list | grep universal-document-mcp`
2. **Check your PATH**: The installation directory might not be in your PATH
3. **Try using the full Python module path**: `python -m universal_document_mcp.server`

#### Permission Errors

On Windows or macOS, you might encounter permission errors:

```bash
# Windows: Run as Administrator or use --user flag
pip install --user universal-document-mcp

# macOS/Linux: Use --user flag or virtual environment
pip install --user universal-document-mcp
```

#### Playwright Installation Issues

If Playwright browser installation fails:

```bash
# Try installing manually
python -m playwright install chromium

# Or install system dependencies (Linux)
sudo apt install libnss3 libatk-bridge2.0-0 libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 libxrandr2 libgbm1 libxss1 libasound2
```

#### Python Version Issues

Ensure you're using Python 3.8 or higher:

```bash
python --version
# or
python3 --version
```

If you have multiple Python versions, you might need to use `python3` and `pip3` instead of `python` and `pip`.

### Getting Help

If you encounter issues:

1. **Check the status**: `universal-document-mcp --config`
2. **Enable debug logging**: Set `LOG_LEVEL=DEBUG` environment variable
3. **Check the logs**: Look for error messages in the console output
4. **Test with a simple file**: Try converting a basic markdown file
5. **Regenerate configurations**: Run `universal-document-mcp --generate-configs`

For additional support:
- **GitHub Issues**: [Report bugs or request features](https://github.com/augment-ai/universal-document-mcp/issues)
- **Discussions**: [Ask questions or share tips](https://github.com/augment-ai/universal-document-mcp/discussions)
- **Documentation**: [Read the full documentation](https://github.com/augment-ai/universal-document-mcp/wiki)

## Next Steps

After successful installation:

1. **Test the installation** with a sample markdown file
2. **Configure your preferred MCP applications**
3. **Explore the features** like AI-powered layout optimization
4. **Read the usage guide** for advanced features and customization options

Congratulations! You now have the Universal Document Converter MCP Server installed and ready to use.
