# Claude IDE in Docker

This setup provides a secure, containerized environment for running Claude with VS Code in the browser, complete with controlled file access and MCP server configuration.

## Prerequisites

- Docker and Docker Compose installed
- Git (for version control)

## Getting Started

1. **Clone the repository** (if not already done):
   ```bash
   git clone https://github.com/yourusername/wrd.git
   cd wrd
   ```

2. **Configure environment variables**:
   - Copy `.env.example` to `.env`
   - Update the `.env` file with your preferred settings
   ```bash
   cp .env.example .env
   nano .env  # or use your preferred editor
   ```

3. **Build and start the container**:
   ```bash
   docker-compose up -d --build
   ```

4. **Access VS Code in your browser**:
   - Open `https://localhost:8443` in your browser
   - Log in with the password from your `.env` file

## File Access

By default, the container has access to:
- `./workspace` - Your main workspace directory
- `./config` - Configuration files for VS Code

To add more directories, edit the `volumes` section in `docker-compose.yml`.

## MCP Server Configuration

To connect to an MCP server:

1. Uncomment and configure the MCP server section in `docker-compose.yml`
2. Update the MCP-related environment variables in `.env`
3. Restart the container:
   ```bash
   docker-compose down
   docker-compose up -d
   ```

## Security Notes

- The container runs with minimal privileges
- File system access is restricted to specified volumes
- All unnecessary capabilities are dropped
- The container runs in read-only mode with temporary file systems

## Stopping the Container

To stop the container:
```bash
docker-compose down
```

## Troubleshooting

- If you can't access the web interface, check if the ports are already in use
- Check container logs: `docker-compose logs -f`
- For permission issues, ensure the current user has access to the mounted volumes

## Customization

- To install additional VS Code extensions, add them to the `Dockerfile.claude-ide`
- To add more tools, update the Dockerfile and rebuild the container
