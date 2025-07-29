"""Hanzo MCP - Implementation of Hanzo capabilities using MCP."""

import warnings

# Aggressively suppress ALL deprecation warnings from pydantic before any imports
warnings.filterwarnings("ignore", category=DeprecationWarning, module="pydantic.*")
warnings.filterwarnings("ignore", category=DeprecationWarning, module="pydantic._internal.*")
warnings.filterwarnings("ignore", category=DeprecationWarning, module="litellm.*")

# Also catch specific patterns
warnings.filterwarnings("ignore", message=".*class-based.*config.*deprecated.*")
warnings.filterwarnings("ignore", message=".*PydanticDeprecatedSince20.*")

__version__ = "0.6.8"
