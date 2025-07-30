"""
DependencyTrack MCP Server Entry Point
"""

from .dtrack_client import main


def main_entry():
    """Entry point for the MCP server."""
    import asyncio
    asyncio.run(main())


if __name__ == "__main__":
    main_entry() 