"""
Google Gemini adapter using estimation.
"""

from typing import Tuple
from ..models import get_model_config
from ..exceptions import UnsupportedModelError
from . import BaseAdapter


class GoogleAdapter(BaseAdapter):
    """Adapter for Google Gemini models using token estimation."""

    def __init__(self, model_name: str) -> None:
        super().__init__(model_name)

        self.config = get_model_config(model_name)
        if not self.config:
            raise UnsupportedModelError(model_name)

    def count_tokens(self, text: str) -> int:
        """
        Estimate tokens for Gemini models.
        Google's tokenization tends to be more efficient for many languages.
        """
        if not text.strip():
            return 0

        # Simple character-based estimation
        # Gemini tends to be efficient, roughly 3.5-4 chars per token for English
        char_count = len(text)
        estimated_tokens = max(1, char_count // 4)

        # Adjust for different types of content
        # Code and structured text tend to use more tokens
        if self._looks_like_code(text):
            estimated_tokens = int(estimated_tokens * 1.2)

        return estimated_tokens

    def _looks_like_code(self, text: str) -> bool:
        """Simple heuristic to detect if text looks like code."""
        code_indicators = ["{", "}", "()", "=>", "function", "class", "def ", "import "]
        code_score = sum(1 for indicator in code_indicators if indicator in text)
        return code_score >= 2 or text.count("\n") > len(text) // 50

    def get_cost_per_token(self) -> Tuple[float, float]:
        """Return (input_cost, output_cost) per token."""
        return (self.config.input_cost_per_token, self.config.output_cost_per_token)

    def get_context_length(self) -> int:
        """Return maximum context length."""
        return self.config.context_length
