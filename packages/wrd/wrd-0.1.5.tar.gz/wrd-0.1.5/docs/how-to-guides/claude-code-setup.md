# Claude Code Setup Guide

This guide provides comprehensive instructions for setting up Claude Code on Linux systems, including Fedora. Claude Code is a powerful AI coding assistant that can be accessed via the command line.

> **Note**: Claude Code is currently available only in supported countries. Please check the [Anthropic website](https://www.anthropic.com) for availability in your region.

## Prerequisites

- A Linux distribution (tested on Fedora, Ubuntu, and Debian)
- Node.js (v16 or later recommended)
- npm (Node Package Manager)
- Python 3.8+ (for alternative Python client)
- Git
- An Anthropic API key

## Installation

### Prerequisites

- Node.js 18 or later
- npm (comes with Node.js)
- Git (recommended for version control)
- An Anthropic account with active billing (for API access)
- Supported shell: Bash, Zsh, or Fish

### Method 1: Using the Installation Script (Recommended)

We provide a convenient installation script that handles all the setup for you:

1. Download the installation script:
   ```bash
   curl -O https://raw.githubusercontent.com/wronai/wrd/main/install_claude_code.sh
   chmod +x install_claude_code.sh
   ```

2. Run the installation script:
   ```bash
   ./install_claude_code.sh
   ```

3. The script will:
   - Install system dependencies
   - Set up Node.js using NVM (Node Version Manager)
   - Configure npm to use a local directory to avoid permission issues
   - Install the Claude Code CLI globally
   - Provide instructions for authentication

### Method 2: Manual Installation

If you prefer to install manually, follow these steps:

1. **Install Node.js and npm**:
   ```bash
   # For Fedora
   sudo dnf install -y nodejs npm
   
   # For Debian/Ubuntu
   # sudo apt update && sudo apt install -y nodejs npm
   ```

2. **Set up npm to use a local directory** (avoids permission issues):
   ```bash
   mkdir -p ~/.npm-global
   npm config set prefix '~/.npm-global'
   echo 'export PATH=~/.npm-global/bin:$PATH' >> ~/.bashrc
   source ~/.bashrc
   ```

3. **Install Claude Code CLI globally**:
   ```bash
   npm install -g @anthropic-ai/claude-code
   ```

## Configuration

## Authentication

Claude Code offers multiple authentication options:

### 1. Anthropic Console (Default)
1. Run `claude` in your terminal
2. Select the option to authenticate via Anthropic Console
3. Complete the OAuth process in your browser
4. Requires active billing at [console.anthropic.com](https://console.anthropic.com)

### 2. Claude App (Pro or Max Plan)
1. Subscribe to Claude's Pro or Max plan at [claude.ai](https://claude.ai)
2. Run `claude` in your terminal
3. Select the Claude App authentication option
4. Log in with your Claude.ai credentials

### 3. Enterprise Platforms
For enterprise deployments, you can configure Claude Code to use:
- Amazon Bedrock
- Google Vertex AI

Contact your enterprise administrator for specific configuration details.

### 4. API Key (Legacy)
If you prefer to use an API key directly:

1. Get your Anthropic API key from the [Anthropic Console](https://console.anthropic.com/)
2. Set the API key as an environment variable:
   ```bash
   # For Bash
   echo 'export ANTHROPIC_API_KEY="your-api-key-here"' >> ~/.bashrc
   source ~/.bashrc
   
   # For Zsh
   echo 'export ANTHROPIC_API_KEY="your-api-key-here"' >> ~/.zshrc
   source ~/.zshrc
   
   # For Fish
   set -Ux ANTHROPIC_API_KEY "your-api-key-here"
   ```

### WRD Integration

If you're using WRD, you can configure Claude Code by updating your `~/.wrd/config.yaml`:

```yaml
ai_tools:
  claude_code:
    enabled: true
    api_key: ${ANTHROPIC_API_KEY}  # Read from environment variable
    default_model: claude-3-opus-20240229
    max_tokens: 4000
    temperature: 0.7
```

## Project Initialization

For first-time users, we recommend initializing your project:

1. Navigate to your project directory:
   ```bash
   cd your-project-directory
   ```

2. Start Claude Code:
   ```bash
   claude
   ```

3. Run a simple command to test the setup:
   ```
   > summarize this project
   ```

4. Generate a `CLAUDE.md` project guide:
   ```
   /init
   ```

5. Commit the generated `CLAUDE.md` file to your repository.

## Usage

### Basic Usage

```bash
# Start an interactive chat session
claude-code chat

# Get a response to a single prompt
claude-code prompt "Explain how to use Claude Code"

# Specify a different model
claude-code --model claude-3-sonnet-20240229 prompt "Write a Python function to reverse a string"
```

### Common Options

- `--model`: Specify the model to use (default: claude-3-opus-20240229)
- `--max-tokens`: Maximum number of tokens to generate (default: 4000)
- `--temperature`: Controls randomness (0.0 to 1.0, default: 0.7)
- `--top-p`: Nucleus sampling parameter (0.0 to 1.0)
- `--stream`: Stream the response

### Interactive Mode

```bash
claude-code interactive
```

In interactive mode, you can:
- Type your messages and press Enter to send
- Use `Ctrl+D` to exit
- Type `/help` to see available commands

## Troubleshooting

## Troubleshooting

### Permission Denied Errors

If you encounter permission errors when installing npm packages globally:

1. Make sure you've set up npm to use a local directory as shown in the installation steps
2. Ensure the npm global bin directory is in your PATH:
   ```bash
   echo 'export PATH="$(npm config get prefix)/bin:$PATH"' >> ~/.bashrc
   source ~/.bashrc
   ```

### WSL (Windows Subsystem for Linux) Issues

If you're using WSL and encounter issues:

1. **OS/Platform Detection Issues**:
   ```bash
   # Set the correct OS before installation
   npm config set os linux
   
   # Install with OS check disabled
   npm install -g @anthropic-ai/claude-code --force --no-os-check
   ```
   > **Important**: Do NOT use `sudo` with npm install as it can lead to permission issues.

2. **Node Not Found Errors**:
   If you see `exec: node: not found` when running `claude`:
   - Check your Node.js installation paths:
     ```bash
     which npm
     which node
     ```
   - These should point to Linux paths (starting with `/usr/`) not Windows paths (starting with `/mnt/c/`)
   - If needed, reinstall Node.js using your Linux distribution's package manager or nvm

### Node.js Version Issues

If you need to manage multiple Node.js versions, we recommend using NVM (Node Version Manager):

```bash
# Install NVM
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.3/install.sh | bash

# Install and use Node.js LTS
nvm install --lts
nvm use --lts
```

### API Key Not Found

If you get an error about the API key not being found:

1. Verify the API key is set in your environment:
   ```bash
   echo $ANTHROPIC_API_KEY
   ```
2. Make sure you've sourced your shell configuration file after adding the API key
3. Try setting the API key directly in your command:
   ```bash
   ANTHROPIC_API_KEY=your-key-here claude-code prompt "Hello"
   ```

## Advanced Usage

### Using with WRD Workflows

You can integrate Claude Code with WRD workflows by adding it to your project's workflow configuration:

```yaml
# .wrd/workflows/code_review.yaml
name: Code Review Workflow
description: Automated code review using Claude Code
triggers:
  - pull_request
  - push

jobs:
  claude-code-review:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
        
      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          
      - name: Install Claude Code
        run: npm install -g @anthropic-ai/claude-code
        
      - name: Run code review
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          # Example: Run code review on changed files
          git diff --name-only HEAD^ HEAD | xargs -I{} sh -c '
            echo "\nReviewing $1..."
            claude-code prompt "Review this code for potential issues, security vulnerabilities, and improvements:\n\n$(cat "$1")"
          ' _ {}'
```

### Customizing the Model Behavior

You can customize how Claude Code responds by providing a system prompt:

```bash
claude-code --system "You are a senior software engineer with 10+ years of experience in Python and cloud technologies. Provide concise, professional code reviews." prompt "Review this code..."
```

## Terminal Optimization

For the best Claude Code experience, optimize your terminal setup:

### Supported Shells
- Bash
- Zsh
- Fish

### Recommended Configuration
1. Enable syntax highlighting in your shell
2. Use a modern terminal emulator that supports:
   - 24-bit color
   - Unicode characters
   - Smooth scrolling
3. Consider using a terminal multiplexer like `tmux` or `screen` for long-running sessions

## Best Practices

1. **Environment Variables**: Always use environment variables for API keys instead of hardcoding them in scripts.
2. **Model Selection**: Choose the appropriate model based on your needs:
   - `claude-3-opus-20240229`: Most capable, highest cost
   - `claude-3-sonnet-20240229`: Balanced performance and cost
   - `claude-3-haiku-20240307`: Fastest, most cost-effective
3. **Rate Limiting**: Be aware of API rate limits and implement appropriate backoff strategies in automated workflows.
4. **Error Handling**: Always implement proper error handling when using Claude Code in scripts.
5. **Security**: 
   - Never commit API keys to version control
   - Use environment variables or secret management solutions
   - Regularly rotate your API keys
   - Use the principle of least privilege for API key permissions

## Support

For additional help, please refer to:
- [Anthropic Documentation](https://docs.anthropic.com/)
- [WRD Documentation](https://wronai.github.io/wrd/)
- [GitHub Issues](https://github.com/wronai/wrd/issues)

## License

This documentation is part of the WRD project and is licensed under the MIT License.
