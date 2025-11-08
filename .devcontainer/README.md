# VS Code Dev Container

This directory contains the VS Code Dev Container configuration for the Composable Toolkit project.

## What is a Dev Container?

A development container (dev container) is a running Docker container with a well-defined tool/runtime stack and its prerequisites. The VS Code Dev Containers extension lets you use a Docker container as a full-featured development environment.

## Features

This dev container provides:

✅ **Complete Development Environment**:
- Python 3.11 with all toolkit dependencies
- Node.js 20 for frontend development
- All required VS Code extensions pre-installed
- Pre-configured linting, formatting, and testing

✅ **Infrastructure Services**:
- PostgreSQL database
- Redis cache
- Kafka message broker
- TimescaleDB for time-series data

✅ **Pre-configured Tools**:
- pytest for testing
- black for code formatting
- ruff for linting
- mypy for type checking
- Docker-in-Docker for building images

✅ **VS Code Extensions**:
- Python development (Pylance, Black, Ruff)
- Testing (Python Test Adapter)
- Docker support
- GitLens
- REST Client
- Database tools (PostgreSQL)
- Markdown support
- Code quality (SonarLint)

## Getting Started

### Prerequisites

1. **VS Code**: Install [Visual Studio Code](https://code.visualstudio.com/)
2. **Dev Containers Extension**: Install the [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)
3. **Docker**: Install [Docker Desktop](https://www.docker.com/products/docker-desktop/)

### Opening the Project

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/toolkit
   cd toolkit
   ```

2. **Open in VS Code**:
   ```bash
   code .
   ```

3. **Reopen in Container**:
   - Press `F1` or `Cmd/Ctrl+Shift+P`
   - Select: `Dev Containers: Reopen in Container`
   - Wait for the container to build (first time takes 2-5 minutes)

4. **Start Development**:
   - Open terminal in VS Code (`Ctrl+` `)
   - Run `make dev` to start all services
   - Start coding!

## What Happens on First Start

1. **Container Build**: Docker builds the development container with all dependencies
2. **Post-Create**: Installs Python dependencies (`pip install -e '.[dev,all]'`)
3. **Post-Start**: Starts infrastructure services (PostgreSQL, Redis, Kafka)
4. **Extensions**: Installs and configures all VS Code extensions
5. **Ready**: Development environment is ready to use!

## Available Services

Once the dev container is running, you can access:

| Service | URL | Description |
|---------|-----|-------------|
| **Backend APIs** | http://localhost:8001-8019 | All 19 backend services |
| **Frontend** | http://localhost:3000 | React development server |
| **Documentation** | http://localhost:5173 | VitePress documentation site |
| **PostgreSQL** | localhost:5432 | Database (user: toolkit, pass: toolkit_dev) |
| **Redis** | localhost:6379 | Cache and session store |
| **Kafka** | localhost:9092 | Message broker |

## Common Tasks

### Running Tests
```bash
# Backend tests
pytest tests/ -v

# Frontend tests
cd frontend && npm test

# All tests
make test
```

### Code Quality
```bash
# Format code
make format

# Run linters
make lint

# Security scan
make security
```

### Docker Commands
```bash
# Start all services
make dev

# Start only infrastructure
make dev-infra

# View logs
make logs

# Stop all services
make down
```

### Database Access
```bash
# PostgreSQL shell
docker-compose exec postgres psql -U toolkit -d toolkit

# Redis CLI
docker-compose exec redis redis-cli
```

## Customization

### Add More Extensions

Edit `.devcontainer/devcontainer.json` and add to the `extensions` array:
```json
"extensions": [
  "existing.extension",
  "your.new-extension"
]
```

### Change Python Version

Edit `Dockerfile` and change the base image:
```dockerfile
FROM python:3.12-slim as base
```

### Add Environment Variables

Edit `.devcontainer/devcontainer.json`:
```json
"remoteEnv": {
  "CUSTOM_VAR": "value"
}
```

## Troubleshooting

### Container Won't Start

1. **Check Docker is running**: `docker ps`
2. **Rebuild container**: `Dev Containers: Rebuild Container`
3. **Check logs**: View Docker logs in VS Code

### Port Conflicts

If ports are already in use:
1. Stop conflicting services
2. Or change ports in `docker-compose.yml`

### Slow Performance

1. **Allocate more resources** in Docker Desktop settings
2. **Use named volumes** instead of bind mounts for node_modules
3. **Close unused services**: `make down` then start only what you need

### Extensions Not Installing

1. **Rebuild container**: `Dev Containers: Rebuild Container`
2. **Check internet connection**: Extensions download from marketplace
3. **Install manually**: Use VS Code extension marketplace

## Additional Resources

- [VS Code Dev Containers](https://code.visualstudio.com/docs/devcontainers/containers)
- [Dev Container Specification](https://containers.dev/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Project Documentation](../docs/README.md)

## Tips

💡 **Use the integrated terminal**: All terminals opened in VS Code run inside the container

💡 **Git works seamlessly**: Your host Git credentials are forwarded to the container

💡 **Hot reload enabled**: Code changes are immediately reflected (backend and frontend)

💡 **Debug support**: Set breakpoints and debug Python code directly in VS Code

💡 **Multiple terminals**: Open multiple terminals for different services (backend, frontend, etc.)

## Support

For issues with the dev container setup:
1. Check the [troubleshooting section](#troubleshooting) above
2. Search [existing issues](https://github.com/yourusername/toolkit/issues)
3. Create a new issue with the `devcontainer` label
