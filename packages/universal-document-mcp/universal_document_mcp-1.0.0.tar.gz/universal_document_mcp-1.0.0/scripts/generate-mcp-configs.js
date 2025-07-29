#!/usr/bin/env node

/**
 * Generate MCP configuration files for various applications
 */

import fs from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';
import os from 'os';
import chalk from 'chalk';
import inquirer from 'inquirer';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const packageRoot = path.join(__dirname, '..');

class MCPConfigGenerator {
    constructor() {
        this.configTemplates = {
            'claude-desktop': {
                name: 'Claude Desktop',
                filename: 'claude-desktop.json',
                path: this.getClaudeDesktopConfigPath(),
                template: this.getClaudeDesktopTemplate()
            },
            'cline-vscode': {
                name: 'Cline (VS Code)',
                filename: 'cline-mcp-config.json',
                path: this.getVSCodeConfigPath(),
                template: this.getClineTemplate()
            },
            'roo': {
                name: 'Roo',
                filename: 'roo-mcp-config.json',
                path: path.join(os.homedir(), '.config', 'roo'),
                template: this.getRooTemplate()
            },
            'continue': {
                name: 'Continue',
                filename: 'continue-mcp-config.json',
                path: path.join(os.homedir(), '.continue'),
                template: this.getContinueTemplate()
            },
            'zed': {
                name: 'Zed Editor',
                filename: 'zed-mcp-config.json',
                path: this.getZedConfigPath(),
                template: this.getZedTemplate()
            }
        };
    }

    getClaudeDesktopConfigPath() {
        switch (process.platform) {
            case 'darwin':
                return path.join(os.homedir(), 'Library', 'Application Support', 'Claude');
            case 'win32':
                return path.join(os.homedir(), 'AppData', 'Roaming', 'Claude');
            default:
                return path.join(os.homedir(), '.config', 'claude');
        }
    }

    getVSCodeConfigPath() {
        switch (process.platform) {
            case 'darwin':
                return path.join(os.homedir(), 'Library', 'Application Support', 'Code', 'User');
            case 'win32':
                return path.join(os.homedir(), 'AppData', 'Roaming', 'Code', 'User');
            default:
                return path.join(os.homedir(), '.config', 'Code', 'User');
        }
    }

    getZedConfigPath() {
        switch (process.platform) {
            case 'darwin':
                return path.join(os.homedir(), 'Library', 'Application Support', 'Zed');
            case 'win32':
                return path.join(os.homedir(), 'AppData', 'Roaming', 'Zed');
            default:
                return path.join(os.homedir(), '.config', 'zed');
        }
    }

    getClaudeDesktopTemplate() {
        return {
            mcpServers: {
                "universal-document-converter": {
                    command: "python",
                    args: ["-m", "universal_document_mcp.server"],
                    env: {
                        PYTHONPATH: ".",
                        LOG_LEVEL: "INFO"
                    }
                }
            }
        };
    }

    getClineTemplate() {
        return {
            mcpServers: {
                "universal-document-converter": {
                    command: "python",
                    args: ["-m", "universal_document_mcp.server"],
                    cwd: "${workspaceFolder}",
                    env: {
                        PYTHONPATH: "${workspaceFolder}",
                        LOG_LEVEL: "INFO",
                        WORKSPACE_ROOT: "${workspaceFolder}"
                    }
                }
            }
        };
    }

    getRooTemplate() {
        return {
            servers: {
                "universal-document-converter": {
                    command: "python",
                    args: ["-m", "universal_document_mcp.server"],
                    env: {
                        PYTHONPATH: ".",
                        LOG_LEVEL: "INFO"
                    }
                }
            }
        };
    }

    getContinueTemplate() {
        return {
            mcpServers: {
                "universal-document-converter": {
                    command: "python",
                    args: ["-m", "universal_document_mcp.server"],
                    env: {
                        PYTHONPATH: ".",
                        LOG_LEVEL: "INFO"
                    }
                }
            }
        };
    }

    getZedTemplate() {
        return {
            mcp_servers: {
                "universal-document-converter": {
                    command: "python",
                    args: ["-m", "universal_document_mcp.server"],
                    env: {
                        PYTHONPATH: ".",
                        LOG_LEVEL: "INFO"
                    }
                }
            }
        };
    }

    async generateConfig(appKey, options = {}) {
        const config = this.configTemplates[appKey];
        if (!config) {
            throw new Error(`Unknown application: ${appKey}`);
        }

        const { outputPath, merge = false } = options;
        const targetPath = outputPath || path.join(config.path, config.filename);
        
        try {
            // Ensure directory exists
            await fs.mkdir(path.dirname(targetPath), { recursive: true });

            let finalConfig = config.template;

            // If merge is requested and file exists, merge configurations
            if (merge) {
                try {
                    const existingContent = await fs.readFile(targetPath, 'utf8');
                    const existingConfig = JSON.parse(existingContent);
                    
                    // Simple merge - add our server to existing config
                    if (existingConfig.mcpServers) {
                        existingConfig.mcpServers['universal-document-converter'] = 
                            finalConfig.mcpServers['universal-document-converter'];
                        finalConfig = existingConfig;
                    } else if (existingConfig.servers) {
                        existingConfig.servers['universal-document-converter'] = 
                            finalConfig.servers['universal-document-converter'];
                        finalConfig = existingConfig;
                    }
                } catch (error) {
                    // If file doesn't exist or can't be parsed, use new config
                    console.log(chalk.yellow(`⚠️  Could not merge with existing config: ${error.message}`));
                }
            }

            // Write configuration file
            await fs.writeFile(targetPath, JSON.stringify(finalConfig, null, 2), 'utf8');
            
            return {
                success: true,
                path: targetPath,
                app: config.name
            };
        } catch (error) {
            return {
                success: false,
                error: error.message,
                app: config.name
            };
        }
    }

    async generateAllConfigs(options = {}) {
        const results = [];
        
        for (const [appKey, config] of Object.entries(this.configTemplates)) {
            console.log(chalk.blue(`📝 Generating ${config.name} configuration...`));
            
            const result = await this.generateConfig(appKey, options);
            results.push(result);
            
            if (result.success) {
                console.log(chalk.green(`✅ ${result.app}: ${result.path}`));
            } else {
                console.log(chalk.red(`❌ ${result.app}: ${result.error}`));
            }
        }
        
        return results;
    }

    async interactiveGeneration() {
        console.log(chalk.blue('🔧 Interactive MCP Configuration Generator'));
        console.log('==========================================\n');

        const { selectedApps } = await inquirer.prompt([
            {
                type: 'checkbox',
                name: 'selectedApps',
                message: 'Select applications to generate configurations for:',
                choices: Object.entries(this.configTemplates).map(([key, config]) => ({
                    name: config.name,
                    value: key,
                    checked: true
                }))
            }
        ]);

        if (selectedApps.length === 0) {
            console.log(chalk.yellow('No applications selected. Exiting.'));
            return;
        }

        const { merge, customPath } = await inquirer.prompt([
            {
                type: 'confirm',
                name: 'merge',
                message: 'Merge with existing configurations (if they exist)?',
                default: true
            },
            {
                type: 'input',
                name: 'customPath',
                message: 'Custom output directory (leave empty for default locations):',
                default: ''
            }
        ]);

        console.log('\n' + chalk.blue('Generating configurations...'));
        
        const results = [];
        for (const appKey of selectedApps) {
            const config = this.configTemplates[appKey];
            console.log(chalk.blue(`📝 Generating ${config.name} configuration...`));
            
            const options = { merge };
            if (customPath) {
                options.outputPath = path.join(customPath, config.filename);
            }
            
            const result = await this.generateConfig(appKey, options);
            results.push(result);
            
            if (result.success) {
                console.log(chalk.green(`✅ ${result.app}: ${result.path}`));
            } else {
                console.log(chalk.red(`❌ ${result.app}: ${result.error}`));
            }
        }

        // Summary
        const successful = results.filter(r => r.success).length;
        const failed = results.filter(r => !r.success).length;
        
        console.log('\n' + chalk.blue('Summary:'));
        console.log(chalk.green(`✅ Successfully generated: ${successful}`));
        if (failed > 0) {
            console.log(chalk.red(`❌ Failed: ${failed}`));
        }
        
        console.log('\n' + chalk.yellow('Next steps:'));
        console.log('1. Restart your MCP-compatible applications');
        console.log('2. The Universal Document Converter should now be available');
        console.log('3. Test by asking to convert a markdown file to PDF');
    }
}

export async function generateMCPConfigs(options = {}) {
    const generator = new MCPConfigGenerator();

    if (options.interactive) {
        await generator.interactiveGeneration();
    } else {
        await generator.generateAllConfigs(options);
    }
}

// CLI usage
if (import.meta.url === `file://${process.argv[1]}`) {
    const generator = new MCPConfigGenerator();
    await generator.interactiveGeneration();
}
