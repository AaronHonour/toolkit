# Unistax

A composable full-stack toolkit for building unified applications with coordinated frontend and backend components.

[![CI](https://github.com/AaronHonour/unistax/actions/workflows/ci.yml/badge.svg)](https://github.com/AaronHonour/unistax/actions/workflows/ci.yml)
[![Backend PyPI](https://img.shields.io/pypi/v/unistax)](https://pypi.org/project/unistax/)
[![Frontend npm](https://img.shields.io/npm/v/@unistax/frontend)](https://www.npmjs.com/package/@unistax/frontend)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

This monorepo contains:

- **Backend Components** (Python) - Composable backend building blocks for full-stack applications
- **Frontend Components** (JavaScript/TypeScript) - Composable frontend building blocks that integrate seamlessly with the backend
- **Examples** - Demonstration code showing how to compose full-stack applications (not published)
- **Documentation** - Comprehensive guides and API references

## Quick Start

### Backend (Python)

```bash
pip install unistax
```

```python
from unistax import YourModule

# Use composable backend components
```

### Frontend (JavaScript/TypeScript)

```bash
npm install @unistax/frontend
# or
yarn add @unistax/frontend
```

```typescript
import { YourComponent } from '@unistax/frontend';

// Use composable frontend components
```

## Repository Structure

```
unistax/
├── backend/              # Python package
│   ├── src/
│   │   └── unistax/     # Source code
│   ├── tests/           # Test suite
│   ├── pyproject.toml   # Package configuration
│   └── README.md        # Backend documentation
│
├── frontend/            # TypeScript/JavaScript package
│   ├── src/             # Source code
│   ├── tests/           # Test suite
│   ├── package.json     # Package configuration
│   └── README.md        # Frontend documentation
│
├── examples/            # Usage examples (not published)
│   ├── python-examples/
│   └── javascript-examples/
│
├── docs/                # Documentation
│
├── .github/
│   └── workflows/       # CI/CD automation
│       ├── ci.yml       # Continuous Integration
│       ├── release.yml  # Publishing automation
│       └── codeql.yml   # Security analysis
│
├── CONTRIBUTING.md      # Development workflow and branching strategy
├── LICENSE              # MIT License
└── README.md            # This file
```

## Development

### Prerequisites

**Backend:**
- Python 3.9+
- pip or uv

**Frontend:**
- Node.js 18+
- npm or yarn

### Setup

```bash
# Clone the repository
git clone https://github.com/AaronHonour/unistax.git
cd unistax

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e ".[dev]"

# Frontend setup
cd ../frontend
npm install
```

### Running Tests

**Backend:**
```bash
cd backend
pytest                    # Run tests
pytest --cov=unistax      # With coverage
ruff check src tests      # Lint
black src tests           # Format
mypy src                  # Type check
```

**Frontend:**
```bash
cd frontend
npm test                  # Run tests
npm run test:coverage     # With coverage
npm run lint              # Lint
npm run typecheck         # Type check
npm run format            # Format
```

### Local Development Workflow

We follow **GitHub Flow** for a streamlined development process:

1. Create feature branch from `main`
2. Make changes and commit
3. Push and open Pull Request
4. Automated CI runs tests
5. Review and merge to `main`
6. Tag release when ready

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed workflow and branching strategy.

## Release Process

We use **continuous releases** with semantic versioning:

### Creating a Release

```bash
# Ensure you're on main and up to date
git checkout main
git pull origin main

# Create and push version tag
git tag -a v1.0.0 -m "Release v1.0.0: Description"
git push origin v1.0.0
```

This automatically:
1. Runs full test suite
2. Builds both packages
3. Publishes backend to PyPI
4. Publishes frontend to npm
5. Creates GitHub release

See [CONTRIBUTING.md](CONTRIBUTING.md) for complete release documentation.

## Branching Strategy

### Main Branch
- Always production-ready
- Protected with required PR reviews
- All tests must pass before merge
- Tagged commits trigger releases

### Feature Branches
- Create from `main`
- Use descriptive names: `feature/add-auth`, `fix/validation-bug`
- Delete after merging

### Why This Strategy?

Perfect for our needs:
- **Continuous releases** - Tag when ready, publish automatically
- **Small team** (1-5 developers) - Simple workflow without overhead
- **Monorepo toolkit** - Unified versioning and release process
- **Fast iteration** - No long-lived branches to manage

## CI/CD Pipeline

### Pull Request Checks
- ✅ Backend tests (Python 3.9, 3.10, 3.11, 3.12)
- ✅ Frontend tests (Node 18, 20)
- ✅ Linting and formatting
- ✅ Type checking
- ✅ Code coverage
- ✅ Security scanning (CodeQL)

### Release Pipeline
- 📦 Automated package building
- 🚀 Publishing to PyPI and npm
- 📝 GitHub release creation with changelog
- 🏷️ Pre-release support (alpha, beta, rc)

## Documentation

- [Backend README](backend/README.md) - Python package documentation
- [Frontend README](frontend/README.md) - JavaScript/TypeScript package documentation
- [CONTRIBUTING.md](CONTRIBUTING.md) - Development workflow and branching strategy
- [Examples](examples/) - Usage examples and demos

## Publishing

### Prerequisites

**PyPI (Backend):**
- Configure [Trusted Publishing](https://docs.pypi.org/trusted-publishers/) on PyPI, OR
- Add `PYPI_API_TOKEN` to repository secrets

**npm (Frontend):**
- Add `NPM_TOKEN` to repository secrets
- Token needs publish access to `@toolkit` scope

### Package Registry Setup

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed publishing configuration.

## Features

### Backend Components
- 🐍 Modern Python (3.9+) with type hints
- 🧩 Composable building blocks
- 🧪 Comprehensive test coverage
- 📚 Well-documented APIs

### Frontend Components
- 🎨 TypeScript for type safety
- 🧩 Composable building blocks
- ⚡ Modern ESM and CommonJS support
- 🧪 Jest testing setup
- 📦 Tree-shakeable exports

### Development Experience
- 🔄 Automated CI/CD pipeline
- 🛡️ Security scanning with CodeQL
- 📊 Code coverage tracking
- 🔧 Pre-configured linting and formatting

## Architecture Decisions

### Monorepo Structure
- **Pros**: Unified versioning, coordinated releases, shared tooling
- **Cons**: Larger repo size
- **Decision**: Monorepo is optimal for composable full-stack components with coordinated releases

### GitHub Flow vs Gitflow
- **GitHub Flow**: Simple feature/main workflow
- **Gitflow**: Complex develop/release/main workflow
- **Decision**: GitHub Flow chosen for continuous releases and small team

### Unified vs Independent Versioning
- **Current**: Unified versioning (v1.0.0 for both packages)
- **Rationale**: Simpler for users, coordinated releases
- **Future**: Can switch to independent versioning if needed

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for:

- Development workflow
- Branching strategy
- Code quality standards
- Release process
- Testing guidelines

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Support

- 📖 [Documentation](docs/)
- 🐛 [Issue Tracker](https://github.com/AaronHonour/unistax/issues)
- 💬 [Discussions](https://github.com/AaronHonour/unistax/discussions)

## Changelog

See [Releases](https://github.com/AaronHonour/unistax/releases) for version history and changes.

---

**Status**: 🚧 Active Development

Unistax is under active development. APIs may change between minor versions until v1.0.0 release.
