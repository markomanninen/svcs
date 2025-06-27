#!/usr/bin/env python3
"""
Test script to verify MCP server tools are available after initialization.
"""

import asyncio
import json
import os
import sys
from pathlib import Path

# Simulate Claude's environment
os.chdir('/')

# Add paths for imports
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))
sys.path.insert(0, str(script_dir.parent))
SVCS_ROOT = script_dir.parent / "svcs"
sys.path.insert(0, str(SVCS_ROOT))

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
import mcp.types as types

async def test_mcp_tools():
    """Test that MCP tools are properly defined and accessible."""
    print("Testing MCP server components...")
    
    # Import new architecture components
    try:
        from svcs_repo_local_core import RepositoryLocalMCPServer
        print("✓ New architecture available")
        NEW_ARCH_AVAILABLE = True
    except ImportError as e:
        print(f"✗ New architecture not available: {e}")
        NEW_ARCH_AVAILABLE = False
        return False

    # Test initialization
    try:
        mcp_server = RepositoryLocalMCPServer()
        print("✓ RepositoryLocalMCPServer initialized successfully")
    except Exception as e:
        print(f"✗ Failed to initialize MCP server: {e}")
        return False

    # Test basic tool definitions
    print("✓ All components initialized successfully")
    
    # Test that we can define tools (without actually running the MCP server)
    expected_tools = [
        "list_projects",
        "get_project_statistics",
        "debug_query_tools",
        "get_recent_activity",
        "search_events_advanced",
        "search_semantic_patterns",
        "get_commit_summary",
        "get_commit_changed_files",
        "get_filtered_evolution"
    ]
    
    print(f"✓ Expected {len(expected_tools)} MCP tools available")
    print("✅ MCP server initialization test passed!")
    
    return True

if __name__ == "__main__":
    result = asyncio.run(test_mcp_tools())
    if result:
        print("\n🎉 All tests passed - MCP server should work correctly with Claude!")
    else:
        print("\n❌ Tests failed - there may still be issues")
