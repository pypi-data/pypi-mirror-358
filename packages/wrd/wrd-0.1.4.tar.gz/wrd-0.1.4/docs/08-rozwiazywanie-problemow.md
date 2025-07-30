# Rozwiązywanie problemów

W tym rozdzieniu znajdziesz rozwiązania najczęstszych problemów związanych z użytkowaniem WRD.

## Spis treści

- [Problemy z uruchomieniem](#problemy-z-uruchomieniem)
- [Problemy z autoryzacją](#problemy-z-autoryzacją)
- [Problemy z wydajnością](#problemy-z-wydajnością)
- [Błędy API](#błędy-api)
- [Problemy z kontenerami Docker](#problemy-z-kontenerami-docker)
- [Problemy z VS Code](#problemy-z-vs-code)
- [Pomoc i wsparcie](#pomoc-i-wsparcie)

## Problemy z uruchomieniem

### Błąd: "Cannot connect to the Docker daemon"

**Objawy:**
```
Cannot connect to the Docker daemon at unix:///var/run/docker.sock. Is the docker daemon running?
```

**Rozwiązanie:**
1. Upewnij się, że Docker jest uruchomiony:
   ```bash
   sudo systemctl start docker
   ```
2. Sprawdź status Dockera:
   ```bash
   sudo systemctl status docker
   ```
3. Jeśli używasz Dockera Desktop, upewnij się, że aplikacja jest uruchomiona

### Błąd: "Port already in use"

**Objawy:**
```
Error starting userland proxy: listen tcp4 0.0.0.0:8083: bind: address already in use
```

**Rozwiązanie:**
1. Znajdź proces używający portu:
   ```bash
   sudo lsof -i :8083
   ```
2. Zatrzymaj proces używający portu lub zmień port w pliku `.env`:
   ```
   VSCODE_PORT=8084
   ```
3. Uruchom ponownie kontenery:
   ```bash
   docker-compose -f docker-compose.claude-code.yml down
   docker-compose -f docker-compose.claude-code.yml up -d
   ```

## Problemy z autoryzacją

### Błąd: "Invalid API key"

**Objawy:**
```
Error: 401 {"type":"error","error":{"type":"authentication_error","message":"invalid x-api-key"}}
```

**Rozwiązanie:**
1. Sprawdź, czy klucz API jest poprawnie ustawiony w pliku `.env`:
   ```
   ANTHROPIC_API_KEY=twój_klucz_api
   ```
2. Upewnij się, że klucz jest aktywny i ma odpowiednie uprawnienia
3. Sprawdź, czy nie ma niechcianych spacji wokół klucza
4. Zrestartuj kontenery po zmianie klucza:
   ```bash
   docker-compose -f docker-compose.claude-code.yml down
   docker-compose -f docker-compose.claude-code.yml up -d
   ```

## Problemy z wydajnością

### Wysokie zużycie pamięci

**Objawy:**
- Kontenery działają bardzo wolno
- System zgłasza brak pamięci

**Rozwiązanie:**
1. Ogranicz zasoby przydzielone Dockerowi w ustawieniach Docker Desktop
2. Zwiększ limit pamięci RAM w pliku `docker-compose.claude-code.yml`:
   ```yaml
   services:
     vscode:
       deploy:
         resources:
           limits:
             cpus: '2'
             memory: 2G
   ```
3. Użyj lżeższego modelu Claude (np. Haiku zamiast Opus)

## Błędy API

### Błąd: "Rate limit exceeded"

**Objawy:**
```
Error: 429 Too Many Requests
```

**Rozwiązanie:**
1. Poczekaj chwilę i spróbuj ponownie
2. Ogranicz liczbę równoległych żądań
3. Zaimplementuj mechanizm ponawiania żądań z opóźnieniem
4. Skontaktuj się z supportem Anthropic, aby zwiększyć limity

### Błąd: "Model not found"

**Objawy:**
```
Error: 404 {"type":"error","error":{"type":"not_found_error","message":"Model not found"}}
```

**Rozwiązanie:**
1. Sprawdź poprawność nazwy modelu
2. Upewnij się, że model jest dostępny w Twoim regionie
3. Sprawdź, czy masz odpowiednie uprawnienia dostępu do modelu

## Problemy z kontenerami Docker

### Kontener się nie uruchamia

**Rozwiązanie:**
1. Sprawdź logi kontenera:
   ```bash
   docker logs claude-vscode
   ```
2. Sprawdź status kontenera:
   ```bash
   docker ps -a
   ```
3. Uruchom kontener w trybie interaktywnym:
   ```bash
   docker-compose -f docker-compose.claude-code.yml up
   ```

### Brak zmian w plikach hosta

**Rozwiązanie:**
1. Sprawdź, czy katalog projektu jest poprawnie zamontowany:
   ```bash
   docker inspect claude-vscode | grep Mounts -A 20
   ```
2. Upewnij się, że masz odpowiednie uprawnienia do katalogu projektu
3. Zrestartuj kontener z opcją `--force-recreate`:
   ```bash
   docker-compose -f docker-compose.claude-code.yml up -d --force-recreate
   ```

## Problemy z VS Code

### Rozszerzenia się nie instalują

**Rozwiązanie:**
1. Sprawdź uprawnienia do katalogu z rozszerzeniami:
   ```bash
   sudo chown -R $USER:$USER ~/.local/share/code-server
   ```
2. Zainstaluj rozszerzenie ręcznie:
   ```bash
   code-server --install-extension ms-python.python
   ```

### Brak połączenia z serwerem

**Rozwiązanie:**
1. Sprawdź, czy kontener działa:
   ```bash
   docker ps
   ```
2. Sprawdź logi kontenera:
   ```bash
   docker logs claude-vscode
   ```
3. Spróbuj połączyć się ponownie po kilku sekundach
4. Wyczyść pamięć podręczną przeglądarki

## Pomoc i wsparcie

### Gdzie szukać pomocy

1. **Dokumentacja**
   - Przeczytaj dokumentację w katalogu `docs/`
   - Sprawdź [oficjalną dokumentację Anthropic](https://docs.anthropic.com/)

2. **Społeczność**
   - [Forum Anthropic](https://community.anthropic.com/)
   - [Stack Overflow](https://stackoverflow.com/questions/tagged/anthropic)

3. **Zgłaszanie błędów**
   - Sprawdź istniejące problemy w repozytorium
   - Jeśli problem nie został jeszcze zgłoszony, utwórz nowe issue z następującymi informacjami:
     - Wersja oprogramowania
     - Kroki do odtworzenia błędu
     - Komunikaty o błędach
     - Zrzuty ekranu (jeśli dotyczy)

### Zbieranie informacji diagnostycznych

Przed zgłoszeniem problemu zbierz następujące informacje:

1. Wersja Dockera:
   ```bash
   docker --version
   docker-compose --version
   ```

2. Logi kontenera VS Code:
   ```bash
   docker logs claude-vscode
   ```

3. Logi kontenera Claude CLI:
   ```bash
   docker logs claude-code
   ```

4. Informacje o systemie:
   ```bash
   uname -a
   cat /etc/os-release
   ```

## Często zadawane pytania (FAQ)

### Jak zresetować hasło do VS Code?

1. Zatrzymaj kontener:
   ```bash
   docker-compose -f docker-compose.claude-code.yml stop vscode
   ```
2. Uruchom kontener bez hasła:
   ```bash
   docker run -e PASSWORD= -p 8083:8080 -v "$PWD:/workspace" -v "$HOME/.config:/home/coder/.config" --name temp-vscode codercom/code-server:latest --auth none
   ```
3. Po zalogowaniu zatrzymaj i usuń kontener tymczasowy, a następnie uruchom ponownie oryginalny.

### Jak zaktualizować do najnowszej wersji?

```bash
git pull origin main
docker-compose -f docker-compose.claude-code.yml down
docker-compose -f docker-compose.claude-code.yml pull
docker-compose -f docker-compose.claude-code.yml up -d --build
```

### Jak wyczyścić dane kontenera?

1. Zatrzymaj i usuń kontenery:
   ```bash
   docker-compose -f docker-compose.claude-code.yml down -v
   ```
2. Usuń nieużywane obrazy i woluminy:
   ```bash
   docker system prune -a --volumes
   ```
3. Uruchom ponownie:
   ```bash
   docker-compose -f docker-compose.claude-code.yml up -d
   ```

## Znane problemy

1. **Wysokie zużycie pamięci**
   - Problem: VS Code może zużywać dużo pamięci przy długotrwałym użytkowaniu
   - Rozwiązanie: Zrestartuj kontener co jakiś czas

2. **Opóźnienia w synchronizacji plików**
   - Problem: Zmiany w plikach mogą nie być od razu widoczne w kontenerze
   - Rozwiązanie: Użyj `rsync` do synchronizacji plików lub zrestartuj kontener

3. **Brak dostępu do GPU**
   - Problem: Domyślnie kontenery nie mają dostępu do GPU
   - Rozwiązanie: Skonfiguruj Docker do obsługi GPU i dodaj odpowiednie flagi w pliku `docker-compose.claude-code.yml`

## Przydatne polecenia

### Zarządzanie kontenerami

```bash
# Uruchomienie kontenerów w tle
docker-compose -f docker-compose.claude-code.yml up -d

# Zatrzymanie kontenerów
docker-compose -f docker-compose.claude-code.yml down

# Wyświetlenie logów
docker logs -f claude-vscode

# Wejście do kontenera
docker exec -it claude-vscode /bin/bash
```

### Zarządzanie obrazami

```bash
# Lista obrazów
docker images

# Usunięcie nieużywanych obrazów
docker image prune -a

# Przebudowanie obrazu
docker-compose -f docker-compose.claude-code.yml build --no-cache
```

## Dodatkowe zasoby

- [Dokumentacja Dockera](https://docs.docker.com/)
- [Dokumentacja Docker Compose](https://docs.docker.com/compose/)
- [Dokumentacja VS Code Server](https://github.com/cdr/code-server)
- [Dokumentacja Anthropic API](https://docs.anthropic.com/)
