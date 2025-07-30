#!/bin/bash

# Fedora Claude Code Environment Setup
# Skrypt do konfiguracji środowiska Claude Code na Fedorze

set -e

echo "🔧 Konfiguracja środowiska Claude Code na Fedora..."

# Aktualizacja systemu
echo "📦 Aktualizacja systemu..."
sudo dnf update -y

# Instalacja podstawowych narzędzi
echo "🛠️ Instalacja podstawowych narzędzi..."
sudo dnf install -y \
    git \
    curl \
    wget \
    vim \
    nano \
    tmux \
    screen \
    htop \
    tree \
    jq \
    unzip \
    make \
    gcc \
    g++ \
    python3 \
    python3-pip \
    python3-venv \
    nodejs \
    npm \
    openssh-clients \
    openssh-server

# Instalacja Docker (dla konteneryzacji projektów)
echo "🐳 Instalacja Docker..."
sudo dnf install -y docker docker-compose
sudo systemctl enable docker
sudo systemctl start docker
sudo usermod -aG docker $USER

# Instalacja narzędzi deweloperskich
echo "🔨 Instalacja narzędzi deweloperskich..."
sudo dnf install -y \
    code \
    rust \
    cargo \
    golang \
    java-latest-openjdk \
    java-latest-openjdk-devel

# Instalacja Node.js tools
echo "📦 Instalacja Node.js tools..."
npm install -g \
    typescript \
    ts-node \
    nodemon \
    pm2 \
    http-server

# Konfiguracja SSH dla zdalnej pracy
echo "🔐 Konfiguracja SSH..."
sudo systemctl enable sshd
sudo systemctl start sshd

# Tworzenie struktury katalogów dla projektów
echo "📁 Tworzenie struktury katalogów..."
mkdir -p ~/claude-projects/{templates,scripts,docs,archive}
mkdir -p ~/claude-projects/templates/{python,javascript,rust,go,docs}

# Konfiguracja środowiska Python
echo "🐍 Konfiguracja środowiska Python..."
python3 -m venv ~/claude-projects/venv
source ~/claude-projects/venv/bin/activate
pip install --upgrade pip setuptools wheel

# Instalacja przydatnych pakietów Python
pip install \
    requests \
    pandas \
    numpy \
    matplotlib \
    seaborn \
    jupyter \
    black \
    flake8 \
    pytest \
    click \
    rich \
    typer \
    pydantic \
    fastapi \
    uvicorn

# Tworzenie pliku konfiguracyjnego
echo "⚙️ Tworzenie konfiguracji..."
cat > ~/claude-projects/.claude-config << 'EOF'
# Claude Code Configuration
export CLAUDE_WORKSPACE=~/claude-projects
export CLAUDE_TEMPLATES=$CLAUDE_WORKSPACE/templates
export CLAUDE_SCRIPTS=$CLAUDE_WORKSPACE/scripts
export CLAUDE_DOCS=$CLAUDE_WORKSPACE/docs
export CLAUDE_VENV=$CLAUDE_WORKSPACE/venv

# Aliasy dla szybkiej pracy
alias cc-activate='source $CLAUDE_VENV/bin/activate'
alias cc-workspace='cd $CLAUDE_WORKSPACE'
alias cc-new='cd $CLAUDE_WORKSPACE && mkdir'
alias cc-list='ls -la $CLAUDE_WORKSPACE'
alias cc-docs='cd $CLAUDE_DOCS'
alias cc-templates='cd $CLAUDE_TEMPLATES'

# Funkcje pomocnicze
cc-project() {
    mkdir -p "$CLAUDE_WORKSPACE/$1"
    cd "$CLAUDE_WORKSPACE/$1"
    echo "# $1 Project" > README.md
    echo "# Claude Code Configuration for $1" > CLAUDE.md
    echo "Utworzono projekt: $1"
}

cc-commit() {
    git add .
    git commit -m "$(date '+%Y-%m-%d %H:%M'): $1"
}

cc-backup() {
    local backup_name="backup-$(date +%Y%m%d-%H%M%S)"
    tar -czf "$CLAUDE_WORKSPACE/archive/$backup_name.tar.gz" -C "$CLAUDE_WORKSPACE" . --exclude=archive
    echo "Backup utworzony: $backup_name.tar.gz"
}
EOF

# Dodanie konfiguracji do .bashrc
echo "📝 Dodanie konfiguracji do .bashrc..."
echo "" >> ~/.bashrc
echo "# Claude Code Environment" >> ~/.bashrc
echo "source ~/claude-projects/.claude-config" >> ~/.bashrc

# Tworzenie szablonu CLAUDE.md
cat > ~/claude-projects/templates/CLAUDE.md << 'EOF'
# Claude Code Project Configuration

## Project Overview
- **Name**: [PROJECT_NAME]
- **Description**: [PROJECT_DESCRIPTION]
- **Type**: [python/javascript/rust/go/other]
- **Created**: [DATE]

## Development Environment
- **OS**: Fedora Linux
- **Python Version**: [VERSION]
- **Dependencies**: See requirements.txt
- **Virtual Environment**: ~/claude-projects/venv

## Project Structure
```
project_name/
├── src/
├── tests/
├── docs/
├── scripts/
├── README.md
├── CLAUDE.md
└── requirements.txt
```

## Development Workflow
1. Activate environment: `cc-activate`
2. Navigate to project: `cc-workspace && cd project_name`
3. Make changes
4. Document progress in this file
5. Commit: `cc-commit "description"`

## Claude Code Commands
- Initial setup: `claude-code init`
- Run development: `claude-code dev`
- Build project: `claude-code build`
- Run tests: `claude-code test`

## Notes and Progress
- [DATE]: Initial setup
- [DATE]: [PROGRESS_NOTE]

## Issues and Solutions
- **Issue**: [DESCRIPTION]
- **Solution**: [SOLUTION]
- **Date**: [DATE]

## Performance Optimizations
- [OPTIMIZATION_NOTE]

## Deployment Notes
- [DEPLOYMENT_INFO]
EOF

# Tworzenie skryptu startowego
cat > ~/claude-projects/scripts/start-session.sh << 'EOF'
#!/bin/bash
# Claude Code Session Starter

echo "🚀 Uruchamianie sesji Claude Code..."

# Aktywacja środowiska
source ~/claude-projects/venv/bin/activate

# Sprawdzenie statusu
echo "📊 Status środowiska:"
echo "- Python: $(python --version)"
echo "- Pip: $(pip --version)"
echo "- Workspace: $CLAUDE_WORKSPACE"
echo "- Aktywne projekty:"
ls -1 ~/claude-projects/ | grep -v -E "(venv|templates|scripts|docs|archive|\.claude-config)" | head -5

# Uruchomienie tmux dla multitaskingu
if command -v tmux &> /dev/null; then
    tmux new-session -d -s claude-code
    echo "🖥️ Sesja tmux 'claude-code' utworzona"
    echo "Użyj: tmux attach -t claude-code"
fi

echo "✅ Środowisko gotowe!"
echo "Użyj: cc-activate && cc-workspace"
EOF

chmod +x ~/claude-projects/scripts/start-session.sh

# Instalacja Claude Code (symulacja - rzeczywista instalacja wymaga dostępu do Anthropic)
echo "📋 Instrukcje instalacji Claude Code:"
echo "1. Zaloguj się na https://claude.ai"
echo "2. Przejdź do ustawień API"
echo "3. Wygeneruj klucz API"
echo "4. Zainstaluj Claude Code zgodnie z oficjalną dokumentacją"

# Finalizacja
echo "🎉 Konfiguracja zakończona!"
echo ""
echo "Następne kroki:"
echo "1. Zaloguj się ponownie lub wykonaj: source ~/.bashrc"
echo "2. Uruchom: ~/claude-projects/scripts/start-session.sh"
echo "3. Użyj: cc-project nazwa_projektu"
echo "4. Zainstaluj oficjalne Claude Code"
echo ""
echo "Przydatne komendy:"
echo "- cc-workspace    : przejdź do workspace"
echo "- cc-activate     : aktywuj Python venv"
echo "- cc-project NAME : utwórz nowy projekt"
echo "- cc-commit MSG   : szybki commit"
echo "- cc-backup       : backup projektów"