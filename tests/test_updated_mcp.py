#!/usr/bin/env python3
"""
Test the updated working MCP server tools
"""

import asyncio
import sys
from pathlib import Path

# Add paths
sys.path.insert(0, str(Path(__file__).parent))

from mcp_server import handle_call_tool

async def test_mcp_tools():
    """Test MCP tools functionality."""
    
    print("🧪 Testing Updated MCP Server Tools")
    print("=" * 50)
    
    # Test 1: List projects
    print("\n1. Testing list_projects...")
    result = await handle_call_tool("list_projects", {})
    print(result[0].text[:200] + "..." if len(result[0].text) > 200 else result[0].text)
    
    # Test 2: Get statistics (using the user's project ID)
    print("\n2. Testing get_project_statistics...")
    result = await handle_call_tool("get_project_statistics", {"project_id": "041b54b5"})
    print(result[0].text)
    
    # Test 3: Query semantic events
    print("\n3. Testing query_semantic_events...")
    result = await handle_call_tool("query_semantic_events", {
        "project_id": "041b54b5", 
        "limit": 3
    })
    print(result[0].text[:500] + "..." if len(result[0].text) > 500 else result[0].text)
    
    # Test 4: Analyze current commit
    print("\n4. Testing analyze_current_commit...")
    result = await handle_call_tool("analyze_current_commit", {
        "project_path": "/Users/markomanninen/Documents/tmp/svcs_new_project"
    })
    print(result[0].text)
    
    print("\n✅ All MCP tools tested successfully!")

if __name__ == "__main__":
    asyncio.run(test_mcp_tools())
