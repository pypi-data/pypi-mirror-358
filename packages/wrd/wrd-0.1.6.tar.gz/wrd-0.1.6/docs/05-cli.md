# Interfejs wiersza poleceń (CLI)

W tym rozdziale poznasz narzędzia wiersza poleceń dostępne w środowisku WRD.

## Dostępne narzędzia

### Claude CLI

Główne narzędzie do interakcji z modelami Claude.

#### Uruchamianie interaktywnego trybu konwersacji:

```bash
claude
```

#### Przykłady użycia:

1. **Proste zapytanie**
   ```bash
   claude "Jaka jest stolica Francji?"
   ```

2. **Użycie konkretnego modelu**
   ```bash
   claude --model claude-3-opus-20240229 "Opowiedz mi o sztucznej inteligencji"
   ```

3. **Przetwarzanie pliku**
   ```bash
   claude --file dokument.txt "Podsumuj ten dokument"
   ```

#### Opcje:

```
  --help           Wyświetla pomoc
  --version        Wyświetla wersję
  --model <nazwa>  Określa model do użycia (domyślnie: claude-3-opus-20240229)
  --temp <wartość> Ustawia temperaturę (0-1, domyślnie: 0.7)
  --max-tokens <n> Maksymalna liczba tokenów w odpowiedzi
  --file <ścieżka> Przesyła zawartość pliku jako kontekst
```

### Narzędzia pomocnicze

#### Sprawdzanie wersji

```bash
node -v
npm -v
```

#### Zarządzanie zależnościami

```bash
# Instalacja pakietu
npm install <nazwa-pakietu>

# Aktualizacja pakietów
npm update

# Lista zainstalowanych pakietów
npm list
```

## Przykładowe przepływy pracy

### 1. Rozpoczęcie nowego projektu

```bash
# Utwórz nowy katalog projektu
mkdir moj-projekt
cd moj-projekt

# Inicjalizuj nowy projekt Node.js
npm init -y

# Zainstaluj zależności
npm install @anthropic-ai/sdk

# Utwórz prosty skrypt
cat > index.js << 'EOL'
const { Anthropic } = require('@anthropic-ai/sdk');

const anthropic = new Anthropic({
  apiKey: process.env.ANTHROPIC_API_KEY
});

async function main() {
  const message = await anthropic.messages.create({
    model: "claude-3-opus-20240229",
    max_tokens: 1024,
    messages: [{ role: "user", content: "Witaj, Claude!" }]
  });
  
  console.log(message.content[0].text);
}

main().catch(console.error);
EOL

# Uruchom skrypt
node index.js
```

### 2. Przetwarzanie wielu plików

```bash
# Przetwórz wszystkie pliki .txt w katalogu
for file in *.txt; do
  echo "Przetwarzanie $file..."
  claude --file "$file" "Podsumuj ten dokument" > "${file%.*}_podsumowanie.txt"
done
```

## Rozwiązywanie problemów

### Błąd: "Command not found: claude"

1. Upewnij się, że kontener został poprawnie uruchomiony
2. Sprawdź, czy plik `/home/coder/.local/bin/claude` istnieje i ma uprawnienia do wykonania:
   ```bash
   ls -la /home/coder/.local/bin/claude
   chmod +x /home/coder/.local/bin/claude
   ```

### Błąd autoryzacji

1. Sprawdź, czy klucz API jest poprawnie ustawiony w zmiennej środowiskowej:
   ```bash
   echo $ANTHROPIC_API_KEY
   ```
2. Upewnij się, że klucz jest aktywny i ma odpowiednie uprawnienia

### Niska wydajność

1. Sprawdź obciążenie systemu:
   ```bash
   top
   ```
2. Ogranicz zużycie pamięci przez kontenery w pliku `docker-compose.claude-code.yml`

## Automatyzacja zadań

Możesz tworzyć skrypty powłoki, które wykorzystują narzędzia CLI do automatyzacji zadań. Przykładowy skrypt:

```bash
#!/bin/bash

# Skrypt do generowania podsumowania dokumentów

INPUT_DIR="./dokumenty"
OUTPUT_DIR="./podsumowania"

mkdir -p "$OUTPUT_DIR"

for file in "$INPUT_DIR"/*.txt; do
  if [ -f "$file" ]; then
    filename=$(basename -- "$file")
    echo "Przetwarzanie: $filename"
    claude --file "$file" "Stwórz szczegółowe podsumowanie tego dokumentu, uwzględniając kluczowe punkty i wnioski." > "$OUTPUT_DIR/podsumowanie_${filename%.*}.md"
  fi
done

echo "Zakończono przetwarzanie dokumentów."
```

## Następne kroki

- [Modele Claude](06-modele-claude.md)
- [Rozwój](07-rozwoj.md)
