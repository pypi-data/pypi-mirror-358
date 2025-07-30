# Instalacja

W tym rozdziale dowiesz się, jak zainstalować i skonfigurować środowisko WRD na swoim komputerze.

## Wymagania wstępne

Przed rozpoczęciem instalacji upewnij się, że masz zainstalowane następujące narzędzia:

- [Docker](https://docs.docker.com/get-docker/) w wersji 20.10 lub nowszej
- [Docker Compose](https://docs.docker.com/compose/install/) w wersji 2.0 lub nowszej
- System operacyjny: Linux, macOS lub Windows 10/11 z WSL2
- Minimum 4GB wolnej pamięci RAM
- Minimum 2GB wolnego miejsca na dysku

## Krok 1: Pobieranie kodu źródłowego

1. Sklonuj repozytorium WRD:
   ```bash
   git clone https://github.com/wronai/wrd.git
   cd wrd
   ```

## Krok 2: Konfiguracja środowiska

1. Skopiuj plik z przykładową konfiguracją:
   ```bash
   cp .env.example .env
   ```

2. Edytuj plik `.env` i ustaw następujące parametry:
   ```bash
   # Klucz API z konta Anthropic
   ANTHROPIC_API_KEY=twój_klucz_api
   
   # Konfiguracja użytkownika (opcjonalnie)
   UID=$(id -u)
   GID=$(id -g)
   ```

## Krok 3: Uruchomienie środowiska

1. Uruchom kontenery za pomocą Docker Compose:
   ```bash
   docker-compose -f docker-compose.claude-code.yml up -d
   ```

2. Poczekaj na zakończenie procesu uruchamiania kontenerów.

## Krok 4: Weryfikacja instalacji

1. Sprawdź, czy kontenery działają poprawnie:
   ```bash
   docker ps
   ```
   Powinieneś zobaczyć dwa działające kontenery: `claude-vscode` i `claude-code`.

2. Otwórz przeglądarkę i przejdź pod adres:
   ```
   http://localhost:8083
   ```

## Rozwiązywanie problemów

### Brak dostępu do VS Code
- Sprawdź, czy port 8083 nie jest zajęty przez inną aplikację
- Upewnij się, że Docker działa poprawnie
- Sprawdź logi kontenera: `docker logs claude-vscode`

### Problemy z kontenerami
- Zatrzymaj wszystkie kontenery: `docker-compose -f docker-compose.claude-code.yml down`
- Usuń woluminy: `docker volume prune`
- Uruchom ponownie: `docker-compose -f docker-compose.claude-code.yml up -d --build`

## Aktualizacja do najnowszej wersji

Aby zaktualizować środowisko do najnowszej wersji:

```bash
git pull origin main
docker-compose -f docker-compose.claude-code.yml down
docker-compose -f docker-compose.claude-code.yml up -d --build
```

## Następne kroki

- [Konfiguracja środowiska](03-konfiguracja.md)
- [Pierwsze uruchomienie VS Code](04-uzycie-vscode.md)
