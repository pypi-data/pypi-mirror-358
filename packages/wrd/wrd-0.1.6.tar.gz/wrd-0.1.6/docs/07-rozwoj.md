# Rozwój i współtworzenie

W tym rozdziale znajdziesz informacje dla programistów chcących współtworzyć projekt WRD.

## Środowisko deweloperskie

### Wymagania

- Docker 20.10+
- Docker Compose 2.0+
- Node.js 18+
- Python 3.8+
- Git

### Konfiguracja środowiska

1. Sklonuj repozytorium:
   ```bash
   git clone https://github.com/wronai/wrd.git
   cd wrd
   ```

2. Skonfiguruj plik `.env`:
   ```bash
   cp .env.example .env
   # Edytuj plik .env według potrzeb
   ```

3. Zbuduj i uruchom kontenery:
   ```bash
   docker-compose -f docker-compose.claude-code.yml up -d --build
   ```

## Struktura projektu

```
.
├── cli/                  # Skrypty CLI
│   └── claude-code.sh    # Główny skrypt CLI
├── docs/                 # Dokumentacja
├── scripts/             # Skrypty pomocnicze
│   └── cli-wrapper.sh   # Opakowanie CLI dla VS Code
├── src/                 # Kod źródłowy
├── .env.example         # Przykładowa konfiguracja
├── docker-compose.claude-code.yml  # Konfiguracja Docker Compose
└── README.md           # Dokumentacja główna
```

## Rozwój CLI

### Struktura kodu

- `cli/claude-code.sh` - Główny skrypt CLI
- `scripts/cli-wrapper.sh` - Opakowanie dla VS Code
- `src/` - Kod źródłowy aplikacji

### Testowanie zmian

1. Po wprowadzeniu zmian w skryptach:
   ```bash
   # Zbuduj ponownie kontener
   docker-compose -f docker-compose.claude-code.yml build
   
   # Uruchom ponownie kontenery
   docker-compose -f docker-compose.claude-code.yml up -d
   ```

2. Przetestuj zmiany:
   ```bash
   # W kontenerze VS Code
   claude --version
   claude "Testuję zmiany"
   ```

## Zasady współtworzenia

1. **Tworzenie gałęzi**
   - Dla nowych funkcji: `feature/nazwa-funkcjonalności`
   - Dla poprawek błędów: `fix/opis-bledu`
   - Dla dokumentacji: `docs/opis-zmian`

2. **Commity**
   - Pisz jasne i zwięzłe komunikaty commitów
   - Używaj czasu teraźniejszego (np. "Dodaj funkcję X" zamiast "Dodałem funkcję X")

3. **Pull Requesty**
   - Opisuj wprowadzane zmiany
   - Wskazuj powiązane issue
   - Dołącz screenshoty, jeśli to możliwe

## Testowanie

### Testy jednostkowe

```bash
# Uruchom testy w kontenerze
npm test
```

### Testy integracyjne

```bash
# Uruchom testy integracyjne
npm run test:integration
```

## Dokumentacja

### Aktualizacja dokumentacji

1. Edytuj odpowiednie pliki w katalogu `docs/`
2. Użyj języka Markdown do formatowania
3. Sprawdź poprawność linków

### Generowanie dokumentacji

```bash
# Uruchom lokalny serwer dokumentacji
npm run docs:serve
```

## Wersjonowanie

Projekt używa [Semantic Versioning](https://semver.org/):

- **MAJOR** - niezgodne zmiany w API
- **MINOR** - nowe funkcje z zachowaniem wstecznej zgodności
- **PATCH** - poprawki błędów i optymalizacje

## Wkład w projekt

1. Zgłoś błąd lub sugestię funkcji poprzez nowe Issue
2. Stwórz fork repozytorium
3. Utwórz nową gałąź dla swoich zmian
4. Zatwierdź zmiany i wyślij Pull Request

## Kod postępowania

Prosimy o zapoznanie się z naszym [Kodeksem Postępowania](CODE_OF_CONDUCT.md), który określa standardy zachowań w społeczności naszego projektu.

## Licencja

Ten projekt jest objęty licencją MIT - szczegóły znajdują się w pliku [LICENSE](LICENSE).

## Podziękowania

- Zespołowi Anthropic za stworzenie modeli Claude
- Społeczności open source za ich wkład i wsparcie

## Następne kroki

- [Rozwiązywanie problemów](08-rozwiazywanie-problemow.md)
