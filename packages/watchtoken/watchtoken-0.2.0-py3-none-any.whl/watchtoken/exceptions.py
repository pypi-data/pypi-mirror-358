"""
Custom exceptions for WatchToken library.
"""


class WatchTokenError(Exception):
    """Base exception class for WatchToken library."""

    pass


class TokenLimitExceededError(WatchTokenError):
    """Raised when token limit is exceeded."""

    def __init__(self, tokens: int, limit: int, model: str) -> None:
        self.tokens = tokens
        self.limit = limit
        self.model = model
        super().__init__(
            f"Token limit exceeded for model '{model}': {tokens} > {limit}"
        )


class UnsupportedModelError(WatchTokenError):
    """Raised when trying to use an unsupported model."""

    def __init__(self, model: str) -> None:
        self.model = model
        super().__init__(f"Model '{model}' is not supported")


class TokenizerError(WatchTokenError):
    """Raised when tokenizer fails to process text."""

    def __init__(self, message: str, model: str) -> None:
        self.model = model
        super().__init__(f"Tokenizer error for model '{model}': {message}")


class ConfigurationError(WatchTokenError):
    """Raised when configuration is invalid."""

    pass
