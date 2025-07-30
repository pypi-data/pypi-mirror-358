#!/usr/bin/env python3
"""WRD (Word) - Python Package

A powerful workflow automation tool for developers, inspired by Claude Code workflow.

Features:
- Project management
- Documentation automation
- AI tools integration
- Workflow optimization
- Interactive shell
- Project templates
"""

import logging
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, TypeVar, Union

import typer
import yaml
from rich.console import Console
from rich.logging import RichHandler
from rich.table import Table

from . import __version__

# Template manager is imported on demand to avoid circular imports

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[
        RichHandler(
            rich_tracebacks=True, markup=True, show_time=False, show_path=False
        ),
        logging.FileHandler(Path.home() / ".wrd" / "wrd.log"),
    ],
)
logger = logging.getLogger("wrd")
console = Console()

# Type variable for generic function return type
T = TypeVar('T')


# Global configuration cache
_config = None


class WRDConfig:
    """WRD Configuration Manager"""

    def __init__(self):
        self.home_dir = Path.home()
        self.wrd_dir = self.home_dir / ".wrd"
        self.config_file = self.wrd_dir / "config.yaml"
        self.projects_dir = Path(
            os.getenv("WRD_PROJECTS_DIR", self.home_dir / "projects")
        )
        self.templates_dir = self.wrd_dir / "templates"
        self.user_templates_dir = self.wrd_dir / "user_templates"
        self.cache_dir = self.wrd_dir / "cache"

        # Ensure all required directories exist
        self.ensure_directories()
        self.config = self.load_config()

    def ensure_directories(self) -> None:
        """Ensure all required directories exist."""
        for directory in [
            self.wrd_dir,
            self.projects_dir,
            self.templates_dir,
            self.user_templates_dir,
            self.cache_dir,
        ]:
            directory.mkdir(parents=True, exist_ok=True)

    def load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return yaml.safe_load(f) or {}
            except Exception as e:
                logger.error(f"Error loading config file: {e}")
                return {}
        return {}

    def save_config(self) -> None:
        """Save configuration to YAML file."""
        try:
            with open(self.config_file, 'w') as f:
                yaml.dump(self.config, f, default_flow_style=False)
        except Exception as e:
            logger.error(f"Error saving config file: {e}")

    def get_default_config(self) -> Dict[str, Any]:
        """Return default configuration."""
        return {
            'projects_dir': str(self.projects_dir),
            'templates_dir': str(self.templates_dir),
            'user_templates_dir': str(self.user_templates_dir),
            'cache_dir': str(self.cache_dir),
            'recent_projects': [],
            'settings': {
                'auto_commit': True,
                'default_editor': os.getenv('EDITOR', 'nano'),
                'confirm_deletion': True,
            },
        }


class WRDProject:
    """Klasa reprezentująca projekt WRD"""

    def __init__(self, name: str, project_type: str = 'python'):
        self.name = name
        self.project_type = project_type
        self.config = WRDConfig()
        self.project_dir = self.config.projects_dir / name
        self.claude_md_file = self.project_dir / 'CLAUDE.md'

        if not self.project_dir.exists():
            self.project_dir.mkdir(parents=True, exist_ok=True)

    def create(self, description: str = "") -> None:
        """Tworzenie nowego projektu"""
        try:
            # Create project structure
            self.project_dir.mkdir(parents=True, exist_ok=True)

            # Create README.md
            self._create_readme(description)

            # Create CLAUDE.md for Claude Code
            self._create_claude_md(description)

            # Create requirements.txt
            self._create_requirements_txt()

            # Create .gitignore
            self._create_gitignore()

            logger.info(f"Created new project: {self.name}")

        except Exception as e:
            logger.error(f"Error creating project: {e}")
            raise

    def _create_readme(self, description: str) -> None:
        """Tworzenie README.md"""
        readme_content = f"""# {self.name}

{description}

## Project Structure

```
{self.project_dir.name}/
├── CLAUDE.md           # Claude Code instructions
├── README.md           # This file
├── requirements.txt    # Project dependencies
└── .gitignore         # Git ignore file
```

## Getting Started

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Start developing!
"""

        with open(self.project_dir / 'README.md', 'w') as f:
            f.write(readme_content)

    def _create_claude_md(self, description: str) -> None:
        """Tworzenie CLAUDE.md dla Claude Code"""
        claude_content = f"""# {self.name}

{description}

## Project Structure

- `src/` - Source code
- `tests/` - Test files
- `docs/` - Documentation
- `data/` - Data files
- `notebooks/` - Jupyter notebooks

## Development Workflow

1. Describe your task or question in this file
2. Use Claude Code to generate or modify code
3. Test your changes
4. Commit and push your work
"""
        with open(self.claude_md_file, 'w') as f:
            f.write(claude_content)

    def _create_requirements_txt(self) -> None:
        """Tworzenie requirements.txt"""
        requirements = [
            "# Core dependencies",
            "numpy>=1.21.0",
            "pandas>=1.3.0",
            "matplotlib>=3.4.0",
            "",
            "# Development dependencies",
            "pytest>=6.2.0",
            "black>=21.0",
            "isort>=5.0.0",
            "mypy>=0.900",
            "pylint>=2.0.0",
            "",
        ]

        with open(self.project_dir / 'requirements.txt', 'w') as f:
            f.write('\n'.join(requirements))

    def _create_gitignore(self) -> None:
        """Tworzenie .gitignore"""
        gitignore_content = """# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# C extensions
*.so

# Distribution / packaging
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

# PyInstaller
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.nox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
.hypothesis/
.pytest_cache/

# Translations
*.mo
*.pot

# Django stuff:
*.log
local_settings.py
db.sqlite3

# Flask stuff:
instance/
.webassets-cache

# Scrapy stuff:
.scrapy

# Sphinx documentation
docs/_build/

# PyBuilder
target/


# Jupyter Notebook
.ipynb_checkpoints

# pyenv
.python-version

# celery beat schedule file
celerybeat-schedule

# SageMath parsed files
*.sage.py

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# Spyder project settings
.spyderproject
.spyproject

# Rope project settings
.ropeproject

# mkdocs documentation
/site

# mypy
.mypy_cache/
.dmypy.json
dmypy.json

# Pyre type checker
.pyre/

# PyCharm
.idea/
*.iml

# VS Code
.vscode/
!.vscode/settings.json
!.vscode/tasks.json
!.vscode/launch.json
!.vscode/extensions.json

# macOS
.DS_Store

# Windows
Thumbs.db
desktop.ini

# Project specific
*.swp
*~
.project
.pydevproject
"""
        with open(self.project_dir / '.gitignore', 'w') as f:
            f.write(gitignore_content)

    def delete(self, force: bool = False) -> bool:
        """Usuwa projekt.

        Args:
            force: Jeśli True, nie pyta o potwierdzenie

        Returns:
            bool: True jeśli projekt został usunięty, w przeciwnym razie False
        """
        if not self.project_dir.exists():
            logger.error(f"Project directory {self.project_dir} does not exist")
            return False

        if not force:
            confirm = typer.confirm(
                f"Czy na pewno chcesz usunąć projekt '{self.name}'?"
            )
            if not confirm:
                return False

        try:
            import shutil

            shutil.rmtree(self.project_dir)
            logger.info(f"Project '{self.name}' has been deleted")
            return True
        except Exception as e:
            logger.error(f"Error deleting project: {e}")
            return False

    def open_in_editor(self) -> None:
        """Otwiera projekt w domyślnym edytorze."""
        editor = os.getenv('EDITOR', 'code' if sys.platform == 'win32' else 'xdg-open')
        try:
            subprocess.run([editor, str(self.project_dir)], check=True)
        except Exception as e:
            logger.error(f"Error opening editor: {e}")

    def run_command(self, command: str) -> None:
        """Uruchamia polecenie w katalogu projektu.

        Args:
            command: Polecenie do wykonania
        """
        try:
            subprocess.run(command, shell=True, cwd=self.project_dir, check=True)
        except subprocess.CalledProcessError as e:
            logger.error(f"Command failed with exit code {e.returncode}")
        except Exception as e:
            logger.error(f"Error running command: {e}")

    def get_status(self) -> str:
        """Zwraca status projektu."""
        if not self.project_dir.exists():
            return "not_found"
        return "active"

    def to_dict(self) -> Dict[str, Any]:
        """Konwertuje projekt na słownik."""
        return {
            'name': self.name,
            'type': self.project_type,
            'path': str(self.project_dir),
            'status': self.get_status(),
            'created_at': (
                datetime.fromtimestamp(self.project_dir.stat().st_ctime).isoformat()
                if self.project_dir.exists()
                else None
            ),
            'modified_at': (
                datetime.fromtimestamp(self.project_dir.stat().st_mtime).isoformat()
                if self.project_dir.exists()
                else None
            ),
        }


def run_command(
    cmd: Union[str, List[str]],
    cwd: Optional[Union[str, Path]] = None,
    capture_output: bool = False,
    **kwargs: Any,
) -> subprocess.CompletedProcess:
    """Uruchamia polecenie w podprocesie.

    Args:
        cmd: Polecenie do wykonania (jako string lub lista argumentów)
        cwd: Katalog roboczy
        capture_output: Czy przechwytywać wyjście polecenia
        **kwargs: Dodatkowe argumenty dla subprocess.run()

    Returns:
        subprocess.CompletedProcess: Wynik wykonania polecenia
    """
    if isinstance(cmd, str):
        shell = True
    else:
        shell = False
        cmd = [str(c) for c in cmd]

    try:
        return subprocess.run(
            cmd,
            cwd=cwd,
            shell=shell,
            check=False,
            capture_output=capture_output,
            text=True,
            **kwargs,
        )
    except Exception as e:
        logger.error(f"Error running command '{cmd}': {e}")
        raise


# Initialize Typer app
app = typer.Typer(
    name="wrd",
    help="WRD (Word) - A powerful workflow automation tool for developers",
    add_completion=False,
)


# Global configuration and state
_config: WRDConfig | None = None
_projects: Dict[str, WRDProject] = {}


def get_config() -> 'WRDConfig':
    """Get or create the global configuration."""
    global _config
    if _config is None:
        _config = WRDConfig()
    return _config


def get_projects() -> Dict[str, WRDProject]:
    """Get or load all projects."""
    global _projects
    if not _projects:
        config = get_config()
        for project_dir in config.projects_dir.glob("*"):
            if project_dir.is_dir():
                _projects[project_dir.name] = WRDProject(project_dir.name)
    return _projects


@app.command()
def init() -> None:
    """Initialize WRD configuration."""
    config = get_config()
    console.print(f"WRD initialized at {config.wrd_dir}")
    console.print(f"Projects directory: {config.projects_dir}")


@app.command()
@typer.argument("name")
@typer.option("--description", "-d", help="Project description")
@typer.option("--type", "project_type", default="python", help="Project type")
def new(name: str, description: str = "", project_type: str = "python") -> None:
    """Create a new project."""
    project = WRDProject(name, project_type)
    project.create(description)
    console.print(f"[green]Created project: {name}[/green]")
    console.print(f"Project directory: {project.project_dir}")


@app.command()
@typer.argument("name")
@typer.option("--force", "-f", is_flag=True, help="Force deletion without confirmation")
def delete(name: str, force: bool = False) -> None:
    """Delete a project."""
    projects = get_projects()
    if name not in projects:
        console.print(f"[red]Error: Project '{name}' not found[/red]")
        raise typer.Exit(1)

    project = projects[name]
    if not force and not typer.confirm(
        f"Are you sure you want to delete project '{name}'?", default=False
    ):
        console.print("Project deletion cancelled")
        raise typer.Exit(0)

    if project.delete(force=force):
        console.print(f"[green]Deleted project: {name}[/green]")
    else:
        console.print(f"[red]Failed to delete project: {name}[/red]")
        raise typer.Exit(1)


@app.command()
def list() -> None:  # noqa: A001
    """List all projects."""
    projects = get_projects()
    if not projects:
        console.print("No projects found")
        return

    table = Table(title="Projects")
    table.add_column("Name", style="cyan")
    table.add_column("Type", style="magenta")
    table.add_column("Path", style="green")
    table.add_column("Created", style="yellow")
    table.add_column("Modified", style="yellow")

    for project in projects.values():
        created = datetime.fromtimestamp(project.project_dir.stat().st_ctime)
        modified = datetime.fromtimestamp(project.project_dir.stat().st_mtime)
        table.add_row(
            project.name,
            project.project_type,
            str(project.project_dir),
            created.strftime("%Y-%m-%d %H:%M"),
            modified.strftime("%Y-%m-%d %H:%M"),
        )

    console.print(table)


@app.command()
@typer.argument("name")
@typer.option("--editor", "-e", help="Editor to use")
def edit(name: str, editor: Optional[str] = None) -> None:
    """Open a project in the default editor."""
    projects = get_projects()
    if name not in projects:
        console.print(f"[red]Error: Project '{name}' not found[/red]")
        raise typer.Exit(1)

    project = projects[name]
    if not project.project_dir.exists():
        console.print(
            f"[red]Error: Project directory not found: " f"{project.project_dir}[/red]"
        )
        raise typer.Exit(1)

    editor_cmd = editor or os.getenv("EDITOR")
    if not editor_cmd:
        console.print(
            "[red]Error: No editor specified and $EDITOR "
            "environment variable not set[/red]"
        )
        raise typer.Exit(1)

    try:
        project.open_in_editor(editor_cmd)
    except Exception as e:
        console.print(f"[red]Error opening editor: {e}[/red]")
        raise typer.Exit(1) from e


@app.command()
@typer.argument("command", nargs=-1)
def run(command: List[str]) -> None:
    """Run a command in the project directory."""
    if not command:
        console.print("[red]Error: No command specified[/red]")
        raise typer.Exit(1)

    project_name = Path.cwd().name
    projects = get_projects()
    if project_name not in projects:
        console.print(
            f"[red]Error: Not in a valid project directory: " f"{Path.cwd()}[/red]"
        )
        raise typer.Exit(1)

    project = projects[project_name]
    try:
        project.run_command(" ".join(command))
    except Exception as e:
        console.print(f"[red]Error running command: {e}[/red]")
        raise typer.Exit(1) from e


@app.command()
def config() -> None:
    """Configure WRD settings."""
    config = get_config()
    editor = os.getenv("EDITOR", "nano")
    os.system(f"{editor} {config.config_file}")


@app.command()
def version() -> None:
    """Display the current WRD version.

    This command prints the version of the WRD package to the console.
    """
    console.print(f"WRD version: [bold cyan]{__version__}[/]")


if __name__ == "__main__":
    app()
