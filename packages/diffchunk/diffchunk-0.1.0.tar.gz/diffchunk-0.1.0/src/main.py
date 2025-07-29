"""Main entry point for diffchunk MCP server."""

import argparse
import asyncio
import sys
from .server import DiffChunkServer


def main():
    """Main entry point for the MCP server."""
    parser = argparse.ArgumentParser(
        description="diffchunk MCP server for navigating large diff files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  diffchunk-mcp                    # Start MCP server
  diffchunk-mcp --help            # Show this help

MCP Client Configuration:
  {
    "mcpServers": {
      "diffchunk": {
        "command": "diffchunk-mcp"
      }
    }
  }
        """,
    )
    parser.add_argument("--version", action="version", version="diffchunk 0.1.0")

    parser.parse_args()

    try:
        server = DiffChunkServer()
        asyncio.run(server.run())
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as e:
        print(f"Error starting diffchunk MCP server: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
