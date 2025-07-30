"""
Logging utilities for token usage and costs.
"""

import json
import datetime
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from pathlib import Path


class BaseLogger(ABC):
    """Abstract base class for loggers."""

    @abstractmethod
    def log_token_usage(
        self,
        model: str,
        prompt: str,
        token_count: int,
        timestamp: Optional[datetime.datetime] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Log token usage."""
        pass

    @abstractmethod
    def log_cost_estimation(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
        estimated_cost: float,
        timestamp: Optional[datetime.datetime] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Log cost estimation."""
        pass


class ConsoleLogger(BaseLogger):
    """Logger that outputs to console."""

    def __init__(self, verbose: bool = True) -> None:
        self.verbose = verbose

    def log_token_usage(
        self,
        model: str,
        prompt: str,
        token_count: int,
        timestamp: Optional[datetime.datetime] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Log token usage to console."""
        if not self.verbose:
            return

        ts = timestamp or datetime.datetime.now()
        prompt_preview = prompt[:50] + "..." if len(prompt) > 50 else prompt
        print(f"[{ts.isoformat()}] {model}: {token_count} tokens - '{prompt_preview}'")

    def log_cost_estimation(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
        estimated_cost: float,
        timestamp: Optional[datetime.datetime] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Log cost estimation to console."""
        if not self.verbose:
            return

        ts = timestamp or datetime.datetime.now()
        total_tokens = input_tokens + output_tokens
        print(
            f"[{ts.isoformat()}] {model}: ${estimated_cost:.6f} "
            f"({total_tokens} tokens: {input_tokens} in + {output_tokens} out)"
        )


class FileLogger(BaseLogger):
    """Logger that outputs to JSON file."""

    def __init__(self, filepath: str, append: bool = True) -> None:
        self.filepath = Path(filepath)
        self.append = append

        # Create directory if it doesn't exist
        self.filepath.parent.mkdir(parents=True, exist_ok=True)

        # Initialize file if it doesn't exist or not appending
        if not self.filepath.exists() or not append:
            self._initialize_file()

    def _initialize_file(self) -> None:
        """Initialize the log file with empty structure."""
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump({"token_usage": [], "cost_estimations": []}, f, indent=2)

    def _read_log_data(self) -> Dict[str, list]:
        """Read existing log data."""
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {"token_usage": [], "cost_estimations": []}

    def _write_log_data(self, data: Dict[str, list]) -> None:
        """Write log data to file."""
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str)

    def log_token_usage(
        self,
        model: str,
        prompt: str,
        token_count: int,
        timestamp: Optional[datetime.datetime] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Log token usage to file."""
        data = self._read_log_data()

        log_entry = {
            "timestamp": (timestamp or datetime.datetime.now()).isoformat(),
            "model": model,
            "prompt": prompt,
            "token_count": token_count,
            "metadata": metadata or {},
        }

        data["token_usage"].append(log_entry)
        self._write_log_data(data)

    def log_cost_estimation(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
        estimated_cost: float,
        timestamp: Optional[datetime.datetime] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Log cost estimation to file."""
        data = self._read_log_data()

        log_entry = {
            "timestamp": (timestamp or datetime.datetime.now()).isoformat(),
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens,
            "estimated_cost": estimated_cost,
            "metadata": metadata or {},
        }

        data["cost_estimations"].append(log_entry)
        self._write_log_data(data)


class MultiLogger(BaseLogger):
    """Logger that delegates to multiple other loggers."""

    def __init__(self, loggers: list[BaseLogger]) -> None:
        self.loggers = loggers

    def log_token_usage(
        self,
        model: str,
        prompt: str,
        token_count: int,
        timestamp: Optional[datetime.datetime] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Log token usage to all loggers."""
        for logger in self.loggers:
            logger.log_token_usage(model, prompt, token_count, timestamp, metadata)

    def log_cost_estimation(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
        estimated_cost: float,
        timestamp: Optional[datetime.datetime] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Log cost estimation to all loggers."""
        for logger in self.loggers:
            logger.log_cost_estimation(
                model, input_tokens, output_tokens, estimated_cost, timestamp, metadata
            )
