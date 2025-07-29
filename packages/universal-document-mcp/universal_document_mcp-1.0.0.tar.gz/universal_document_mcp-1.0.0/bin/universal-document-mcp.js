#!/usr/bin/env node

/**
 * Universal Document Converter MCP Server
 * Node.js wrapper for system-wide installation
 */

import { spawn } from 'child_process';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import { existsSync } from 'fs';
import { program } from 'commander';
import chalk from 'chalk';
import ora from 'ora';
import which from 'which';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const packageRoot = join(__dirname, '..');

class MCPServerWrapper {
    constructor() {
        this.pythonCmd = null;
        this.packageRoot = packageRoot;
    }

    async findPython() {
        const candidates = ['python3', 'python', 'py'];
        
        for (const cmd of candidates) {
            try {
                const pythonPath = await which(cmd);
                // Verify Python version
                const versionCheck = spawn(cmd, ['--version'], { stdio: 'pipe' });
                
                return new Promise((resolve) => {
                    let output = '';
                    versionCheck.stdout.on('data', (data) => {
                        output += data.toString();
                    });
                    versionCheck.stderr.on('data', (data) => {
                        output += data.toString();
                    });
                    versionCheck.on('close', (code) => {
                        if (code === 0) {
                            const match = output.match(/Python (\d+)\.(\d+)/);
                            if (match) {
                                const major = parseInt(match[1]);
                                const minor = parseInt(match[2]);
                                if (major >= 3 && minor >= 8) {
                                    resolve(pythonPath);
                                    return;
                                }
                            }
                        }
                        resolve(null);
                    });
                });
            } catch (error) {
                continue;
            }
        }
        return null;
    }

    async checkPythonPackage() {
        if (!this.pythonCmd) {
            this.pythonCmd = await this.findPython();
        }
        
        if (!this.pythonCmd) {
            throw new Error('Python 3.8+ not found. Please install Python 3.8 or higher.');
        }

        // Check if the Python package is installed
        const checkProcess = spawn(this.pythonCmd, ['-c', 'import universal_document_mcp'], { stdio: 'pipe' });
        
        return new Promise((resolve) => {
            checkProcess.on('close', (code) => {
                resolve(code === 0);
            });
        });
    }

    async installPythonPackage() {
        const spinner = ora('Installing Python MCP server package...').start();
        
        try {
            if (!this.pythonCmd) {
                this.pythonCmd = await this.findPython();
            }

            // Install the package in development mode from current directory
            const installProcess = spawn(this.pythonCmd, ['-m', 'pip', 'install', '-e', '.'], {
                cwd: this.packageRoot,
                stdio: 'pipe'
            });

            return new Promise((resolve, reject) => {
                let output = '';
                let errorOutput = '';

                installProcess.stdout.on('data', (data) => {
                    output += data.toString();
                });

                installProcess.stderr.on('data', (data) => {
                    errorOutput += data.toString();
                });

                installProcess.on('close', (code) => {
                    spinner.stop();
                    if (code === 0) {
                        console.log(chalk.green('✅ Python package installed successfully'));
                        resolve(true);
                    } else {
                        console.error(chalk.red('❌ Failed to install Python package'));
                        console.error(errorOutput);
                        reject(new Error(`Installation failed with code ${code}`));
                    }
                });
            });
        } catch (error) {
            spinner.stop();
            throw error;
        }
    }

    async runMCPServer(args = []) {
        try {
            // Check if Python package is available
            const packageInstalled = await this.checkPythonPackage();
            
            if (!packageInstalled) {
                console.log(chalk.yellow('Python package not found. Installing...'));
                await this.installPythonPackage();
            }

            // Run the MCP server
            console.log(chalk.blue('🚀 Starting Universal Document Converter MCP Server...'));
            
            const serverProcess = spawn(this.pythonCmd, ['-m', 'universal_document_mcp.server', ...args], {
                stdio: 'inherit',
                cwd: process.cwd()
            });

            // Handle process termination
            process.on('SIGINT', () => {
                console.log(chalk.yellow('\n🛑 Shutting down MCP server...'));
                serverProcess.kill('SIGINT');
            });

            process.on('SIGTERM', () => {
                serverProcess.kill('SIGTERM');
            });

            serverProcess.on('close', (code) => {
                if (code !== 0 && code !== null) {
                    console.error(chalk.red(`❌ MCP server exited with code ${code}`));
                    process.exit(code);
                }
            });

        } catch (error) {
            console.error(chalk.red(`❌ Error: ${error.message}`));
            process.exit(1);
        }
    }

    async generateConfigs() {
        const { generateMCPConfigs } = await import('../scripts/generate-mcp-configs.js');
        await generateMCPConfigs();
    }

    async runSetup() {
        const { setupWizard } = await import('../scripts/setup-wizard.js');
        await setupWizard();
    }

    async showConfig() {
        const { showConfig } = await import('../scripts/show-config.js');
        await showConfig();
    }
}

// CLI Setup
program
    .name('universal-document-mcp')
    .description('Universal Document Converter MCP Server')
    .version('1.0.0');

program
    .command('server')
    .description('Start the MCP server (default)')
    .option('--workspace <path>', 'Workspace directory path')
    .option('--ai-enabled', 'Enable AI-powered features')
    .option('--debug', 'Enable debug logging')
    .action(async (options) => {
        const wrapper = new MCPServerWrapper();
        const args = [];
        
        if (options.workspace) args.push('--workspace', options.workspace);
        if (options.aiEnabled) args.push('--ai-enabled');
        if (options.debug) args.push('--debug');
        
        await wrapper.runMCPServer(args);
    });

program
    .command('convert <file>')
    .description('Quick conversion mode')
    .action(async (file) => {
        const wrapper = new MCPServerWrapper();
        await wrapper.runMCPServer(['--convert', file]);
    });

program
    .command('setup')
    .description('Run interactive setup wizard')
    .action(async () => {
        const wrapper = new MCPServerWrapper();
        await wrapper.runSetup();
    });

program
    .command('config')
    .description('Show current configuration')
    .action(async () => {
        const wrapper = new MCPServerWrapper();
        await wrapper.showConfig();
    });

program
    .command('generate-configs')
    .description('Generate MCP configuration files for various applications')
    .action(async () => {
        const wrapper = new MCPServerWrapper();
        await wrapper.generateConfigs();
    });

// Default action (run server)
if (process.argv.length === 2) {
    const wrapper = new MCPServerWrapper();
    wrapper.runMCPServer();
} else {
    program.parse();
}
