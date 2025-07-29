"""
Main entry point for the Screeny MCP server.

This allows the server to be run as:
- python -m screeny
- uv run screeny (via pyproject.toml script)
"""

from screeny import main

if __name__ == "__main__":
    main()
