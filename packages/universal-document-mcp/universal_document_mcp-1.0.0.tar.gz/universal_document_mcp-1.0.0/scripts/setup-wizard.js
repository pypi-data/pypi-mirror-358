#!/usr/bin/env node

/**
 * Interactive setup wizard for Universal Document Converter MCP Server
 */

import inquirer from 'inquirer';
import chalk from 'chalk';
import ora from 'ora';
import { spawn } from 'child_process';
import fs from 'fs/promises';
import path from 'path';
import os from 'os';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

class SetupWizard {
    constructor() {
        this.config = {
            pythonCommand: null,
            nodeAvailable: false,
            installMethod: null,
            applications: [],
            workspace: process.cwd(),
            aiEnabled: false
        };
    }

    async welcome() {
        console.log(chalk.blue.bold('\n🚀 Universal Document Converter MCP Server Setup Wizard'));
        console.log(chalk.blue('========================================================='));
        console.log(chalk.white('\nThis wizard will help you install and configure the Universal Document'));
        console.log(chalk.white('Converter MCP Server for your preferred applications.\n'));
        
        const { proceed } = await inquirer.prompt([
            {
                type: 'confirm',
                name: 'proceed',
                message: 'Would you like to continue with the setup?',
                default: true
            }
        ]);

        if (!proceed) {
            console.log(chalk.yellow('Setup cancelled.'));
            process.exit(0);
        }
    }

    async checkEnvironment() {
        console.log(chalk.blue('\n🔍 Checking your environment...'));
        
        // Check Python
        const pythonSpinner = ora('Checking Python installation...').start();
        this.config.pythonCommand = await this.findPython();
        
        if (this.config.pythonCommand) {
            pythonSpinner.succeed(chalk.green(`Python found: ${this.config.pythonCommand.version}`));
        } else {
            pythonSpinner.fail(chalk.red('Python 3.8+ not found'));
            console.log(chalk.yellow('Please install Python 3.8+ from https://python.org/downloads/'));
            process.exit(1);
        }

        // Check Node.js
        const nodeSpinner = ora('Checking Node.js installation...').start();
        this.config.nodeAvailable = await this.checkNode();
        
        if (this.config.nodeAvailable) {
            nodeSpinner.succeed(chalk.green('Node.js found'));
        } else {
            nodeSpinner.warn(chalk.yellow('Node.js not found (optional)'));
        }
    }

    async findPython() {
        const candidates = ['python3', 'python', 'py'];
        
        for (const cmd of candidates) {
            try {
                const result = await this.runCommand(cmd, ['--version']);
                const match = result.stdout.match(/Python (\d+\.\d+\.\d+)/);
                if (match) {
                    const version = match[1];
                    const [major, minor] = version.split('.').map(Number);
                    if (major >= 3 && minor >= 8) {
                        return { command: cmd, version };
                    }
                }
            } catch (error) {
                continue;
            }
        }
        return null;
    }

    async checkNode() {
        try {
            const result = await this.runCommand('node', ['--version']);
            const version = result.stdout.trim().replace('v', '');
            const [major] = version.split('.').map(Number);
            return major >= 18;
        } catch (error) {
            return false;
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

    async selectInstallMethod() {
        const choices = [
            {
                name: 'Python (pip install) - Recommended',
                value: 'python',
                short: 'Python'
            }
        ];

        if (this.config.nodeAvailable) {
            choices.push({
                name: 'Node.js (npm install) - Alternative',
                value: 'node',
                short: 'Node.js'
            });
        }

        const { installMethod } = await inquirer.prompt([
            {
                type: 'list',
                name: 'installMethod',
                message: 'How would you like to install the MCP server?',
                choices
            }
        ]);

        this.config.installMethod = installMethod;
    }

    async selectApplications() {
        const applications = [
            { name: 'Claude Desktop', value: 'claude-desktop', checked: true },
            { name: 'Cline (VS Code Extension)', value: 'cline-vscode', checked: true },
            { name: 'Roo', value: 'roo', checked: false },
            { name: 'Continue', value: 'continue', checked: false },
            { name: 'Zed Editor', value: 'zed', checked: false }
        ];

        const { selectedApps } = await inquirer.prompt([
            {
                type: 'checkbox',
                name: 'selectedApps',
                message: 'Which applications would you like to configure?',
                choices: applications,
                validate: (input) => {
                    if (input.length === 0) {
                        return 'Please select at least one application.';
                    }
                    return true;
                }
            }
        ]);

        this.config.applications = selectedApps;
    }

    async configureSettings() {
        const { workspace, aiEnabled } = await inquirer.prompt([
            {
                type: 'input',
                name: 'workspace',
                message: 'Default workspace directory:',
                default: this.config.workspace
            },
            {
                type: 'confirm',
                name: 'aiEnabled',
                message: 'Enable AI-powered features (requires API keys)?',
                default: false
            }
        ]);

        this.config.workspace = workspace;
        this.config.aiEnabled = aiEnabled;
    }

    async installPackage() {
        console.log(chalk.blue('\n📦 Installing MCP server package...'));
        
        const spinner = ora('Installing package...').start();
        
        try {
            if (this.config.installMethod === 'python') {
                await this.runCommand(this.config.pythonCommand.command, [
                    '-m', 'pip', 'install', 'universal-document-mcp'
                ]);
                
                // Install Playwright browsers
                spinner.text = 'Installing Playwright browsers...';
                await this.runCommand(this.config.pythonCommand.command, [
                    '-m', 'playwright', 'install', 'chromium'
                ]);
            } else if (this.config.installMethod === 'node') {
                await this.runCommand('npm', ['install', '-g', 'universal-document-mcp']);
            }
            
            spinner.succeed(chalk.green('Package installed successfully'));
        } catch (error) {
            spinner.fail(chalk.red(`Installation failed: ${error.message}`));
            throw error;
        }
    }

    async generateConfigurations() {
        console.log(chalk.blue('\n⚙️  Generating configuration files...'));
        
        const { generateMCPConfigs } = await import('./generate-mcp-configs.js');
        
        const spinner = ora('Generating configurations...').start();
        
        try {
            await generateMCPConfigs({
                interactive: false,
                selectedApps: this.config.applications,
                merge: true
            });
            
            spinner.succeed(chalk.green('Configuration files generated'));
        } catch (error) {
            spinner.fail(chalk.red(`Configuration generation failed: ${error.message}`));
            throw error;
        }
    }

    async testInstallation() {
        console.log(chalk.blue('\n🧪 Testing installation...'));
        
        const spinner = ora('Testing MCP server...').start();
        
        try {
            if (this.config.installMethod === 'python') {
                await this.runCommand(this.config.pythonCommand.command, [
                    '-c', 'import universal_document_mcp; print("OK")'
                ]);
            }
            
            spinner.succeed(chalk.green('Installation test passed'));
        } catch (error) {
            spinner.fail(chalk.red(`Installation test failed: ${error.message}`));
            throw error;
        }
    }

    async showSummary() {
        console.log(chalk.green.bold('\n🎉 Setup completed successfully!'));
        console.log(chalk.blue('====================================='));
        
        console.log(chalk.white('\nInstallation Summary:'));
        console.log(chalk.gray(`• Install method: ${this.config.installMethod}`));
        console.log(chalk.gray(`• Python: ${this.config.pythonCommand.version}`));
        console.log(chalk.gray(`• Applications configured: ${this.config.applications.length}`));
        console.log(chalk.gray(`• AI features: ${this.config.aiEnabled ? 'Enabled' : 'Disabled'}`));
        
        console.log(chalk.white('\nConfigured Applications:'));
        this.config.applications.forEach(app => {
            console.log(chalk.gray(`• ${app}`));
        });
        
        console.log(chalk.yellow('\nNext Steps:'));
        console.log(chalk.white('1. Restart your MCP-compatible applications'));
        console.log(chalk.white('2. The Universal Document Converter should now be available'));
        console.log(chalk.white('3. Test by asking to convert a markdown file to PDF'));
        
        console.log(chalk.blue('\nUsage Examples:'));
        console.log(chalk.gray('• "Convert this markdown file to PDF"'));
        console.log(chalk.gray('• "Generate a PDF from document.md"'));
        console.log(chalk.gray('• "Export my markdown with Mermaid diagrams to PDF"'));
        
        console.log(chalk.white('\nFor help: universal-document-mcp --help\n'));
    }

    async run() {
        try {
            await this.welcome();
            await this.checkEnvironment();
            await this.selectInstallMethod();
            await this.selectApplications();
            await this.configureSettings();
            await this.installPackage();
            await this.generateConfigurations();
            await this.testInstallation();
            await this.showSummary();
        } catch (error) {
            console.error(chalk.red(`\n❌ Setup failed: ${error.message}`));
            process.exit(1);
        }
    }
}

export async function setupWizard() {
    const wizard = new SetupWizard();
    await wizard.run();
}

// CLI usage
if (import.meta.url === `file://${process.argv[1]}`) {
    await setupWizard();
}
