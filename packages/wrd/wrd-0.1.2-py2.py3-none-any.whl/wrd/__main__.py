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

import json
import logging
import os
import signal
import subprocess
import sys
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, TypeVar, Union, Tuple

import typer
from rich.console import Console
from rich.logging import RichHandler
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.table import Table
from rich.prompt import Confirm, Prompt

from . import __version__
from .cli import WRDShell
from .template_manager import get_template_manager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[
        RichHandler(rich_tracebacks=True, markup=True, show_time=False, show_path=False),
        logging.FileHandler(Path.home() / ".wrd" / "wrd.log")
    ]
)
logger = logging.getLogger("wrd")
console = Console()

# Type variable for generic function return type
T = TypeVar("T")

# Initialize Typer app
app = typer.Typer(
    name="wrd",
    help="WRD (WRonai Development) - A powerful workflow tool for developers",
    add_completion=False,
    no_args_is_help=True,
    rich_markup_mode="rich"
)


class WRDConfig:
    """WRD Configuration Manager"""

    def __init__(self):
        self.home_dir = Path.home()
        self.wrd_dir = self.home_dir / ".wrd"
        self.config_file = self.wrd_dir / "config.yaml"
        self.projects_dir = Path(os.getenv("WRD_PROJECTS_DIR", self.home_dir / "projects"))
        self.templates_dir = self.wrd_dir / "templates"
        self.user_templates_dir = self.wrd_dir / "user_templates"
        self.cache_dir = self.wrd_dir / "cache"

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
        if not self.config_file.exists():
            return self.get_default_config()

        try:
            with open(self.config_file, "r") as f:
                config = yaml.safe_load(f) or {}
                return {**self.get_default_config(), **config}
        except Exception as e:
            logger.warning(f"Error loading config: {e}. Using default configuration.")
            return self.get_default_config()

    def save_config(self) -> None:
        """Save configuration to YAML file."""
        try:
            with open(self.config_file, "w") as f:
                yaml.dump(self.config, f, default_flow_style=False)
        except Exception as e:
            logger.error(f"Error saving config: {e}")

    def get_default_config(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            "editor": os.getenv("EDITOR", "code"),
            "default_language": "python",
            "default_template": "python",
            "templates": {},
            "recent_projects": [],
            "settings": {
                "auto_update": True,
                "check_updates": True,
                "notifications": True,
            },
        }


class WRDConfig:
    """WRD Configuration Manager"""

    def __init__(self):
        self.home_dir = Path.home()
        self.wrd_dir = self.home_dir / ".wrd"
        self.config_file = self.wrd_dir / "config.yaml"
        self.projects_dir = Path(os.getenv("WRD_PROJECTS_DIR", self.home_dir / "projects"))
        self.templates_dir = self.wrd_dir / "templates"
        self.user_templates_dir = self.wrd_dir / "user_templates"
        self.cache_dir = self.wrd_dir / "cache"
        
        # Ensure all required directories exist
        self.ensure_directories()
        self.config = self.load_config()
        
    def ensure_directories(self) -> None:
        """Ensure all required directories exist."""
        directories = [
            self.wrd_dir,
            self.projects_dir,
            self.templates_dir,
            self.user_templates_dir,
            self.cache_dir
        ]
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

    def load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        if not self.config_file.exists():
            return self.get_default_config()

        try:
            with open(self.config_file, 'r') as f:
                config = yaml.safe_load(f) or {}
                return {**self.get_default_config(), **config}
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            return self.get_default_config()

    def save_config(self) -> None:
        """Save configuration to YAML file."""
        try:
            with open(self.config_file, 'w') as f:
                yaml.dump(self.config, f, default_flow_style=False)
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")

    def get_default_config(self) -> Dict[str, Any]:
        """Return default configuration."""
        return {
            'version': '1.0.0',
            'projects_dir': str(self.projects_dir),
            'editor': os.getenv('EDITOR', 'code'),
            'default_language': 'python',
            'default_template': 'python',
            'templates': {},
            'ai_tools': {
                'claude_code': {
                    'enabled': True,
                    'api_key': os.getenv('CLAUDE_API_KEY', '')
                }
            },
            'workflows': {
                'documentation_auto': True,
                'commit_auto_describe': True
            },
            'recent_projects': [],
            'settings': {
                'auto_update': True,
                'check_updates': True,
                'notifications': True
            }
        }


class WRDProject:
    """Klasa reprezentująca projekt WRD"""

    def __init__(self, name: str, project_type: str = 'python'):
        self.name = name
        self.project_type = project_type
        self.config = WRDConfig()
        self.project_dir = self.config.projects_dir / name
        self.claude_md_file = self.project_dir / 'CLAUDE.md'

    def create(self, description: str = ""):
        """Tworzenie nowego projektu"""
        if self.project_dir.exists():
            logger.warning(f"Projekt {self.name} już istnieje")
            return False

        # Tworzenie struktury katalogów
        dirs = ['src', 'tests', 'docs', 'scripts', 'config']
        for dir_name in dirs:
            (self.project_dir / dir_name).mkdir(parents=True)

        # Tworzenie plików bazowych
        self._create_readme(description)
        self._create_claude_md(description)
        self._create_requirements_txt()
        self._create_gitignore()

        # Inicjalizacja git
        subprocess.run(['git', 'init'], cwd=self.project_dir, capture_output=True)

        logger.info(f"Projekt {self.name} został utworzony w {self.project_dir}")
        return True

    def _create_readme(self, description: str):
        """Tworzenie README.md"""
        readme_content = f"""# {self.name}

{description}

## Opis projektu
Projekt typu: {self.project_type}
Utworzony: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}

## Instalacja
```bash
cd {self.name}
python -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

## Użycie
```bash
python src/main.py
```

## Rozwój
Ten projekt został utworzony z użyciem WRD (Word) - narzędzia do zarządzania projektami Claude Code.

## Dokumentacja
Szczegółowa dokumentacja znajduje się w pliku CLAUDE.md
"""

        with open(self.project_dir / 'README.md', 'w') as f:
            f.write(readme_content)

    def _create_claude_md(self, description: str):
        """Tworzenie CLAUDE.md dla Claude Code"""
        claude_content = f"""# Claude Code Project: {self.name}

## Przegląd projektu
- **Nazwa**: {self.name}
- **Typ**: {self.project_type}
- **Opis**: {description}
- **Utworzony**: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}
- **Narzędzie**: WRD (Word) v1.0

## Środowisko deweloperskie
- **OS**: Fedora Linux
- **Python**: {sys.version.split()[0]}
- **Virtual Environment**: venv/
- **Narzędzia**: Claude Code, WRD

## Struktura projektu
```
{self.name}/
├── src/           # Kod źródłowy
├── tests/         # Testy
├── docs/          # Dokumentacja
├── scripts/       # Skrypty pomocnicze
├── config/        # Konfiguracja
├── venv/          # Środowisko wirtualne
├── README.md      # Podstawowa dokumentacja
├── CLAUDE.md      # Ten plik - dokumentacja dla Claude Code
├── requirements.txt # Zależności Python
└── .gitignore     # Git ignore
```

## Workflow z Claude Code
1. **Planowanie** (Gemini 2.5 Pro/Claude.ai)
   - Architektura rozwiązania
   - Specyfikacja funkcjonalności
   - Planowanie iteracji

2. **Implementacja** (Claude Code)
   - Kodowanie w 5-godzinnych sesjach
   - Automatyczne commity z opisami
   - Iteracyjny rozwój

3. **Dokumentacja** (Automatyczna)
   - WRD automatycznie dokumentuje proces
   - Śledzenie błędów i rozwiązań
   - Historia zmian

## Postęp prac
### {datetime.datetime.now().strftime('%Y-%m-%d')}
- ✅ Inicjalizacja projektu
- ✅ Struktura katalogów
- ⏳ Implementacja podstawowej funkcjonalności

## Błędy i rozwiązania
<!-- Automatycznie aktualizowane przez WRD -->

## Notatki techniczne
<!-- Miejsce na notatki specyficzne dla Claude Code -->

## Optymalizacje wydajności
<!-- Dokumentacja optymalizacji -->

## Deployment
<!-- Instrukcje wdrożenia -->

---
*Dokumentacja generowana przez WRD (Word) - narzędzie workflow dla Claude Code*
"""

        with open(self.claude_md_file, 'w') as f:
            f.write(claude_content)

    def _create_requirements_txt(self):
        """Tworzenie requirements.txt"""
        requirements = [
            "requests>=2.28.0",
            "click>=8.0.0",
            "rich>=12.0.0",
            "pydantic>=1.9.0",
            "python-dotenv>=0.19.0"
        ]

        if self.project_type == 'fastapi':
            requirements.extend([
                "fastapi>=0.95.0",
                "uvicorn>=0.20.0"
            ])
        elif self.project_type == 'data':
            requirements.extend([
                "pandas>=1.5.0",
                "numpy>=1.24.0",
                "matplotlib>=3.6.0"
            ])

        with open(self.project_dir / 'requirements.txt', 'w') as f:
            f.write('\n'.join(requirements))

    def _create_gitignore(self):
        """Tworzenie .gitignore"""
        gitignore_content = """# WRD Generated .gitignore

# Python
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
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Environment variables
.env
.env.local



class WRDManager:
    """Main class for managing WRD projects."""
    
    def __init__(self, config: 'WRDConfig'):
        self.config = config
        self.projects: Dict[str, WRDProject] = {}
        self.load_projects()
    
    def load_projects(self) -> None:
        """Load all projects from the projects directory."""
        self.projects = {}
        if not self.config.projects_dir.exists():
            return
            
        for project_dir in self.config.projects_dir.glob('*'):
            if project_dir.is_dir() and not project_dir.name.startswith('.'):
                try:
                    project = WRDProject(project_dir, self.config)
                    self.projects[project.name] = project
                except Exception as e:
                    logger.warning(f"Error loading project {project_dir.name}: {e}")
    
    def create_project(
        self, 
        name: str, 
        project_type: str = 'python', 
        description: str = '',
        template: Optional[str] = None,
        **kwargs
    ) -> 'WRDProject':
        """Create a new project.
        
        Args:
            name: Name of the project
            project_type: Type of project (e.g., 'python', 'web', 'data')
            description: Project description
            template: Optional template to use for project creation
            **kwargs: Additional project metadata
            
        Returns:
            WRDProject: The created project
            
        Raises:
            ValueError: If project already exists or creation fails
        """
        project_path = self.config.projects_dir / name
        
        if project_path.exists():
            raise ValueError(f"Project '{name}' already exists")
        
        try:
            # Create project directory structure
            project_path.mkdir(parents=True, exist_ok=True)
            
            # Initialize project with metadata
            project = WRDProject(project_path, self.config)
            project._metadata.update({
                'name': name,
                'type': project_type,
                'description': description,
                'created_at': datetime.now().isoformat(),
                'status': 'active',
                'ai_tools': [],
                'workflows': {},
                **kwargs
            })
            
            # Apply template if specified
            if template:
                self._apply_template(project, template)
            
            # Initialize Git repository
            self._init_git_repo(project_path)
            
            # Save metadata and add to projects
            project.save_metadata()
            self.projects[name] = project
            
            # Update recent projects
            self._update_recent_projects(name)
            
            return project
            
        except Exception as e:
            # Clean up on failure
            if project_path.exists():
                import shutil
                shutil.rmtree(project_path, ignore_errors=True)
            raise ValueError(f"Failed to create project: {e}")
    
    def _apply_template(self, project: 'WRDProject', template_name: str) -> None:
        """Apply a template to the project.
        
        Args:
            project: The project to apply the template to
            template_name: Name of the template to apply
            
        Raises:
            ValueError: If template is not found or application fails
        """
        try:
            template_manager = get_template_manager()
            context = {
                'project_name': project.name,
                'project_path': str(project.path),
                'project_type': project._metadata.get('type', 'python'),
                'description': project._metadata.get('description', ''),
                'author': os.getenv('USER', 'Your Name'),
                'email': '',
                'year': datetime.now().year,
                'version': '0.1.0',
            }
            
            success = template_manager.create_project(
                template_name=template_name,
                project_path=project.path,
                context=context,
                overwrite=False
            )
            
            if not success:
                raise ValueError(f"Failed to apply template: {template_name}")
                
        except Exception as e:
            logger.error(f"Error applying template: {e}")
            if os.getenv("WRD_DEBUG"):
                import traceback
                logger.debug(traceback.format_exc())
            raise
    
    def _init_git_repo(self, path: Path) -> None:
        """Initialize a Git repository for the project."""
        try:
            # Initialize repository
            run_command(['git', 'init'], cwd=path)
            
            # Configure basic Git settings
            run_command(['git', 'config', 'pull.rebase', 'false'], cwd=path)
            
            # Create basic .gitignore if it doesn't exist
            gitignore = path / '.gitignore'
            if not gitignore.exists():
                gitignore_content = (
                    "# Python\n"
                    "__pycache__/\n"
                    "*.py[cod]\n"
                    "*$py.class\n"
                    "*.so\n"
                    ".Python\n"
                    "build/\n"
                    "develop-eggs/\n"
                    "dist/\n"
                    "downloads/\n"
                    "eggs/\n"
                    ".eggs/\n"
                    "lib\n"
                    "lib64\n"
                    "parts/\n"
                    "sdist/\n"
                    "var/\n"
                    "wheels/\n"
                    "*.egg-info/\n"
                    ".env\n"
                    ".venv\n"
                    "venv/\n"
                    "ENV/\n"
                    ".mypy_cache/\n"
                    ".pytest_cache/\n"
                    ".coverage\n"
                    "htmlcov/\n"
                    ".DS_Store\n"
                    "Thumbs.db\n"
                )
                with open(gitignore, 'w') as f:
                    f.write(gitignore_content)
            
            # Make initial commit
            run_command(['git', 'add', '.'], cwd=path)
            run_command(
                ['git', 'commit', '-m', 'Initial commit'],
                cwd=path
            )
            
        except Exception as e:
            logger.warning(f"Git repository initialization failed: {e}")
    
    def _update_recent_projects(self, project_name: str) -> None:
        """Update the list of recently used projects."""
        recent = self.config.config.get('recent_projects', [])
        if project_name in recent:
            recent.remove(project_name)
        recent.insert(0, project_name)
        self.config.config['recent_projects'] = recent[:10]  # Keep only 10 most recent
        self.config.save_config()
    
    def list_projects(self, status: Optional[str] = None) -> List['WRDProject']:
        """List all projects with optional status filter."""
        if status:
            return [p for p in self.projects.values() if p.get_status() == status]
        return list(self.projects.values())
    
    def get_project(self, name: str) -> Optional['WRDProject']:
        """Get a project by name."""
        return self.projects.get(name)
    
    def delete_project(self, name: str, force: bool = False) -> bool:
        """Delete a project.
        
        Args:
            name: Name of the project to delete
            force: If True, don't ask for confirmation
            
        Returns:
            bool: True if project was deleted, False otherwise
        """
        if name not in self.projects:
            logger.error(f"Project '{name}' not found")
            return False
        
        project = self.projects[name]
        
        if not force:
            confirm = click.confirm(
                f"Are you sure you want to delete project '{name}'? This cannot be undone.",
                default=False
            )
            if not confirm:
                return False
        
        try:
            if project.path.exists():
                import shutil
                shutil.rmtree(project.path, ignore_errors=True)
            
            # Remove from projects list and recent projects
            del self.projects[name]
            self._remove_from_recent_projects(name)
            
            logger.info(f"Project '{name}' deleted successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete project '{name}': {e}")
            return False
    
    def _remove_from_recent_projects(self, project_name: str) -> None:
        """Remove a project from recent projects list."""
        if 'recent_projects' in self.config.config:
            recent = self.config.config['recent_projects']
            if project_name in recent:
                recent.remove(project_name)
                self.config.save_config()
    
    def auto_commit(self, message: Optional[str] = None) -> None:
        """Automatically commit changes in all projects."""
        for project in self.projects.values():
            if (project.path / '.git').exists():
                try:
                    # Check for changes
                    result = run_command(
                        ['git', 'status', '--porcelain'],
                        cwd=project.path,
                        capture_output=True
                    )
                    
                    if result.stdout.strip():
                        # There are changes to commit
                        if not message:
                            message = f"Auto-commit: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                        
                        run_command(['git', 'add', '.'], cwd=project.path)
                        run_command(
                            ['git', 'commit', '-m', message],
                            cwd=project.path
                        )
                        logger.info(f"Committed changes in {project.name}")
                        
                except Exception as e:
                    logger.error(f"Failed to auto-commit in {project.name}: {e}")
    
    def show_status(self) -> None:
        """Show status of all projects."""
        projects = self.list_projects()
        if not projects:
            console.print("[yellow]No projects found.[/]")
            return

        table = Table(title="WRD Projects")
        table.add_column("Name", style="cyan")
        table.add_column("Type")
        table.add_column("Status")
        table.add_column("Path")
        
        for project in sorted(projects, key=lambda p: p.name):
            project_dir = self.config.projects_dir / project.name
            
            # Get Git status if available
            git_status = ""
            if (project_dir / '.git').exists():
                try:
                    # Check if there are uncommitted changes
                    result = run_command(
                        ['git', 'status', '--porcelain'],
                        cwd=project_dir,
                        capture_output=True
                    )
                    if result.stdout.strip():
                        git_status = "[yellow]uncommitted[/]"
                    else:
                        git_status = "[green]clean[/]"
                except Exception:
                    git_status = "[red]error[/]"
            
            table.add_row(
                project.name,
                project._metadata.get('type', 'unknown'),
                git_status or "[dim]no git[/]",
                str(project.path)
            )
        
        console.print(table)


# Helper functions
def run_command(
    cmd: Union[str, List[str]], 
    cwd: Optional[Union[str, Path]] = None, 
    capture_output: bool = False,
    check: bool = True
) -> subprocess.CompletedProcess:
    """Run a shell command with proper error handling.
    
    Args:
        cmd: Command to run as string or list of arguments
        cwd: Working directory for the command
        capture_output: Whether to capture command output
        check: Whether to raise an exception on non-zero exit code
        
    Returns:
        CompletedProcess object with command results
    """
    try:
        if isinstance(cmd, str):
            # Use shell=True for string commands
            return subprocess.run(
                cmd,
                shell=True,
                cwd=str(cwd) if cwd else None,
                check=check,
                capture_output=capture_output,
                text=True,
                encoding='utf-8',
                errors='replace'
            )
        else:
            # Use shell=False for list of arguments (safer)
            return subprocess.run(
                [str(arg) for arg in cmd],
                shell=False,
                cwd=str(cwd) if cwd else None,
                check=check,
                capture_output=capture_output,
                text=True,
                encoding='utf-8',
                errors='replace'
            )
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed with exit code {e.returncode}: {e.cmd}")
        if e.stdout:
            logger.debug(f"Command output:\n{e.stdout}")
        if e.stderr:
            logger.error(f"Command error:\n{e.stderr}")
        raise
    except FileNotFoundError as e:
        logger.error(f"Command not found: {e.filename}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error running command: {e}")
        raise


def handle_keyboard_interrupt() -> None:
    """Handle keyboard interrupt gracefully."""
    console.print("\n[red]Operation cancelled by user.[/]")
    sys.exit(1)


# Register signal handler for graceful exit
signal.signal(signal.SIGINT, lambda *_: handle_keyboard_interrupt())


# CLI Commands
@app.command()
def shell():
    """Start interactive WRD shell."""
    try:
        WRDShell().shell()
    except Exception as e:
        logger.error(f"Error in shell: {e}")
        raise typer.Exit(1)


@app.command()
def init(
    name: str = typer.Argument(..., help="Project name"),
    path: Path = typer.Argument(
        None,
        exists=False,
        file_okay=False,
        dir_okay=True,
        writable=True,
        resolve_path=True,
        help="Project path (default: current directory/name)",
    ),
    template: str = typer.Option(
        None, "--template", "-t", help="Template to use for the project"
    ),
    description: str = typer.Option(
        "", "--description", "-d", help="Project description"
    ),
    interactive: bool = typer.Option(
        True, "--interactive/--no-interactive", "-i/-I", help="Interactive mode"
    ),
):
    """Initialize a new project."""
    try:
        config = get_config()
        template_manager = get_template_manager()
        
        # Set default path if not provided
        if path is None:
            path = Path.cwd() / name
        
        # List available templates if none specified
        available_templates = template_manager.list_templates()
        if not template and interactive:
            if not available_templates:
                console.print("[yellow]No templates found. Using default Python template.[/]")
                template = "python"
            else:
                table = Table(title="Available Templates")
                table.add_column("Name", style="cyan")
                table.add_column("Description")
                
                for tpl_name in available_templates:
                    tpl = template_manager.get_template(tpl_name)
                    desc = tpl['config'].get('description', 'No description')
                    table.add_row(tpl_name, desc)
                
                console.print(table)
                template = console.input("\n[bold]Choose a template[/] (default: python): ") or "python"
        
        # Get project details interactively
        if interactive:
            name = console.input(f"Project name [[cyan]{name}[/]]: ") or name
            path = Path(console.input(f"Project path [[cyan]{path}[/]]: ") or path)
            description = console.input(f"Description [[cyan]{description or 'No description'}[/]]: ") or description or ""
        
        # Create project context
        context = {
            "project_name": name,
            "package_name": name.lower().replace("-", "_").replace(" ", "_"),
            "description": description,
            "author_name": os.getenv("USER", "Your Name"),
            "author_email": "",
            "license": "MIT",
            "year": datetime.now().year,
        }
        
        # Create project
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            progress.add_task(description="Creating project...", total=None)
            success = template_manager.create_project(
                template_name=template,
                project_path=path,
                context=context,
                overwrite=False,
            )
        
        if success:
            console.print(f"\n[green]✓ Project created at {path}[/]")
            
            # Open in editor if configured
            editor = config.config.get("editor")
            if editor and interactive and typer.confirm("Open project in editor?"):
                run_command(f"{editor} {path}")
        else:
            console.print("[red]Failed to create project.[/]")
            raise typer.Exit(1)
            
    except Exception as e:
        logger.error(f"Error initializing project: {e}")
        raise typer.Exit(1)


@app.command()
def list_templates():
    """List all available project templates."""
    try:
        template_manager = get_template_manager()
        templates = template_manager.list_templates()
        
        if not templates:
            console.print("[yellow]No templates found.[/]")
            return
        
        table = Table(
            title="Available Templates",
            caption=f"Use 'wrd init --template <name>' to create a project with a template"
        )
        table.add_column("Name", style="cyan", no_wrap=True)
        table.add_column("Description")
        table.add_column("Type", no_wrap=True)
        
        # Sort templates by name
        for name in sorted(templates):
            template = template_manager.get_template(name)
            if not template:
                continue
                
            desc = template.get('config', {}).get('description', 'No description')
            
            # Determine template type
            template_path = str(template.get('path', ''))
            if "site-packages" in template_path:
                tpl_type = "Built-in"
            elif str(Path.home()) in template_path:
                tpl_type = "User"
            else:
                tpl_type = "System"
                
            table.add_row(name, desc, tpl_type)
        
        console.print(table)
        
    except Exception as e:
        logger.error(f"Error listing templates: {e}")
        if os.getenv("WRD_DEBUG"):
            import traceback
            logger.debug(traceback.format_exc())
        raise typer.Exit(1)


@app.command()
def config():
    """Configure WRD settings."""
    config = get_config()
    
    console.print("[bold]Current Configuration:[/]")
    console.print_json(json.dumps(config.config, indent=2, default=str))
    
    if typer.confirm("\nDo you want to edit the configuration?"):
        editor = os.getenv("EDITOR", "nano")
        os.system(f"{editor} {config.config_file}")


@app.command()
def version():
    """Show WRD version."""
    console.print(f"WRD version: [bold cyan]{__version__}[/]")

        success = manager.auto_commit(args.project, args.message or "")
        if success:
            print(f"✅ Commit wykonany dla projektu '{args.project}'")
        else:
            print(f"❌ Nie udało się wykonać commit dla projektu '{args.project}'")

    elif args.command == 'backup':
        success = manager.backup_projects()
        if success:
            print("✅ Backup projektów wykonany")
        else:
            print("❌ Nie udało się wykonać backup")

    elif args.command == 'progress':

if __name__ == "__main__":
    main()