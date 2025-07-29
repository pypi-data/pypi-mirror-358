"""Main entry point for hanzo-mcp when run as a module."""

import warnings

# Suppress ALL Pydantic deprecation warnings before any imports
warnings.filterwarnings(
    "ignore", 
    category=DeprecationWarning,
    module="pydantic.*"
)

# Also try to catch the specific message pattern
warnings.filterwarnings(
    "ignore",
    message=".*class-based.*config.*deprecated.*"
)

# Import cli after setting up warnings
from hanzo_mcp.cli import main

if __name__ == "__main__":
    main()