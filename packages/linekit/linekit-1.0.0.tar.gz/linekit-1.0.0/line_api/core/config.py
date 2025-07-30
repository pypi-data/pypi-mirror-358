"""Configuration management for LINE API integration."""

from __future__ import annotations

from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from .exceptions import LineConfigError


class LineAPIConfig(BaseSettings):
    """Configuration for LINE API integration."""

    model_config = SettingsConfigDict(
        env_prefix="",  # No prefix, use direct environment variable names
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Required LINE Bot configuration
    channel_access_token: str = Field(
        ...,
        alias="LINE_CHANNEL_ACCESS_TOKEN",
        description="LINE Channel Access Token for Messaging API",
        min_length=1,
    )
    channel_secret: str = Field(
        ...,
        alias="LINE_CHANNEL_SECRET",
        description="LINE Channel Secret for webhook verification",
        min_length=1,
    )

    # Optional LINE Login configuration
    login_channel_id: str | None = Field(
        None,
        description="LINE Login Channel ID",
    )
    login_channel_secret: str | None = Field(
        None,
        description="LINE Login Channel Secret",
    )

    # Optional LIFF configuration
    liff_channel_id: str | None = Field(
        None,
        description="LIFF Channel ID",
    )

    # API configuration
    api_base_url: str = Field(
        "https://api.line.me/v2/bot",
        description="LINE API base URL",
    )
    timeout: float = Field(
        30.0,
        description="Request timeout in seconds",
        gt=0,
    )
    max_retries: int = Field(
        3,
        description="Maximum number of retries for failed requests",
        ge=0,
    )
    retry_delay: float = Field(
        1.0,
        description="Initial delay between retries in seconds",
        gt=0,
    )

    # Development configuration
    debug: bool = Field(
        False,
        description="Enable debug mode",
    )

    @field_validator("channel_access_token")
    @classmethod
    def validate_channel_access_token(cls, v: str) -> str:
        """Validate channel access token format."""
        if not v.strip():
            msg = "Channel access token cannot be empty"
            raise LineConfigError(msg)
        return v.strip()

    @field_validator("channel_secret")
    @classmethod
    def validate_channel_secret(cls, v: str) -> str:
        """Validate channel secret format."""
        if not v.strip():
            msg = "Channel secret cannot be empty"
            raise LineConfigError(msg)
        return v.strip()

    @classmethod
    def from_env_file(cls, env_file: str | Path | None = None) -> LineAPIConfig:
        """
        Create configuration from environment file.

        Args:
            env_file: Path to environment file. If None, will search for .env file.

        Returns:
            LineAPIConfig instance

        Raises:
            LineConfigError: If configuration is invalid

        """
        try:
            if env_file is None:
                # Search for .env file in current directory and parent directories
                current_dir = Path.cwd()
                for path in [current_dir, *current_dir.parents]:
                    env_path = path / ".env"
                    if env_path.exists():
                        env_file = env_path
                        break

            # Create a new settings instance with the found env file
            config_dict = {}
            if env_file:
                config_dict["env_file"] = str(env_file)

            return cls.model_validate({}, strict=False)
        except Exception as e:
            msg = f"Failed to load configuration: {e}"
            raise LineConfigError(msg) from e

    def get_auth_headers(self) -> dict[str, str]:
        """
        Get authorization headers for LINE API requests.

        Returns:
            Dictionary with authorization headers

        """
        return {
            "Authorization": f"Bearer {self.channel_access_token}",
            "Content-Type": "application/json",
        }

    def is_valid(self) -> bool:
        """
        Check if the configuration is valid.

        Returns:
            True if configuration is valid

        """
        try:
            return bool(self.channel_access_token and self.channel_secret)
        except Exception:
            return False

    def __repr__(self) -> str:
        """Return string representation of the config."""
        return (
            f"LineAPIConfig("
            f"debug={self.debug}, "
            f"timeout={self.timeout}, "
            f"max_retries={self.max_retries})"
        )


def load_config(env_file: str | Path | None = None) -> LineAPIConfig:
    """
    Load LINE API configuration from environment.

    Args:
        env_file: Optional path to environment file

    Returns:
        LineAPIConfig instance

    Raises:
        LineConfigError: If configuration cannot be loaded

    """
    return LineAPIConfig.from_env_file(env_file)
