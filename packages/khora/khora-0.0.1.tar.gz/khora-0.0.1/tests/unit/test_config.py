"""Unit tests for configuration management."""

import os
from unittest.mock import patch

from khora.utils.config import load_config


class TestConfig:
    """Tests for configuration loading."""

    @patch.dict(
        os.environ,
        {
            "OPENAI_API_KEY": "test_key",
            "OPENAI_MODEL": "gpt-4",
            "GOOGLE_CREDENTIALS_PATH": "/path/to/creds.json",
            "DAGSTER_HOME": "/custom/dagster",
            "LOG_LEVEL": "DEBUG",
            "CACHE_ENABLED": "false",
            "CACHE_TTL": "7200",
        },
    )
    def test_load_config_from_env(self):
        """Test loading configuration from environment variables."""
        config = load_config()

        assert config["openai_api_key"] == "test_key"
        assert config["openai_model"] == "gpt-4"
        assert config["google_credentials_path"] == "/path/to/creds.json"
        assert config["dagster_home"] == "/custom/dagster"
        assert config["log_level"] == "DEBUG"
        assert config["cache_enabled"] is False
        assert config["cache_ttl"] == 7200

    @patch.dict(os.environ, {}, clear=True)
    def test_load_config_defaults(self):
        """Test loading configuration with defaults."""
        config = load_config()

        assert config.get("openai_api_key") is None
        assert config.get("openai_model") == "gpt-4-turbo-preview"
        assert config.get("dagster_home") == "/tmp/dagster"
        assert config.get("log_level") == "INFO"
        assert config.get("cache_enabled") is True
        assert config.get("cache_ttl") == 3600

    def test_google_scopes_always_included(self):
        """Test that Google scopes are always included."""
        config = load_config()

        assert "google_scopes" in config
        assert len(config["google_scopes"]) == 3
        assert (
            "https://www.googleapis.com/auth/documents.readonly"
            in config["google_scopes"]
        )
        assert (
            "https://www.googleapis.com/auth/spreadsheets.readonly"
            in config["google_scopes"]
        )
        assert (
            "https://www.googleapis.com/auth/drive.readonly" in config["google_scopes"]
        )
