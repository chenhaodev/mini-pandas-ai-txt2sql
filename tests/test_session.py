"""Unit tests for session state management module."""

from unittest.mock import MagicMock, patch

import pytest


class TestInitSessionState:
    """Tests for init_session_state function."""

    def test_initializes_all_keys(self):
        """Test that all session state keys are initialized."""
        mock_session_state = {}

        with patch("streamlit.session_state", mock_session_state):
            from src.utils.session import init_session_state

            init_session_state()

            assert "messages" in mock_session_state
            assert "uploaded_files" in mock_session_state
            assert "api_key" in mock_session_state
            assert "model" in mock_session_state

    def test_default_values(self):
        """Test default values are set correctly."""
        mock_session_state = {}

        with patch("streamlit.session_state", mock_session_state):
            from src.utils.session import init_session_state

            init_session_state()

            assert mock_session_state["messages"] == []
            assert mock_session_state["uploaded_files"] == []
            assert mock_session_state["api_key"] == ""
            assert mock_session_state["model"] == "deepseek-chat"

    def test_does_not_overwrite_existing_values(self):
        """Test that existing session state values are not overwritten."""
        mock_session_state = {
            "messages": [{"role": "user", "content": "Hello"}],
            "api_key": "existing-key",
        }

        with patch("streamlit.session_state", mock_session_state):
            from src.utils.session import init_session_state

            init_session_state()

            # Existing values should be preserved
            assert len(mock_session_state["messages"]) == 1
            assert mock_session_state["api_key"] == "existing-key"
            # New keys should be added
            assert "uploaded_files" in mock_session_state
            assert "model" in mock_session_state


class TestMessageFunctions:
    """Tests for message-related functions."""

    def test_add_message_basic(self):
        """Test adding a basic message."""
        mock_session_state = {"messages": []}

        with patch("streamlit.session_state", mock_session_state):
            from src.utils.session import add_message

            add_message("user", "Hello, world!")

            assert len(mock_session_state["messages"]) == 1
            msg = mock_session_state["messages"][0]
            assert msg["role"] == "user"
            assert msg["content"] == "Hello, world!"
            assert msg["type"] == "text"

    def test_add_message_with_type(self):
        """Test adding a message with specific type."""
        mock_session_state = {"messages": []}

        with patch("streamlit.session_state", mock_session_state):
            from src.utils.session import add_message

            add_message("assistant", "Error occurred", type_="error")

            msg = mock_session_state["messages"][0]
            assert msg["type"] == "error"

    def test_add_message_with_dataframe_type(self):
        """Test adding a message with dataframe type."""
        import pandas as pd

        mock_session_state = {"messages": []}
        df = pd.DataFrame({"a": [1, 2, 3]})

        with patch("streamlit.session_state", mock_session_state):
            from src.utils.session import add_message

            add_message("assistant", df, type_="dataframe")

            msg = mock_session_state["messages"][0]
            assert msg["type"] == "dataframe"
            assert isinstance(msg["content"], pd.DataFrame)

    def test_get_chat_history_empty(self):
        """Test getting empty chat history."""
        mock_session_state = {"messages": []}

        with patch("streamlit.session_state", mock_session_state):
            from src.utils.session import get_chat_history

            history = get_chat_history()

            assert history == []

    def test_get_chat_history_with_messages(self):
        """Test getting chat history with messages."""
        mock_session_state = {
            "messages": [
                {"role": "user", "content": "Hello", "type": "text"},
                {"role": "assistant", "content": "Hi!", "type": "text"},
            ]
        }

        with patch("streamlit.session_state", mock_session_state):
            from src.utils.session import get_chat_history

            history = get_chat_history()

            assert len(history) == 2
            assert history[0]["role"] == "user"
            assert history[1]["role"] == "assistant"

    def test_clear_chat_history(self):
        """Test clearing chat history."""
        mock_session_state = {
            "messages": [
                {"role": "user", "content": "Hello", "type": "text"},
                {"role": "assistant", "content": "Hi!", "type": "text"},
            ]
        }

        with patch("streamlit.session_state", mock_session_state):
            from src.utils.session import clear_chat_history

            clear_chat_history()

            assert mock_session_state["messages"] == []


class TestUploadedFilesFunctions:
    """Tests for uploaded files management functions."""

    def test_set_uploaded_files(self):
        """Test setting uploaded files."""
        mock_session_state = {"uploaded_files": []}
        mock_files = [MagicMock(name="file1.xlsx"), MagicMock(name="file2.xlsx")]

        with patch("streamlit.session_state", mock_session_state):
            from src.utils.session import set_uploaded_files

            set_uploaded_files(mock_files)

            assert len(mock_session_state["uploaded_files"]) == 2

    def test_set_uploaded_files_empty_list(self):
        """Test setting empty list of files."""
        mock_session_state = {"uploaded_files": [MagicMock()]}

        with patch("streamlit.session_state", mock_session_state):
            from src.utils.session import set_uploaded_files

            set_uploaded_files([])

            assert mock_session_state["uploaded_files"] == []

    def test_get_uploaded_files_empty(self):
        """Test getting empty uploaded files list."""
        mock_session_state = {"uploaded_files": []}

        with patch("streamlit.session_state", mock_session_state):
            from src.utils.session import get_uploaded_files

            files = get_uploaded_files()

            assert files == []

    def test_get_uploaded_files_with_files(self):
        """Test getting uploaded files."""
        mock_files = [MagicMock(name="file1.xlsx")]
        mock_session_state = {"uploaded_files": mock_files}

        with patch("streamlit.session_state", mock_session_state):
            from src.utils.session import get_uploaded_files

            files = get_uploaded_files()

            assert len(files) == 1


class TestApiKeyFunctions:
    """Tests for API key management functions."""

    def test_set_api_key(self):
        """Test setting API key."""
        mock_session_state = {"api_key": ""}

        with patch("streamlit.session_state", mock_session_state):
            from src.utils.session import set_api_key

            set_api_key("test-api-key-123")

            assert mock_session_state["api_key"] == "test-api-key-123"

    def test_set_api_key_overwrites_existing(self):
        """Test setting API key overwrites existing value."""
        mock_session_state = {"api_key": "old-key"}

        with patch("streamlit.session_state", mock_session_state):
            from src.utils.session import set_api_key

            set_api_key("new-key")

            assert mock_session_state["api_key"] == "new-key"

    def test_get_api_key_returns_value(self):
        """Test getting API key returns the stored value."""
        mock_session_state = {"api_key": "stored-api-key"}

        with patch("streamlit.session_state", mock_session_state):
            from src.utils.session import get_api_key

            key = get_api_key()

            assert key == "stored-api-key"

    def test_get_api_key_returns_none_when_empty(self):
        """Test getting API key returns None when empty string."""
        mock_session_state = {"api_key": ""}

        with patch("streamlit.session_state", mock_session_state):
            from src.utils.session import get_api_key

            key = get_api_key()

            assert key is None

    def test_get_api_key_returns_none_when_missing(self):
        """Test getting API key returns None when key is missing."""
        mock_session_state = {}

        with patch("streamlit.session_state", mock_session_state):
            from src.utils.session import get_api_key

            key = get_api_key()

            assert key is None


class TestModelFunctions:
    """Tests for model management functions."""

    def test_set_model(self):
        """Test setting model."""
        mock_session_state = {"model": "deepseek-chat"}

        with patch("streamlit.session_state", mock_session_state):
            from src.utils.session import set_model

            set_model("deepseek-reasoner")

            assert mock_session_state["model"] == "deepseek-reasoner"

    def test_get_model_returns_value(self):
        """Test getting model returns the stored value."""
        mock_session_state = {"model": "deepseek-reasoner"}

        with patch("streamlit.session_state", mock_session_state):
            from src.utils.session import get_model

            model = get_model()

            assert model == "deepseek-reasoner"

    def test_get_model_returns_default_when_missing(self):
        """Test getting model returns default when key is missing."""
        mock_session_state = {}

        with patch("streamlit.session_state", mock_session_state):
            from src.utils.session import get_model

            model = get_model()

            assert model == "deepseek-chat"


class TestUtilsExports:
    """Tests for utils module exports."""

    def test_all_functions_are_exported(self):
        """Test that all expected functions are exported from utils."""
        from src.utils import (
            init_session_state,
            add_message,
            get_chat_history,
            clear_chat_history,
            set_uploaded_files,
            get_uploaded_files,
            set_api_key,
            get_api_key,
            set_model,
            get_model,
        )

        # All imports should succeed - just verify they are callable
        assert callable(init_session_state)
        assert callable(add_message)
        assert callable(get_chat_history)
        assert callable(clear_chat_history)
        assert callable(set_uploaded_files)
        assert callable(get_uploaded_files)
        assert callable(set_api_key)
        assert callable(get_api_key)
        assert callable(set_model)
        assert callable(get_model)
