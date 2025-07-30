#!/bin/bash

# Install Claude CLI on Linux
# Supports Fedora, Ubuntu/Debian, and other RPM/DNF-based distributions

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to install Python and pip if not present
install_python() {
    if ! command_exists python3 || ! command_exists pip3; then
        echo -e "${YELLOW}Python 3 and pip not found. Installing...${NC}"
        
        if command_exists dnf; then
            sudo dnf install -y python3 python3-pip
        elif command_exists yum; then
            sudo yum install -y python3 python3-pip
        elif command_exists apt-get; then
            sudo apt-get update
            sudo apt-get install -y python3 python3-pip
        elif command_exists pacman; then
            sudo pacman -S --noconfirm python python-pip
        else
            echo -e "${RED}Could not determine package manager. Please install Python 3 and pip manually.${NC}"
            exit 1
        fi
    fi
    
    # Upgrade pip
    pip3 install --upgrade pip
}

# Function to install Claude API Python package
install_claude() {
    echo -e "${YELLOW}Installing Claude API Python package...${NC}"
    pip3 install anthropic
    
    # Create CLI script
    local cli_path="$HOME/.local/bin/claude"
    
    cat > "$cli_path" << 'EOF'
#!/usr/bin/env python3

import os
import sys
import argparse
from anthropic import Anthropic
from getpass import getpass

def main():
    parser = argparse.ArgumentParser(description='Claude CLI')
    parser.add_argument('prompt', nargs='?', help='Your prompt to Claude')
    parser.add_argument('-m', '--model', default='claude-3-opus-20240229', 
                      help='Model to use (default: claude-3-opus-20240229)')
    parser.add_argument('-t', '--temperature', type=float, default=0.7,
                      help='Sampling temperature (0.0 to 1.0, default: 0.7)')
    args = parser.parse_args()

    # Get API key from environment or prompt
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        api_key = getpass('Enter your Anthropic API key: ')
        os.environ['ANTHROPIC_API_KEY'] = api_key

    client = Anthropic(api_key=api_key)

    if not args.prompt:
        print("Enter your prompt (Ctrl+D on a new line to finish):")
        prompt = sys.stdin.read()
    else:
        prompt = args.prompt

    try:
        message = client.messages.create(
            model=args.model,
            max_tokens=4000,
            temperature=args.temperature,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        print("\nClaude:")
        print(message.content[0].text)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
EOF

    chmod +x "$cli_path"
    echo -e "${GREEN}Claude CLI installed successfully at $cli_path${NC}"
    echo -e "${YELLOW}Make sure to add $HOME/.local/bin to your PATH if it's not already.${NC}"
    echo -e "${YELLOW}Set your Anthropic API key as ANTHROPIC_API_KEY environment variable or enter it when prompted.${NC}"
}

# Main installation process
main() {
    echo -e "${GREEN}Starting Claude CLI installation...${NC}"
    
    # Install Python and pip if not present
    install_python
    
    # Install Claude API
    install_claude
    
    echo -e "\n${GREEN}Installation complete!${NC}"
    echo -e "Usage examples:"
    echo -e "  $ claude "'"'Your prompt here'"'"
    echo -e "  $ echo "'"'Your prompt here'"' | claude"
    echo -e "  $ claude -m claude-3-sonnet-20240229 "'"'Your prompt'"'"
    echo -e "\n${YELLOW}Note: You'll need to set your Anthropic API key as an environment variable:${NC}"
    echo -e "  export ANTHROPIC_API_KEY='your-api-key-here'"
    echo -e "Or you'll be prompted to enter it on first use."
}

# Run the installation
main "$@"
