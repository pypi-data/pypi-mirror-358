#!/bin/bash
# Universal Document Converter MCP Server Installation Script (Unix/Linux/macOS)

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PACKAGE_NAME="universal-document-mcp"
PYTHON_MIN_VERSION="3.8"
NODE_MIN_VERSION="18.0"

echo -e "${BLUE}🚀 Universal Document Converter MCP Server Installation${NC}"
echo "=================================================="

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to compare versions
version_ge() {
    printf '%s\n%s\n' "$2" "$1" | sort -V -C
}

# Check Python installation
check_python() {
    echo -e "${BLUE}🐍 Checking Python installation...${NC}"
    
    if command_exists python3; then
        PYTHON_CMD="python3"
    elif command_exists python; then
        PYTHON_CMD="python"
    else
        echo -e "${RED}❌ Python not found. Please install Python ${PYTHON_MIN_VERSION}+ first.${NC}"
        exit 1
    fi
    
    PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | cut -d' ' -f2)
    if version_ge "$PYTHON_VERSION" "$PYTHON_MIN_VERSION"; then
        echo -e "${GREEN}✅ Python ${PYTHON_VERSION} found${NC}"
    else
        echo -e "${RED}❌ Python ${PYTHON_VERSION} is too old. Please install Python ${PYTHON_MIN_VERSION}+${NC}"
        exit 1
    fi
}

# Check Node.js installation (optional)
check_node() {
    echo -e "${BLUE}📦 Checking Node.js installation...${NC}"
    
    if command_exists node; then
        NODE_VERSION=$(node --version | sed 's/v//')
        if version_ge "$NODE_VERSION" "$NODE_MIN_VERSION"; then
            echo -e "${GREEN}✅ Node.js ${NODE_VERSION} found${NC}"
            return 0
        else
            echo -e "${YELLOW}⚠️  Node.js ${NODE_VERSION} is too old (need ${NODE_MIN_VERSION}+)${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  Node.js not found (optional for npm installation)${NC}"
    fi
    return 1
}

# Install Python package
install_python_package() {
    echo -e "${BLUE}📦 Installing Python package...${NC}"
    
    # Install the package
    if $PYTHON_CMD -m pip install "$PACKAGE_NAME"; then
        echo -e "${GREEN}✅ Python package installed successfully${NC}"
    else
        echo -e "${RED}❌ Failed to install Python package${NC}"
        exit 1
    fi
    
    # Install Playwright browsers
    echo -e "${BLUE}🎭 Installing Playwright browsers...${NC}"
    if $PYTHON_CMD -m playwright install chromium; then
        echo -e "${GREEN}✅ Playwright browsers installed${NC}"
    else
        echo -e "${YELLOW}⚠️  Warning: Failed to install Playwright browsers${NC}"
        echo -e "${YELLOW}   You may need to run: $PYTHON_CMD -m playwright install chromium${NC}"
    fi
}

# Install Node.js package (optional)
install_node_package() {
    if check_node; then
        echo -e "${BLUE}📦 Installing Node.js package...${NC}"
        if npm install -g "$PACKAGE_NAME"; then
            echo -e "${GREEN}✅ Node.js package installed successfully${NC}"
        else
            echo -e "${YELLOW}⚠️  Warning: Failed to install Node.js package${NC}"
        fi
    fi
}

# Generate configuration files
generate_configs() {
    echo -e "${BLUE}⚙️  Generating configuration files...${NC}"
    
    # Create config directory in user's home
    CONFIG_DIR="$HOME/.config/mcp-servers"
    mkdir -p "$CONFIG_DIR"
    
    # Generate Claude Desktop config
    if command_exists claude; then
        echo -e "${BLUE}   Generating Claude Desktop configuration...${NC}"
        cat > "$CONFIG_DIR/claude-desktop.json" << 'EOF'
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
EOF
        echo -e "${GREEN}   ✅ Claude Desktop config: $CONFIG_DIR/claude-desktop.json${NC}"
    fi
    
    # Generate generic MCP config
    cat > "$CONFIG_DIR/universal-document-converter.json" << 'EOF'
{
  "name": "universal-document-converter",
  "command": "python",
  "args": ["-m", "universal_document_mcp.server"],
  "description": "Universal Document Converter MCP Server"
}
EOF
    echo -e "${GREEN}   ✅ Generic MCP config: $CONFIG_DIR/universal-document-converter.json${NC}"
}

# Test installation
test_installation() {
    echo -e "${BLUE}🧪 Testing installation...${NC}"
    
    if $PYTHON_CMD -c "import universal_document_mcp; print('✅ Python package import successful')"; then
        echo -e "${GREEN}✅ Python package test passed${NC}"
    else
        echo -e "${RED}❌ Python package test failed${NC}"
        exit 1
    fi
    
    if command_exists universal-document-mcp; then
        echo -e "${GREEN}✅ Command-line tool available${NC}"
    else
        echo -e "${YELLOW}⚠️  Command-line tool not in PATH${NC}"
    fi
}

# Main installation process
main() {
    echo -e "${BLUE}Starting installation process...${NC}"
    
    check_python
    install_python_package
    install_node_package
    generate_configs
    test_installation
    
    echo ""
    echo -e "${GREEN}🎉 Installation completed successfully!${NC}"
    echo ""
    echo -e "${BLUE}Usage:${NC}"
    echo "  # Start MCP server"
    echo "  universal-document-mcp"
    echo ""
    echo "  # Quick conversion"
    echo "  universal-document-mcp --convert document.md"
    echo ""
    echo "  # Generate configuration files"
    echo "  universal-document-mcp --generate-configs"
    echo ""
    echo -e "${BLUE}Configuration files generated in:${NC} $HOME/.config/mcp-servers/"
    echo ""
    echo -e "${YELLOW}Next steps:${NC}"
    echo "1. Configure your MCP client (Claude Desktop, Cline, etc.)"
    echo "2. Copy the appropriate config file to your client's configuration"
    echo "3. Restart your MCP client"
    echo ""
}

# Run main function
main "$@"
