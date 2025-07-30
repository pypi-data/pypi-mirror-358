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
    # --- OpenAI Models ---
    "gpt-3.5-turbo": ModelConfig(
        name="gpt-3.5-turbo",
        provider=ModelProvider.OPENAI,
        context_length=4096,
        input_cost_per_token=0.0000015,
        output_cost_per_token=0.000002,
        tokenizer_type="tiktoken",
        tokenizer_name="cl100k_base",
    ),
    "gpt-3.5-turbo-16k": ModelConfig(
        name="gpt-3.5-turbo-16k",
        provider=ModelProvider.OPENAI,
        context_length=16384,
        input_cost_per_token=0.000003,
        output_cost_per_token=0.000004,
        tokenizer_type="tiktoken",
        tokenizer_name="cl100k_base",
    ),
    "gpt-4": ModelConfig(
        name="gpt-4",
        provider=ModelProvider.OPENAI,
        context_length=8192,
        input_cost_per_token=0.00003,
        output_cost_per_token=0.00006,
        tokenizer_type="tiktoken",
        tokenizer_name="cl100k_base",
    ),
    "gpt-4-32k": ModelConfig(
        name="gpt-4-32k",
        provider=ModelProvider.OPENAI,
        context_length=32768,
        input_cost_per_token=0.00006,
        output_cost_per_token=0.00012,
        tokenizer_type="tiktoken",
        tokenizer_name="cl100k_base",
    ),
    "gpt-4-turbo": ModelConfig(
        name="gpt-4-turbo",
        provider=ModelProvider.OPENAI,
        context_length=128000,
        input_cost_per_token=0.00001,
        output_cost_per_token=0.00003,
        tokenizer_type="tiktoken",
        tokenizer_name="cl100k_base",
    ),
    "gpt-4o": ModelConfig(
        name="gpt-4o",
        provider=ModelProvider.OPENAI,
        context_length=128000,
        input_cost_per_token=0.0000025,  # $2.50 per 1M tokens
        output_cost_per_token=0.00001,   # $10 per 1M tokens
        tokenizer_type="tiktoken",
        tokenizer_name="cl100k_base",
    ),  # multimodal :contentReference[oaicite:1]{index=1}
    "gpt-4o-mini": ModelConfig(
        name="gpt-4o-mini",
        provider=ModelProvider.OPENAI,
        context_length=128000,
        input_cost_per_token=0.00000015,  # $0.15 per 1M tokens
        output_cost_per_token=0.0000006,  # $0.60 per 1M tokens
        tokenizer_type="tiktoken",
        tokenizer_name="cl100k_base",
    ),  # :contentReference[oaicite:2]{index=2}
    "gpt-4.1": ModelConfig(
        name="gpt-4.1",
        provider=ModelProvider.OPENAI,
        context_length=1000000,
        input_cost_per_token=0.0000074,  # ~26% cheaper than gpt-4o
        output_cost_per_token=0.000029,
        tokenizer_type="tiktoken",
        tokenizer_name="cl100k_base",
    ),  # :contentReference[oaicite:3]{index=3}
    "gpt-4.1-mini": ModelConfig(
        name="gpt-4.1-mini",
        provider=ModelProvider.OPENAI,
        context_length=1000000,
        input_cost_per_token=0.0000074 * 0.5,
        output_cost_per_token=0.000029 * 0.5,
        tokenizer_type="tiktoken",
        tokenizer_name="cl100k_base",
    ),  # szacowane
    "gpt-4.1-nano": ModelConfig(
        name="gpt-4.1-nano",
        provider=ModelProvider.OPENAI,
        context_length=1000000,
        input_cost_per_token=0.0000074 * 0.25,
        output_cost_per_token=0.000029 * 0.25,
        tokenizer_type="tiktoken",
        tokenizer_name="cl100k_base",
    ),  # szacowane

    # --- Anthropic Claude Models ---
    "claude-3-haiku": ModelConfig(
        name="claude-3-haiku",
        provider=ModelProvider.ANTHROPIC,
        context_length=200000,
        input_cost_per_token=0.00000025,
        output_cost_per_token=0.00000125,
        tokenizer_type="estimation",
    ),
    "claude-3-sonnet": ModelConfig(
        name="claude-3-sonnet",
        provider=ModelProvider.ANTHROPIC,
        context_length=200000,
        input_cost_per_token=0.000003,
        output_cost_per_token=0.000015,
        tokenizer_type="estimation",
    ),
    "claude-3-opus": ModelConfig(
        name="claude-3-opus",
        provider=ModelProvider.ANTHROPIC,
        context_length=200000,
        input_cost_per_token=0.000015,
        output_cost_per_token=0.000075,
        tokenizer_type="estimation",
    ),

    "claude-sonnet-4": ModelConfig(
        name="claude-sonnet-4",
        provider=ModelProvider.ANTHROPIC,
        context_length=200000,
        input_cost_per_token=0.000003,
        output_cost_per_token=0.000015,
        tokenizer_type="estimation",
    ),  # :contentReference[oaicite:4]{index=4}
    "claude-opus-4": ModelConfig(
        name="claude-opus-4",
        provider=ModelProvider.ANTHROPIC,
        context_length=200000,
        input_cost_per_token=0.000015,
        output_cost_per_token=0.000075,
        tokenizer_type="estimation",
    ),  # :contentReference[oaicite:5]{index=5}
    "claude-3-7-sonnet": ModelConfig(
        name="claude-3-7-sonnet",
        provider=ModelProvider.ANTHROPIC,
        context_length=200000,
        input_cost_per_token=0.000003,
        output_cost_per_token=0.000015,
        tokenizer_type="estimation",
    ),  # :contentReference[oaicite:6]{index=6}

    # --- Google Gemini Models ---
    "gemini-pro": ModelConfig(
        name="gemini-pro",
        provider=ModelProvider.GOOGLE,
        context_length=30720,
        input_cost_per_token=0.0000005,
        output_cost_per_token=0.0000015,
        tokenizer_type="estimation",
    ),
    "gemini-pro-vision": ModelConfig(
        name="gemini-pro-vision",
        provider=ModelProvider.GOOGLE,
        context_length=30720,
        input_cost_per_token=0.0000005,
        output_cost_per_token=0.0000015,
        tokenizer_type="estimation",
    ),
    "gemini-1.5-pro": ModelConfig(
        name="gemini-1.5-pro",
        provider=ModelProvider.GOOGLE,
        context_length=1048576,
        input_cost_per_token=0.000007,
        output_cost_per_token=0.000021,
        tokenizer_type="estimation",
    ),
    "gemini-1.5-flash": ModelConfig(
        name="gemini-1.5-flash",
        provider=ModelProvider.GOOGLE,
        context_length=1048576,
        input_cost_per_token=0.0000007,
        output_cost_per_token=0.0000021,
        tokenizer_type="estimation",
    ),

    # --- Mistral Models ---
    "mistral-7b": ModelConfig(
        name="mistral-7b",
        provider=ModelProvider.MISTRAL,
        context_length=8192,
        input_cost_per_token=0.00000025,
        output_cost_per_token=0.00000025,
        tokenizer_type="sentencepiece",
    ),
    "mixtral-8x7b": ModelConfig(
        name="mixtral-8x7b",
        provider=ModelProvider.MISTRAL,
        context_length=32768,
        input_cost_per_token=0.0000007,
        output_cost_per_token=0.0000007,
        tokenizer_type="sentencepiece",
    ),

    # --- OpenAI Vision-specific ---
    "gpt-image-1": ModelConfig(
        name="gpt-image-1",
        provider=ModelProvider.OPENAI,
        context_length=8192,
        input_cost_per_token=0.00001,   # $10 per 1M input
        output_cost_per_token=0.00004,  # $40 per 1M output
        tokenizer_type="tiktoken",
        tokenizer_name="cl100k_base",
    ),  # :contentReference[oaicite:7]{index=7}
        # Google Gemini Models (aktualizacja 2025‑06)
    "gemini-2.5-pro": ModelConfig(
        name="gemini-2.5-pro",
        provider=ModelProvider.GOOGLE,
        context_length=1048576,  # 1 000 000 input, 65 536 output :contentReference[oaicite:1]{index=1}
        input_cost_per_token=0.00000125,  # $1.25 per 1M tokens :contentReference[oaicite:2]{index=2}
        output_cost_per_token=0.00001,     # $10 per 1M tokens :contentReference[oaicite:3]{index=3}
        tokenizer_type="estimation",
    ),
    "gemini-2.5-flash": ModelConfig(
        name="gemini-2.5-flash",
        provider=ModelProvider.GOOGLE,
        context_length=1048576,  # 1 000 000 input, 65 536 output :contentReference[oaicite:4]{index=4}
        input_cost_per_token=0.00000030,  # $0.30 per 1M input :contentReference[oaicite:5]{index=5}
        output_cost_per_token=0.00000250, # $2.50 per 1M output :contentReference[oaicite:6]{index=6}
        tokenizer_type="estimation",
    ),
    "gemini-2.5-flash-lite": ModelConfig(
        name="gemini-2.5-flash-lite",
        provider=ModelProvider.GOOGLE,
        context_length=1000000,  # 1 000 000 input, ~64 000 output :contentReference[oaicite:7]{index=7}
        input_cost_per_token=0.00000010,  # $0.10 per 1M input :contentReference[oaicite:8]{index=8}
        output_cost_per_token=0.00000040, # $0.40 per 1M output :contentReference[oaicite:9]{index=9}
        tokenizer_type="estimation",
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
