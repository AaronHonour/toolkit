# Pre-Commit Hooks Setup

## Current Status

**Before this setup**: No local linting - only CI runs ruff, black, and mypy
**After this setup**: Automatic linting on every commit

## What You Had

Your CI (`.github/workflows/ci.yml`) runs:
- ✅ `ruff check` - Linting
- ✅ `black --check` - Format checking
- ✅ `mypy` - Type checking

**But**: No local git hooks, so you only found issues after pushing to CI.

## What I Added

### 1. Pre-Commit Configuration (`.pre-commit-config.yaml`)

Runs automatically on `git commit`:

**Python:**
- Black (formatting)
- Ruff (linting + auto-fix)
- MyPy (type checking)

**JavaScript/TypeScript:**
- ESLint (linting + auto-fix)
- Prettier (formatting)

**General:**
- Trailing whitespace removal
- YAML/JSON/TOML validation
- Large file detection
- Secret detection
- Dockerfile linting

### 2. Updated `python/pyproject.toml`

Added `pre-commit>=3.5.0` to dev dependencies.

## Setup Instructions

### One-Time Setup

```bash
# 1. Install pre-commit
pip install pre-commit

# 2. Install the git hooks
cd /c/Users/aaron/toolkit
pre-commit install

# 3. (Optional) Run on all existing files
pre-commit run --all-files
```

### How It Works

```bash
# Make changes
git add .

# Commit - hooks run automatically
git commit -m "feat: add new feature"

# If hooks fail/fix things, they'll show you what changed
# Add the fixes and commit again
git add .
git commit -m "feat: add new feature"
```

### Manual Usage

```bash
# Run on all files
pre-commit run --all-files

# Run specific hook
pre-commit run ruff
pre-commit run black
pre-commit run mypy

# Update hook versions
pre-commit autoupdate
```

### Skip Hooks (Emergency Only)

```bash
# Skip all hooks
git commit --no-verify -m "emergency fix"
```

**Warning**: CI will still run all checks, so this will likely cause CI failures.

## Benefits

1. **Catch issues early** - Before pushing to CI
2. **Auto-fix** - Many issues are fixed automatically
3. **Faster feedback** - No waiting for CI to run
4. **Consistent code** - Everyone uses same formatters
5. **CI matches local** - Same tools, same settings

## What Gets Auto-Fixed

- Code formatting (Black/Ruff/Prettier)
- Import sorting (Ruff)
- Trailing whitespace
- End-of-file newlines
- Mixed line endings
- Common Python issues (Ruff --fix)

## What Requires Manual Fix

- Type errors (MyPy)
- Complex linting issues
- Security issues
- Logic errors

## Example Output

```bash
$ git commit -m "feat: add cache"

black....................................................................Passed
ruff.....................................................................Failed
- hook id: ruff
- exit code: 1

Found 3 errors:
  src/cache.py:10: F401 'time' imported but unused
  src/cache.py:25: E501 Line too long (105 > 100)
  src/cache.py:30: B008 Do not perform function call in argument defaults

# Fix the issues or let ruff fix them
$ pre-commit run ruff --files src/cache.py
ruff.....................................................................Passed

# Commit again
$ git commit -m "feat: add cache"
All checks passed!
```

## Troubleshooting

### Pre-commit not found

```bash
pip install pre-commit
```

### Hooks not running

```bash
pre-commit install
```

### Want to skip a specific hook temporarily

Edit `.pre-commit-config.yaml` and comment out the hook.

### Slow first run

First run downloads and caches all tools. Subsequent runs are fast (~1-5 seconds).

## Comparison: Before vs After

**Before:**
```bash
git commit -m "feat: add feature"
git push
# Wait 5 minutes for CI
# CI fails on formatting
# Fix locally
# Push again
# Wait 5 minutes for CI
```

**After:**
```bash
git commit -m "feat: add feature"
# Hooks run in 2 seconds
# Auto-fix formatting
git add .
git commit -m "feat: add feature"
git push
# CI passes immediately
```

## Next Steps

1. Run `pip install pre-commit`
2. Run `pre-commit install`
3. Try committing something to see it work
4. Optionally run `pre-commit run --all-files` to clean up existing code

That's it! You're now set up with automatic code quality checks.
