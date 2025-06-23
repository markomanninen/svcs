#!/usr/bin/env python3
"""
Test script to verify MCP tools provide the same debug output as original .svcs
"""

import sys
import os
from pathlib import Path

# Add the MCP directory to Python path
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

# Import MCP tools
from svcs_core import GlobalSVCSDatabase, process_commit

def test_mcp_tools():
    """Test the MCP tools to ensure they provide comprehensive debug output."""
    
    print("🧪 Testing SVCS MCP Tools")
    print("=" * 50)
    
    # Test project path
    project_path = "/Users/markomanninen/Documents/tmp/svcs_new_project"
    
    print(f"📁 Project path: {project_path}")
    
    # Initialize database
    db = GlobalSVCSDatabase()
    
    # Check if project is registered
    project = db.get_project_by_path(project_path)
    if project:
        print(f"✅ Project registered: {project['name']} (ID: {project['project_id'][:8]}...)")
    else:
        print("❌ Project not registered")
        return
    
    # Get some statistics
    with db.get_connection() as conn:
        cursor = conn.execute(
            "SELECT COUNT(*) FROM semantic_events WHERE project_id = ?",
            (project['project_id'],)
        )
        event_count = cursor.fetchone()[0]
    print(f"📊 Current events in database: {event_count}")
    
    # Test process_commit to ensure it provides the debug table
    print("\n🔍 Testing process_commit debug output:")
    print("-" * 50)
    
    # This should trigger the full debug output with table
    process_commit(project_path)
    
    print("\n✅ Test completed!")

if __name__ == "__main__":
    test_mcp_tools()
