"""
Anthropic Claude adapter using estimation.
"""

from typing import Tuple
from ..models import get_model_config
from ..exceptions import UnsupportedModelError
from . import BaseAdapter


class AnthropicAdapter(BaseAdapter):
    """Adapter for Anthropic Claude models using token estimation."""

    def __init__(self, model_name: str) -> None:
        super().__init__(model_name)

        self.config = get_model_config(model_name)
        if not self.config:
            raise UnsupportedModelError(model_name)

    def count_tokens(self, text: str) -> int:
        """
        Estimate tokens for Claude models.
        Claude uses a different tokenization than OpenAI, but this provides
        a reasonable approximation.
        """
        # Claude tokenization is roughly similar to GPT-4
        # but tends to be slightly more efficient for natural language

        # Basic estimation: count words and punctuation
        import re

        # Split on whitespace and count words
        words = len(text.split())

        # Count punctuation marks as separate tokens
        punctuation_count = len(re.findall(r"[^\w\s]", text))

        # Claude is generally more efficient, so we use a lower multiplier
        estimated_tokens = int((words + punctuation_count) * 0.75)

        # Ensure minimum of 1 token for non-empty text
        return max(1, estimated_tokens) if text.strip() else 0

    def get_cost_per_token(self) -> Tuple[float, float]:
        """Return (input_cost, output_cost) per token."""
        return (self.config.input_cost_per_token, self.config.output_cost_per_token)

    def get_context_length(self) -> int:
        """Return maximum context length."""
        return self.config.context_length
