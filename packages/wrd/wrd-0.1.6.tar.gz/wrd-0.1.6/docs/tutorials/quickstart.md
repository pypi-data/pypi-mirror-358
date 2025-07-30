# Quick Start Guide

This guide will help you quickly get started with WRD.

## Installation

```bash
# Install from PyPI
pip install wrd

# Or install from source
git clone https://github.com/yourusername/wrd.git
cd wrd
pip install -e .
```

## Basic Usage

### Initialize a New Project

```bash
# Interactive mode
wrd init my-project

# Non-interactive mode
wrd init my-project --template python --description "My awesome project"
```

### Use the Interactive Shell

```bash
wrd shell
```

### List Available Templates

```bash
wrd list-templates
```

### Configure WRD

```bash
wrd config
```

## Creating a Python Project

1. Initialize a new project:
   ```bash
   wrd init my-python-project --template python
   ```

2. Navigate to your project:
   ```bash
   cd my-python-project
   ```

3. Start developing!

## Next Steps

- Learn how to [configure WRD](how-to-guides/configuration.md)
- Explore [creating custom templates](how-to-guides/custom-templates.md)
- Check out [example projects](examples/)
