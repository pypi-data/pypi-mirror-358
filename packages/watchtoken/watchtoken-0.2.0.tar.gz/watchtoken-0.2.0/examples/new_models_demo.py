#!/usr/bin/env python3
"""
Przykład wykorzystania nowych modeli w WatchToken
Demonstracja najnowszych modeli OpenAI, Anthropic i Google
"""

from watchtoken import TokenCounter

def compare_latest_models():
    """Porównanie najnowszych modeli pod kątem kosztów i wydajności."""
    
    print("🚀 Porównanie najnowszych modeli AI")
    print("=" * 60)
    
    test_prompt = """
    Jesteś ekspertem od analizy danych. Przeanalizuj następujące dane sprzedażowe:
    - Styczeń: 120,000 PLN
    - Luty: 135,000 PLN  
    - Marzec: 128,000 PLN
    
    Napisz szczegółowy raport z wnioskami i rekomendacjami dla zespołu zarządzającego.
    """
    
    models_to_compare = [
        # OpenAI - najnowsze
        ("gpt-4o", "OpenAI GPT-4o (multimodal)"),
        ("gpt-4o-mini", "OpenAI GPT-4o Mini (ekonomiczny)"),
        ("gpt-4.1", "OpenAI GPT-4.1 (najnowszy)"),
        
        # Anthropic - najnowsze
        ("claude-sonnet-4", "Claude Sonnet 4"),
        ("claude-3-haiku", "Claude 3 Haiku (szybki)"),
        
        # Google - najnowsze  
        ("gemini-1.5-pro", "Gemini 1.5 Pro (duży kontekst)"),
        ("gemini-2.5-flash", "Gemini 2.5 Flash (szybki)"),
    ]
    
    results = []
    
    for model_id, model_name in models_to_compare:
        try:
            tc = TokenCounter(model_id)
            
            input_tokens = tc.count(test_prompt)
            estimated_output = 500  # Zakładamy 500 tokenów odpowiedzi
            
            cost = tc.estimate_cost(test_prompt, output_tokens=estimated_output)
            info = tc.get_model_info()
            
            results.append({
                'name': model_name,
                'model_id': model_id,
                'input_tokens': input_tokens,
                'total_cost': cost,
                'context_length': info['context_length'],
                'provider': info['provider']
            })
            
        except Exception as e:
            print(f"❌ Błąd dla {model_name}: {e}")
    
    # Sortuj po kosztach
    results.sort(key=lambda x: x['total_cost'])
    
    print(f"\n📊 Wyniki (prompt: {len(test_prompt)} znaków, zakładane {estimated_output} tokenów odpowiedzi):")
    print(f"{'Model':<30} {'Provider':<10} {'Tokeny':<7} {'Koszt':<12} {'Kontekst':<10}")
    print("-" * 75)
    
    for result in results:
        print(f"{result['name']:<30} "
              f"{result['provider']:<10} "
              f"{result['input_tokens']:<7} "
              f"${result['total_cost']:<11.6f} "
              f"{result['context_length']:>9,}")

def test_large_context_capabilities():
    """Test możliwości modeli z dużymi kontekstami."""
    
    print("\n\n🎯 Test modeli z dużymi kontekstami")
    print("=" * 60)
    
    large_context_models = [
        ("gpt-4.1", "1M tokenów"),
        ("gemini-1.5-pro", "1M tokenów"), 
        ("gemini-1.5-flash", "1M tokenów"),
        ("claude-sonnet-4", "200K tokenów"),
    ]
    
    # Stwórz bardzo długi prompt
    base_text = "To jest przykład bardzo długiego tekstu. " * 1000  # ~8000 tokenów
    
    print(f"📝 Test z długim promptem (~{len(base_text)} znaków)")
    print("-" * 50)
    
    for model_id, context_desc in large_context_models:
        try:
            tc = TokenCounter(model_id)
            tokens = tc.count(base_text)
            
            # Sprawdź ile miejsca zostało w kontekście
            remaining = tc.get_remaining_tokens(base_text)
            context_usage = (tokens / tc.get_model_info()['context_length']) * 100
            
            print(f"✅ {model_id:<20} | "
                  f"Użyte: {tokens:>6,} | "
                  f"Zostało: {remaining:>8,} | "
                  f"Wykorzystanie: {context_usage:>5.1f}%")
            
        except Exception as e:
            print(f"❌ {model_id:<20} | Błąd: {e}")

def demo_cost_optimization():
    """Demonstracja optymalizacji kosztów."""
    
    print("\n\n💰 Optymalizacja kosztów - wybór modelu")
    print("=" * 60)
    
    scenarios = [
        ("Krótkie zapytania (<100 tokenów)", "Jak działa AI?"),
        ("Średnie analizy (200-500 tokenów)", "Przeanalizuj trendy rynkowe w branży technologicznej w 2024 roku."),
        ("Długie zadania (1000+ tokenów)", "Napisz szczegółowy biznesplan dla startup'u AI " * 10),
    ]
    
    for scenario_name, prompt in scenarios:
        print(f"\n📋 {scenario_name}")
        print("-" * 40)
        
        # Wybierz reprezentatywne modele dla każdej kategorii cenowej
        models = [
            ("gpt-4o-mini", "Ekonomiczny"),
            ("gpt-4o", "Średni"),  
            ("claude-3-haiku", "Szybki"),
            ("gemini-2.5-flash", "Flash"),
        ]
        
        costs = []
        for model_id, category in models:
            try:
                tc = TokenCounter(model_id)
                cost = tc.estimate_cost(prompt, output_tokens=200)
                costs.append((model_id, category, cost))
            except:
                continue
        
        # Sortuj po kosztach
        costs.sort(key=lambda x: x[2])
        
        cheapest_cost = costs[0][2] if costs else 0
        
        for model_id, category, cost in costs:
            savings = ((cost - cheapest_cost) / cheapest_cost * 100) if cheapest_cost > 0 else 0
            marker = "🥇" if cost == cheapest_cost else f"+{savings:.0f}%"
            print(f"   {model_id:<20} ({category:<10}) ${cost:.6f} {marker}")

def main():
    """Główna funkcja demonstracyjna."""
    try:
        compare_latest_models()
        test_large_context_capabilities() 
        demo_cost_optimization()
        
        print("\n\n✅ Demo zakończone pomyślnie!")
        print("\n💡 Wnioski:")
        print("   • GPT-4o-mini to świetny wybór ekonomiczny")
        print("   • Modele z dużymi kontekstami nadają się do złożonych zadań")
        print("   • Claude Haiku to najszybsza opcja")
        print("   • Gemini Flash oferuje dobry stosunek ceny do wydajności")
        
    except Exception as e:
        print(f"\n❌ Błąd: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
