# Konfiguracja środowiska

W tym rozdziale znajdziesz informacje na temat konfigurowania środowiska WRD według własnych potrzeb.

## Plik konfiguracyjny .env

Głównym plikiem konfiguracyjnym jest plik `.env` w katalogu głównym projektu. Zawiera on wszystkie niezbędne ustawienia środowiskowe.

### Podstawowe parametry

```bash
# Klucz API do usługi Anthropic (wymagany)
ANTHROPIC_API_KEY=twoj_klucz_api

# ID i grupa użytkownika (domyślnie: 1000:1000)
UID=1000
GID=1000

# Strefa czasowa (np. Europe/Warsaw)
TZ=Europe/Warsaw

# Hasło do VS Code (opcjonalne)
VSCODE_PASSWORD=twoje_haslo

# Hasło sudo wewnątrz kontenera (do celów deweloperskich)
SUDO_PASSWORD=twoje_haslo
```

### Zaawansowane ustawienia

```bash
# Port dla VS Code (domyślnie: 8083)
VSCODE_PORT=8083

# Katalog roboczy wewnątrz kontenera
WORKSPACE_DIR=/workspace

# Ścieżka do konfiguracji VS Code
VSCODE_CONFIG_DIR=/home/coder/.config

# Ścieżka do rozszerzeń VS Code
VSCODE_EXTENSIONS_DIR=/home/coder/.local/share/code-server/extensions
```

## Konfiguracja VS Code

### Rozszerzenia

Domyślnie VS Code ładuje rozszerzenia z katalogu `~/.local/share/code-server/extensions` wewnątrz kontenera. Możesz zainstalować dodatkowe rozszerzenia bezpośrednio z poziomu VS Code.

### Ustawienia użytkownika

Ustawienia VS Code są przechowywane w katalogu `~/.local/share/code-server/User` wewnątrz kontenera. Aby zmodyfikować ustawienia:

1. Otwórz paletę poleceń (Ctrl+Shift+P)
2. Wpisz "Preferences: Open Settings (JSON)"
3. Dodaj lub zmodyfikuj ustawienia

## Zmienne środowiskowe

Możesz przekazać dodatkowe zmienne środowiskowe do kontenera modyfikując plik `docker-compose.claude-code.yml`:

```yaml
environment:
  - NODE_ENV=development
  - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
  # Dodatkowe zmienne środowiskowe
```

## Konfiguracja proxy

Jeśli korzystasz z serwera proxy, dodaj następujące ustawienia do pliku `.env`:

```bash
# Przykładowa konfiguracja proxy
HTTP_PROXY=http://proxy.example.com:8080
HTTPS_PROXY=http://proxy.example.com:8080
NO_PROXY=localhost,127.0.0.1,.example.com
```

## Konfiguracja sieci

Domyślnie kontenery używają domyślnej sieci Docker. Aby zmienić ustawienia sieci:

1. Zatrzymaj działające kontenery:
   ```bash
   docker-compose -f docker-compose.claude-code.yml down
   ```

2. Zdefiniuj własną sieć w pliku `docker-compose.claude-code.yml`:
   ```yaml
   networks:
     wrd-network:
       driver: bridge
   
   services:
     vscode:
       networks:
         - wrd-network
     claude-code:
       networks:
         - wrd-network
   ```

## Zasoby systemowe

Domyślnie kontenery używają nieograniczonych zasobów systemowych. Aby ustawić limity, zmodyfikuj plik `docker-compose.claude-code.yml`:

```yaml
services:
  vscode:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
```

## Następne kroki

- [Korzystanie z VS Code](04-uzycie-vscode.md)
- [Interfejs wiersza poleceń](05-cli.md)
