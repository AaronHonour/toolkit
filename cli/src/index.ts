#!/usr/bin/env node

import { Command } from 'commander';
import chalk from 'chalk';
import inquirer from 'inquirer';
import ora from 'ora';
import path from 'path';
import fs from 'fs-extra';
import execa from 'execa';
import { Listr } from 'listr2';
import { generateProject } from './generator';
import { PATTERNS, FRAMEWORKS, TEMPLATES } from './constants';

// @ts-ignore - no types available
import validateNpmPackageName from 'validate-npm-package-name';

const program = new Command();

console.log(chalk.cyan.bold(`
╔═══════════════════════════════════════╗
║  🚀 Composable Toolkit Generator     ║
║  Create production-ready apps fast   ║
╚═══════════════════════════════════════╝
`));

program
  .name('create-composable-app')
  .description('Scaffold a new Composable Toolkit application')
  .version('1.0.0')
  .argument('[project-name]', 'Name of the project')
  .option('-t, --template <type>', 'Template type (monorepo, microservices, serverless)')
  .option('-f, --framework <name>', 'Framework (fastapi, django, nestjs)')
  .option('-p, --patterns <items>', 'Comma-separated list of patterns')
  .option('--skip-install', 'Skip dependency installation')
  .option('--skip-git', 'Skip git initialization')
  .action(async (projectName, options) => {
    try {
      let answers: any = {};

      // Get project name
      if (!projectName) {
        const nameAnswer = await inquirer.prompt([
          {
            type: 'input',
            name: 'projectName',
            message: 'Project name:',
            default: 'my-composable-app',
            validate: (input) => {
              const validation = validateNpmPackageName(input);
              if (validation.validForNewPackages) {
                return true;
              }
              return validation.errors?.[0] || 'Invalid project name';
            },
          },
        ]);
        projectName = nameAnswer.projectName;
      }

      // Validate project name
      const validation = validateNpmPackageName(projectName);
      if (!validation.validForNewPackages) {
        console.error(chalk.red(`Error: ${validation.errors?.[0]}`));
        process.exit(1);
      }

      // Check if directory exists
      const projectPath = path.resolve(process.cwd(), projectName);
      if (fs.existsSync(projectPath)) {
        const { overwrite } = await inquirer.prompt([
          {
            type: 'confirm',
            name: 'overwrite',
            message: `Directory ${projectName} already exists. Overwrite?`,
            default: false,
          },
        ]);

        if (!overwrite) {
          console.log(chalk.yellow('Aborted.'));
          process.exit(0);
        }

        await fs.remove(projectPath);
      }

      // Interactive prompts if options not provided
      if (!options.template || !options.framework) {
        answers = await inquirer.prompt([
          {
            type: 'list',
            name: 'template',
            message: 'Select project template:',
            choices: TEMPLATES.map(t => ({
              name: `${t.icon} ${t.name} - ${t.description}`,
              value: t.value,
            })),
            when: !options.template,
          },
          {
            type: 'list',
            name: 'framework',
            message: 'Select framework:',
            choices: FRAMEWORKS.map(f => ({
              name: `${f.icon} ${f.name} (${f.language}) - ${f.description}`,
              value: f.value,
            })),
            when: !options.framework,
          },
          {
            type: 'checkbox',
            name: 'patterns',
            message: 'Select patterns to include:',
            choices: PATTERNS.map(p => ({
              name: `${p.name} - ${p.description}`,
              value: p.value,
              checked: p.recommended,
            })),
            validate: (input) => {
              if (input.length === 0) {
                return 'Please select at least one pattern';
              }
              return true;
            },
            when: !options.patterns,
          },
          {
            type: 'confirm',
            name: 'includeDocker',
            message: 'Include Docker configuration?',
            default: true,
          },
          {
            type: 'confirm',
            name: 'includeCICD',
            message: 'Include CI/CD configuration (GitHub Actions)?',
            default: true,
          },
          {
            type: 'confirm',
            name: 'includeObservability',
            message: 'Include observability stack (Prometheus, Grafana)?',
            default: true,
          },
          {
            type: 'confirm',
            name: 'includeTests',
            message: 'Include test configuration and examples?',
            default: true,
          },
        ]);
      }

      // Merge options and answers
      const config = {
        projectName,
        template: options.template || answers.template,
        framework: options.framework || answers.framework,
        patterns: options.patterns
          ? options.patterns.split(',').map((p: string) => p.trim())
          : answers.patterns || [],
        includeDocker: answers.includeDocker !== false,
        includeCICD: answers.includeCICD !== false,
        includeObservability: answers.includeObservability !== false,
        includeTests: answers.includeTests !== false,
        skipInstall: options.skipInstall || false,
        skipGit: options.skipGit || false,
      };

      console.log();
      console.log(chalk.cyan('Configuration:'));
      console.log(chalk.gray('  Project:'), chalk.white(config.projectName));
      console.log(chalk.gray('  Template:'), chalk.white(config.template));
      console.log(chalk.gray('  Framework:'), chalk.white(config.framework));
      console.log(chalk.gray('  Patterns:'), chalk.white(config.patterns.join(', ')));
      console.log();

      // Generate project
      const tasks = new Listr([
        {
          title: 'Creating project structure',
          task: async () => {
            await generateProject(config);
          },
        },
        {
          title: 'Initializing git repository',
          enabled: () => !config.skipGit,
          task: async () => {
            await execa('git', ['init'], { cwd: projectPath });
            await execa('git', ['add', '.'], { cwd: projectPath });
            await execa('git', ['commit', '-m', 'Initial commit from create-composable-app'], {
              cwd: projectPath,
            });
          },
        },
        {
          title: 'Installing dependencies',
          enabled: () => !config.skipInstall,
          task: async () => {
            const framework = FRAMEWORKS.find(f => f.value === config.framework);
            if (framework?.language === 'python') {
              await execa('python', ['-m', 'venv', 'venv'], { cwd: projectPath });
              await execa('venv/bin/pip', ['install', '-e', '.[dev]'], { cwd: projectPath });
            } else if (framework?.language === 'typescript') {
              await execa('npm', ['install'], { cwd: projectPath });
            }
          },
        },
      ]);

      await tasks.run();

      // Success message
      console.log();
      console.log(chalk.green.bold('✓ Project created successfully!'));
      console.log();
      console.log(chalk.cyan('Next steps:'));
      console.log(chalk.white(`  cd ${projectName}`));

      if (config.includeDocker) {
        console.log(chalk.white('  make dev              # Start development environment'));
      }

      const framework = FRAMEWORKS.find(f => f.value === config.framework);
      if (framework?.language === 'python') {
        console.log(chalk.white('  source venv/bin/activate'));
        console.log(chalk.white('  python main.py        # Run application'));
      } else {
        console.log(chalk.white('  npm run dev           # Run application'));
      }

      console.log(chalk.white('  make test             # Run tests'));
      console.log();
      console.log(chalk.gray('Documentation:'));
      console.log(chalk.gray(`  ${projectPath}/README.md`));
      console.log();
      console.log(chalk.cyan.bold('Happy coding! 🚀'));

    } catch (error) {
      console.error(chalk.red('Error:'), error);
      process.exit(1);
    }
  });

program.parse();
