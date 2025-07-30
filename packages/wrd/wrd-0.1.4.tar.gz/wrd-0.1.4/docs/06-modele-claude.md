# Modele Claude

W tym rozdziale znajdziesz informacje o dostępnych modelach Claude i ich możliwościach.

## Dostępne modele

### Claude 3 Opus (najnowszy)
- **Identyfikator:** `claude-3-opus-20240229`
- **Opis:** Najpotężniejszy model z rodziny Claude 3, oferujący zaawansowane możliwości rozumienia i generowania tekstu.
- **Zalecane zastosowania:**
  - Złożone analizy
  - Zaawansowane zadania programistyczne
  - Tworzenie szczegółowych treści
  - Złożone rozumowanie

### Claude 3 Sonnet
- **Identyfikator:** `claude-3-sonnet-20240229`
- **Opis:** Idealny balans między wydajnością a szybkością.
- **Zalecane zastosowania:**
  - Generowanie kodu
  - Podsumowywanie dokumentów
  - Odpowiedzi na pytania
  - Analiza danych

### Claude 3 Haiku (najszybszy)
- **Identyfikator:** `claude-3-haiku-20240307`
- **Opis:** Najszybszy i najbardziej opłacalny model w swojej klasie.
- **Zalecane zastosowania:**
  - Szybkie odpowiedzi
  - Proste zapytania
  - Moderacja treści
  - Klasyfikacja

## Wybór odpowiedniego modelu

| Model | Prędkość | Koszt | Złożoność zadań |
|-------|----------|-------|-----------------|
| Opus  | ⚡⚡      | $$$   | Bardzo złożone  |
| Sonnet| ⚡⚡⚡     | $$    | Średnio złożone |
| Haiku | ⚡⚡⚡⚡    | $     | Proste          |


## Ograniczenia i limity

### Długość kontekstu
- Maksymalna długość kontekstu: 200 000 tokenów (~150 000 słów)
- Domyślna maksymalna długość odpowiedzi: 4 096 tokenów
- Możliwość zwiększenia maksymalnej długości odpowiedzi do 8 192 tokenów

### Ograniczenia szybkości (Rate Limits)
- Domyślny limit: 40 000 tokenów na minutę
- Maksymalna liczba równoległych żądań: 5

## Najlepsze praktyki

### Optymalizacja wydajności
1. Używaj krótszych kontekstów, gdy to możliwe
2. Ogranicz maksymalną długość odpowiedzi do potrzebnego minimum
3. Wykorzystuj buforowanie odpowiedzi dla powtarzających się zapytań

### Efektywne wykorzystanie tokenów
1. Usuwaj niepotrzebne białe znaki
2. Używaj skrótów tam, gdzie to możliwe
3. Rozważ użycie mniejszego modelu dla prostszych zadań

## Przykłady użycia

### 1. Użycie konkretnego modelu

```javascript
const response = await anthropic.messages.create({
  model: "claude-3-opus-20240229",
  max_tokens: 1000,
  messages: [{ role: "user", content: "Witaj, Claude!" }]
});
```

### 2. Kontrola temperatury

```javascript
// Niższa temperatura = bardziej deterministyczne odpowiedzi
const response = await anthropic.messages.create({
  model: "claude-3-sonnet-20240229",
  temperature: 0.3,  // zakres 0-1
  messages: [/* ... */]
});
```

### 3. Użycie systemowego promptu

```javascript
const response = await anthropic.messages.create({
  model: "claude-3-opus-20240229",
  system: "Odpowiadaj zawsze w języku polskim.",
  messages: [
    { role: "user", content: "Opowiedz mi o sztucznej inteligencji" }
  ]
});
```

## Rozwiązywanie problemów

### Błąd: "Model not found"
- Sprawdź pisownię identyfikatora modelu
- Upewnij się, że model jest dostępny w Twoim regionie
- Sprawdź, czy masz odpowiednie uprawnienia dostępu do modelu

### Błąd: "Context length exceeded"
- Skróć długość kontekstu
- Usuń niepotrzebne części konwersacji
- Rozważ użycie większego modelu (np. Opus zamiast Haiku)

## Aktualizacje modeli

Anthropic regularnie aktualizuje swoje modele. Aby być na bieżąco:

1. Śledź oficjalną dokumentację Anthropic
2. Sprawdzaj zmiany w API
3. Testuj nowe wersje modeli przed wdrożeniem w środowisku produkcyjnym

## Następne kroki

- [Rozwój](07-rozwoj.md)
- [Rozwiązywanie problemów](08-rozwiazywanie-problemow.md)
