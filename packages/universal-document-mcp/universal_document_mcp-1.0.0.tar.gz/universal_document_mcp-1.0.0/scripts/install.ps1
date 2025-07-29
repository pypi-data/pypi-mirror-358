# Universal Document Converter MCP Server Installation Script (Windows PowerShell)

param(
    [switch]$SkipNode,
    [switch]$Verbose
)

# Configuration
$PackageName = "universal-document-mcp"
$PythonMinVersion = [Version]"3.8.0"
$NodeMinVersion = [Version]"18.0.0"

# Colors for output
$Colors = @{
    Red = "Red"
    Green = "Green" 
    Yellow = "Yellow"
    Blue = "Blue"
    White = "White"
}

function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Colors[$Color]
}

function Test-CommandExists {
    param([string]$Command)
    $null -ne (Get-Command $Command -ErrorAction SilentlyContinue)
}

function Get-PythonCommand {
    $pythonCommands = @("python", "python3", "py")
    
    foreach ($cmd in $pythonCommands) {
        if (Test-CommandExists $cmd) {
            try {
                $version = & $cmd --version 2>&1
                if ($version -match "Python (\d+\.\d+\.\d+)") {
                    $pythonVersion = [Version]$matches[1]
                    if ($pythonVersion -ge $PythonMinVersion) {
                        return @{
                            Command = $cmd
                            Version = $pythonVersion
                        }
                    }
                }
            }
            catch {
                continue
            }
        }
    }
    return $null
}

function Test-NodeVersion {
    if (-not (Test-CommandExists "node")) {
        return $false
    }
    
    try {
        $nodeVersionOutput = node --version
        $nodeVersion = [Version]($nodeVersionOutput -replace "v", "")
        return $nodeVersion -ge $NodeMinVersion
    }
    catch {
        return $false
    }
}

function Install-PythonPackage {
    param([string]$PythonCmd)
    
    Write-ColorOutput "📦 Installing Python package..." "Blue"
    
    try {
        & $PythonCmd -m pip install $PackageName
        Write-ColorOutput "✅ Python package installed successfully" "Green"
        
        # Install Playwright browsers
        Write-ColorOutput "🎭 Installing Playwright browsers..." "Blue"
        & $PythonCmd -m playwright install chromium
        Write-ColorOutput "✅ Playwright browsers installed" "Green"
    }
    catch {
        Write-ColorOutput "❌ Failed to install Python package: $_" "Red"
        exit 1
    }
}

function Install-NodePackage {
    if ($SkipNode) {
        Write-ColorOutput "⏭️  Skipping Node.js package installation" "Yellow"
        return
    }
    
    if (Test-NodeVersion) {
        Write-ColorOutput "📦 Installing Node.js package..." "Blue"
        try {
            npm install -g $PackageName
            Write-ColorOutput "✅ Node.js package installed successfully" "Green"
        }
        catch {
            Write-ColorOutput "⚠️  Warning: Failed to install Node.js package: $_" "Yellow"
        }
    }
    else {
        Write-ColorOutput "⚠️  Node.js not found or version too old (need $NodeMinVersion+)" "Yellow"
    }
}

function New-ConfigurationFiles {
    Write-ColorOutput "⚙️  Generating configuration files..." "Blue"
    
    # Create config directory
    $configDir = Join-Path $env:USERPROFILE ".config\mcp-servers"
    if (-not (Test-Path $configDir)) {
        New-Item -ItemType Directory -Path $configDir -Force | Out-Null
    }
    
    # Claude Desktop configuration
    $claudeConfig = @{
        mcpServers = @{
            "universal-document-converter" = @{
                command = "python"
                args = @("-m", "universal_document_mcp.server")
                env = @{
                    PYTHONPATH = "."
                    LOG_LEVEL = "INFO"
                }
            }
        }
    }
    
    $claudeConfigPath = Join-Path $configDir "claude-desktop.json"
    $claudeConfig | ConvertTo-Json -Depth 10 | Out-File -FilePath $claudeConfigPath -Encoding UTF8
    Write-ColorOutput "   ✅ Claude Desktop config: $claudeConfigPath" "Green"
    
    # Generic MCP configuration
    $genericConfig = @{
        name = "universal-document-converter"
        command = "python"
        args = @("-m", "universal_document_mcp.server")
        description = "Universal Document Converter MCP Server"
    }
    
    $genericConfigPath = Join-Path $configDir "universal-document-converter.json"
    $genericConfig | ConvertTo-Json -Depth 10 | Out-File -FilePath $genericConfigPath -Encoding UTF8
    Write-ColorOutput "   ✅ Generic MCP config: $genericConfigPath" "Green"
    
    return $configDir
}

function Test-Installation {
    param([string]$PythonCmd)
    
    Write-ColorOutput "🧪 Testing installation..." "Blue"
    
    try {
        & $PythonCmd -c "import universal_document_mcp; print('✅ Python package import successful')"
        Write-ColorOutput "✅ Python package test passed" "Green"
    }
    catch {
        Write-ColorOutput "❌ Python package test failed: $_" "Red"
        exit 1
    }
    
    if (Test-CommandExists "universal-document-mcp") {
        Write-ColorOutput "✅ Command-line tool available" "Green"
    }
    else {
        Write-ColorOutput "⚠️  Command-line tool not in PATH" "Yellow"
    }
}

# Main installation process
function Main {
    Write-ColorOutput "🚀 Universal Document Converter MCP Server Installation" "Blue"
    Write-ColorOutput "==================================================" "Blue"
    
    # Check Python
    Write-ColorOutput "🐍 Checking Python installation..." "Blue"
    $pythonInfo = Get-PythonCommand
    
    if ($null -eq $pythonInfo) {
        Write-ColorOutput "❌ Python $PythonMinVersion+ not found. Please install Python first." "Red"
        Write-ColorOutput "   Download from: https://www.python.org/downloads/" "Yellow"
        exit 1
    }
    
    Write-ColorOutput "✅ Python $($pythonInfo.Version) found" "Green"
    
    # Check Node.js (optional)
    Write-ColorOutput "📦 Checking Node.js installation..." "Blue"
    if (Test-NodeVersion) {
        $nodeVersion = (node --version) -replace "v", ""
        Write-ColorOutput "✅ Node.js $nodeVersion found" "Green"
    }
    else {
        Write-ColorOutput "⚠️  Node.js not found or version too old (optional)" "Yellow"
    }
    
    # Install packages
    Install-PythonPackage -PythonCmd $pythonInfo.Command
    Install-NodePackage
    
    # Generate configurations
    $configDir = New-ConfigurationFiles
    
    # Test installation
    Test-Installation -PythonCmd $pythonInfo.Command
    
    # Success message
    Write-ColorOutput "" "White"
    Write-ColorOutput "🎉 Installation completed successfully!" "Green"
    Write-ColorOutput "" "White"
    Write-ColorOutput "Usage:" "Blue"
    Write-ColorOutput "  # Start MCP server" "White"
    Write-ColorOutput "  universal-document-mcp" "White"
    Write-ColorOutput "" "White"
    Write-ColorOutput "  # Quick conversion" "White"
    Write-ColorOutput "  universal-document-mcp --convert document.md" "White"
    Write-ColorOutput "" "White"
    Write-ColorOutput "  # Generate configuration files" "White"
    Write-ColorOutput "  universal-document-mcp --generate-configs" "White"
    Write-ColorOutput "" "White"
    Write-ColorOutput "Configuration files generated in: $configDir" "Blue"
    Write-ColorOutput "" "White"
    Write-ColorOutput "Next steps:" "Yellow"
    Write-ColorOutput "1. Configure your MCP client (Claude Desktop, Cline, etc.)" "White"
    Write-ColorOutput "2. Copy the appropriate config file to your client's configuration" "White"
    Write-ColorOutput "3. Restart your MCP client" "White"
    Write-ColorOutput "" "White"
}

# Run main function
try {
    Main
}
catch {
    Write-ColorOutput "❌ Installation failed: $_" "Red"
    if ($Verbose) {
        Write-ColorOutput $_.ScriptStackTrace "Red"
    }
    exit 1
}
