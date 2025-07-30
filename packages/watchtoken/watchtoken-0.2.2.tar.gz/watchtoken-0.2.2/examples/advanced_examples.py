"""
Zaawansowane przykłady użycia WatchToken.
"""

from watchtoken import TokenCounter, FileLogger, ConsoleLogger
from watchtoken.loggers import MultiLogger
from watchtoken.adapters import BaseAdapter
from watchtoken.models import ModelConfig, ModelProvider, add_model_config
from watchtoken.exceptions import TokenLimitExceededError
import time


def custom_adapter_example():
    """Przykład tworzenia własnego adaptera."""
    print("=== Własny adapter ===")
    
    class SimpleWordCountAdapter(BaseAdapter):
        """Prosty adapter liczący słowa jako tokeny."""
        
        def count_tokens(self, text: str) -> int:
            if not text.strip():
                return 0
            return len(text.split())
        
        def get_cost_per_token(self):
            # Bardzo tanie: $0.0001 za input, $0.0002 za output na token
            return (0.0001, 0.0002)
        
        def get_context_length(self) -> int:
            return 1000  # Limit 1000 "tokenów" (słów)
    
    # Rejestracja własnego modelu
    add_model_config("simple-model", ModelConfig(
        name="simple-model",
        provider=ModelProvider.CUSTOM,
        context_length=1000,
        input_cost_per_token=0.0001,
        output_cost_per_token=0.0002,
        tokenizer_type="word-count"
    ))
    
    # Rejestracja adaptera
    TokenCounter.register_adapter("simple-model", SimpleWordCountAdapter)
    
    # Użycie
    tc = TokenCounter("simple-model")
    
    text = "To jest przykład tekstu z dziesięcioma słowami w sumie"
    tokens = tc.count(text)
    cost = tc.estimate_cost(text, output_tokens=5)
    
    print(f"Tekst: '{text}'")
    print(f"Tokens (słowa): {tokens}")
    print(f"Koszt: ${cost:.6f}")
    
    info = tc.get_model_info()
    print(f"Model info: {info}")


def multi_logger_example():
    """Przykład użycia wielu loggerów jednocześnie."""
    print("\n=== Multi-logger ===")
    
    # Utworzenie różnych loggerów
    file_logger = FileLogger("detailed_usage.log")
    console_logger = ConsoleLogger(verbose=True)
    
    # Multi-logger łączący oba
    multi_logger = MultiLogger([file_logger, console_logger])
    
    # TokenCounter z multi-loggerem
    tc = TokenCounter("gpt-3.5-turbo", logger=multi_logger, auto_log=True)
    
    print("Testowanie z wieloma loggerami...")
    
    prompts = [
        "Quick test",
        "Medium length prompt for testing",
        "This is a longer prompt that should demonstrate the logging capabilities"
    ]
    
    for prompt in prompts:
        tokens = tc.count(prompt)
        print(f"Processed: '{prompt[:30]}...' -> {tokens} tokens")
        time.sleep(0.1)  # Krótka pauza dla czytelności


def error_handling_example():
    """Przykład obsługi błędów."""
    print("\n=== Obsługa błędów ===")
    
    # Test nieobsługiwanego modelu
    try:
        tc = TokenCounter("nonexistent-model")
    except Exception as e:
        print(f"Oczekiwany błąd: {type(e).__name__}: {e}")
    
    # Test przekroczenia limitu z wyjątkiem
    tc = TokenCounter("gpt-3.5-turbo", limit=5)
    
    try:
        long_text = "This is definitely a text that will exceed the very small token limit set for this example"
        tc.check_limit(long_text, raise_on_exceed=True)
    except TokenLimitExceededError as e:
        print(f"Złapano wyjątek: {e}")
        print(f"  Tokeny: {e.tokens}")
        print(f"  Limit: {e.limit}")
        print(f"  Model: {e.model}")


def prompt_optimization_example():
    """Przykład optymalizacji promptów pod kątem kosztów."""
    print("\n=== Optymalizacja promptów ===")
    
    tc = TokenCounter("gpt-4-turbo")
    
    # Różne wersje tego samego promptu
    prompts = {
        "verbose": """
        Please provide me with a comprehensive and detailed analysis of the current state 
        of artificial intelligence technology, including but not limited to machine learning 
        algorithms, deep learning frameworks, natural language processing capabilities, 
        computer vision applications, and the potential future implications for various 
        industries and sectors of the economy.
        """,
        
        "medium": """
        Analyze the current state of AI technology including machine learning, NLP, 
        computer vision, and future implications for industries.
        """,
        
        "concise": "Analyze current AI technology and its industry impact."
    }
    
    print("Porównanie różnych wersji promptu:")
    print(f"{'Wersja':<12} {'Tokens':<8} {'Koszt (200 out)':<15}")
    print("-" * 40)
    
    for version, prompt in prompts.items():
        tokens = tc.count(prompt.strip())
        cost = tc.estimate_cost(prompt.strip(), output_tokens=200)
        print(f"{version:<12} {tokens:<8} ${cost:<14.6f}")
    
    # Obliczenie oszczędności
    verbose_cost = tc.estimate_cost(prompts["verbose"].strip(), output_tokens=200)
    concise_cost = tc.estimate_cost(prompts["concise"].strip(), output_tokens=200)
    savings = verbose_cost - concise_cost
    savings_percent = (savings / verbose_cost) * 100
    
    print(f"\nOszczędności przy użyciu zwięzłej wersji:")
    print(f"  Absolutne: ${savings:.6f}")
    print(f"  Procentowe: {savings_percent:.1f}%")


def batch_limit_checking():
    """Przykład sprawdzania limitów dla paczki tekstów."""
    print("\n=== Sprawdzanie limitów dla paczki ===")
    
    tc = TokenCounter("gpt-4-turbo", limit=50)
    
    texts = [
        "Short text",
        "This is a medium length text that might be close to the limit",
        "This is a very long text that will definitely exceed the token limit that we have set for this particular example",
        "Another short one",
        "Medium length text for testing purposes and seeing how the limit checking works"
    ]
    
    print(f"Sprawdzanie {len(texts)} tekstów z limitem {tc.limit} tokenów:")
    print()
    
    total_tokens = 0
    within_limit = 0
    exceeded_limit = 0
    
    for i, text in enumerate(texts, 1):
        tokens = tc.count(text)
        total_tokens += tokens
        
        status = "✅ OK" if tokens <= tc.limit else "❌ EXCEED"
        if tokens <= tc.limit:
            within_limit += 1
        else:
            exceeded_limit += 1
        
        print(f"{i}. [{status}] {tokens:3d} tokens: '{text[:40]}...'")
    
    print(f"\nPodsumowanie:")
    print(f"  Teksty w limicie: {within_limit}")
    print(f"  Teksty przekraczające: {exceeded_limit}")
    print(f"  Średnia tokenów: {total_tokens / len(texts):.1f}")


def dynamic_limit_adjustment():
    """Przykład dynamicznego dostosowywania limitów."""
    print("\n=== Dynamiczne dostosowywanie limitów ===")
    
    tc = TokenCounter("gpt-3.5-turbo")
    
    # Symulacja różnych scenariuszy użycia
    scenarios = {
        "quick_question": {
            "limit": 100,
            "description": "Szybkie pytania"
        },
        "detailed_analysis": {
            "limit": 1000,
            "description": "Szczegółowa analiza"
        },
        "creative_writing": {
            "limit": 2000,
            "description": "Pisanie kreatywne"
        }
    }
    
    test_prompt = "Napisz szczegółową analizę wpływu sztucznej inteligencji na rynek pracy"
    tokens = tc.count(test_prompt)
    
    print(f"Prompt do analizy: '{test_prompt}'")
    print(f"Liczba tokenów: {tokens}")
    print()
    
    for scenario, config in scenarios.items():
        tc.set_limit(config["limit"])
        
        if tc.is_over(test_prompt):
            status = "❌ Przekracza limit"
            action = "Skróć prompt lub zwiększ limit"
        else:
            remaining = tc.get_remaining_tokens(test_prompt)
            status = f"✅ OK (pozostało: {remaining})"
            action = "Można wysłać"
        
        print(f"{config['description']} (limit: {config['limit']}):")
        print(f"  Status: {status}")
        print(f"  Akcja: {action}")
        print()


def cost_tracking_example():
    """Przykład śledzenia kosztów w czasie."""
    print("\n=== Śledzenie kosztów ===")
    
    class CostTracker:
        def __init__(self):
            self.total_cost = 0.0
            self.daily_limit = 1.00  # $1.00 dzienny limit
        
        def track_cost(self, cost):
            self.total_cost += cost
            remaining = self.daily_limit - self.total_cost
            
            print(f"  Koszt operacji: ${cost:.6f}")
            print(f"  Łączny koszt: ${self.total_cost:.6f}")
            print(f"  Pozostały budget: ${remaining:.6f}")
            
            if remaining <= 0:
                print("  ⚠️ UWAGA: Przekroczono dzienny limit kosztów!")
            elif remaining < 0.10:
                print("  ⚠️ UWAGA: Mało pozostało do limitu!")
            
            return remaining > 0
    
    tracker = CostTracker()
    tc = TokenCounter("gpt-4-turbo")
    
    # Symulacja kilku operacji
    operations = [
        ("Translate: Hello world", 20),
        ("Write a short story about AI", 300),
        ("Analyze financial data", 150),
        ("Generate marketing copy", 200),
        ("Code review and suggestions", 400)
    ]
    
    print(f"Śledzenie kosztów z dziennym limitem ${tracker.daily_limit:.2f}:")
    print()
    
    for prompt, expected_output in operations:
        cost = tc.estimate_cost(prompt, output_tokens=expected_output)
        
        print(f"Operacja: '{prompt}'")
        can_continue = tracker.track_cost(cost)
        
        if not can_continue:
            print("🛑 Zatrzymano operacje z powodu przekroczenia budżetu")
            break
        
        print()


if __name__ == "__main__":
    print("🚀 WatchToken - Zaawansowane przykłady\n")
    
    try:
        custom_adapter_example()
        multi_logger_example()
        error_handling_example()
        prompt_optimization_example()
        batch_limit_checking()
        dynamic_limit_adjustment()
        cost_tracking_example()
        
        print("\n✅ Wszystkie zaawansowane przykłady wykonane pomyślnie!")
        
    except Exception as e:
        print(f"\n❌ Wystąpił błąd: {e}")
        import traceback
        traceback.print_exc()
