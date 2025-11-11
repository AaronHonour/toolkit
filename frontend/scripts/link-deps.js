#!/usr/bin/env node
import { readdirSync, existsSync, symlinkSync, rmSync } from 'fs';
import { join, resolve } from 'path';
import { fileURLToPath } from 'url';
import { dirname } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const rootDir = resolve(__dirname, '..');
const nodeModulesPath = join(rootDir, 'node_modules');
const frontendAppsPath = resolve(rootDir, '../examples/frontends');

console.log('Linking node_modules to frontend apps...');
console.log(`Root node_modules: ${nodeModulesPath}`);
console.log(`Frontend apps path: ${frontendAppsPath}`);

if (!existsSync(frontendAppsPath)) {
  console.log('Frontend apps directory not found, skipping link...');
  process.exit(0);
}

const apps = readdirSync(frontendAppsPath, { withFileTypes: true })
  .filter(dirent => dirent.isDirectory())
  .map(dirent => dirent.name);

console.log(`Found ${apps.length} frontend apps`);

for (const app of apps) {
  const appPath = join(frontendAppsPath, app);
  const appNodeModules = join(appPath, 'node_modules');

  try {
    // Remove existing node_modules if it exists
    if (existsSync(appNodeModules)) {
      rmSync(appNodeModules, { recursive: true, force: true });
    }

    // Create symlink
    symlinkSync(nodeModulesPath, appNodeModules, 'junction');
    console.log(`  Linked: ${app}`);
  } catch (error) {
    console.error(`  Failed to link ${app}: ${error.message}`);
  }
}

console.log('Done linking node_modules');
