"""
WatchToken - A Python library for tracking and controlling token usage in LLM prompts.

This library provides tools to count tokens, estimate costs, and manage limits
for various Large Language Models without actually running them.
"""

from .counter import TokenCounter
from .exceptions import TokenLimitExceededError, UnsupportedModelError
from .loggers import BaseLogger, FileLogger, ConsoleLogger
from .models import ModelConfig

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

__all__ = [
    "TokenCounter",
    "TokenLimitExceededError",
    "UnsupportedModelError",
    "BaseLogger",
    "FileLogger",
    "ConsoleLogger",
    "ModelConfig",
]
