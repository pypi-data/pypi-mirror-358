# Korzystanie z VS Code w przeglądarce

W tym rozdziale dowiesz się, jak efektywnie korzystać ze zintegrowanego środowiska VS Code dostępnego przez przeglądarkę.

## Pierwsze uruchomienie

1. Otwórz przeglądarkę i przejdź pod adres:
   ```
   http://localhost:8083
   ```

2. Zostaniesz poproszony o podanie hasła (jeśli jest skonfigurowane w pliku `.env`).

3. Po zalogowaniu zobaczysz standardowy interfejs VS Code działający w przeglądarce.

## Podstawowe funkcje

### Eksplorator plików

- Po lewej stronie znajduje się panel eksploratora plików
- Kliknij prawym przyciskiem myszy, aby wyświetlić menu kontekstowe z dostępnymi opcjami
- Użyj przycisku "Open Folder" aby otworzyć katalog roboczy

### Terminal zintegrowany

1. Otwórz terminal za pomocą skrótu `Ctrl+`` (tylda) lub wybierając z menu:
   ```
   View > Terminal
   ```

2. Domyślnie terminal uruchamia się w katalogu `/workspace`

3. Dostępne są następujące narzędzia w terminalu:
   - `claude` - interfejs wiersza poleceń Claude
   - `git` - system kontroli wersji
   - `node` i `npm` - środowisko Node.js

### Edycja kodu

- Wszystkie standardowe funkcje edytora VS Code są dostępne
- Obsługa podświetlania składni dla wielu języków programowania
- Autouzupełnianie kodu (IntelliSense)
- Podgląd plików Markdown
- Integracja z Git

## Praca z plikami

### Otwieranie plików

1. Użyj eksploratora plików po lewej stronie
2. Kliknij dwukrotnie plik, aby go otworzyć
3. Użyj skrótu `Ctrl+P` do szybkiego otwierania plików

### Zapisywanie zmian

- Automatyczne zapisywanie jest domyślnie włączone
- Aby zapisać ręcznie, użyj `Ctrl+S`

## Integracja z Claude

### Uruchamianie Claude CLI

1. Otwórz zintegrowany terminal (`Ctrl+``)
2. Wpisz polecenie:
   ```bash
   claude
   ```
3. Postępuj zgodnie z instrukcjami wyświetlanymi na ekranie

### Używanie rozszerzeń

1. Kliknij ikonę rozszerzeń na pasku bocznym (lub naciśnij `Ctrl+Shift+X`)
2. Wyszukaj i zainstaluj potrzebne rozszerzenia
3. Po zainstalowaniu niektóre rozszerzenia mogą wymagać ponownego załadowania interfejsu

## Skróty klawiszowe

| Skrót | Opis |
|--------|-------------|
| `Ctrl+P` | Szybkie otwieranie plików |
| `Ctrl+Shift+E` | Przełączanie widoku eksploratora plików |
| `Ctrl+`` | Przełączanie terminala |
| `Ctrl+Shift+`` | Nowy terminal |
| `Ctrl+,` | Otwórz ustawienia |
| `F5` | Rozpocznij debugowanie |

## Dostosowywanie środowiska

### Motywy kolorystyczne

1. Otwórz ustawienia (`Ctrl+,`)
2. Wyszukaj "Color Theme"
3. Wybierz preferowany motyw z listy

### Ustawienia użytkownika

1. Otwórz ustawienia (`Ctrl+,`)
2. Dostosuj ustawienia według własnych preferencji
3. Kliknij ikonę "Open Settings (JSON)" w prawym górnym rogu, aby edytować plik ustawień bezpośrednio

## Rozwiązywanie problemów

### Jeśli VS Code nie odpowiada

1. Spróbuj odświeżyć stronę w przeglądarce
2. Sprawdź stan kontenera:
   ```bash
   docker ps
   docker logs claude-vscode
   ```

### Jeśli nie widzisz zmian w plikach

1. Sprawdź, czy pliki zostały zapisane
2. Upewnij się, że pracujesz w odpowiednim katalogu
3. Sprawdź uprawnienia do plików

## Następne kroki

- [Interfejs wiersza poleceń](05-cli.md)
- [Modele Claude](06-modele-claude.md)
