"""
Central place for all configuration values.

Everything sensitive (like the LLM API key) is read from environment
variables / a local .env file - never hardcoded.
"""

import os

from dotenv import load_dotenv

# Loads variables from a local .env file into os.environ, if one exists.
load_dotenv()

# --- LLM settings -----------------------------------------------------
LLM_API_KEY: str = os.getenv("LLM_API_KEY", "")
LLM_API_BASE: str = os.getenv("LLM_API_BASE", "https://api.openai.com/v1")
LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-4o-mini")
LLM_REQUEST_TIMEOUT: int = int(os.getenv("LLM_REQUEST_TIMEOUT", "20"))

# --- Self-healing settings --------------------------------------------
MAX_HEALING_ATTEMPTS: int = int(os.getenv("MAX_HEALING_ATTEMPTS", "3"))

# --- Playwright settings ------------------------------------------------
HEADLESS: bool = os.getenv("HEADLESS", "true").lower() == "true"
