"""WRD Command Line Interface."""

import os
import sys
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List
from rich.console import Console
from rich.prompt import Prompt, Confirm, IntPrompt
from rich.panel import Panel
from rich.table import Table
from rich.progress import track
import subprocess
import shutil

console = Console()


class WRDConfig:
    """Manage WRD configuration."""

    def __init__(self):
        self.config_dir = Path.home() / ".wrd"
        self.config_file = self.config_dir / "config.yaml"
        self.templates_dir = self.config_dir / "templates"
        self.ensure_directories()
        self.config = self.load_config()

    def ensure_directories(self):
        """Ensure configuration directories exist."""
        self.config_dir.mkdir(exist_ok=True)
        self.templates_dir.mkdir(exist_ok=True)

    def load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        if not self.config_file.exists():
            return {
                "projects_dir": str(Path.home() / "projects"),
                "editor": os.environ.get("EDITOR", "code"),
                "default_language": "python",
                "templates": {},
            }

        with open(self.config_file, 'r') as f:
            return yaml.safe_load(f) or {}

    def save_config(self):
        """Save configuration to YAML file."""
        with open(self.config_file, 'w') as f:
            yaml.dump(self.config, f, default_flow_style=False)


class WRDShell:
    """Interactive WRD shell."""

    def __init__(self):
        self.config = WRDConfig()
        self.current_project = None
        self.console = Console()

    def print_banner(self):
        """Print WRD banner."""
        banner = """
        ██╗    ██╗██████╗ ██████╗ 
        ██║    ██║██╔══██╗██╔══██╗
        ██║ █╗ ██║██████╔╝██║  ██║
        ██║███╗██║██╔══██╗██║  ██║
        ╚███╔███╔╝██║  ██║██████╔╝
         ╚══╝╚══╝ ╚═╝  ╚═╝╚═════╝ 
        WRD - WRonai Development Tool
        """
        self.console.print(Panel.fit(banner, style="bold blue"))

    def get_menu_choice(
        self, title: str, options: List[Dict[str, str]], timeout: int = 10
    ) -> str:
        """Display a menu and get user choice."""
        table = Table(title=title, show_header=False, show_lines=True)
        table.add_column("Option", style="cyan")
        table.add_column("Description")

        for i, option in enumerate(options, 1):
            table.add_row(str(i), option['description'])

        self.console.print(table)

        try:
            choice = IntPrompt.ask(
                "\nEnter your choice",
                choices=[str(i) for i in range(1, len(options) + 1)],
                timeout=timeout,
            )
            return options[int(choice) - 1]['command']
        except Exception:
            self.console.print("\n[bold red]Timeout reached. Using default option.[/]")
            return options[0]['command']

    def init_project(self, project_path: Optional[str] = None):
        """Initialize a new project."""
        if project_path is None:
            project_path = Prompt.ask("Enter project path", default=str(Path.cwd()))

        project_path = Path(project_path).absolute()

        if project_path.exists() and any(project_path.iterdir()):
            self.console.print(f"[yellow]Directory {project_path} is not empty.[/]")
            if not Confirm.ask("Do you want to initialize a project here anyway?"):
                return

        # Get project details
        project_name = project_path.name
        language = Prompt.ask(
            "Project language",
            default=self.config.config.get('default_language', 'python'),
        )
        description = Prompt.ask("Project description", default="")

        # Create project structure
        project_path.mkdir(parents=True, exist_ok=True)

        # Initialize project based on language
        if language == 'python':
            self._init_python_project(project_path, project_name, description)
        # Add more language support here

        self.console.print(
            f"[green]✓ Project {project_name} initialized successfully![/]"
        )

    def _init_python_project(self, project_path: Path, name: str, description: str):
        """Initialize a Python project."""
        # Create basic Python project structure
        (project_path / 'src' / name.replace('-', '_')).mkdir(
            parents=True, exist_ok=True
        )
        (project_path / 'tests').mkdir(exist_ok=True)

        # Create pyproject.toml
        pyproject = f"""[build-system]
requires = ["setuptools>=42.0"]
build-backend = "setuptools.build_meta"

[project]
name = "{name}"
version = "0.1.0"
description = "{description}"
authors = [
    {{ name = "Your Name", email = "your.email@example.com" }}
]
readme = "README.md"
requires-python = ">=3.8"

[project.optional-dependencies]
dev = [
    "pytest>=6.0",
    "black>=21.12b0",
    "isort>=5.10.1",
    "mypy>=0.910",
    "pytest-cov>=2.0"
]
"""
        (project_path / 'pyproject.toml').write_text(pyproject)

        # Create README.md
        readme = f"""# {name}

{description}

## Installation

```bash
pip install -e .
```

## Development

Install development dependencies:

```bash
pip install -e ".[dev]"
```

Run tests:

```bash
pytest
```
"""
        (project_path / 'README.md').write_text(readme)

        # Create .gitignore
        gitignore = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
env/

# IDE
.idea/
.vscode/
*.swp
*.swo

# Testing
.coverage
htmlcov/
.pytest_cache/
"""
        (project_path / '.gitignore').write_text(gitignore)

        # Initialize git repository
        try:
            subprocess.run(['git', 'init'], cwd=project_path, check=True)
            subprocess.run(['git', 'add', '.'], cwd=project_path, check=True)
            subprocess.run(
                ['git', 'commit', '-m', 'Initial commit'], cwd=project_path, check=True
            )
        except Exception as e:
            self.console.print(
                f"[yellow]Warning: Failed to initialize git repository: {e}[/]"
            )

    def shell(self):
        """Start interactive shell."""
        self.print_banner()

        while True:
            try:
                options = [
                    {'command': 'init', 'description': 'Initialize a new project'},
                    {'command': 'list', 'description': 'List all projects'},
                    {'command': 'config', 'description': 'Configure WRD'},
                    {'command': 'exit', 'description': 'Exit WRD shell'},
                ]

                choice = self.get_menu_choice("WRD - Main Menu", options, timeout=60)

                if choice == 'init':
                    self.init_project()
                elif choice == 'list':
                    self.list_projects()
                elif choice == 'config':
                    self.configure()
                elif choice == 'exit':
                    self.console.print("[green]Goodbye![/]")
                    break

            except KeyboardInterrupt:
                self.console.print("\n[red]Operation cancelled.[/]")
            except Exception as e:
                self.console.print(f"[red]Error: {e}[/]")

    def list_projects(self):
        """List all projects in the projects directory."""
        projects_dir = Path(
            self.config.config.get('projects_dir', Path.home() / 'projects')
        )

        if not projects_dir.exists():
            self.console.print("[yellow]No projects directory found.[/]")
            return

        table = Table(title="Projects")
        table.add_column("Name", style="cyan")
        table.add_column("Path")
        table.add_column("Modified")

        for project_dir in projects_dir.iterdir():
            if project_dir.is_dir():
                modified = datetime.fromtimestamp(project_dir.stat().st_mtime).strftime(
                    '%Y-%m-%d %H:%M'
                )
                table.add_row(project_dir.name, str(project_dir), modified)

        self.console.print(table)

    def configure(self):
        """Configure WRD settings."""
        self.console.print("[bold]Current Configuration:[/]")
        for key, value in self.config.config.items():
            self.console.print(f"  [cyan]{key}:[/] {value}")

        if Confirm.ask("\nDo you want to change any settings?"):
            setting = Prompt.ask("Enter setting name")
            if setting in self.config.config:
                if isinstance(self.config.config[setting], bool):
                    new_value = Confirm.ask(f"New value for {setting}")
                else:
                    new_value = Prompt.ask(f"New value for {setting}")
                self.config.config[setting] = new_value
                self.config.save_config()
                self.console.print("[green]✓ Configuration updated.[/]")
            else:
                self.console.print("[red]Invalid setting name.[/]")


def main():
    """Entry point for the WRD CLI."""
    if len(sys.argv) > 1 and sys.argv[1] == 'shell':
        WRDShell().shell()
    elif len(sys.argv) > 1 and sys.argv[1] == 'init':
        WRDShell().init_project(sys.argv[2] if len(sys.argv) > 2 else None)
    else:
        console = Console()
        console.print("WRD - WRonai Development Tool")
        console.print("\nUsage:")
        console.print("  wrd shell     - Start interactive shell")
        console.print("  wrd init [path] - Initialize a new project")
        console.print("  wrd --help    - Show this help")


if __name__ == "__main__":
    main()
