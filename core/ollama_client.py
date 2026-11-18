import json
import re
import subprocess
from typing import Optional

import requests

from config import (
    OLLAMA_BASE_URL,
    OLLAMA_MODELS_FILE,
    MODEL_FILTER_KEYWORDS,
)

# Ollama names look like "llama3.2", "llama3.2:1b" or "hf.co/user/repo:Q4_K_M".
# Must not start with "-", so user input can never be read as a CLI option.
_MODEL_NAME_PATTERN = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:/-]{0,199}")


class OllamaClient:
    """Client for interacting with the Ollama API."""

    def __init__(self, base_url: str = None):
        """
        Initialize OllamaClient.

        Args:
            base_url: Optional custom base URL for Ollama API
        """
        self.base_url = base_url or OLLAMA_BASE_URL
        self.api_tags = f"{self.base_url}/api/tags"

    def is_running(self) -> bool:
        """Check if Ollama API is running and accessible."""
        try:
            response = requests.get(self.api_tags, timeout=5)
            return response.status_code == 200
        except requests.RequestException:
            return False

    def get_available_models(self) -> list[str]:
        """
        Retrieve available models from Ollama API.

        Returns:
            List of available model names, filtered by keywords
        """
        try:
            response = requests.get(self.api_tags, timeout=10)
            if response.status_code == 200:
                models = response.json()
                return [
                    model["name"]
                    for model in models.get("models", [])
                    if not any(
                        keyword in model["name"].lower()
                        for keyword in MODEL_FILTER_KEYWORDS
                    )
                ]
            return []
        except (requests.RequestException, ValueError, KeyError, TypeError, AttributeError):
            return []  # Ollama down, or something else answering on its port

    def get_model_info(self, model_name: str) -> Optional[str]:
        """
        Get detailed information about a specific model.

        Returns:
            Formatted string with model information or None on error
        """
        try:
            result = subprocess.run(
                ["ollama", "show", model_name],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode != 0 or not result.stdout:
                return self._format_unavailable_info(model_name)

            return self._parse_model_info(result.stdout)

        except subprocess.TimeoutExpired:
            return self._format_unavailable_info(model_name)
        except Exception:
            return None

    def pull_model(self, model_name: str) -> tuple[bool, str]:
        """
        Download a model from Ollama.

        Returns:
            Tuple of (success: bool, message: str)
        """
        if not _MODEL_NAME_PATTERN.fullmatch(model_name):
            return False, f"Invalid model name: {model_name!r}"

        try:
            process = subprocess.run(
                ["ollama", "pull", model_name],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )

            if process.returncode == 0:
                return True, f"Successfully installed {model_name}"
            else:
                return False, f"Error pulling {model_name}: {process.stderr}"

        except Exception as e:
            return False, f"Error downloading {model_name}: {str(e)}"

    def _parse_model_info(self, raw_info: str) -> str:
        """Parse raw model info into formatted display string."""

        def get_value(key: str) -> str:
            try:
                return raw_info.split(key)[1].split("\n")[0].strip()
            except (IndexError, AttributeError):
                return "N/A"

        display_lines = [
            "",
            "📱 Model Architecture",
            "-------------------",
            f"• Architecture: {get_value('architecture')}",
            f"• Parameters: {get_value('parameters')}",
            f"• Quantization: {get_value('quantization')}",
            "",
            "🔄 Context Settings",
            "----------------",
            f"• Context Length: {get_value('context length')}",
            f"• Embedding Length: {get_value('embedding length')}",
            "",
        ]

        return "\n".join(display_lines)

    def _format_unavailable_info(self, model_name: str) -> str:
        """Format message for unavailable model info."""
        return "\n".join([
            "",
            "⚠️ Model Information Unavailable",
            "-------------------------",
            "Unable to fetch model details. The model might be:",
            "• Still downloading",
            "• Partially downloaded",
            "• Not properly installed",
            "",
            f"You can try: 'ollama show {model_name}' in terminal for more details.",
        ])


class ModelLibrary:
    """Manages the static model library data."""

    _cache: Optional[dict] = None

    @classmethod
    def load(cls) -> dict:
        """Load model library from JSON file."""
        if cls._cache is None:
            try:
                with open(OLLAMA_MODELS_FILE, "r") as f:
                    cls._cache = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                cls._cache = {}
        return cls._cache

    @classmethod
    def get_dataframe_data(cls) -> list[dict]:
        """Get model data formatted for DataFrame creation."""
        models = cls.load()
        return [
            {
                "Model Name": name,
                "Description": info.get("description", ""),
                "Parameter Sizes": info.get("params", ""),
            }
            for name, info in models.items()
        ]


# Module-level convenience instance
ollama_client = OllamaClient()


def get_ollama_models() -> list[str]:
    """Convenience function to get available Ollama models."""
    return ollama_client.get_available_models()


def get_model_info(model_name: str) -> Optional[str]:
    """Convenience function to get model information."""
    return ollama_client.get_model_info(model_name)