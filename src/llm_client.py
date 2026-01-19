"""DeepSeek LLM client wrapper for PandasAI integration."""

from typing import Any, Dict, List

from openai import OpenAI as OpenAIClient
from pandasai.llm import OpenAI


class DeepSeekClient:
    """Wrapper for DeepSeek API using PandasAI's LLM abstraction.

    This class provides a unified interface for interacting with DeepSeek's
    chat completion API through PandasAI's LLM layer.
    """

    def __init__(
        self,
        api_key: str,
        model: str = "deepseek-chat",
        base_url: str = "https://api.deepseek.com",
        **kwargs: Any,
    ):
        """Initialize the DeepSeek client.

        Args:
            api_key: DeepSeek API key.
            model: Model name (deepseek-chat or deepseek-reasoner).
            base_url: DeepSeek API base URL.
            **kwargs: Additional parameters for OpenAI client.
        """
        self.api_key = api_key
        self.model = model
        self.base_url = base_url
        self._additional_params = kwargs

        # Reason: Keep OpenAI client for direct API calls
        self.client = OpenAIClient(
            api_key=api_key,
            base_url=base_url,
        )

        # Reason: Use PandasAI's OpenAI LLM wrapper with DeepSeek config
        # Initialize with a supported model, then override for DeepSeek
        # Note: PandasAI's OpenAI uses 'api_base' not 'base_url'
        self.llm = OpenAI(
            api_token=api_key,
            api_base=base_url,
            **kwargs,
        )
        # Reason: Override model to use DeepSeek models
        self.llm.model = model

    def get_llm(self) -> OpenAI:
        """Get the PandasAI LLM instance.

        Returns:
            OpenAI: The PandasAI OpenAI LLM instance.
        """
        return self.llm

    def chat(self, messages: List[Dict[str, str]], **kwargs: Any) -> str:
        """Send a chat completion request to DeepSeek API.

        Args:
            messages: List of message dictionaries with 'role' and 'content' keys.
            **kwargs: Additional parameters for the API call.

        Returns:
            str: The assistant's response content.

        Raises:
            Exception: If the API call fails.
        """
        # Reason: Merge additional params with call-specific params
        params = {**self._additional_params, **kwargs}
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            **params,
        )
        return response.choices[0].message.content

    def set_temperature(self, temperature: float) -> None:
        """Set the temperature for generation.

        Args:
            temperature: Sampling temperature (0.0 to 1.0).
        """
        self._additional_params["temperature"] = temperature

    def set_max_retries(self, max_retries: int) -> None:
        """Set the maximum number of retries.

        Args:
            max_retries: Maximum number of retry attempts.
        """
        self._additional_params["max_retries"] = max_retries
