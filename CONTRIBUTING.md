# Contributing to Toolkit

Thank you for your interest in contributing to Toolkit! This document outlines our development workflow, branching strategy, and release process.

## Table of Contents

- [Development Workflow](#development-workflow)
- [Branching Strategy](#branching-strategy)
- [Making Changes](#making-changes)
- [Testing](#testing)
- [Release Process](#release-process)
- [Code Quality Standards](#code-quality-standards)

## Development Workflow

We follow **GitHub Flow** - a simple, branch-based workflow optimized for continuous releases:

```
main (always stable, production-ready)
  ↑
feature/* branches (short-lived)
```

### Key Principles

1. **Main is always deployable** - All code in `main` is production-ready
2. **Feature branches** - Create descriptive feature branches for all work
3. **Pull Requests** - All changes go through PR review before merging
4. **CI/CD automation** - Automated testing and deployment on merge

## Branching Strategy

### Main Branch

- **Purpose**: Production-ready code, always stable
- **Protection**: Requires PR approval and passing CI checks
- **Deployment**: Tagged releases trigger automatic package publishing

### Feature Branches

Create feature branches from `main` using descriptive names:

```bash
# Format
feature/descriptive-name
feature/add-auth-module
feature/fix-validation-bug
feature/improve-logging
```

**Naming conventions:**
- `feature/*` - New features or enhancements
- `fix/*` - Bug fixes
- `docs/*` - Documentation updates
- `refactor/*` - Code refactoring
- `test/*` - Test additions or improvements

### Branch Lifecycle

1. **Create** from latest `main`
2. **Develop** with frequent commits
3. **Push** and open PR when ready
4. **Review** by team member
5. **Merge** to main (squash or merge commit)
6. **Delete** feature branch after merge

## Making Changes

### 1. Setup Development Environment

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e ".[dev]"
```

**Frontend:**
```bash
cd frontend
npm install
```

### 2. Create Feature Branch

```bash
# Ensure main is up to date
git checkout main
git pull origin main

# Create and switch to feature branch
git checkout -b feature/your-feature-name
```

### 3. Make Your Changes

- Write clear, focused commits
- Follow code quality standards (see below)
- Add tests for new functionality
- Update documentation as needed

### 4. Run Tests Locally

**Backend:**
```bash
cd backend
pytest                    # Run tests
ruff check src tests      # Lint
black src tests           # Format
mypy src                  # Type check
```

**Frontend:**
```bash
cd frontend
npm test                  # Run tests
npm run lint              # Lint
npm run typecheck         # Type check
npm run format            # Format
```

### 5. Push and Create PR

```bash
git push origin feature/your-feature-name
```

Then open a Pull Request on GitHub:
- Fill in the PR template
- Link any related issues
- Request review from team member
- Ensure CI checks pass

### 6. Address Review Comments

- Make requested changes in new commits
- Push updates to the same branch
- Re-request review when ready

### 7. Merge

Once approved and CI passes:
- Squash merge (for clean history) or merge commit (to preserve history)
- Delete feature branch after merge

## Testing

### Backend Testing

```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=toolkit --cov-report=html

# Run specific test file
pytest tests/test_specific.py

# Run with verbose output
pytest -v
```

### Frontend Testing

```bash
cd frontend

# Run all tests
npm test

# Run in watch mode
npm run test:watch

# Run with coverage
npm run test:coverage
```

## Release Process

We use **tag-based continuous releases** - tagging `main` triggers automatic publishing.

### Semantic Versioning

We follow [Semantic Versioning](https://semver.org/) (MAJOR.MINOR.PATCH):

- **MAJOR** (1.0.0): Breaking changes
- **MINOR** (0.1.0): New features (backwards compatible)
- **PATCH** (0.0.1): Bug fixes (backwards compatible)

### Creating a Release

1. **Ensure main is stable**
   ```bash
   git checkout main
   git pull origin main
   ```

2. **Determine version number**
   - Check current version: `git tag -l`
   - Decide next version based on changes

3. **Create and push tag**
   ```bash
   # Create annotated tag
   git tag -a v1.2.3 -m "Release v1.2.3: Brief description of changes"

   # Push tag to trigger release workflow
   git push origin v1.2.3
   ```

4. **Automated publishing**
   - GitHub Actions workflow automatically:
     - Runs full test suite
     - Builds both packages
     - Publishes backend to PyPI
     - Publishes frontend to npm
     - Creates GitHub release with changelog

5. **Verify release**
   - Check GitHub Actions for successful workflow
   - Verify package on PyPI: https://pypi.org/project/toolkit/
   - Verify package on npm: https://www.npmjs.com/package/@toolkit/frontend
   - Review GitHub release notes

### Pre-releases

For alpha, beta, or release candidates:

```bash
git tag -a v1.0.0-beta.1 -m "Beta release"
git push origin v1.0.0-beta.1
```

Pre-release versions are marked as such on GitHub.

### Hotfixes

For urgent production fixes:

```bash
# Create hotfix branch from main
git checkout -b hotfix/critical-security-fix main

# Make fix, test thoroughly
# ... make changes ...

# Create PR, get expedited review
# After merge, immediately create release tag
git checkout main
git pull origin main
git tag -a v1.2.4 -m "Hotfix: Security vulnerability patch"
git push origin v1.2.4
```

## Code Quality Standards

### Backend (Python)

- **Style**: PEP 8 (enforced by Black with 100 char line length)
- **Linting**: Ruff
- **Type hints**: Required for all functions (checked by mypy)
- **Testing**: Pytest with 80%+ coverage
- **Documentation**: Docstrings for all public APIs

Example:
```python
def calculate_total(items: list[Item], tax_rate: float) -> Decimal:
    """
    Calculate total price including tax.

    Args:
        items: List of items to calculate total for
        tax_rate: Tax rate as decimal (e.g., 0.08 for 8%)

    Returns:
        Total price including tax

    Raises:
        ValueError: If tax_rate is negative
    """
    if tax_rate < 0:
        raise ValueError("Tax rate cannot be negative")

    subtotal = sum(item.price for item in items)
    return subtotal * (1 + tax_rate)
```

### Frontend (TypeScript)

- **Style**: Prettier (100 char line length)
- **Linting**: ESLint with TypeScript plugin
- **Type safety**: Strict TypeScript (no `any` without justification)
- **Testing**: Jest with 80%+ coverage
- **Documentation**: TSDoc for all exported APIs

Example:
```typescript
/**
 * Formats a date according to the specified locale and options
 *
 * @param date - The date to format
 * @param locale - BCP 47 language tag (e.g., 'en-US', 'fr-FR')
 * @param options - Intl.DateTimeFormat options
 * @returns Formatted date string
 *
 * @example
 * ```typescript
 * formatDate(new Date(), 'en-US', { dateStyle: 'full' })
 * // Returns: "Monday, January 1, 2024"
 * ```
 */
export function formatDate(
  date: Date,
  locale: string = 'en-US',
  options: Intl.DateTimeFormatOptions = {}
): string {
  return new Intl.DateTimeFormat(locale, options).format(date);
}
```

### Commit Messages

Use clear, descriptive commit messages:

```
<type>: <short summary>

<optional detailed description>

<optional footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `refactor`: Code refactoring
- `test`: Test additions/changes
- `chore`: Maintenance tasks

**Examples:**
```
feat: add JWT authentication module

Implements JWT token generation and validation with refresh token support.
Includes middleware for protecting routes.

Closes #123
```

```
fix: resolve memory leak in event handlers

Event listeners were not being properly cleaned up on component unmount.
Added cleanup in useEffect return function.
```

## Getting Help

- Open an issue for bugs or feature requests
- Start a discussion for questions or ideas
- Review existing issues and PRs before creating new ones

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Celebrate contributions of all sizes

---

Thank you for contributing to Toolkit! 🚀
