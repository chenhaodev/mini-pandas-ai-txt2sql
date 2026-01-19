"""Unit tests for LLM client module."""

from unittest.mock import MagicMock, patch

import pytest

from src.llm_client import DeepSeekClient


class TestDeepSeekClient:
    """Tests for DeepSeekClient class."""

    def test_initialization(self):
        """Test client initialization."""
        client = DeepSeekClient(
            api_key="test-key",
            model="deepseek-chat",
            base_url="https://api.deepseek.com",
        )

        assert client.api_key == "test-key"
        assert client.model == "deepseek-chat"
        assert client.base_url == "https://api.deepseek.com"

    def test_initialization_with_defaults(self):
        """Test client initialization with default values."""
        client = DeepSeekClient(api_key="test-key")

        assert client.model == "deepseek-chat"
        assert client.base_url == "https://api.deepseek.com"

    def test_get_llm_returns_pandasai_instance(self):
        """Test get_llm returns PandasAI LLM instance."""
        client = DeepSeekClient(api_key="test-key")
        llm = client.get_llm()

        assert llm is not None
        # Reason: Check that it has expected PandasAI OpenAI attributes
        assert hasattr(llm, "api_token")

    def test_set_temperature(self):
        """Test setting temperature parameter."""
        client = DeepSeekClient(api_key="test-key")
        client.set_temperature(0.7)

        assert client._additional_params["temperature"] == 0.7

    def test_set_max_retries(self):
        """Test setting max_retries parameter."""
        client = DeepSeekClient(api_key="test-key")
        client.set_max_retries(5)

        assert client._additional_params["max_retries"] == 5

    def test_chat_method_returns_response(self):
        """Test chat method returns correct response format."""
        # Reason: Mock OpenAI client
        with patch("src.llm_client.OpenAIClient") as mock_openai:
            mock_client = MagicMock()
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = "Test response"
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai.return_value = mock_client

            client = DeepSeekClient(api_key="test-key")
            result = client.chat([{"role": "user", "content": "Hello"}])

            assert result == "Test response"
            mock_client.chat.completions.create.assert_called_once()

    def test_chat_method_with_additional_params(self):
        """Test chat method with additional parameters."""
        with patch("src.llm_client.OpenAIClient") as mock_openai:
            mock_client = MagicMock()
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = "Response"
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai.return_value = mock_client

            client = DeepSeekClient(
                api_key="test-key",
                temperature=0.5,
                max_tokens=100,
            )

            client.chat([{"role": "user", "content": "Test"}])

            # Reason: Verify temperature and max_tokens are passed
            call_kwargs = mock_client.chat.completions.create.call_args.kwargs
            assert call_kwargs.get("temperature") == 0.5
            assert call_kwargs.get("max_tokens") == 100

    def test_chat_method_propagates_exception(self):
        """Test chat method propagates API exceptions."""
        with patch("src.llm_client.OpenAIClient") as mock_openai:
            mock_client = MagicMock()
            mock_client.chat.completions.create.side_effect = Exception("API Error")
            mock_openai.return_value = mock_client

            client = DeepSeekClient(api_key="test-key")

            with pytest.raises(Exception, match="API Error"):
                client.chat([{"role": "user", "content": "Test"}])
