"""Configuration management for Khora."""

import os
from pathlib import Path
from typing import Any, Dict, Optional

from dotenv import load_dotenv


def load_config(config_path: Optional[Path] = None) -> Dict[str, Any]:
    """
    Load configuration from environment variables and optional config file.

    Args:
        config_path: Optional path to configuration file

    Returns:
        Configuration dictionary
    """
    # Load environment variables
    load_dotenv()

    config = {
        # OpenAI Configuration
        "openai_api_key": os.getenv("OPENAI_API_KEY"),
        "openai_model": os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview"),
        # Google Configuration
        "google_credentials_path": os.getenv("GOOGLE_CREDENTIALS_PATH"),
        "google_scopes": [
            "https://www.googleapis.com/auth/documents.readonly",
            "https://www.googleapis.com/auth/spreadsheets.readonly",
            "https://www.googleapis.com/auth/drive.readonly",
        ],
        # Dagster Configuration
        "dagster_home": os.getenv("DAGSTER_HOME", "/tmp/dagster"),
        "dagster_storage": {
            "postgres": {
                "postgres_db": os.getenv("DAGSTER_PG_DB", "dagster"),
                "postgres_host": os.getenv("DAGSTER_PG_HOST", "localhost"),
                "postgres_port": int(os.getenv("DAGSTER_PG_PORT", "5432")),
                "postgres_user": os.getenv("DAGSTER_PG_USER", "dagster"),
                "postgres_password": os.getenv("DAGSTER_PG_PASSWORD", ""),
            }
        },
        # General Configuration
        "log_level": os.getenv("LOG_LEVEL", "INFO"),
        "cache_enabled": os.getenv("CACHE_ENABLED", "true").lower() == "true",
        "cache_ttl": int(os.getenv("CACHE_TTL", "3600")),
    }

    # Remove None values
    config = {k: v for k, v in config.items() if v is not None}

    return config
