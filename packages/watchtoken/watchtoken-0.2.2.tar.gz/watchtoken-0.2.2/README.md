# WatchToken

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Biblioteka Pythona do śledzenia i kontroli liczby tokenów w promptach wysyłanych do różnych modeli językowych (LLM), bez konieczności ich uruchamiania.

## 🚀 Funkcje

- **Obsługa wielu modeli**: OpenAI GPT-3.5/4/4-turbo, Claude 3, Gemini, Mistral i inne
- **Tokenizacja bez uruchamiania modelu**: Wykorzystuje tiktoken, sentencepiece lub estymacje
- **Elastyczne limity**: Definiowanie limitów tokenów per model lub globalnie
- **Inteligentne ostrzeganie**: Powiadomienia o przekroczeniu limitów
- **Estymacja kosztów**: Obliczanie szacunkowych kosztów na podstawie liczby tokenów
- **Logowanie użycia**: Śledzenie użycia tokenów i kosztów
- **Modularna architektura**: Łatwa rozbudowa o własne tokenizery i modele
- **Typowanie**: Pełne wsparcie dla type hints

## 📦 Instalacja

```bash
pip install watchtoken
```

Dodatkowe zależności:
```bash
# Dla modeli używających SentencePiece
pip install watchtoken[sentencepiece]

# Dla modeli Hugging Face
pip install watchtoken[transformers]

# Wszystkie dodatkowe zależności
pip install watchtoken[sentencepiece,transformers]
```

## 🔧 Szybki start

```python
from watchtoken import TokenCounter

# Podstawowe użycie
tc = TokenCounter(model="gpt-4-turbo", limit=8000)

prompt = "Napisz streszczenie 'Pana Tadeusza' w formie opisu filmowego..."

# Sprawdzenie czy prompt przekracza limit
if tc.is_over(prompt):
    print("Zbyt długi prompt!")
else:
    print(f"Zużyto {tc.count(prompt)} tokenów.")

# Estymacja kosztu (zakładając 200 tokenów odpowiedzi)
cost = tc.estimate_cost(prompt, output_tokens=200)
print(f"Szacowany koszt: ${cost:.4f}")
```

## 📖 Szczegółowe przykłady

### Różne modele

```python
from watchtoken import TokenCounter

# OpenAI modele - najnowsze
gpt4o_counter = TokenCounter("gpt-4o", limit=128000)  # Multimodal
gpt4o_mini_counter = TokenCounter("gpt-4o-mini", limit=128000)  # Ekonomiczny
gpt41_counter = TokenCounter("gpt-4.1", limit=1000000)  # Najnowszy z dużym kontekstem

# Claude modele - najnowsze
claude_sonnet4_counter = TokenCounter("claude-sonnet-4", limit=200000)
claude_haiku_counter = TokenCounter("claude-3-haiku", limit=200000)  # Najszybszy

# Gemini modele
gemini25_pro_counter = TokenCounter("gemini-2.5-pro", limit=1048576)  # Najnowszy Pro
gemini25_flash_counter = TokenCounter("gemini-2.5-flash", limit=1048576)  # Szybki 2.5
gemini25_lite_counter = TokenCounter("gemini-2.5-flash-lite", limit=1000000)  # Ultra-ekonomiczny
```

### Callbacki i obsługa przekroczeń

```python
from watchtoken import TokenCounter

def on_limit_exceeded(tokens: int, limit: int, model: str) -> None:
    print(f"⚠️ Przekroczono limit! {tokens}/{limit} tokenów dla {model}")

tc = TokenCounter(
    model="gpt-4-turbo",
    limit=1000,
    on_limit_exceeded=on_limit_exceeded
)

# Automatyczne wywołanie callbacka przy przekroczeniu
tc.check_limit("Very long prompt...")
```

### Estymacja kosztów z różnymi parametrami

```python
from watchtoken import TokenCounter

tc = TokenCounter("gpt-4-turbo")

prompt = "Analyze this data..."

# Podstawowa estymacja
cost = tc.estimate_cost(prompt, output_tokens=500)

# Z uwzględnieniem dodatkowych parametrów
cost_detailed = tc.estimate_cost(
    prompt,
    output_tokens=500,
    input_multiplier=1.0,  # Standardowa cena za input
    output_multiplier=2.0  # 2x cena za output (typowe dla GPT-4)
)
```

### Logowanie użycia

```python
from watchtoken import TokenCounter, FileLogger

# Logowanie do pliku
logger = FileLogger("token_usage.log")
tc = TokenCounter("gpt-4-turbo", logger=logger)

# Każde użycie zostanie zalogowane
tokens = tc.count("Hello world!")
cost = tc.estimate_cost("Hello world!", output_tokens=10)
```

## 🏗️ Architektura

### Obsługiwane modele

| Provider | Model | Tokenizer | Status |
|----------|-------|-----------|--------|
| OpenAI | gpt-3.5-turbo, gpt-4, gpt-4-turbo, gpt-4o, gpt-4o-mini, gpt-4.1* | tiktoken | ✅ |
| Anthropic | claude-3-haiku, claude-3-sonnet, claude-3-opus, claude-sonnet-4* | Estymacja | ✅ |
| Google | gemini-2.5-pro, gemini-2.5-flash, gemini-2.5-flash-lite, gemini-1.5-pro | Estymacja | ✅ |
| Mistral | mistral-7b, mixtral-8x7b | SentencePiece | ✅ |
| Custom | Własne modele | Pluginy | ✅ |

*Najnowsze modele z szacowanymi cenami

### Własne adaptery

```python
from watchtoken.adapters import BaseAdapter
from watchtoken import TokenCounter

class CustomAdapter(BaseAdapter):
    def count_tokens(self, text: str) -> int:
        # Twoja implementacja tokenizacji
        return len(text.split())
    
    def get_cost_per_token(self) -> tuple[float, float]:
        # (input_cost, output_cost) per token
        return (0.00001, 0.00002)

# Rejestracja własnego adaptera
TokenCounter.register_adapter("my-model", CustomAdapter)

# Użycie
tc = TokenCounter("my-model")
```

## 🧪 Rozwój

```bash
# Klonowanie repozytorium
git clone https://github.com/yourusername/watchtoken.git
cd watchtoken

# Instalacja w trybie deweloperskim
pip install -e .[dev]

# Uruchomienie testów
pytest

# Formatowanie kodu
black watchtoken tests
isort watchtoken tests

# Sprawdzenie typów
mypy watchtoken
```

## 📋 Roadmapa

- [x] **v0.2.0**: ✅ Wsparcie dla najnowszych modeli (GPT-4o, Claude Sonnet 4, Gemini 2.5)
- [ ] **v0.3.0**: CLI interface
- [ ] **v0.4.0**: Asynchroniczne API
- [ ] **v0.5.0**: Integracje z popularnymi frameworkami (LangChain, LlamaIndex)
- [ ] **v0.6.0**: Wsparcie dla więcej modeli (LLaMA, xAI Grok)
- [ ] **v1.0.0**: Stabilne API, pełna dokumentacja

## 🤝 Współpraca

Zachęcamy do współpracy! Zobacz [CONTRIBUTING.md](CONTRIBUTING.md) dla szczegółów.

## 📄 Licencja

MIT License - zobacz [LICENSE](LICENSE) dla szczegółów.

## 🙏 Podziękowania

- [tiktoken](https://github.com/openai/tiktoken) - tokenizacja OpenAI
- [sentencepiece](https://github.com/google/sentencepiece) - tokenizacja Google
- Społeczność open-source za inspirację

---

**WatchToken** - Kontroluj swoje tokeny, zanim one kontrolują Twój budżet! 💰
