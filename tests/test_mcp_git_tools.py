#!/usr/bin/env python3
"""
Test the new MCP tools for git integration.
"""

import os
import sys
import asyncio
from pathlib import Path

# Add paths for imports
svcs_root = Path(__file__).parent.parent  # Go up from tests/ to svcs/
sys.path.insert(0, str(svcs_root / 'svcs_mcp'))

async def test_mcp_git_tools():
    """Test the new MCP git integration tools."""
    print("🔍 Testing SVCS MCP Git Integration Tools")
    print("=" * 50)
    
    try:
        from mcp_server import handle_call_tool
        print("✅ Successfully imported MCP server")
    except ImportError as e:
        print(f"❌ Failed to import MCP server: {e}")
        return
    
    # Change to SVCS project directory for testing
    os.chdir(svcs_root)
    
    # Get latest commit hash
    import subprocess
    try:
        result = subprocess.run(['git', 'rev-parse', 'HEAD'], 
                              capture_output=True, text=True, check=True)
        latest_commit = result.stdout.strip()
        print(f"📝 Testing with latest commit: {latest_commit[:8]}")
    except subprocess.CalledProcessError:
        print("❌ Failed to get latest commit hash")
        return
    
    # Test get_commit_changed_files tool
    print("\n1. Testing get_commit_changed_files tool:")
    try:
        result = await handle_call_tool("get_commit_changed_files", {
            "project_path": str(svcs_root),
            "commit_hash": latest_commit
        })
        print(f"   ✅ Tool executed successfully")
        print(f"   📄 Result: {result[0].text[:200]}...")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test get_commit_summary tool
    print("\n2. Testing get_commit_summary tool:")
    try:
        result = await handle_call_tool("get_commit_summary", {
            "project_path": str(svcs_root),
            "commit_hash": latest_commit
        })
        print(f"   ✅ Tool executed successfully")
        print(f"   📄 Result: {result[0].text[:300]}...")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n🎉 MCP git integration testing completed!")

if __name__ == "__main__":
    asyncio.run(test_mcp_git_tools())
