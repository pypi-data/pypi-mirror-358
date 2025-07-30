#!/bin/bash

# Claude Code Installation Script for Linux
# Supports Fedora, Ubuntu/Debian, and other Linux distributions
# This script will set up Node.js, npm, and install Claude Code

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

# Function to detect Linux distribution
detect_linux_distro() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        echo "$ID"
    elif [ -f /etc/redhat-release ]; then
        echo "rhel"
    elif [ -f /etc/debian_version ]; then
        echo "debian"
    else
        echo "unknown"
    fi
}

# Function to install system dependencies
install_dependencies() {
    local distro=$(detect_linux_distro)
    
    echo -e "${YELLOW}Installing system dependencies...${NC}"
    
    case $distro in
        "fedora" | "rhel" | "centos")
            sudo dnf install -y curl git nodejs npm
            ;;
        "ubuntu" | "debian" | "linuxmint" | "pop" | "elementary" | "kali" | "parrot")
            sudo apt-get update
            sudo apt-get install -y curl git nodejs npm
            ;;
        "arch" | "manjaro" | "endeavouros")
            sudo pacman -S --noconfirm curl git nodejs npm
            ;;
        "opensuse-tumbleweed" | "opensuse-leap" | "suse")
            sudo zypper install -y curl git nodejs npm
            ;;
        *)
            echo -e "${YELLOW}Unsupported distribution. Trying to install with generic package manager...${NC}"
            if command_exists dnf; then
                sudo dnf install -y curl git nodejs npm
            elif command_exists apt-get; then
                sudo apt-get update
                sudo apt-get install -y curl git nodejs npm
            elif command_exists pacman; then
                sudo pacman -S --noconfirm curl git nodejs npm
            elif command_exists zypper; then
                sudo zypper install -y curl git nodejs npm
            else
                echo -e "${RED}Could not determine package manager. Please install Node.js and npm manually.${NC}"
                exit 1
            fi
            ;;
    esac
}

# Function to install NVM (Node Version Manager)
install_nvm() {
    echo -e "${YELLOW}Installing NVM (Node Version Manager)...${NC}"
    
    if [ ! -d "$HOME/.nvm" ]; then
        curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
        
        # Load NVM
        export NVM_DIR="$HOME/.nvm"
        [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
        [ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"
        
        echo -e "${GREEN}NVM installed successfully.${NC}"
    else
        echo -e "${YELLOW}NVM is already installed.${NC}"
        # Load NVM if not already loaded
        export NVM_DIR="$HOME/.nvm"
        [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
        [ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"
    fi
    
    # Install the latest LTS version of Node.js
    nvm install --lts
    nvm use --lts
}

# Function to set up npm global directory
setup_npm_global() {
    echo -e "${YELLOW}Setting up npm global directory...${NC}"
    
    # Create a directory for global npm packages
    mkdir -p "$HOME/.npm-global"
    
    # Configure npm to use the new directory
    npm config set prefix "$HOME/.npm-global"
    
    # Add to PATH if not already present
    if ! grep -q "\.npm-global" "$HOME/.bashrc"; then
        echo 'export PATH=~/.npm-global/bin:$PATH' >> "$HOME/.bashrc"
        echo 'export NPM_CONFIG_PREFIX=~/.npm-global' >> "$HOME/.bashrc"
    fi
    
    # Update current shell
    export PATH="$HOME/.npm-global/bin:$PATH"
    export NPM_CONFIG_PREFIX="$HOME/.npm-global"
    
    echo -e "${GREEN}npm global directory set up at $HOME/.npm-global${NC}"
}

# Function to install Claude Code
install_claude_code() {
    echo -e "${YELLOW}Installing Claude Code...${NC}"
    
    # Install Claude Code globally
    npm install -g @anthropic-ai/claude-code
    
    echo -e "${GREEN}Claude Code installed successfully!${NC}"
}

# Function to verify installation
verify_installation() {
    echo -e "\n${YELLOW}Verifying installation...${NC}"
    
    echo -e "\n${GREEN}Installation complete!${NC}"
    echo -e "\nTo start using Claude Code, you may need to run:"
    echo -e "source ~/.bashrc  # or open a new terminal"
    echo -e "claude-code --help  # to see available commands"
    
    echo -e "\n${YELLOW}Note:${NC} Make sure to set your Anthropic API key as an environment variable:"
    echo -e "export ANTHROPIC_API_KEY='your-api-key-here'"
    echo -e "Or add it to your ~/.bashrc file for persistence."
}

# Main installation process
main() {
    echo -e "${GREEN}Starting Claude Code installation...${NC}"
    
    # Check if running as root
    if [ "$(id -u)" -eq 0 ]; then
        echo -e "${RED}This script should not be run as root. Please run as a normal user.${NC}"
        exit 1
    fi
    
    # Install system dependencies
    install_dependencies
    
    # Install NVM and Node.js
    install_nvm
    
    # Set up npm global directory
    setup_npm_global
    
    # Install Claude Code
    install_claude_code
    
    # Verify installation
    verify_installation
}

# Run the installation
main "$@"
