"""
Podstawowe przykłady użycia biblioteki WatchToken.
"""

from watchtoken import TokenCounter, FileLogger


def basic_usage():
    """Podstawowe użycie - liczenie tokenów i sprawdzanie limitów."""
    print("=== Podstawowe użycie ===")
    
    # Inicjalizacja TokenCounter
    tc = TokenCounter(model="gpt-4-turbo", limit=100)
    
    # Przykładowy tekst
    text = "Napisz streszczenie książki 'Pan Tadeusz' Adama Mickiewicza."
    
    # Liczenie tokenów
    tokens = tc.count(text)
    print(f"Tekst: '{text}'")
    print(f"Liczba tokenów: {tokens}")
    
    # Sprawdzenie czy przekracza limit
    if tc.is_over(text):
        print("⚠️ Tekst przekracza limit!")
    else:
        print("✅ Tekst mieści się w limicie")
    
    # Sprawdzenie pozostałych tokenów
    remaining = tc.get_remaining_tokens(text)
    print(f"Pozostałe tokeny: {remaining}")


def cost_estimation():
    """Przykład estymacji kosztów."""
    print("\n=== Estymacja kosztów ===")
    
    tc = TokenCounter("gpt-4-turbo")
    
    prompts = [
        "Hello world!",
        "Napisz artykuł o sztucznej inteligencji (500 słów).",
        "Przetłumacz następujący tekst na język angielski: 'Dzień dobry, jak się masz?'"
    ]
    
    for prompt in prompts:
        tokens = tc.count(prompt)
        
        # Estymacja kosztu dla różnych długości odpowiedzi
        cost_short = tc.estimate_cost(prompt, output_tokens=50)
        cost_medium = tc.estimate_cost(prompt, output_tokens=200)
        cost_long = tc.estimate_cost(prompt, output_tokens=500)
        
        print(f"\nPrompt: '{prompt[:50]}...'")
        print(f"Input tokens: {tokens}")
        print(f"Koszt (50 tokens output): ${cost_short:.6f}")
        print(f"Koszt (200 tokens output): ${cost_medium:.6f}")
        print(f"Koszt (500 tokens output): ${cost_long:.6f}")


def model_comparison():
    """Porównanie różnych modeli."""
    print("\n=== Porównanie modeli ===")
    
    models = ["gpt-3.5-turbo", "gpt-4-turbo", "claude-3-sonnet", "gemini-pro"]
    text = "Analyze the impact of artificial intelligence on modern education."
    
    print(f"Tekst do analizy: '{text}'")
    print(f"{'Model':<20} {'Tokens':<8} {'Koszt (100 out)':<15} {'Limit':<10}")
    print("-" * 60)
    
    for model in models:
        try:
            tc = TokenCounter(model)
            tokens = tc.count(text)
            cost = tc.estimate_cost(text, output_tokens=100)
            info = tc.get_model_info()
            
            print(f"{model:<20} {tokens:<8} ${cost:<14.6f} {info['context_length']:<10}")
        except Exception as e:
            print(f"{model:<20} Error: {e}")


def callback_example():
    """Przykład użycia callbacków."""
    print("\n=== Callbacki przy przekroczeniu limitu ===")
    
    def on_limit_exceeded(tokens, limit, model):
        print(f"🚨 ALERT: Model {model} przekroczył limit!")
        print(f"   Użyto: {tokens} tokenów")
        print(f"   Limit: {limit} tokenów")
        print(f"   Przekroczenie: {tokens - limit} tokenów")
    
    # TokenCounter z małym limitem i callbackiem
    tc = TokenCounter(
        model="gpt-3.5-turbo", 
        limit=10,
        on_limit_exceeded=on_limit_exceeded
    )
    
    # Ten tekst przekroczy limit
    long_text = """
    Sztuczna inteligencja to dziedzina informatyki, która zajmuje się tworzeniem 
    systemów zdolnych do wykonywania zadań wymagających inteligencji, gdy są 
    wykonywane przez ludzi. Obejmuje to uczenie maszynowe, przetwarzanie języka 
    naturalnego, rozpoznawanie obrazów i wiele innych technologii.
    """
    
    print("Sprawdzanie długiego tekstu...")
    tc.check_limit(long_text.strip())


def logging_example():
    """Przykład logowania użycia tokenów."""
    print("\n=== Logowanie użycia ===")
    
    # Utworzenie loggera do pliku
    logger = FileLogger("token_usage.log")
    
    # TokenCounter z automatycznym logowaniem
    tc = TokenCounter("gpt-4-turbo", logger=logger, auto_log=True)
    
    # Przykładowe użycie (zostanie automatycznie zalogowane)
    prompts = [
        "Translate: Hello world",
        "Summarize: The quick brown fox jumps over the lazy dog",
        "Explain: quantum computing"
    ]
    
    print("Przetwarzanie promptów z logowaniem...")
    for prompt in prompts:
        tokens = tc.count(prompt)
        cost = tc.estimate_cost(prompt, output_tokens=30)
        print(f"  '{prompt}' -> {tokens} tokens, ${cost:.6f}")
    
    print("✅ Wszystkie operacje zostały zalogowane do 'token_usage.log'")


def batch_processing():
    """Przykład przetwarzania wsadowego."""
    print("\n=== Przetwarzanie wsadowe ===")
    
    from watchtoken.utils import calculate_batch_cost
    
    texts = [
        "What is machine learning?",
        "Explain neural networks in simple terms",
        "How does natural language processing work?",
        "What are the applications of AI in healthcare?",
        "Describe the future of artificial intelligence"
    ]
    
    # Obliczenie kosztu dla całej paczki
    batch_info = calculate_batch_cost(
        texts=texts,
        model="gpt-4-turbo", 
        output_tokens_per_text=150
    )
    
    print(f"Analiza paczki {batch_info['total_texts']} tekstów:")
    print(f"  Model: {batch_info['model']}")
    print(f"  Całkowite tokeny input: {batch_info['total_input_tokens']}")
    print(f"  Całkowite tokeny output: {batch_info['total_output_tokens']}")
    print(f"  Całkowity koszt: ${batch_info['total_cost']:.6f}")
    print(f"  Średni koszt na tekst: ${batch_info['average_cost_per_text']:.6f}")
    
    print("\nSzczegóły dla każdego tekstu:")
    for i, text_info in enumerate(batch_info['text_breakdown']):
        print(f"  {i+1}. '{text_info['text']}' -> {text_info['input_tokens']} tokens, ${text_info['cost']:.6f}")


def model_info_example():
    """Przykład pobierania informacji o modelach."""
    print("\n=== Informacje o modelach ===")
    
    from watchtoken.utils import get_model_summary
    
    # Pobranie podsumowania wszystkich modeli
    models_summary = get_model_summary()
    
    print(f"{'Model':<20} {'Provider':<12} {'Context':<8} {'Input$/1K':<10} {'Output$/1K':<10}")
    print("-" * 70)
    
    for model in models_summary:
        print(
            f"{model['name']:<20} "
            f"{model['provider']:<12} "
            f"{model['context_length']:<8} "
            f"${model['input_cost_per_1k_tokens']:<9.3f} "
            f"${model['output_cost_per_1k_tokens']:<9.3f}"
        )


if __name__ == "__main__":
    print("🕐 WatchToken - Przykłady użycia\n")
    
    try:
        basic_usage()
        cost_estimation()
        model_comparison() 
        callback_example()
        logging_example()
        batch_processing()
        model_info_example()
        
        print("\n✅ Wszystkie przykłady wykonane pomyślnie!")
        
    except Exception as e:
        print(f"\n❌ Wystąpił błąd: {e}")
        print("Upewnij się, że zainstalowałeś wszystkie wymagane zależności:")
        print("pip install tiktoken")
