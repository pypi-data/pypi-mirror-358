# Claude Code CLI

This directory contains the command-line interface (CLI) for the Claude Code project, which provides an interactive environment for working with Anthropic's Claude AI models.

## Overview

The CLI is implemented as a Docker-based environment that provides:

1. A Node.js runtime with the `@anthropic-ai/sdk` pre-installed
2. An interactive shell for running Claude commands
3. Integration with the main Python-based Claude client

## Prerequisites

- Docker and Docker Compose
- Anthropic API key

## Setup

1. Copy the example environment file and update it with your API key:

   ```bash
   cp .env.example .env
   # Edit .env and set your ANTHROPIC_API_KEY
   ```

2. Make the CLI script executable:

   ```bash
   chmod +x cli/claude-code.sh
   ```

## Usage

### Starting the CLI

Run the CLI using the provided script:

```bash
./cli/claude-code.sh
```

This will:
1. Start the Docker container if it's not already running
2. Install the latest `@anthropic-ai/sdk` globally in the container
3. Open an interactive shell in the container

### Available Commands

Once inside the container, you can use the following commands:

- `node` - Start a Node.js REPL with the Anthropic SDK available
- `npm install -g @anthropic-ai/sdk` - Update the SDK to the latest version
- `exit` - Exit the container

### Example: Using the Anthropic SDK

```javascript
// In the Node.js REPL
const { Anthropic } = require('@anthropic-ai/sdk');

const anthropic = new Anthropic({
  apiKey: process.env.ANTHROPIC_API_KEY
});

async function main() {
  const message = await anthropic.messages.create({
    model: 'claude-3-opus-20240229',
    max_tokens: 1024,
    messages: [{ role: 'user', content: 'Hello, Claude' }]
  });
  
  console.log(message);
}

main().catch(console.error);
```

## Development

### File Structure

- `claude-code.sh` - Main script to start the CLI environment
- `docker-compose.claude-code.yml` - Docker Compose configuration

### Adding New Dependencies

To add new Node.js dependencies:

1. Edit the `entrypoint` in `docker-compose.claude-code.yml` to include the new package:

   ```yaml
   entrypoint: |
     /bin/sh -c '
     # ... existing setup ...
     su -c "npm install -g @anthropic-ai/sdk new-package-name" node && \
     # ... rest of the entrypoint
     '
   ```

2. Rebuild and restart the container:

   ```bash
   docker-compose -f docker-compose.claude-code.yml up -d --build
   ```

## Troubleshooting

### Permission Issues

If you encounter permission issues with the container:

```bash
# Check container logs
docker logs claude-code

# Fix permissions on mounted volumes
docker exec claude-code chown -R node:node /workspace
```

### Updating the SDK

To update to the latest version of the Anthropic SDK:

```bash
docker exec -u node claude-code npm install -g @anthropic-ai/sdk@latest
```

## License

This project is licensed under the terms of the MIT license.
