#!/usr/bin/env node

/**
 * Show current MCP server configuration and status
 */

import fs from 'fs/promises';
import path from 'path';
import os from 'os';
import chalk from 'chalk';
import { spawn } from 'child_process';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

class ConfigViewer {
    constructor() {
        this.configPaths = this.getConfigPaths();
    }

    getConfigPaths() {
        const home = os.homedir();
        
        return {
            'claude-desktop': {
                name: 'Claude Desktop',
                paths: [
                    path.join(home, 'Library', 'Application Support', 'Claude', 'claude-desktop.json'), // macOS
                    path.join(home, 'AppData', 'Roaming', 'Claude', 'claude-desktop.json'), // Windows
                    path.join(home, '.config', 'claude', 'claude-desktop.json') // Linux
                ]
            },
            'cline-vscode': {
                name: 'Cline (VS Code)',
                paths: [
                    path.join(home, 'Library', 'Application Support', 'Code', 'User', 'cline-mcp-config.json'), // macOS
                    path.join(home, 'AppData', 'Roaming', 'Code', 'User', 'cline-mcp-config.json'), // Windows
                    path.join(home, '.config', 'Code', 'User', 'cline-mcp-config.json') // Linux
                ]
            },
            'roo': {
                name: 'Roo',
                paths: [
                    path.join(home, '.config', 'roo', 'roo-mcp-config.json')
                ]
            },
            'continue': {
                name: 'Continue',
                paths: [
                    path.join(home, '.continue', 'continue-mcp-config.json')
                ]
            },
            'zed': {
                name: 'Zed Editor',
                paths: [
                    path.join(home, 'Library', 'Application Support', 'Zed', 'zed-mcp-config.json'), // macOS
                    path.join(home, 'AppData', 'Roaming', 'Zed', 'zed-mcp-config.json'), // Windows
                    path.join(home, '.config', 'zed', 'zed-mcp-config.json') // Linux
                ]
            },
            'generic': {
                name: 'Generic MCP',
                paths: [
                    path.join(home, '.config', 'mcp-servers', 'universal-document-converter.json')
                ]
            }
        };
    }

    async checkPythonInstallation() {
        const candidates = ['python3', 'python', 'py'];
        
        for (const cmd of candidates) {
            try {
                const result = await this.runCommand(cmd, ['--version']);
                const match = result.stdout.match(/Python (\d+\.\d+\.\d+)/);
                if (match) {
                    const version = match[1];
                    
                    // Check if our package is installed
                    try {
                        await this.runCommand(cmd, ['-c', 'import universal_document_mcp']);
                        return {
                            command: cmd,
                            version,
                            packageInstalled: true
                        };
                    } catch (error) {
                        return {
                            command: cmd,
                            version,
                            packageInstalled: false
                        };
                    }
                }
            } catch (error) {
                continue;
            }
        }
        return null;
    }

    async checkNodeInstallation() {
        try {
            const versionResult = await this.runCommand('node', ['--version']);
            const version = versionResult.stdout.trim().replace('v', '');
            
            // Check if our package is installed globally
            try {
                await this.runCommand('npm', ['list', '-g', 'universal-document-mcp']);
                return {
                    version,
                    packageInstalled: true
                };
            } catch (error) {
                return {
                    version,
                    packageInstalled: false
                };
            }
        } catch (error) {
            return null;
        }
    }

    async runCommand(command, args) {
        return new Promise((resolve, reject) => {
            const process = spawn(command, args, { stdio: 'pipe' });
            let stdout = '';
            let stderr = '';

            process.stdout.on('data', (data) => {
                stdout += data.toString();
            });

            process.stderr.on('data', (data) => {
                stderr += data.toString();
            });

            process.on('close', (code) => {
                if (code === 0) {
                    resolve({ stdout, stderr });
                } else {
                    reject(new Error(`Command failed with code ${code}: ${stderr}`));
                }
            });
        });
    }

    async findConfigFile(paths) {
        for (const configPath of paths) {
            try {
                await fs.access(configPath);
                return configPath;
            } catch (error) {
                continue;
            }
        }
        return null;
    }

    async readConfig(configPath) {
        try {
            const content = await fs.readFile(configPath, 'utf8');
            return JSON.parse(content);
        } catch (error) {
            return null;
        }
    }

    async checkApplicationConfigs() {
        const results = {};
        
        for (const [key, config] of Object.entries(this.configPaths)) {
            const configPath = await this.findConfigFile(config.paths);
            
            if (configPath) {
                const configData = await this.readConfig(configPath);
                const hasOurServer = this.checkForOurServer(configData);
                
                results[key] = {
                    name: config.name,
                    path: configPath,
                    configured: hasOurServer,
                    config: configData
                };
            } else {
                results[key] = {
                    name: config.name,
                    path: null,
                    configured: false,
                    config: null
                };
            }
        }
        
        return results;
    }

    checkForOurServer(config) {
        if (!config) return false;
        
        // Check different config formats
        if (config.mcpServers && config.mcpServers['universal-document-converter']) {
            return true;
        }
        if (config.servers && config.servers['universal-document-converter']) {
            return true;
        }
        if (config.mcp_servers && config.mcp_servers['universal-document-converter']) {
            return true;
        }
        
        return false;
    }

    async showSystemInfo() {
        console.log(chalk.blue.bold('🖥️  System Information'));
        console.log(chalk.blue('====================='));
        
        console.log(chalk.white(`Platform: ${process.platform}`));
        console.log(chalk.white(`Architecture: ${process.arch}`));
        console.log(chalk.white(`Node.js: ${process.version}`));
        console.log(chalk.white(`Home Directory: ${os.homedir()}`));
        console.log();
    }

    async showInstallationStatus() {
        console.log(chalk.blue.bold('📦 Installation Status'));
        console.log(chalk.blue('======================'));
        
        // Check Python
        const pythonInfo = await this.checkPythonInstallation();
        if (pythonInfo) {
            console.log(chalk.green(`✅ Python: ${pythonInfo.version} (${pythonInfo.command})`));
            if (pythonInfo.packageInstalled) {
                console.log(chalk.green('✅ Python package: Installed'));
            } else {
                console.log(chalk.red('❌ Python package: Not installed'));
                console.log(chalk.yellow('   Install with: pip install universal-document-mcp'));
            }
        } else {
            console.log(chalk.red('❌ Python: Not found or version too old'));
        }
        
        // Check Node.js
        const nodeInfo = await this.checkNodeInstallation();
        if (nodeInfo) {
            console.log(chalk.green(`✅ Node.js: ${nodeInfo.version}`));
            if (nodeInfo.packageInstalled) {
                console.log(chalk.green('✅ Node.js package: Installed'));
            } else {
                console.log(chalk.yellow('⚠️  Node.js package: Not installed globally'));
                console.log(chalk.yellow('   Install with: npm install -g universal-document-mcp'));
            }
        } else {
            console.log(chalk.yellow('⚠️  Node.js: Not found (optional)'));
        }
        
        console.log();
    }

    async showApplicationConfigs() {
        console.log(chalk.blue.bold('🔧 Application Configurations'));
        console.log(chalk.blue('=============================='));
        
        const configs = await this.checkApplicationConfigs();
        
        for (const [key, info] of Object.entries(configs)) {
            if (info.configured) {
                console.log(chalk.green(`✅ ${info.name}`));
                console.log(chalk.gray(`   Config: ${info.path}`));
            } else if (info.path) {
                console.log(chalk.yellow(`⚠️  ${info.name}`));
                console.log(chalk.gray(`   Config exists but server not configured: ${info.path}`));
            } else {
                console.log(chalk.red(`❌ ${info.name}`));
                console.log(chalk.gray('   No configuration file found'));
            }
        }
        
        console.log();
    }

    async showUsageInstructions() {
        console.log(chalk.blue.bold('📖 Usage Instructions'));
        console.log(chalk.blue('====================='));
        
        console.log(chalk.white('Command Line:'));
        console.log(chalk.gray('  universal-document-mcp                    # Start MCP server'));
        console.log(chalk.gray('  universal-document-mcp --convert file.md # Quick conversion'));
        console.log(chalk.gray('  universal-document-mcp --setup           # Run setup wizard'));
        console.log();
        
        console.log(chalk.white('In MCP Applications:'));
        console.log(chalk.gray('  "Convert this markdown file to PDF"'));
        console.log(chalk.gray('  "Generate a PDF from document.md"'));
        console.log(chalk.gray('  "Export my markdown with Mermaid diagrams to PDF"'));
        console.log();
    }

    async run() {
        console.log(chalk.blue.bold('\n🔍 Universal Document Converter MCP Server Configuration'));
        console.log(chalk.blue('========================================================\n'));
        
        await this.showSystemInfo();
        await this.showInstallationStatus();
        await this.showApplicationConfigs();
        await this.showUsageInstructions();
    }
}

export async function showConfig() {
    const viewer = new ConfigViewer();
    await viewer.run();
}

// CLI usage
if (import.meta.url === `file://${process.argv[1]}`) {
    await showConfig();
}
