"""
Model configurations and pricing information.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any
from enum import Enum


class ModelProvider(Enum):
    """Supported model providers."""

    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    MISTRAL = "mistral"
    CUSTOM = "custom"


@dataclass
class ModelConfig:
    """Configuration for a specific model."""

    name: str
    provider: ModelProvider
    context_length: int
    input_cost_per_token: float  # Cost per input token in USD
    output_cost_per_token: float  # Cost per output token in USD
    tokenizer_type: str = "tiktoken"  # tiktoken, sentencepiece, estimation
    tokenizer_name: Optional[str] = None  # e.g., "cl100k_base" for tiktoken
    encoding_name: Optional[str] = None  # Deprecated, use tokenizer_name
    additional_config: Optional[Dict[str, Any]] = None


# Predefiniowane konfiguracje modeli
MODEL_CONFIGS: Dict[str, ModelConfig] = {
    # OpenAI Models
    "gpt-3.5-turbo": ModelConfig(
        name="gpt-3.5-turbo",
        provider=ModelProvider.OPENAI,
        context_length=4096,
        input_cost_per_token=0.0000015,  # $0.0015 per 1K tokens
        output_cost_per_token=0.000002,  # $0.002 per 1K tokens
        tokenizer_type="tiktoken",
        tokenizer_name="cl100k_base",
    ),
    "gpt-3.5-turbo-16k": ModelConfig(
        name="gpt-3.5-turbo-16k",
        provider=ModelProvider.OPENAI,
        context_length=16384,
        input_cost_per_token=0.000003,  # $0.003 per 1K tokens
        output_cost_per_token=0.000004,  # $0.004 per 1K tokens
        tokenizer_type="tiktoken",
        tokenizer_name="cl100k_base",
    ),
    "gpt-4": ModelConfig(
        name="gpt-4",
        provider=ModelProvider.OPENAI,
        context_length=8192,
        input_cost_per_token=0.00003,  # $0.03 per 1K tokens
        output_cost_per_token=0.00006,  # $0.06 per 1K tokens
        tokenizer_type="tiktoken",
        tokenizer_name="cl100k_base",
    ),
    "gpt-4-turbo": ModelConfig(
        name="gpt-4-turbo",
        provider=ModelProvider.OPENAI,
        context_length=128000,
        input_cost_per_token=0.00001,  # $0.01 per 1K tokens
        output_cost_per_token=0.00003,  # $0.03 per 1K tokens
        tokenizer_type="tiktoken",
        tokenizer_name="cl100k_base",
    ),
    "gpt-4-32k": ModelConfig(
        name="gpt-4-32k",
        provider=ModelProvider.OPENAI,
        context_length=32768,
        input_cost_per_token=0.00006,  # $0.06 per 1K tokens
        output_cost_per_token=0.00012,  # $0.12 per 1K tokens
        tokenizer_type="tiktoken",
        tokenizer_name="cl100k_base",
    ),
    # Anthropic Claude Models
    "claude-3-sonnet": ModelConfig(
        name="claude-3-sonnet",
        provider=ModelProvider.ANTHROPIC,
        context_length=200000,
        input_cost_per_token=0.000003,  # $0.003 per 1K tokens
        output_cost_per_token=0.000015,  # $0.015 per 1K tokens
        tokenizer_type="estimation",
    ),
    "claude-3-opus": ModelConfig(
        name="claude-3-opus",
        provider=ModelProvider.ANTHROPIC,
        context_length=200000,
        input_cost_per_token=0.000015,  # $0.015 per 1K tokens
        output_cost_per_token=0.000075,  # $0.075 per 1K tokens
        tokenizer_type="estimation",
    ),
    "claude-3-haiku": ModelConfig(
        name="claude-3-haiku",
        provider=ModelProvider.ANTHROPIC,
        context_length=200000,
        input_cost_per_token=0.00000025,  # $0.00025 per 1K tokens
        output_cost_per_token=0.00000125,  # $0.00125 per 1K tokens
        tokenizer_type="estimation",
    ),
    # Google Gemini Models
    "gemini-pro": ModelConfig(
        name="gemini-pro",
        provider=ModelProvider.GOOGLE,
        context_length=30720,
        input_cost_per_token=0.0000005,  # $0.0005 per 1K tokens
        output_cost_per_token=0.0000015,  # $0.0015 per 1K tokens
        tokenizer_type="estimation",
    ),
    "gemini-pro-vision": ModelConfig(
        name="gemini-pro-vision",
        provider=ModelProvider.GOOGLE,
        context_length=30720,
        input_cost_per_token=0.0000005,  # $0.0005 per 1K tokens
        output_cost_per_token=0.0000015,  # $0.0015 per 1K tokens
        tokenizer_type="estimation",
    ),
    # Mistral Models
    "mistral-7b": ModelConfig(
        name="mistral-7b",
        provider=ModelProvider.MISTRAL,
        context_length=8192,
        input_cost_per_token=0.00000025,  # $0.00025 per 1K tokens
        output_cost_per_token=0.00000025,  # $0.00025 per 1K tokens
        tokenizer_type="sentencepiece",
    ),
    "mixtral-8x7b": ModelConfig(
        name="mixtral-8x7b",
        provider=ModelProvider.MISTRAL,
        context_length=32768,
        input_cost_per_token=0.0000007,  # $0.0007 per 1K tokens
        output_cost_per_token=0.0000007,  # $0.0007 per 1K tokens
        tokenizer_type="sentencepiece",
    ),
}


def get_model_config(model_name: str) -> Optional[ModelConfig]:
    """Get configuration for a specific model."""
    return MODEL_CONFIGS.get(model_name)


def list_supported_models() -> list[str]:
    """Return list of all supported model names."""
    return list(MODEL_CONFIGS.keys())


def add_model_config(model_name: str, config: ModelConfig) -> None:
    """Add or update a model configuration."""
    MODEL_CONFIGS[model_name] = config
