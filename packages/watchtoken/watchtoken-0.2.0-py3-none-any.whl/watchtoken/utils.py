"""
Utility functions for WatchToken library.
"""

from typing import List, Dict, Any, Optional
import re
from .models import list_supported_models, get_model_config


def estimate_tokens_simple(text: str) -> int:
    """
    Simple token estimation based on character count.
    Useful as a fallback when specific tokenizers are not available.

    Args:
        text: Text to estimate tokens for

    Returns:
        Estimated number of tokens
    """
    if not text.strip():
        return 0

    # Simple heuristic: ~4 characters per token for English text
    return max(1, len(text) // 4)


def estimate_tokens_word_based(text: str) -> int:
    """
    Word-based token estimation.
    More accurate than character-based for natural language.

    Args:
        text: Text to estimate tokens for

    Returns:
        Estimated number of tokens
    """
    if not text.strip():
        return 0

    # Count words and punctuation separately
    words = len(text.split())
    punctuation_count = len(re.findall(r"[^\w\s]", text))

    # Most tokenizers split punctuation
    return max(1, words + punctuation_count)


def get_model_summary() -> List[Dict[str, Any]]:
    """
    Get summary of all supported models.

    Returns:
        List of dictionaries with model information
    """
    summary = []

    for model_name in list_supported_models():
        config = get_model_config(model_name)
        if config:
            summary.append(
                {
                    "name": config.name,
                    "provider": config.provider.value,
                    "context_length": config.context_length,
                    "input_cost_per_1k_tokens": config.input_cost_per_token * 1000,
                    "output_cost_per_1k_tokens": config.output_cost_per_token * 1000,
                    "tokenizer": config.tokenizer_type,
                }
            )

    return summary


def format_cost(cost: float) -> str:
    """
    Format cost for display.

    Args:
        cost: Cost in USD

    Returns:
        Formatted cost string
    """
    if cost < 0.0001:
        return f"${cost:.6f}"
    elif cost < 0.01:
        return f"${cost:.4f}"
    else:
        return f"${cost:.2f}"


def truncate_text(text: str, max_length: int = 50) -> str:
    """
    Truncate text for display purposes.

    Args:
        text: Text to truncate
        max_length: Maximum length before truncation

    Returns:
        Truncated text with ellipsis if needed
    """
    if len(text) <= max_length:
        return text
    return text[: max_length - 3] + "..."


def calculate_batch_cost(
    texts: List[str], model: str, output_tokens_per_text: int = 0
) -> Dict[str, Any]:
    """
    Calculate total cost for a batch of texts.

    Args:
        texts: List of input texts
        model: Model name
        output_tokens_per_text: Expected output tokens per text

    Returns:
        Dictionary with batch cost information
    """
    from .counter import TokenCounter

    tc = TokenCounter(model)

    total_input_tokens = 0
    total_output_tokens = len(texts) * output_tokens_per_text
    total_cost = 0.0

    text_costs = []

    for text in texts:
        input_tokens = tc.count(text)
        cost = tc.estimate_cost(text, output_tokens_per_text)

        total_input_tokens += input_tokens
        total_cost += cost

        text_costs.append(
            {
                "text": truncate_text(text),
                "input_tokens": input_tokens,
                "output_tokens": output_tokens_per_text,
                "cost": cost,
            }
        )

    return {
        "model": model,
        "total_texts": len(texts),
        "total_input_tokens": total_input_tokens,
        "total_output_tokens": total_output_tokens,
        "total_tokens": total_input_tokens + total_output_tokens,
        "total_cost": total_cost,
        "average_cost_per_text": total_cost / len(texts) if texts else 0,
        "text_breakdown": text_costs,
    }
