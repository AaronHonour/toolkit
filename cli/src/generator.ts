import fs from 'fs-extra';
import path from 'path';
import ejs from 'ejs';
import { Framework, Pattern, Template } from './constants';

export interface ProjectConfig {
  projectName: string;
  template: string;
  framework: string;
  patterns: string[];
  cloudProvider?: string;
  description?: string;
  author?: string;
}

export class ProjectGenerator {
  private config: ProjectConfig;
  private projectPath: string;
  private templatesPath: string;

  constructor(config: ProjectConfig) {
    this.config = config;
    this.projectPath = path.join(process.cwd(), config.projectName);
    this.templatesPath = path.join(__dirname, '..', 'templates');
  }

  async generate(): Promise<void> {
    // Create project directory
    await fs.ensureDir(this.projectPath);

    // Generate based on template type
    switch (this.config.template) {
      case 'monorepo':
        await this.generateMonorepo();
        break;
      case 'microservices':
        await this.generateMicroservices();
        break;
      case 'serverless':
        await this.generateServerless();
        break;
      default:
        throw new Error(`Unknown template: ${this.config.template}`);
    }

    // Generate common files
    await this.generateCommonFiles();

    // Add selected patterns
    await this.addPatterns();

    // Generate docker configuration
    await this.generateDockerConfig();

    // Generate CI/CD configuration
    await this.generateCICD();

    // Generate documentation
    await this.generateDocs();
  }

  private async generateMonorepo(): Promise<void> {
    const structure = {
      'services': {},
      'shared': {
        'src': {
          'toolkit': {},
        },
      },
      'tests': {},
      'scripts': {},
    };

    await this.createStructure(structure);

    // Generate main service based on framework
    await this.generateService('api', this.config.framework);

    // Copy shared toolkit components
    await this.copyToolkitComponents();
  }

  private async generateMicroservices(): Promise<void> {
    const services = this.getServicesForPatterns();

    const structure = {
      'services': {},
      'infrastructure': {
        'docker': {},
        'kubernetes': {},
      },
      'scripts': {},
    };

    await this.createStructure(structure);

    // Generate each microservice
    for (const service of services) {
      await this.generateService(service, this.config.framework);
    }
  }

  private async generateServerless(): Promise<void> {
    const structure = {
      'functions': {},
      'layers': {
        'toolkit': {
          'python': {},
        },
      },
      'infrastructure': {},
      'tests': {},
    };

    await this.createStructure(structure);

    // Generate Lambda functions for each pattern
    await this.generateServerlessFunctions();
  }

  private async generateService(name: string, framework: string): Promise<void> {
    const servicePath = path.join(this.projectPath, 'services', name);
    await fs.ensureDir(servicePath);

    const templatePath = path.join(this.templatesPath, 'frameworks', framework);

    if (!(await fs.pathExists(templatePath))) {
      console.warn(`Template not found for framework: ${framework}, using base template`);
      return;
    }

    // Copy framework template
    await fs.copy(templatePath, servicePath);

    // Render templates with config
    await this.renderTemplates(servicePath, {
      serviceName: name,
      projectName: this.config.projectName,
      framework: this.config.framework,
      patterns: this.config.patterns,
    });
  }

  private async generateCommonFiles(): Promise<void> {
    const commonFiles = {
      'README.md': this.renderReadme(),
      '.gitignore': this.renderGitignore(),
      'Makefile': await this.renderMakefile(),
      'pyproject.toml': await this.renderPyproject(),
    };

    for (const [filename, content] of Object.entries(commonFiles)) {
      const filepath = path.join(this.projectPath, filename);
      await fs.writeFile(filepath, await content);
    }
  }

  private async addPatterns(): Promise<void> {
    for (const pattern of this.config.patterns) {
      await this.addPattern(pattern);
    }
  }

  private async addPattern(pattern: string): Promise<void> {
    const patternPath = path.join(this.templatesPath, 'patterns', pattern);

    if (!(await fs.pathExists(patternPath))) {
      console.warn(`Pattern template not found: ${pattern}`);
      return;
    }

    // Determine target path based on template type
    let targetPath: string;
    if (this.config.template === 'monorepo') {
      targetPath = path.join(this.projectPath, 'shared', 'src', 'toolkit', pattern);
    } else if (this.config.template === 'microservices') {
      targetPath = path.join(this.projectPath, 'services', pattern);
    } else {
      targetPath = path.join(this.projectPath, 'layers', 'toolkit', 'python', pattern);
    }

    await fs.ensureDir(targetPath);
    await fs.copy(patternPath, targetPath);

    // Render pattern templates
    await this.renderTemplates(targetPath, {
      patternName: pattern,
      projectName: this.config.projectName,
    });
  }

  private async generateDockerConfig(): Promise<void> {
    const dockerPath = path.join(this.projectPath, 'docker');
    await fs.ensureDir(dockerPath);

    // Generate Dockerfile
    const dockerfile = await this.renderTemplate('docker/Dockerfile.ejs', {
      framework: this.config.framework,
      patterns: this.config.patterns,
    });
    await fs.writeFile(path.join(this.projectPath, 'Dockerfile'), dockerfile);

    // Generate docker-compose.yml
    const dockerCompose = await this.renderTemplate('docker/docker-compose.yml.ejs', {
      projectName: this.config.projectName,
      template: this.config.template,
      patterns: this.config.patterns,
      services: this.getServicesForPatterns(),
    });
    await fs.writeFile(path.join(this.projectPath, 'docker-compose.yml'), dockerCompose);

    // Generate .dockerignore
    const dockerignore = await this.renderTemplate('docker/dockerignore.ejs', {});
    await fs.writeFile(path.join(this.projectPath, '.dockerignore'), dockerignore);
  }

  private async generateCICD(): Promise<void> {
    const ciPath = path.join(this.projectPath, '.github', 'workflows');
    await fs.ensureDir(ciPath);

    // Generate CI workflow
    const ci = await this.renderTemplate('ci/ci.yml.ejs', {
      projectName: this.config.projectName,
      framework: this.config.framework,
      patterns: this.config.patterns,
    });
    await fs.writeFile(path.join(ciPath, 'ci.yml'), ci);

    // Generate deployment workflow if cloud provider selected
    if (this.config.cloudProvider) {
      const deploy = await this.renderTemplate(`ci/deploy-${this.config.cloudProvider}.yml.ejs`, {
        projectName: this.config.projectName,
        template: this.config.template,
      });
      await fs.writeFile(path.join(ciPath, 'deploy.yml'), deploy);
    }

    // Generate benchmarks workflow
    const benchmarks = await this.renderTemplate('ci/benchmarks.yml.ejs', {
      projectName: this.config.projectName,
    });
    await fs.writeFile(path.join(ciPath, 'benchmarks.yml'), benchmarks);
  }

  private async generateDocs(): Promise<void> {
    const docsPath = path.join(this.projectPath, 'docs');
    await fs.ensureDir(docsPath);

    const docs = {
      'README.md': await this.renderTemplate('docs/index.md.ejs', {
        projectName: this.config.projectName,
        description: this.config.description,
        framework: this.config.framework,
        patterns: this.config.patterns,
      }),
      'ARCHITECTURE.md': await this.renderTemplate('docs/architecture.md.ejs', {
        template: this.config.template,
        patterns: this.config.patterns,
      }),
      'DEVELOPMENT.md': await this.renderTemplate('docs/development.md.ejs', {
        framework: this.config.framework,
      }),
      'DEPLOYMENT.md': await this.renderTemplate('docs/deployment.md.ejs', {
        cloudProvider: this.config.cloudProvider,
        template: this.config.template,
      }),
    };

    for (const [filename, content] of Object.entries(docs)) {
      await fs.writeFile(path.join(docsPath, filename), content);
    }
  }

  private async generateServerlessFunctions(): Promise<void> {
    const functionsPath = path.join(this.projectPath, 'functions');

    // Generate a function for each pattern
    for (const pattern of this.config.patterns) {
      const functionPath = path.join(functionsPath, pattern);
      await fs.ensureDir(functionPath);

      const handler = await this.renderTemplate('serverless/handler.py.ejs', {
        patternName: pattern,
        projectName: this.config.projectName,
      });

      await fs.writeFile(path.join(functionPath, 'handler.py'), handler);
      await fs.writeFile(path.join(functionPath, 'requirements.txt'), 'composable-toolkit\n');
    }

    // Generate serverless.yml or SAM template
    if (this.config.cloudProvider === 'aws') {
      const sam = await this.renderTemplate('serverless/sam.yml.ejs', {
        projectName: this.config.projectName,
        patterns: this.config.patterns,
      });
      await fs.writeFile(path.join(this.projectPath, 'template.yml'), sam);
    }
  }

  private async copyToolkitComponents(): Promise<void> {
    // Copy selected patterns from main toolkit
    const toolkitSrc = path.join(__dirname, '../../..', 'src', 'toolkit');
    const targetPath = path.join(this.projectPath, 'shared', 'src', 'toolkit');

    for (const pattern of this.config.patterns) {
      const srcPattern = path.join(toolkitSrc, pattern);
      const destPattern = path.join(targetPath, pattern);

      if (await fs.pathExists(srcPattern)) {
        await fs.copy(srcPattern, destPattern);
      }
    }
  }

  private getServicesForPatterns(): string[] {
    const serviceMap: Record<string, string> = {
      'cache': 'cache-service',
      'database': 'database-service',
      'ratelimit': 'ratelimit-service',
      'auth': 'auth-service',
      'gateway': 'api-gateway',
      'events': 'event-service',
      'queue': 'queue-service',
      'storage': 'storage-service',
      'search': 'search-service',
      'notifications': 'notification-service',
    };

    const services = ['api']; // Always have main API service

    for (const pattern of this.config.patterns) {
      if (serviceMap[pattern]) {
        services.push(serviceMap[pattern]);
      }
    }

    return services;
  }

  private async createStructure(structure: any, basePath: string = this.projectPath): Promise<void> {
    if (!structure || typeof structure !== 'object') {
      return;
    }

    for (const [key, value] of Object.entries(structure)) {
      const fullPath = path.join(basePath, key);
      await fs.ensureDir(fullPath);

      if (typeof value === 'object' && value !== null && Object.keys(value).length > 0) {
        await this.createStructure(value, fullPath);
      }
    }
  }

  private async renderTemplate(templateName: string, data: any): Promise<string> {
    const templatePath = path.join(this.templatesPath, templateName);

    if (!(await fs.pathExists(templatePath))) {
      console.warn(`Template not found: ${templateName}`);
      return '';
    }

    const template = await fs.readFile(templatePath, 'utf-8');
    return ejs.render(template, data);
  }

  private async renderTemplates(directory: string, data: any): Promise<void> {
    const files = await fs.readdir(directory, { withFileTypes: true });

    for (const file of files) {
      const fullPath = path.join(directory, file.name);

      if (file.isDirectory()) {
        await this.renderTemplates(fullPath, data);
      } else if (file.name.endsWith('.ejs')) {
        const content = await fs.readFile(fullPath, 'utf-8');
        const rendered = ejs.render(content, data);
        const outputPath = fullPath.replace('.ejs', '');
        await fs.writeFile(outputPath, rendered);
        await fs.remove(fullPath); // Remove .ejs template
      }
    }
  }

  private async renderReadme(): Promise<string> {
    return `# ${this.config.projectName}

${this.config.description || 'A Composable Toolkit application'}

## Quick Start

\`\`\`bash
# Install dependencies
make install

# Start development environment
make dev

# Run tests
make test

# Build for production
make build
\`\`\`

## Architecture

This project uses the **${this.config.template}** template with the following patterns:

${this.config.patterns.map(p => `- ${p}`).join('\n')}

## Framework

Built with **${this.config.framework}**

## Documentation

- [Architecture](docs/ARCHITECTURE.md)
- [Development Guide](docs/DEVELOPMENT.md)
- [Deployment Guide](docs/DEPLOYMENT.md)

## License

MIT
`;
  }

  private renderGitignore(): string {
    return `# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
env/
ENV/

# IDEs
.vscode/
.idea/
*.swp
*.swo

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/

# Docker
*.log

# Environment
.env
.env.local

# OS
.DS_Store
Thumbs.db

# Build artifacts
*.pyc
*.pyo
*.pyd
`;
  }

  private async renderMakefile(): Promise<string> {
    return await this.renderTemplate('Makefile.ejs', {
      projectName: this.config.projectName,
      template: this.config.template,
      framework: this.config.framework,
      patterns: this.config.patterns,
    });
  }

  private async renderPyproject(): Promise<string> {
    return await this.renderTemplate('pyproject.toml.ejs', {
      projectName: this.config.projectName,
      description: this.config.description || '',
      author: this.config.author || '',
      patterns: this.config.patterns,
    });
  }
}

export async function generateProject(config: ProjectConfig): Promise<void> {
  const generator = new ProjectGenerator(config);
  await generator.generate();
}
