"""
Environment variable management for CodeFlux.
"""

import os
from dotenv import load_dotenv


load_dotenv()


def get_env(key, default=None):
    """Get environment variable or default value."""
    return os.environ.get(key, default)


def require_env(key):
    """Get a required environment variable or raise an error."""
    value = os.environ.get(key)
    if value is None:
        raise ValueError(f"Required environment variable '{key}' not set")
    return value
