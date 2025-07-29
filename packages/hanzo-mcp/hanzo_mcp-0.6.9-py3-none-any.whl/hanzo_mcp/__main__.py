"""Main entry point for hanzo-mcp when run as a module."""

# MUST suppress warnings BEFORE any imports
import warnings
import os

# Set environment variable for child processes
os.environ["PYTHONWARNINGS"] = "ignore::DeprecationWarning"

# Suppress all deprecation warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Now we can import
from hanzo_mcp.cli import main

if __name__ == "__main__":
    main()