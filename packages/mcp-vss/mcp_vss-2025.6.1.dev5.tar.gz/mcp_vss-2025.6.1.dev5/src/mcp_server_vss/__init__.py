"""Main package module for the MCP server."""
import asyncio

from . import server


def main():
    """Run main entry point for the package."""
    asyncio.run(server.main())


__version__ = '2025.6.1-dev5'
# Optionally expose other important items at package level
__all__ = ["main", "server", "__version__"]
