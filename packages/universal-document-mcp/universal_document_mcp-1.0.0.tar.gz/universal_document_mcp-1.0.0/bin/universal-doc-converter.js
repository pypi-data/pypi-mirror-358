#!/usr/bin/env node

/**
 * Universal Document Converter - NPX Entry Point
 * AI-powered MD to PDF conversion with intelligent layout optimization
 */

const { program } = require('commander');
const chalk = require('chalk');
const ora = require('ora');
const inquirer = require('inquirer');
const fs = require('fs-extra');
const path = require('path');
const { spawn } = require('cross-spawn');

// Package information
const packageJson = require('../package.json');

// ASCII Art Banner
const banner = `
${chalk.cyan('╔══════════════════════════════════════════════════════════════╗')}
${chalk.cyan('║')}  ${chalk.bold.white('Universal Document Converter')} ${chalk.gray('v' + packageJson.version)}                    ${chalk.cyan('║')}
${chalk.cyan('║')}  ${chalk.gray('AI-powered MD → PDF conversion with intelligent layout')}     ${chalk.cyan('║')}
${chalk.cyan('╚══════════════════════════════════════════════════════════════╝')}
`;

// Configuration management
class ConfigManager {
    constructor() {
        this.configFile = path.join(process.cwd(), 'udc-config.json');
        this.defaultConfig = {
            ai_enabled: false,
            ai_provider: 'openrouter',
            ai_model: 'anthropic/claude-3-haiku',
            output_format: 'pdf',
            optimize_diagrams: true,
            professional_formatting: true,
            backup_enabled: true
        };
    }

    async loadConfig() {
        try {
            if (await fs.pathExists(this.configFile)) {
                const config = await fs.readJson(this.configFile);
                return { ...this.defaultConfig, ...config };
            }
            return this.defaultConfig;
        } catch (error) {
            console.warn(chalk.yellow('Warning: Could not load config, using defaults'));
            return this.defaultConfig;
        }
    }

    async saveConfig(config) {
        try {
            await fs.writeJson(this.configFile, config, { spaces: 2 });
            console.log(chalk.green('✓ Configuration saved'));
        } catch (error) {
            console.error(chalk.red('Error saving configuration:'), error.message);
        }
    }
}

// Python script runner
class PythonRunner {
    constructor() {
        this.scriptPath = path.join(__dirname, '..', 'enhanced_universal_document_converter.py');
    }

    async checkPython() {
        return new Promise((resolve) => {
            const python = spawn('python', ['--version'], { stdio: 'pipe' });
            python.on('close', (code) => {
                if (code === 0) {
                    resolve('python');
                } else {
                    const python3 = spawn('python3', ['--version'], { stdio: 'pipe' });
                    python3.on('close', (code) => {
                        resolve(code === 0 ? 'python3' : null);
                    });
                }
            });
        });
    }

    async installDependencies() {
        const spinner = ora('Installing Python dependencies...').start();
        
        try {
            const pythonCmd = await this.checkPython();
            if (!pythonCmd) {
                throw new Error('Python not found. Please install Python 3.8 or higher.');
            }

            // Install Python packages
            const installProcess = spawn(pythonCmd, [
                '-m', 'pip', 'install', 
                'playwright>=1.40.0', 
                'markdown>=3.5.0', 
                'requests>=2.31.0'
            ], { stdio: 'pipe' });

            await new Promise((resolve, reject) => {
                installProcess.on('close', (code) => {
                    if (code === 0) resolve();
                    else reject(new Error(`pip install failed with code ${code}`));
                });
            });

            // Install Playwright browsers
            const playwrightProcess = spawn(pythonCmd, [
                '-m', 'playwright', 'install', 'chromium'
            ], { stdio: 'pipe' });

            await new Promise((resolve, reject) => {
                playwrightProcess.on('close', (code) => {
                    if (code === 0) resolve();
                    else reject(new Error(`Playwright install failed with code ${code}`));
                });
            });

            spinner.succeed('Dependencies installed successfully');
            return true;
        } catch (error) {
            spinner.fail(`Dependency installation failed: ${error.message}`);
            return false;
        }
    }

    async runConverter(inputFile, options = {}) {
        const spinner = ora('Converting document...').start();
        
        try {
            const pythonCmd = await this.checkPython();
            if (!pythonCmd) {
                throw new Error('Python not found');
            }

            const args = [this.scriptPath, inputFile];
            
            // Add options as command line arguments
            if (options.aiEnabled) args.push('--ai-layout');
            if (options.outputDir) args.push('--output-dir', options.outputDir);
            if (options.configFile) args.push('--config', options.configFile);

            const process = spawn(pythonCmd, args, { 
                stdio: ['inherit', 'pipe', 'pipe'],
                cwd: process.cwd()
            });

            let output = '';
            let error = '';

            process.stdout.on('data', (data) => {
                output += data.toString();
                // Update spinner with progress
                const lines = data.toString().split('\n');
                const lastLine = lines[lines.length - 2] || '';
                if (lastLine.trim()) {
                    spinner.text = lastLine.trim();
                }
            });

            process.stderr.on('data', (data) => {
                error += data.toString();
            });

            const exitCode = await new Promise((resolve) => {
                process.on('close', resolve);
            });

            if (exitCode === 0) {
                spinner.succeed('Document converted successfully!');
                console.log(chalk.green('\n✓ Conversion completed'));
                
                // Parse output for file information
                const outputMatch = output.match(/Generated PDF: (.+)/);
                if (outputMatch) {
                    console.log(chalk.blue(`📄 Output file: ${outputMatch[1]}`));
                }
                
                return true;
            } else {
                spinner.fail('Conversion failed');
                console.error(chalk.red('Error:'), error);
                return false;
            }
        } catch (error) {
            spinner.fail(`Conversion error: ${error.message}`);
            return false;
        }
    }
}

// Interactive setup wizard
async function setupWizard() {
    console.log(chalk.blue('\n🔧 Universal Document Converter Setup\n'));

    const answers = await inquirer.prompt([
        {
            type: 'confirm',
            name: 'enableAI',
            message: 'Enable AI-powered layout optimization?',
            default: false
        },
        {
            type: 'input',
            name: 'apiKey',
            message: 'Enter OpenRouter API key (optional):',
            when: (answers) => answers.enableAI,
            validate: (input) => {
                if (!input.trim()) return 'API key is required for AI features';
                return true;
            }
        },
        {
            type: 'list',
            name: 'aiModel',
            message: 'Select AI model:',
            choices: [
                'anthropic/claude-3-haiku',
                'anthropic/claude-3-sonnet',
                'openai/gpt-4-turbo',
                'openai/gpt-3.5-turbo'
            ],
            when: (answers) => answers.enableAI,
            default: 'anthropic/claude-3-haiku'
        },
        {
            type: 'confirm',
            name: 'optimizeDiagrams',
            message: 'Optimize Mermaid diagrams for PDF?',
            default: true
        },
        {
            type: 'confirm',
            name: 'createBackups',
            message: 'Create backups of original files?',
            default: true
        }
    ]);

    const config = {
        ai_enabled: answers.enableAI,
        ai_model: answers.aiModel || 'anthropic/claude-3-haiku',
        optimize_diagrams: answers.optimizeDiagrams,
        backup_enabled: answers.createBackups,
        setup_completed: true
    };

    // Save API key separately if provided
    if (answers.apiKey) {
        const apiKeyFile = path.join(process.cwd(), 'api_keys.json');
        const apiKeyData = {
            keys: [{ key: answers.apiKey, added: new Date().toISOString() }]
        };
        await fs.writeJson(apiKeyFile, apiKeyData, { spaces: 2 });
        console.log(chalk.green('✓ API key saved securely'));
    }

    const configManager = new ConfigManager();
    await configManager.saveConfig(config);

    console.log(chalk.green('\n✓ Setup completed! You can now use the converter.'));
}

// Main CLI program
program
    .name('universal-doc-converter')
    .description('AI-powered universal document converter (MD → PDF)')
    .version(packageJson.version)
    .option('-a, --ai-layout', 'Enable AI-powered layout optimization')
    .option('-o, --output-dir <dir>', 'Output directory for generated files')
    .option('-c, --config <file>', 'Configuration file path')
    .option('--no-optimize', 'Disable diagram optimization')
    .option('--no-backup', 'Disable backup creation')
    .option('-v, --verbose', 'Verbose output')
    .argument('[file]', 'Markdown file to convert');

program
    .command('setup')
    .description('Run interactive setup wizard')
    .action(setupWizard);

program
    .command('config')
    .description('Show current configuration')
    .action(async () => {
        const configManager = new ConfigManager();
        const config = await configManager.loadConfig();
        console.log(chalk.blue('\nCurrent Configuration:'));
        console.log(JSON.stringify(config, null, 2));
    });

program
    .command('install-deps')
    .description('Install Python dependencies')
    .action(async () => {
        const runner = new PythonRunner();
        await runner.installDependencies();
    });

// Main action
program.action(async (file, options) => {
    console.log(banner);

    if (!file) {
        console.log(chalk.yellow('No input file specified. Use --help for usage information.'));
        console.log(chalk.blue('Run "npx universal-doc-converter setup" for interactive setup.'));
        return;
    }

    // Check if file exists
    if (!await fs.pathExists(file)) {
        console.error(chalk.red(`Error: File "${file}" not found`));
        process.exit(1);
    }

    // Load configuration
    const configManager = new ConfigManager();
    const config = await configManager.loadConfig();

    // Check if setup is needed
    if (!config.setup_completed) {
        console.log(chalk.yellow('First time setup required.'));
        const { runSetup } = await inquirer.prompt([{
            type: 'confirm',
            name: 'runSetup',
            message: 'Run setup wizard now?',
            default: true
        }]);

        if (runSetup) {
            await setupWizard();
        }
    }

    // Run converter
    const runner = new PythonRunner();
    
    // Check dependencies
    const pythonCmd = await runner.checkPython();
    if (!pythonCmd) {
        console.error(chalk.red('Python not found. Please install Python 3.8 or higher.'));
        process.exit(1);
    }

    // Convert document
    const success = await runner.runConverter(file, {
        aiEnabled: options.aiLayout || config.ai_enabled,
        outputDir: options.outputDir,
        configFile: options.config
    });

    process.exit(success ? 0 : 1);
});

// Error handling
process.on('uncaughtException', (error) => {
    console.error(chalk.red('Uncaught Exception:'), error.message);
    process.exit(1);
});

process.on('unhandledRejection', (reason, promise) => {
    console.error(chalk.red('Unhandled Rejection at:'), promise, chalk.red('reason:'), reason);
    process.exit(1);
});

// Parse command line arguments
program.parse();
