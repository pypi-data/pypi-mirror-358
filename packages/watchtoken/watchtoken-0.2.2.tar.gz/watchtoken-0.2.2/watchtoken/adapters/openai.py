"""
OpenAI adapter using tiktoken for accurate tokenization.
"""

from typing import Tuple, Optional
from ..models import get_model_config
from ..exceptions import TokenizerError, UnsupportedModelError
from . import BaseAdapter

try:
    import tiktoken

    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False


class OpenAIAdapter(BaseAdapter):
    """Adapter for OpenAI models using tiktoken."""

    def __init__(self, model_name: str) -> None:
        super().__init__(model_name)

        if not TIKTOKEN_AVAILABLE:
            raise TokenizerError(
                "tiktoken is required for OpenAI models. Install with: pip install tiktoken",
                model_name,
            )

        self.config = get_model_config(model_name)
        if not self.config:
            raise UnsupportedModelError(model_name)

        # Initialize tiktoken encoder
        try:
            if self.config.tokenizer_name:
                self.encoder = tiktoken.get_encoding(self.config.tokenizer_name)
            else:
                # Fallback to model-specific encoder
                self.encoder = tiktoken.encoding_for_model(model_name)
        except Exception as e:
            raise TokenizerError(
                f"Failed to initialize tiktoken encoder: {e}", model_name
            )

    def count_tokens(self, text: str) -> int:
        """Count tokens using tiktoken."""
        try:
            return len(self.encoder.encode(text))
        except Exception as e:
            raise TokenizerError(f"Failed to encode text: {e}", self.model_name)

    def get_cost_per_token(self) -> Tuple[float, float]:
        """Return (input_cost, output_cost) per token."""
        return (self.config.input_cost_per_token, self.config.output_cost_per_token)

    def get_context_length(self) -> int:
        """Return maximum context length."""
        return self.config.context_length
