"""Configuration management for the application."""

from typing import Optional

from dotenv import load_dotenv
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class AppConfig(BaseSettings):
    """Application configuration loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # DeepSeek API Configuration
    deepseek_api_key: str = Field(default="", description="DeepSeek API key")
    deepseek_model: str = Field(
        default="deepseek-chat",
        description="DeepSeek model name (deepseek-chat or deepseek-reasoner)",
    )
    deepseek_base_url: str = Field(
        default="https://api.deepseek.com",
        description="DeepSeek API base URL",
    )

    # Application Settings
    app_title: str = Field(
        default="PandasAI TXT2SQL",
        description="Application title",
    )
    app_log_level: str = Field(
        default="INFO",
        description="Application log level",
    )

    @field_validator("app_log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level is one of the allowed values."""
        allowed_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if v.upper() not in allowed_levels:
            raise ValueError(f"log_level must be one of {allowed_levels}")
        return v.upper()

    @field_validator("deepseek_model")
    @classmethod
    def validate_model(cls, v: str) -> str:
        """Validate DeepSeek model name."""
        allowed_models = {"deepseek-chat", "deepseek-reasoner"}
        if v not in allowed_models:
            raise ValueError(
                f"deepseek_model must be one of {allowed_models}"
            )
        return v


# Global configuration instance
_config: Optional[AppConfig] = None


def get_config() -> AppConfig:
    """Get the global configuration instance.

    Returns:
        AppConfig: The application configuration.

    Raises:
        ValueError: If required environment variables are not set.
    """
    global _config
    if _config is None:
        _config = AppConfig()
    return _config


def reload_config() -> AppConfig:
    """Reload configuration from environment variables.

    Returns:
        AppConfig: The newly loaded configuration.
    """
    global _config
    load_dotenv(override=True)
    _config = AppConfig()
    return _config
