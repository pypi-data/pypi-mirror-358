#!/usr/bin/env python
"""Entry point that suppresses warnings before importing anything."""

def main():
    # Nuclear option - override warnings.warn before ANY imports
    import warnings
    import os
    import sys
    
    # Store original
    _original_warn = warnings.warn
    
    # Override with filter
    def filtered_warn(message, category=None, stacklevel=1):
        # Skip Pydantic deprecation warnings
        if (category == DeprecationWarning and 
            ("class-based `config`" in str(message) or 
             "PydanticDeprecatedSince20" in str(message))):
            return
        _original_warn(message, category, stacklevel)
    
    # Replace globally
    warnings.warn = filtered_warn
    
    # Also set environment
    os.environ["PYTHONWARNINGS"] = "ignore::DeprecationWarning"
    
    # Now import the CLI
    from hanzo_mcp.cli import main as cli_main
    cli_main()

if __name__ == "__main__":
    main()