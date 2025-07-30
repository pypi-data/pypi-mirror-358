"""
Mistral adapter using SentencePiece (when available) or estimation.
"""

from typing import Tuple, Optional
from ..models import get_model_config
from ..exceptions import TokenizerError, UnsupportedModelError
from . import BaseAdapter

try:
    import sentencepiece as spm

    SENTENCEPIECE_AVAILABLE = True
except ImportError:
    SENTENCEPIECE_AVAILABLE = False


class MistralAdapter(BaseAdapter):
    """Adapter for Mistral models using SentencePiece or estimation."""

    def __init__(self, model_name: str, model_path: Optional[str] = None) -> None:
        super().__init__(model_name)

        self.config = get_model_config(model_name)
        if not self.config:
            raise UnsupportedModelError(model_name)

        self.sp_model = None

        # Try to load SentencePiece model if available and path provided
        if SENTENCEPIECE_AVAILABLE and model_path:
            try:
                self.sp_model = spm.SentencePieceProcessor()
                self.sp_model.load(model_path)
            except Exception as e:
                # Fall back to estimation if loading fails
                self.sp_model = None
                print(f"Warning: Could not load SentencePiece model: {e}")

    def count_tokens(self, text: str) -> int:
        """Count tokens using SentencePiece or estimation."""
        if not text.strip():
            return 0

        if self.sp_model:
            try:
                return len(self.sp_model.encode_as_pieces(text))
            except Exception:
                # Fall back to estimation if encoding fails
                pass

        # Fallback estimation
        return self._estimate_tokens(text)

    def _estimate_tokens(self, text: str) -> int:
        """
        Estimate tokens for Mistral models.
        Mistral uses SentencePiece which tends to be efficient.
        """
        # SentencePiece tends to create subword tokens
        # Rough estimation: 0.6-0.8 tokens per word for natural language

        words = len(text.split())
        # Account for subword tokenization
        estimated_tokens = max(1, int(words * 0.75))

        return estimated_tokens

    def get_cost_per_token(self) -> Tuple[float, float]:
        """Return (input_cost, output_cost) per token."""
        return (self.config.input_cost_per_token, self.config.output_cost_per_token)

    def get_context_length(self) -> int:
        """Return maximum context length."""
        return self.config.context_length
