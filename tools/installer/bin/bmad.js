#!/usr/bin/env node

const { program } = require('commander');
const path = require('path');
const fs = require('fs').promises;
const yaml = require('js-yaml');
const chalk = require('chalk');
const inquirer = require('inquirer');

// Handle both execution contexts (from root via npx or from installer directory)
let version;
let installer;
try {
  // Try installer context first (when run from tools/installer/)
  version = require('../package.json').version;
  installer = require('../lib/installer');
} catch (e) {
  // Fall back to root context (when run via npx from GitHub)
  console.log(`Installer context not found (${e.message}), trying root context...`);
  try {
    version = require('../../../package.json').version;
    installer = require('../../../tools/installer/lib/installer');
  } catch (e2) {
    console.error('Error: Could not load required modules. Please ensure you are running from the correct directory.');
    console.error('Debug info:', {
      __dirname,
      cwd: process.cwd(),
      error: e2.message
    });
    process.exit(1);
  }
}

program
  .version(version)
  .description('BMad Method installer - Universal AI agent framework for any domain');

program
  .command('install')
  .description('Install BMad Method agents and tools')
  .option('-f, --full', 'Install complete BMad Method')
  .option('-x, --expansion-only', 'Install only expansion packs (no bmad-core)')
  .option('-d, --directory <path>', 'Installation directory')
  .option('-i, --ide <ide...>', 'Configure for specific IDE(s) - can specify multiple (cursor, claude-code, windsurf, trae, roo, cline, gemini, github-copilot, other)')
  .option('-e, --expansion-packs <packs...>', 'Install specific expansion packs (can specify multiple)')
  .action(async (options) => {
    try {
      if (!options.full && !options.expansionOnly) {
        // Interactive mode
        const answers = await promptInstallation();
        if (!answers._alreadyInstalled) {
          await installer.install(answers);
          process.exit(0);
        }
      } else {
        // Direct mode
        let installType = 'full';
        if (options.expansionOnly) installType = 'expansion-only';

        const config = {
          installType,
          directory: options.directory || '.',
          ides: (options.ide || []).filter(ide => ide !== 'other'),
          expansionPacks: options.expansionPacks || []
        };
        await installer.install(config);
        process.exit(0);
      }
    } catch (error) {
      console.error(chalk.red('Installation failed:'), error.message);
      process.exit(1);
    }
  });

program
  .command('update')
  .description('Update existing BMad installation')
  .option('--force', 'Force update, overwriting modified files')
  .option('--dry-run', 'Show what would be updated without making changes')
  .action(async () => {
    try {
      await installer.update();
    } catch (error) {
      console.error(chalk.red('Update failed:'), error.message);
      process.exit(1);
    }
  });

program
  .command('list:expansions')
  .description('List available expansion packs')
  .action(async () => {
    try {
      await installer.listExpansionPacks();
    } catch (error) {
      console.error(chalk.red('Error:'), error.message);
      process.exit(1);
    }
  });

program
  .command('status')
  .description('Show installation status')
  .action(async () => {
    try {
      await installer.showStatus();
    } catch (error) {
      console.error(chalk.red('Error:'), error.message);
      process.exit(1);
    }
  });

program
  .command('flatten')
  .description('Flatten codebase into a single XML file for AI analysis')
  .option('-o, --output <path>', 'Output file path', 'flattened-codebase.xml')
  .action(async (options) => {
    console.log(`Flattening codebase to: ${options.output}`);

    try {
      // Import flattener functions
      const { 
        discoverFiles, 
        aggregateFileContents, 
        generateXMLOutput, 
        calculateStatistics,
        filterFiles 
      } = require('../../flattener/main');
      
      // Import ora dynamically
      const { default: ora } = await import('ora');
      const fs = require('fs-extra');

      // Start file discovery with spinner
      const discoverySpinner = ora('🔍 Discovering files...').start();
      const files = await discoverFiles(process.cwd());
      const filteredFiles = await filterFiles(files, process.cwd());
      discoverySpinner.succeed(`📁 Found ${filteredFiles.length} files to include`);

      // Process files with progress tracking
      console.log('Reading file contents');
      const processingSpinner = ora('📄 Processing files...').start();
      const aggregatedContent = await aggregateFileContents(filteredFiles, process.cwd(), processingSpinner);
      processingSpinner.succeed(`✅ Processed ${aggregatedContent.processedFiles}/${filteredFiles.length} files`);

      // Log processing results for test validation
      console.log(`Processed ${aggregatedContent.processedFiles}/${filteredFiles.length} files`);
      if (aggregatedContent.errors.length > 0) {
        console.log(`Errors: ${aggregatedContent.errors.length}`);
      }
      console.log(`Text files: ${aggregatedContent.textFiles.length}`);
      if (aggregatedContent.binaryFiles.length > 0) {
        console.log(`Binary files: ${aggregatedContent.binaryFiles.length}`);
      }

      // Generate XML output using streaming
      const xmlSpinner = ora('🔧 Generating XML output...').start();
      await generateXMLOutput(aggregatedContent, options.output);
      xmlSpinner.succeed('📝 XML generation completed');

      // Calculate and display statistics
      const outputStats = await fs.stat(options.output);
      const stats = calculateStatistics(aggregatedContent, outputStats.size);

      // Display completion summary
      console.log('\n📊 Completion Summary:');
      console.log(`✅ Successfully processed ${filteredFiles.length} files into ${options.output}`);
      console.log(`📁 Output file: ${path.resolve(options.output)}`);
      console.log(`📏 Total source size: ${stats.totalSize}`);
      console.log(`📄 Generated XML size: ${stats.xmlSize}`);
      console.log(`📝 Total lines of code: ${stats.totalLines.toLocaleString()}`);
      console.log(`🔢 Estimated tokens: ${stats.estimatedTokens}`);
      console.log(`📊 File breakdown: ${stats.textFiles} text, ${stats.binaryFiles} binary, ${stats.errorFiles} errors`);

    } catch (error) {
      console.error(chalk.red('❌ Critical error:'), error.message);
      console.error('An unexpected error occurred.');
      process.exit(1);
    }
  });

async function promptInstallation() {
  
  // Display ASCII logo
  console.log(chalk.bold.cyan(`
██████╗ ███╗   ███╗ █████╗ ██████╗       ███╗   ███╗███████╗████████╗██╗  ██╗ ██████╗ ██████╗ 
██╔══██╗████╗ ████║██╔══██╗██╔══██╗      ████╗ ████║██╔════╝╚══██╔══╝██║  ██║██╔═══██╗██╔══██╗
██████╔╝██╔████╔██║███████║██║  ██║█████╗██╔████╔██║█████╗     ██║   ███████║██║   ██║██║  ██║
██╔══██╗██║╚██╔╝██║██╔══██║██║  ██║╚════╝██║╚██╔╝██║██╔══╝     ██║   ██╔══██║██║   ██║██║  ██║
██████╔╝██║ ╚═╝ ██║██║  ██║██████╔╝      ██║ ╚═╝ ██║███████╗   ██║   ██║  ██║╚██████╔╝██████╔╝
╚═════╝ ╚═╝     ╚═╝╚═╝  ╚═╝╚═════╝       ╚═╝     ╚═╝╚══════╝   ╚═╝   ╚═╝  ╚═╝ ╚═════╝ ╚═════╝ 
  `));
  
  console.log(chalk.bold.magenta('🚀 Universal AI Agent Framework for Any Domain'));
  console.log(chalk.bold.blue(`✨ Installer v${version}\n`));

  const answers = {};

  // Ask for installation directory first
  const { directory } = await inquirer.prompt([
    {
      type: 'input',
      name: 'directory',
      message: 'Enter the full path to your project directory where BMad should be installed:',
      validate: (input) => {
        if (!input.trim()) {
          return 'Please enter a valid project path';
        }
        return true;
      }
    }
  ]);
  answers.directory = directory;

  // Detect existing installations
  const installDir = path.resolve(directory);
  const state = await installer.detectInstallationState(installDir);
  
  // Check for existing expansion packs
  const existingExpansionPacks = state.expansionPacks || {};
  
  // Get available expansion packs
  const availableExpansionPacks = await installer.getAvailableExpansionPacks();
  
  // Build choices list
  const choices = [];
  
  // Load core config to get short-title
  const coreConfigPath = path.join(__dirname, '..', '..', '..', 'bmad-core', 'core-config.yaml');
  const coreConfig = yaml.load(await fs.readFile(coreConfigPath, 'utf8'));
  const coreShortTitle = coreConfig['short-title'] || 'BMad Agile Core System';
  
  // Add BMad core option
  let bmadOptionText;
  if (state.type === 'v4_existing') {
    const currentVersion = state.manifest?.version || 'unknown';
    const newVersion = version; // Always use package.json version
    const versionInfo = currentVersion === newVersion 
      ? `(v${currentVersion} - reinstall)`
      : `(v${currentVersion} → v${newVersion})`;
    bmadOptionText = `Update ${coreShortTitle} ${versionInfo} .bmad-core`;
  } else {
    bmadOptionText = `${coreShortTitle} (v${version}) .bmad-core`;
  }
  
  choices.push({
    name: bmadOptionText,
    value: 'bmad-core',
    checked: true
  });
  
  // Add expansion pack options
  for (const pack of availableExpansionPacks) {
    const existing = existingExpansionPacks[pack.id];
    let packOptionText;
    
    if (existing) {
      const currentVersion = existing.manifest?.version || 'unknown';
      const newVersion = pack.version;
      const versionInfo = currentVersion === newVersion 
        ? `(v${currentVersion} - reinstall)`
        : `(v${currentVersion} → v${newVersion})`;
      packOptionText = `Update ${pack.shortTitle} ${versionInfo} .${pack.id}`;
    } else {
      packOptionText = `${pack.shortTitle} (v${pack.version}) .${pack.id}`;
    }
    
    choices.push({
      name: packOptionText,
      value: pack.id,
      checked: false
    });
  }
  
  // Ask what to install
  const { selectedItems } = await inquirer.prompt([
    {
      type: 'checkbox',
      name: 'selectedItems',
      message: 'Select what to install/update (use space to select, enter to continue):',
      choices: choices,
      validate: (selected) => {
        if (selected.length === 0) {
          return 'Please select at least one item to install';
        }
        return true;
      }
    }
  ]);
  
  // Process selections
  answers.installType = selectedItems.includes('bmad-core') ? 'full' : 'expansion-only';
  answers.expansionPacks = selectedItems.filter(item => item !== 'bmad-core');

  // Ask sharding questions if installing BMad core
  if (selectedItems.includes('bmad-core')) {
    console.log(chalk.cyan('\n📋 Document Organization Settings'));
    console.log(chalk.dim('Configure how your project documentation should be organized.\n'));
    
    // Ask about PRD sharding
    const { prdSharded } = await inquirer.prompt([
      {
        type: 'confirm',
        name: 'prdSharded',
        message: 'Will the PRD (Product Requirements Document) be sharded into multiple files?',
        default: true
      }
    ]);
    answers.prdSharded = prdSharded;
    
    // Ask about architecture sharding
    const { architectureSharded } = await inquirer.prompt([
      {
        type: 'confirm',
        name: 'architectureSharded',
        message: 'Will the architecture documentation be sharded into multiple files?',
        default: true
      }
    ]);
    answers.architectureSharded = architectureSharded;
    
    // Show warning if architecture sharding is disabled
    if (!architectureSharded) {
      console.log(chalk.yellow.bold('\n⚠️  IMPORTANT: Architecture Sharding Disabled'));
      console.log(chalk.yellow('With architecture sharding disabled, you should still create the files listed'));
      console.log(chalk.yellow('in devLoadAlwaysFiles (like coding-standards.md, tech-stack.md, source-tree.md)'));
      console.log(chalk.yellow('as these are used by the dev agent at runtime.'));
      console.log(chalk.yellow('\nAlternatively, you can remove these files from the devLoadAlwaysFiles list'));
      console.log(chalk.yellow('in your core-config.yaml after installation.'));
      
      const { acknowledge } = await inquirer.prompt([
        {
          type: 'confirm',
          name: 'acknowledge',
          message: 'Do you acknowledge this requirement and want to proceed?',
          default: false
        }
      ]);
      
      if (!acknowledge) {
        console.log(chalk.red('Installation cancelled.'));
        process.exit(0);
      }
    }
  }

  // Ask for IDE configuration
  let ides = [];
  let ideSelectionComplete = false;
  
  while (!ideSelectionComplete) {
    console.log(chalk.cyan('\n🛠️  IDE Configuration'));
    console.log(chalk.bold.yellow.bgRed(' ⚠️  IMPORTANT: This is a MULTISELECT! Use SPACEBAR to toggle each IDE! '));
    console.log(chalk.bold.magenta('🔸 Use arrow keys to navigate'));
    console.log(chalk.bold.magenta('🔸 Use SPACEBAR to select/deselect IDEs'));
    console.log(chalk.bold.magenta('🔸 Press ENTER when finished selecting\n'));
    
    const ideResponse = await inquirer.prompt([
      {
        type: 'checkbox',
        name: 'ides',
        message: 'Which IDE(s) do you want to configure? (Select with SPACEBAR, confirm with ENTER):',
        choices: [
          { name: 'Cursor', value: 'cursor' },
          { name: 'Claude Code', value: 'claude-code' },
          { name: 'Windsurf', value: 'windsurf' },
          { name: 'Trae', value: 'trae' }, // { name: 'Trae', value: 'trae'}
          { name: 'Roo Code', value: 'roo' },
          { name: 'Cline', value: 'cline' },
          { name: 'Gemini CLI', value: 'gemini' },
          { name: 'Github Copilot', value: 'github-copilot' }
        ]
      }
    ]);
    
    ides = ideResponse.ides;

    // Confirm no IDE selection if none selected
    if (ides.length === 0) {
      const { confirmNoIde } = await inquirer.prompt([
        {
          type: 'confirm',
          name: 'confirmNoIde',
          message: chalk.red('⚠️  You have NOT selected any IDEs. This means NO IDE integration will be set up. Is this correct?'),
          default: false
        }
      ]);
      
      if (!confirmNoIde) {
        console.log(chalk.bold.red('\n🔄 Returning to IDE selection. Remember to use SPACEBAR to select IDEs!\n'));
        continue; // Go back to IDE selection only
      }
    }
    
    ideSelectionComplete = true;
  }

  // Use selected IDEs directly
  answers.ides = ides;

  // Ask about Collaborative Workspace System
  if (selectedItems.includes('bmad-core')) {
    console.log(chalk.cyan('\n🤝 Collaborative Workspace System'));
    console.log(chalk.dim('Enable multi-session AI agent coordination and context persistence.\n'));
    
    const { enableWorkspace } = await inquirer.prompt([
      {
        type: 'confirm',
        name: 'enableWorkspace',
        message: chalk.magenta('🚀 Enable Collaborative Workspace System?') + 
                 '\n   • Multi-session AI agent coordination' +
                 '\n   • Context persistence across sessions' + 
                 '\n   • Cross-IDE collaboration support' +
                 '\n   • Enhanced workflow automation' +
                 '\n   Enable workspace system?',
        default: true
      }
    ]);
    
    answers.enableWorkspace = enableWorkspace;
    
    if (enableWorkspace) {
      console.log(chalk.green('✅ Collaborative Workspace System will be configured during installation'));
      
      if (ides.includes('claude-code')) {
        console.log(chalk.blue('🎯 Claude Code CLI users will get native workspace commands'));
      }
      
      if (ides.some(ide => ide !== 'claude-code')) {
        console.log(chalk.blue('🛠️  Other IDE users will get comprehensive utility scripts'));
      }
    } else {
      console.log(chalk.yellow('⚠️  Workspace system disabled - standard BMAD functionality only'));
    }
  }

  // Configure GitHub Copilot immediately if selected
  if (ides.includes('github-copilot')) {
    console.log(chalk.cyan('\n🔧 GitHub Copilot Configuration'));
    console.log(chalk.dim('BMad works best with specific VS Code settings for optimal agent experience.\n'));
    
    const { configChoice } = await inquirer.prompt([
      {
        type: 'list',
        name: 'configChoice',
        message: chalk.yellow('How would you like to configure GitHub Copilot settings?'),
        choices: [
          {
            name: 'Use recommended defaults (fastest setup)',
            value: 'defaults'
          },
          {
            name: 'Configure each setting manually (customize to your preferences)',
            value: 'manual'
          },
          {
            name: 'Skip settings configuration (I\'ll configure manually later)',
            value: 'skip'
          }
        ],
        default: 'defaults'
      }
    ]);
    
    answers.githubCopilotConfig = { configChoice };
  }

  // Ask for web bundles installation
  const { includeWebBundles } = await inquirer.prompt([
    {
      type: 'confirm',
      name: 'includeWebBundles',
      message: 'Would you like to include pre-built web bundles? (standalone files for ChatGPT, Claude, Gemini)',
      default: false
    }
  ]);

  if (includeWebBundles) {
    console.log(chalk.cyan('\n📦 Web bundles are standalone files perfect for web AI platforms.'));
    console.log(chalk.dim('   You can choose different teams/agents than your IDE installation.\n'));

    const { webBundleType } = await inquirer.prompt([
      {
        type: 'list',
        name: 'webBundleType',
        message: 'What web bundles would you like to include?',
        choices: [
          {
            name: 'All available bundles (agents, teams, expansion packs)',
            value: 'all'
          },
          {
            name: 'Specific teams only',
            value: 'teams'
          },
          {
            name: 'Individual agents only',
            value: 'agents'
          },
          {
            name: 'Custom selection',
            value: 'custom'
          }
        ]
      }
    ]);

    answers.webBundleType = webBundleType;

    // If specific teams, let them choose which teams
    if (webBundleType === 'teams' || webBundleType === 'custom') {
      const teams = await installer.getAvailableTeams();
      const { selectedTeams } = await inquirer.prompt([
        {
          type: 'checkbox',
          name: 'selectedTeams',
          message: 'Select team bundles to include:',
          choices: teams.map(t => ({
            name: `${t.icon || '📋'} ${t.name}: ${t.description}`,
            value: t.id,
            checked: webBundleType === 'teams' // Check all if teams-only mode
          })),
          validate: (answer) => {
            if (answer.length < 1) {
              return 'You must select at least one team.';
            }
            return true;
          }
        }
      ]);
      answers.selectedWebBundleTeams = selectedTeams;
    }

    // If custom selection, also ask about individual agents
    if (webBundleType === 'custom') {
      const { includeIndividualAgents } = await inquirer.prompt([
        {
          type: 'confirm',
          name: 'includeIndividualAgents',
          message: 'Also include individual agent bundles?',
          default: true
        }
      ]);
      answers.includeIndividualAgents = includeIndividualAgents;
    }

    const { webBundlesDirectory } = await inquirer.prompt([
      {
        type: 'input',
        name: 'webBundlesDirectory',
        message: 'Enter directory for web bundles:',
        default: `${answers.directory}/web-bundles`,
        validate: (input) => {
          if (!input.trim()) {
            return 'Please enter a valid directory path';
          }
          return true;
        }
      }
    ]);
    answers.webBundlesDirectory = webBundlesDirectory;
  }

  answers.includeWebBundles = includeWebBundles;

  return answers;
}

program.parse(process.argv);

// Show help if no command provided
if (!process.argv.slice(2).length) {
  program.outputHelp();
}