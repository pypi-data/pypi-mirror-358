# Claude Development Environment in Docker

This setup provides a complete, containerized development environment for working with Claude, including:

- VS Code in the browser with Python and Node.js support
- Claude Code CLI (Node.js)
- Python environment with Claude API client
- Secure file access and environment configuration

## Prerequisites

- Docker and Docker Compose installed
- Git (for version control)
- At least 4GB of free disk space

## Getting Started

1. **Clone the repository** (if not already done):
   ```bash
   git clone https://github.com/yourusername/wrd.git
   cd wrd
   ```

2. **Configure environment variables**:
   ```bash
   cp .env.example .env
   nano .env  # or use your preferred editor
   ```
   Update the following variables:
   ```bash
   # User and group IDs (run `id -u` and `id -g` to get your values)
   UID=1000
   GID=1000
   
   # VS Code password
   VSCODE_PASSWORD=your_secure_password
   
   # Claude API Key (get from https://console.anthropic.com/)
   ANTHROPIC_API_KEY=your_api_key_here
   ```

3. **Start the containers**:
   ```bash
   docker-compose -f docker-compose.claude-code.yml up -d
   ```

4. **Access the environment**:
   - VS Code in browser: http://localhost:8080 (password from .env)
   - For CLI access: `docker exec -it claude-code bash`

## Services

### 1. VS Code in Browser
- Access at: http://localhost:8080
- Default password: (set in .env as VSCODE_PASSWORD)
- Includes:
  - Python 3 with Claude API client
  - Jupyter support
  - Node.js and npm
  - Pre-installed VS Code extensions

### 2. Claude Code CLI
- Access via: `docker exec -it claude-code bash`
- Includes:
  - Node.js 18 LTS
  - @anthropic-ai/cli installed globally
  - Workspace mounted at `/workspace`

## File Access

The following directories are mounted in the containers:
- `./workspace` - Your main workspace directory (shared between containers)
- Configuration files are persisted in Docker volumes:
  - `claude-code-cache` - npm cache for Node.js
  - `claude-code-config` - Configuration files
  - `vscode-extensions` - VS Code extensions
  - `vscode-config` - VS Code configuration

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `UID` | User ID for container user | 1000 |
| `GID` | Group ID for container user | 1000 |
| `TZ` | Timezone | UTC |
| `VSCODE_PASSWORD` | Password for VS Code web interface | password |
| `SUDO_PASSWORD` | Password for sudo in container | password |
| `ANTHROPIC_API_KEY` | Your Claude API key | (none) |

## Security Notes

- Containers run with non-root user by default
- File system access is restricted to specified volumes
- Sensitive credentials should be stored in `.env` file (which is in `.gitignore`)
- VS Code web interface is password protected

## Stopping the Environment

To stop all containers:
```bash
docker-compose -f docker-compose.claude-code.yml down
```

To stop and remove all data (including volumes):
```bash
docker-compose -f docker-compose.claude-code.yml down -v
```

## Troubleshooting

### Common Issues

1. **Port conflicts**
   - Ensure ports 8080 (VS Code) and 3000 (Claude web UI) are available
   - Update the ports in `docker-compose.claude-code.yml` if needed

2. **Permission issues**
   - Ensure the current user has read/write access to mounted directories
   - Check that UID/GID in `.env` match your host user

3. **Out of disk space**
   - Clean up unused Docker resources:
     ```bash
     docker system prune -a --volumes
     ```
   - Check disk usage:
     ```bash
     docker system df
     ```

4. **View logs**
   ```bash
   # VS Code container logs
   docker logs claude-vscode
   
   # Claude Code CLI container logs
   docker logs claude-code
   ```

## Customization

### Adding VS Code Extensions
Edit `Dockerfile.claude-ide` and add more extensions:
```dockerfile
RUN code-server --install-extension publisher.extension-id
```

### Adding System Dependencies
Edit `Dockerfile.claude-ide` and add packages:
```dockerfile
RUN apt-get update && apt-get install -y package-name
```

### Adding Node.js Dependencies
Edit `Dockerfile.claude-ide` and add global packages:
```dockerfile
RUN npm install -g package-name
```

## Development Workflow

1. Start the environment:
   ```bash
   docker-compose -f docker-compose.claude-code.yml up -d
   ```

2. Access VS Code in browser at http://localhost:8080

3. For CLI access:
   ```bash
   # Access Claude Code CLI
   docker exec -it claude-code bash
   
   # Run Claude commands
   claude --help
   ```

4. Your code lives in the `workspace` directory and persists between container restarts
