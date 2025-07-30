"""
Base adapter interface for tokenizers.
"""

from abc import ABC, abstractmethod
from typing import Tuple


class BaseAdapter(ABC):
    """Abstract base class for model adapters."""

    def __init__(self, model_name: str) -> None:
        self.model_name = model_name

    @abstractmethod
    def count_tokens(self, text: str) -> int:
        """Count the number of tokens in the given text."""
        pass

    @abstractmethod
    def get_cost_per_token(self) -> Tuple[float, float]:
        """Return (input_cost_per_token, output_cost_per_token)."""
        pass

    def get_context_length(self) -> int:
        """Return the maximum context length for this model."""
        return 4096  # Default value, should be overridden

    def estimate_tokens(self, text: str) -> int:
        """
        Fallback estimation method using simple heuristics.
        This can be overridden by specific adapters.
        """
        # Simple estimation: ~4 characters per token for English text
        return max(1, len(text) // 4)


__all__ = ["BaseAdapter"]
