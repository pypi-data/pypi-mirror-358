# Configuration Guide

WRD can be configured using a YAML configuration file located at `~/.wrd/config.yaml`.

## Default Configuration

When you first run WRD, it will create a default configuration file with the following structure:

```yaml
# WRD Configuration
version: '1.0.0'

# Project settings
projects_dir: ~/projects
editor: code  # Default code editor

default_language: python
default_template: python

# AI Tools configuration
ai_tools:
  claude_code:
    enabled: true
    api_key: ${CLAUDE_API_KEY}  # Read from environment variable

# Workflow settings
workflows:
  documentation_auto: true
  commit_auto_describe: true

# User preferences
settings:
  auto_update: true
  check_updates: true
  notifications: true
  shell_timeout: 10  # seconds
  shell_beep: true   # Audible feedback in shell

# Recently used projects
recent_projects: []
```

## Environment Variables

WRD supports the following environment variables:

- `WRD_PROJECTS_DIR`: Override the default projects directory
- `EDITOR`: Default editor to use
- `CLAUDE_API_KEY`: API key for Claude Code integration
- `WRD_DEBUG`: Enable debug mode

## Custom Templates

You can add custom templates by placing them in `~/.wrd/user_templates/`. Each template should have its own directory with a `template.yml` file.

Example template structure:

```
~/.wrd/user_templates/
└── my-template/
    ├── template.yml
    ├── {{cookiecutter.project_name}}/
    │   ├── {{cookiecutter.project_slug}}/
    │   └── tests/
    └── {{cookiecutter.project_name}}.jinja2
```

## Claude Code Integration

For detailed instructions on setting up and configuring Claude Code, see the [Claude Code Setup Guide](./claude-code-setup.md).

## Shell Configuration

To enable shell completion, add the following to your shell configuration file:

### Bash

```bash
eval "$(_WRD_COMPLETE=bash_source wrd)" >> ~/.bashrc
```

### Zsh

```zsh
eval "$(_WRD_COMPLETE=zsh_source wrd)" >> ~/.zshrc
```

### Fish

```fish
_WRD_COMPLETE=fish_source wrd | source
```
