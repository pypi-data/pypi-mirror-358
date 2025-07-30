# Claude Code in Docker

This setup allows you to run Claude Code in an isolated Docker container with proper permissions and workspace access.

## Prerequisites

- Docker and Docker Compose installed
- Git (recommended for version control)

## Quick Start

1. **Make the setup script executable**:
   ```bash
   chmod +x cli/claude-code.sh
   ```

2. **Run the setup script**:
   ```bash
   ./cli/claude-code.sh
   ```

3. **Complete authentication**:
   - Run `claude` in the container
   - Follow the authentication prompts in your browser
   - Complete the OAuth flow

## Usage

### Starting Claude Code

1. Start the container (if not already running):
   ```bash
   docker-compose -f docker-compose.claude-code.yml up -d
   ```

2. Start an interactive shell:
   ```bash
   docker-compose -f docker-compose.claude-code.yml exec -u node claude-code /bin/bash
   ```

3. Run Claude Code:
   ```bash
   claude
   ```

### Working with Projects

1. Your local `./workspace` directory is mounted at `/workspace` in the container
2. Navigate to your project directory:
   ```bash
   cd /workspace/your-project
   ```

3. Initialize a new project (if needed):
   ```bash
   claude
   > /init
   ```

## Authentication

Claude Code supports multiple authentication methods:

1. **Anthropic Console** (default):
   - Requires active billing at console.anthropic.com
   - Complete OAuth flow in browser

2. **Claude App** (Pro or Max plan):
   - Use your Claude.ai account
   - Select the appropriate plan during authentication

3. **Enterprise platforms**:
   - Configure for Amazon Bedrock or Google Vertex AI
   - Set up using environment variables in `docker-compose.claude-code.yml`

## Troubleshooting

### Permission Issues

If you encounter permission errors:

1. Ensure the `workspace` directory is writable:
   ```bash
   chmod -R 755 workspace
   ```

2. Check container logs:
   ```bash
   docker-compose -f docker-compose.claude-code.yml logs
   ```

### Node.js Version

To verify the Node.js version in the container:
```bash
docker-compose -f docker-compose.claude-code.yml exec -u node claude-code node --version
```

## Stopping the Container

To stop the container:
```bash
docker-compose -f docker-compose.claude-code.yml down
```

## Security Notes

- The container runs as a non-root user
- Only the `workspace` directory is mounted
- NPM cache and config are stored in Docker volumes
- No sudo access inside the container
