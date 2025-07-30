"""
Tests for TokenCounter functionality.
"""

import pytest
import tempfile
import json
from pathlib import Path

from watchtoken import TokenCounter, TokenLimitExceededError, UnsupportedModelError
from watchtoken.loggers import FileLogger, ConsoleLogger
from watchtoken.models import ModelConfig, ModelProvider, add_model_config


class TestTokenCounter:
    """Test cases for TokenCounter class."""

    def test_basic_token_counting(self):
        """Test basic token counting functionality."""
        tc = TokenCounter("gpt-3.5-turbo")

        # Test simple text
        tokens = tc.count("Hello world!")
        assert tokens > 0
        assert isinstance(tokens, int)

        # Test empty text
        empty_tokens = tc.count("")
        assert empty_tokens == 0

    def test_limit_checking(self):
        """Test token limit functionality."""
        tc = TokenCounter("gpt-3.5-turbo", limit=5)

        short_text = "Hi"
        long_text = "This is a much longer text that should exceed the token limit"

        # Short text should not exceed limit
        assert not tc.is_over(short_text)

        # Long text should exceed limit
        assert tc.is_over(long_text)

    def test_limit_exceeded_callback(self):
        """Test callback functionality when limit is exceeded."""
        callback_called = False
        callback_args = {}

        def on_limit_exceeded(tokens, limit, model):
            nonlocal callback_called, callback_args
            callback_called = True
            callback_args = {"tokens": tokens, "limit": limit, "model": model}

        tc = TokenCounter("gpt-3.5-turbo", limit=1, on_limit_exceeded=on_limit_exceeded)

        # This should trigger the callback
        tc.check_limit("This text is definitely longer than one token")

        assert callback_called
        assert callback_args["tokens"] > callback_args["limit"]
        assert callback_args["model"] == "gpt-3.5-turbo"

    def test_limit_exceeded_exception(self):
        """Test exception raising when limit is exceeded."""
        tc = TokenCounter("gpt-3.5-turbo", limit=1)

        with pytest.raises(TokenLimitExceededError):
            tc.check_limit(
                "This text is definitely longer than one token", raise_on_exceed=True
            )

    def test_cost_estimation(self):
        """Test cost estimation functionality."""
        tc = TokenCounter("gpt-4-turbo")

        cost = tc.estimate_cost("Hello world!", output_tokens=50)

        assert cost > 0
        assert isinstance(cost, float)

        # Cost should increase with more tokens
        higher_cost = tc.estimate_cost("Hello world!", output_tokens=100)
        assert higher_cost > cost

    def test_model_info(self):
        """Test model information retrieval."""
        tc = TokenCounter("gpt-4-turbo")
        info = tc.get_model_info()

        assert info["model"] == "gpt-4-turbo"
        assert info["provider"] == "openai"
        assert info["context_length"] > 0
        assert info["input_cost_per_token"] > 0
        assert info["output_cost_per_token"] > 0

    def test_remaining_tokens(self):
        """Test remaining tokens calculation."""
        tc = TokenCounter("gpt-3.5-turbo", limit=100)

        text = "Hello world!"
        used_tokens = tc.count(text)
        remaining = tc.get_remaining_tokens(text)

        assert remaining == 100 - used_tokens
        assert remaining >= 0

    def test_unsupported_model(self):
        """Test handling of unsupported models."""
        with pytest.raises(UnsupportedModelError):
            TokenCounter("nonexistent-model")

    def test_custom_adapter_registration(self):
        """Test registration of custom adapters."""
        from watchtoken.adapters import BaseAdapter

        class TestAdapter(BaseAdapter):
            def count_tokens(self, text: str) -> int:
                return len(text.split())

            def get_cost_per_token(self):
                return (0.001, 0.002)

        # Register custom model
        add_model_config(
            "test-model",
            ModelConfig(
                name="test-model",
                provider=ModelProvider.CUSTOM,
                context_length=1000,
                input_cost_per_token=0.001,
                output_cost_per_token=0.002,
            ),
        )

        TokenCounter.register_adapter("test-model", TestAdapter)

        # Should work with custom adapter
        tc = TokenCounter("test-model")
        tokens = tc.count("hello world test")
        assert tokens == 3  # Word count

    def test_different_models(self):
        """Test different model providers."""
        models_to_test = [
            "gpt-3.5-turbo",
            "gpt-4-turbo",
            "claude-3-sonnet",
            "gemini-pro",
        ]

        for model in models_to_test:
            tc = TokenCounter(model)
            tokens = tc.count("Hello world!")
            assert tokens > 0

            cost = tc.estimate_cost("Hello world!", output_tokens=10)
            assert cost > 0


class TestFileLogger:
    """Test cases for FileLogger."""

    def test_file_logger_creation(self):
        """Test FileLogger initialization."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as tmp:
            tmp_path = tmp.name

        # Remove the empty file so FileLogger can initialize it properly
        Path(tmp_path).unlink()

        logger = FileLogger(tmp_path)

        # File should be initialized
        assert Path(tmp_path).exists()

        # Should contain proper structure
        with open(tmp_path, "r") as f:
            data = json.load(f)
            assert "token_usage" in data
            assert "cost_estimations" in data

        # Cleanup
        Path(tmp_path).unlink()

    def test_file_logger_token_usage(self):
        """Test logging token usage."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as tmp:
            logger = FileLogger(tmp.name)

            logger.log_token_usage("gpt-4", "Hello world!", 3)

            # Check logged data
            with open(tmp.name, "r") as f:
                data = json.load(f)
                assert len(data["token_usage"]) == 1

                entry = data["token_usage"][0]
                assert entry["model"] == "gpt-4"
                assert entry["prompt"] == "Hello world!"
                assert entry["token_count"] == 3

    def test_file_logger_cost_estimation(self):
        """Test logging cost estimations."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as tmp:
            logger = FileLogger(tmp.name)

            logger.log_cost_estimation("gpt-4", 10, 20, 0.005)

            # Check logged data
            with open(tmp.name, "r") as f:
                data = json.load(f)
                assert len(data["cost_estimations"]) == 1

                entry = data["cost_estimations"][0]
                assert entry["model"] == "gpt-4"
                assert entry["input_tokens"] == 10
                assert entry["output_tokens"] == 20
                assert entry["estimated_cost"] == pytest.approx(0.005)


class TestIntegration:
    """Integration tests."""

    def test_token_counter_with_file_logger(self):
        """Test TokenCounter with FileLogger integration."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as tmp:
            logger = FileLogger(tmp.name)
            tc = TokenCounter("gpt-3.5-turbo", logger=logger, auto_log=True)

            # Count tokens (should auto-log)
            tc.count("Hello world!")

            # Estimate cost (should auto-log)
            tc.estimate_cost("Hello world!", output_tokens=10)

            # Check logs
            with open(tmp.name, "r") as f:
                data = json.load(f)
                assert (
                    len(data["token_usage"]) == 2
                )  # count() and estimate_cost() both call count()
                assert len(data["cost_estimations"]) == 1

    def test_console_logger(self):
        """Test ConsoleLogger (basic functionality)."""
        logger = ConsoleLogger(verbose=False)  # Don't actually print during tests

        # Should not raise any exceptions
        logger.log_token_usage("gpt-4", "Hello", 1)
        logger.log_cost_estimation("gpt-4", 5, 10, 0.001)


if __name__ == "__main__":
    pytest.main([__file__])
