#!/usr/bin/env python3
"""
SVCS MCP Server entry point.
"""

import asyncio
import sys
from pathlib import Path

# Add the parent directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp_server import main


def server_main():
    """Entry point for svcs-mcp-server command."""
    asyncio.run(main())


if __name__ == "__main__":
    server_main()
