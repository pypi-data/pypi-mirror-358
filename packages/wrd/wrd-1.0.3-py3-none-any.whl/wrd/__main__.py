#!/usr/bin/env python3
"""
WRD (Word) - Python Package
Narzędzie inspirowane workflow opisanym przez użytkownika Claude Code

Funkcjonalności:
- Zarządzanie projektami Claude Code
- Automatyzacja dokumentacji
- Integracja z różnymi AI tools
- Workflow optimization
"""

import os
import sys
import json
import argparse
import subprocess
import datetime
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

# Konfiguracja logowania
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('wrd.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class WRDConfig:
    """Konfiguracja WRD"""

    def __init__(self):
        self.home_dir = Path.home()
        self.wrd_dir = self.home_dir / '.wrd'
        self.config_file = self.wrd_dir / 'config.json'
        self.projects_dir = self.home_dir / 'claude-projects'
        self.templates_dir = self.projects_dir / 'templates'

        self.ensure_directories()
        self.load_config()

    def ensure_directories(self):
        """Tworzenie niezbędnych katalogów"""
        dirs = [
            self.wrd_dir,
            self.projects_dir,
            self.templates_dir,
            self.projects_dir / 'scripts',
            self.projects_dir / 'docs',
            self.projects_dir / 'archive'
        ]

        for dir_path in dirs:
            dir_path.mkdir(parents=True, exist_ok=True)

    def load_config(self):
        """Wczytanie konfiguracji"""
        default_config = {
            'ai_tools': {
                'claude_code': {'enabled': True, 'priority': 1},
                'gemini_cli': {'enabled': False, 'priority': 2},
                'cursor': {'enabled': False, 'priority': 3}
            },
            'workflows': {
                'documentation_auto': True,
                'commit_auto_describe': True,
                'project_templates': True
            },
            'limits': {
                'session_duration': 5,  # hours
                'max_concurrent_projects': 3
            }
        }

        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = default_config
            self.save_config()

    def save_config(self):
        """Zapisanie konfiguracji"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)


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

# WRD
.wrd/
wrd.log
"""

        with open(self.project_dir / '.gitignore', 'w') as f:
            f.write(gitignore_content)

    def update_progress(self, message: str, task_type: str = "progress"):
        """Aktualizacja postępu w CLAUDE.md"""
        if not self.claude_md_file.exists():
            return

        # Wczytanie zawartości
        with open(self.claude_md_file, 'r') as f:
            content = f.read()

        # Dodanie wpisu
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
        progress_entry = f"### {timestamp}\n- {task_type.upper()}: {message}\n\n"

        # Wstawianie po sekcji "Postęp prac"
        progress_marker = "## Postęp prac\n"
        if progress_marker in content:
            parts = content.split(progress_marker, 1)
            content = parts[0] + progress_marker + progress_entry + parts[1]

        # Zapisanie
        with open(self.claude_md_file, 'w') as f:
            f.write(content)

        logger.info(f"Zaktualizowano postęp: {message}")


class WRDManager:
    """Główny manager WRD"""

    def __init__(self):
        self.config = WRDConfig()

    def list_projects(self) -> List[str]:
        """Lista projektów"""
        projects = []
        if self.config.projects_dir.exists():
            for item in self.config.projects_dir.iterdir():
                if item.is_dir() and not item.name.startswith('.'):
                    exclude_dirs = {'templates', 'scripts', 'docs', 'archive', 'venv'}
                    if item.name not in exclude_dirs:
                        projects.append(item.name)
        return sorted(projects)

    def create_project(self, name: str, project_type: str = 'python', description: str = ""):
        """Tworzenie nowego projektu"""
        project = WRDProject(name, project_type)
        return project.create(description)

    def auto_commit(self, project_name: str, message: str = ""):
        """Automatyczny commit z opisem"""
        project_dir = self.config.projects_dir / project_name
        if not project_dir.exists():
            logger.error(f"Projekt {project_name} nie istnieje")
            return False

        # Auto-generated commit message if not provided
        if not message:
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
            message = f"WRD auto-commit: {timestamp}"

        try:
            # Git add
            subprocess.run(['git', 'add', '.'], cwd=project_dir, check=True)

            # Git commit
            subprocess.run(['git', 'commit', '-m', message], cwd=project_dir, check=True)

            # Update progress
            project = WRDProject(project_name)
            project.update_progress(f"Commit: {message}", "git")

            logger.info(f"Commit wykonany: {message}")
            return True

        except subprocess.CalledProcessError as e:
            logger.error(f"Błąd podczas commit: {e}")
            return False

    def backup_projects(self):
        """Backup wszystkich projektów"""
        backup_name = f"wrd-backup-{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}"
        archive_dir = self.config.projects_dir / 'archive'
        backup_path = archive_dir / f"{backup_name}.tar.gz"

        try:
            subprocess.run([
                'tar', '-czf', str(backup_path),
                '-C', str(self.config.projects_dir),
                '--exclude=archive',
                '--exclude=venv',
                '.'
            ], check=True)

            logger.info(f"Backup utworzony: {backup_path}")
            return True

        except subprocess.CalledProcessError as e:
            logger.error(f"Błąd podczas tworzenia backup: {e}")
            return False

    def status(self):
        """Status WRD"""
        projects = self.list_projects()

        print(f"🔧 WRD (Word) Status")
        print(f"📁 Workspace: {self.config.projects_dir}")
        print(f"📊 Aktywne projekty: {len(projects)}")

        if projects:
            print("\n🚀 Projekty:")
            for project in projects[:10]:  # Limit to 10
                project_dir = self.config.projects_dir / project
                if (project_dir / '.git').exists():
                    status = "🔄 Git repo"
                else:
                    status = "📁 Folder"
                print(f"  - {project} {status}")

        print(f"\n⚙️ Konfiguracja:")
        print(f"  - Claude Code: {'✅' if self.config.config['ai_tools']['claude_code']['enabled'] else '❌'}")
        print(f"  - Auto dokumentacja: {'✅' if self.config.config['workflows']['documentation_auto'] else '❌'}")
        print(f"  - Auto commit opisy: {'✅' if self.config.config['workflows']['commit_auto_describe'] else '❌'}")


def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(description='WRD (Word) - Narzędzie workflow dla Claude Code')
    subparsers = parser.add_subparsers(dest='command', help='Dostępne komendy')

    # Status
    subparsers.add_parser('status', help='Pokaż status WRD')

    # List projects
    subparsers.add_parser('list', help='Lista projektów')

    # Create project
    create_parser = subparsers.add_parser('create', help='Utwórz nowy projekt')
    create_parser.add_argument('name', help='Nazwa projektu')
    create_parser.add_argument('--type', default='python',
                               choices=['python', 'javascript', 'rust', 'go', 'fastapi', 'data'], help='Typ projektu')
    create_parser.add_argument('--description', default='', help='Opis projektu')

    # Commit
    commit_parser = subparsers.add_parser('commit', help='Auto commit projektu')
    commit_parser.add_argument('project', help='Nazwa projektu')
    commit_parser.add_argument('--message', help='Wiadomość commit')

    # Backup
    subparsers.add_parser('backup', help='Backup wszystkich projektów')

    # Progress update
    progress_parser = subparsers.add_parser('progress', help='Aktualizuj postęp projektu')
    progress_parser.add_argument('project', help='Nazwa projektu')
    progress_parser.add_argument('message', help='Wiadomość o postępie')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    manager = WRDManager()

    if args.command == 'status':
        manager.status()

    elif args.command == 'list':
        projects = manager.list_projects()
        print("📁 Projekty WRD:")
        for project in projects:
            print(f"  - {project}")
        if not projects:
            print("  (brak projektów)")

    elif args.command == 'create':
        success = manager.create_project(args.name, args.type, args.description)
        if success:
            print(f"✅ Projekt '{args.name}' został utworzony")
        else:
            print(f"❌ Nie udało się utworzyć projektu '{args.name}'")

    elif args.command == 'commit':
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
        project = WRDProject(args.project)
        project.update_progress(args.message)
        print(f"✅ Postęp zaktualizowany dla projektu '{args.project}'")


if __name__ == '__main__':
    main()