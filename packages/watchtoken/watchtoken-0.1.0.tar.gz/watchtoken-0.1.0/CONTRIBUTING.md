# Contributing to WatchToken

Dziękujemy za zainteresowanie współpracą przy projekcie WatchToken! 🎉

## 🚀 Jak zacząć

1. **Forkuj repozytorium** na GitHubie
2. **Sklonuj swój fork** lokalnie:
   ```bash
   git clone https://github.com/twojusername/watchtoken.git
   cd watchtoken
   ```
3. **Utwórz nowy branch** dla swojej funkcji:
   ```bash
   git checkout -b feature/nazwa-funkcji
   ```

## 🛠️ Konfiguracja środowiska deweloperskiego

```bash
# Instalacja w trybie deweloperskim
pip install -e .[dev]

# Instalacja dodatkowych zależności (opcjonalnie)
pip install -e .[sentencepiece,transformers]
```

## 📝 Standardy kodowania

### Formatowanie kodu
```bash
# Automatyczne formatowanie
black watchtoken tests
isort watchtoken tests

# Sprawdzenie stylu
flake8 watchtoken tests
```

### Typowanie
```bash
# Sprawdzenie typów
mypy watchtoken
```

### Testy
```bash
# Uruchomienie wszystkich testów
pytest

# Z pokryciem kodu
pytest --cov=watchtoken

# Tylko konkretny test
pytest tests/test_watchtoken.py::TestTokenCounter::test_basic_token_counting
```

## 🎯 Rodzaje kontrybucji

### 🐛 Zgłaszanie błędów
- Użyj GitHub Issues
- Opisz problem szczegółowo
- Podaj kod do reprodukcji
- Wskaż środowisko (Python version, OS)

### ✨ Nowe funkcje
- Omów pomysł w GitHub Issues przed implementacją
- Upewnij się, że funkcja jest zgodna z celami projektu
- Dodaj testy dla nowej funkcjonalności
- Zaktualizuj dokumentację

### 📚 Dokumentacja
- Popraw README.md
- Dodaj docstringi do funkcji
- Napisz przykłady użycia
- Przetłumacz dokumentację

### 🔧 Adaptery dla nowych modeli
Aby dodać wsparcie dla nowego modelu:

1. **Utwórz nowy adapter** w `watchtoken/adapters/`:
   ```python
   from . import BaseAdapter
   
   class NewModelAdapter(BaseAdapter):
       def count_tokens(self, text: str) -> int:
           # Implementacja tokenizacji
           pass
       
       def get_cost_per_token(self) -> tuple[float, float]:
           # Zwróć (input_cost, output_cost)
           pass
   ```

2. **Dodaj konfigurację modelu** w `watchtoken/models.py`:
   ```python
   MODEL_CONFIGS["new-model"] = ModelConfig(
       name="new-model",
       provider=ModelProvider.CUSTOM,
       context_length=4096,
       input_cost_per_token=0.001,
       output_cost_per_token=0.002,
       tokenizer_type="custom"
   )
   ```

3. **Zarejestruj adapter** w `watchtoken/counter.py`

4. **Dodaj testy** w `tests/`

## ✅ Checklist przed Pull Request

- [ ] Kod jest sformatowany (black, isort)
- [ ] Wszystkie testy przechodzą
- [ ] Dodano testy dla nowych funkcji
- [ ] Dokumentacja jest zaktualizowana
- [ ] Nie ma błędów typowania (mypy)
- [ ] Commit messages są opisowe

## 📋 Szablon Pull Request

```markdown
## Opis
Krótki opis zmian...

## Typ zmiany
- [ ] Naprawa błędu
- [ ] Nowa funkcja
- [ ] Zmiana łamliwa
- [ ] Aktualizacja dokumentacji

## Testy
- [ ] Istniejące testy przechodzą
- [ ] Dodano nowe testy
- [ ] Testowano manualnie

## Dodatkowe informacje
Dodatkowy kontekst, screenshoty, etc.
```

## 🏗️ Struktura projektu

```
watchtoken/
├── watchtoken/           # Główny pakiet
│   ├── __init__.py      # Eksporty publiczne
│   ├── counter.py       # Główna klasa TokenCounter
│   ├── models.py        # Konfiguracje modeli
│   ├── exceptions.py    # Wyjątki
│   ├── loggers.py       # System logowania
│   ├── utils.py         # Funkcje pomocnicze
│   └── adapters/        # Adaptery dla różnych modeli
│       ├── __init__.py  # Bazowy adapter
│       ├── openai.py    # Adapter OpenAI
│       ├── anthropic.py # Adapter Anthropic
│       └── ...
├── tests/               # Testy jednostkowe
├── examples/            # Przykłady użycia
└── docs/               # Dokumentacja
```

## 🌟 Wskazówki

### Dobre praktyki
- **Jeden commit = jedna zmiana logiczna**
- **Opisowe commit messages**: `Add: support for Mistral models` zamiast `fix`
- **Małe Pull Requesty**: łatwiejsze do przeglądu
- **Testy pierwsze**: napisz test, potem implementację

### Performance
- Adaptery powinny być efektywne
- Cachuj wyniki jeśli to możliwe
- Unikaj niepotrzebnych wywołań API

### Kompatybilność
- Wspieraj Python 3.8+
- Używaj type hints
- Graceful degradation dla opcjonalnych zależności

## 💬 Komunikacja

- **GitHub Issues**: błędy, propozycje funkcji
- **GitHub Discussions**: pytania, pomysły
- **Pull Requests**: code review

## 🎉 Podziękowania

Każda kontrybucja jest ceniona! Contributors będą wymienieni w README.md.

---

**Happy coding!** 🚀
