"""
Main TokenCounter class for tracking and managing token usage.
"""

from typing import Optional, Callable, Dict, Type, Union
import datetime

from .models import get_model_config, ModelProvider
from .exceptions import TokenLimitExceededError, UnsupportedModelError
from .loggers import BaseLogger, ConsoleLogger
from .adapters import BaseAdapter
from .adapters.openai import OpenAIAdapter
from .adapters.anthropic import AnthropicAdapter
from .adapters.google import GoogleAdapter
from .adapters.mistral import MistralAdapter


class TokenCounter:
    """
    Main class for counting tokens and managing limits across different LLM models.

    Examples:
        Basic usage:
        >>> tc = TokenCounter(model="gpt-4-turbo", limit=8000)
        >>> tokens = tc.count("Hello world!")
        >>> print(f"Tokens: {tokens}")

        With cost estimation:
        >>> cost = tc.estimate_cost("Hello world!", output_tokens=50)
        >>> print(f"Estimated cost: ${cost:.4f}")

        With custom callback:
        >>> def on_limit(tokens, limit, model):
        ...     print(f"Limit exceeded: {tokens} > {limit}")
        >>> tc = TokenCounter("gpt-4", limit=1000, on_limit_exceeded=on_limit)
    """

    # Registry for custom adapters
    _adapters: Dict[str, Type[BaseAdapter]] = {}

    def __init__(
        self,
        model: str,
        limit: Optional[int] = None,
        logger: Optional[BaseLogger] = None,
        on_limit_exceeded: Optional[Callable[[int, int, str], None]] = None,
        auto_log: bool = False,
    ) -> None:
        """
        Initialize TokenCounter.

        Args:
            model: Model name (e.g., "gpt-4-turbo", "claude-3-sonnet")
            limit: Maximum token limit (optional)
            logger: Logger instance for usage tracking (optional)
            on_limit_exceeded: Callback function when limit is exceeded (optional)
            auto_log: Whether to automatically log all token usage (default: False)
        """
        self.model = model
        self.limit = limit
        self.logger = logger
        self.on_limit_exceeded = on_limit_exceeded
        self.auto_log = auto_log

        # Initialize adapter
        self.adapter = self._create_adapter(model)

        # Set default limit if not provided
        if self.limit is None:
            self.limit = self.adapter.get_context_length()

        # Set up default logger if auto_log is enabled
        if self.auto_log and not self.logger:
            self.logger = ConsoleLogger(verbose=True)

    def _create_adapter(self, model: str) -> BaseAdapter:
        """Create appropriate adapter for the given model."""
        # Check custom adapters first
        if model in self._adapters:
            return self._adapters[model](model)

        # Get model config to determine provider
        config = get_model_config(model)
        if not config:
            raise UnsupportedModelError(model)

        # Create adapter based on provider
        if config.provider == ModelProvider.OPENAI:
            return OpenAIAdapter(model)
        elif config.provider == ModelProvider.ANTHROPIC:
            return AnthropicAdapter(model)
        elif config.provider == ModelProvider.GOOGLE:
            return GoogleAdapter(model)
        elif config.provider == ModelProvider.MISTRAL:
            return MistralAdapter(model)
        else:
            raise UnsupportedModelError(
                f"No adapter available for provider: {config.provider}"
            )

    @classmethod
    def register_adapter(
        cls, model_name: str, adapter_class: Type[BaseAdapter]
    ) -> None:
        """Register a custom adapter for a model."""
        cls._adapters[model_name] = adapter_class

    def count(self, text: str) -> int:
        """
        Count tokens in the given text.

        Args:
            text: Text to tokenize

        Returns:
            Number of tokens
        """
        tokens = self.adapter.count_tokens(text)

        # Auto-log if enabled
        if self.auto_log and self.logger:
            self.logger.log_token_usage(self.model, text, tokens)

        return tokens

    def is_over(self, text: str) -> bool:
        """
        Check if text exceeds the token limit.

        Args:
            text: Text to check

        Returns:
            True if text exceeds limit, False otherwise
        """
        tokens = self.count(text)
        return tokens > self.limit if self.limit else False

    def check_limit(self, text: str, raise_on_exceed: bool = False) -> int:
        """
        Check token count against limit and optionally raise exception.

        Args:
            text: Text to check
            raise_on_exceed: Whether to raise exception if limit exceeded

        Returns:
            Number of tokens

        Raises:
            TokenLimitExceededError: If limit exceeded and raise_on_exceed=True
        """
        tokens = self.count(text)

        if self.limit and tokens > self.limit:
            # Call callback if provided
            if self.on_limit_exceeded:
                self.on_limit_exceeded(tokens, self.limit, self.model)

            # Raise exception if requested
            if raise_on_exceed:
                raise TokenLimitExceededError(tokens, self.limit, self.model)

        return tokens

    def estimate_cost(
        self,
        input_text: str,
        output_tokens: int = 0,
        input_multiplier: float = 1.0,
        output_multiplier: float = 1.0,
    ) -> float:
        """
        Estimate cost for the given input and expected output.

        Args:
            input_text: Input text to tokenize
            output_tokens: Expected number of output tokens
            input_multiplier: Multiplier for input cost (default: 1.0)
            output_multiplier: Multiplier for output cost (default: 1.0)

        Returns:
            Estimated cost in USD
        """
        input_tokens = self.count(input_text)
        input_cost_per_token, output_cost_per_token = self.adapter.get_cost_per_token()

        input_cost = input_tokens * input_cost_per_token * input_multiplier
        output_cost = output_tokens * output_cost_per_token * output_multiplier

        total_cost = input_cost + output_cost

        # Auto-log if enabled
        if self.auto_log and self.logger:
            self.logger.log_cost_estimation(
                self.model, input_tokens, output_tokens, total_cost
            )

        return total_cost

    def get_remaining_tokens(self, text: str) -> int:
        """
        Get number of remaining tokens before hitting the limit.

        Args:
            text: Text to check against

        Returns:
            Number of remaining tokens (0 if no limit set)
        """
        if not self.limit:
            return 0

        used_tokens = self.count(text)
        return max(0, self.limit - used_tokens)

    def get_model_info(self) -> Dict[str, Union[str, int, float]]:
        """
        Get information about the current model.

        Returns:
            Dictionary with model information
        """
        config = get_model_config(self.model)
        input_cost, output_cost = self.adapter.get_cost_per_token()

        return {
            "model": self.model,
            "provider": config.provider.value if config else "unknown",
            "context_length": self.adapter.get_context_length(),
            "current_limit": self.limit,
            "input_cost_per_token": input_cost,
            "output_cost_per_token": output_cost,
            "tokenizer_type": config.tokenizer_type if config else "unknown",
        }

    def set_limit(self, limit: Optional[int]) -> None:
        """Update the token limit."""
        self.limit = limit

    def set_logger(self, logger: Optional[BaseLogger]) -> None:
        """Update the logger."""
        self.logger = logger
