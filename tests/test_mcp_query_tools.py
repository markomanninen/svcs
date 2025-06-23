#!/usr/bin/env python3
"""
Test MCP query tools with specific project ID
"""

import sys
import os
from pathlib import Path

# Add the MCP directory to Python path
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

# Import MCP tools
from svcs_core import GlobalSVCSDatabase

def test_mcp_query_tools():
    """Test MCP query tools exactly as the user would use them."""
    
    print("🔧 Testing MCP Query Tools")
    print("=" * 40)
    
    # Initialize database
    db = GlobalSVCSDatabase()
    
    # Test with user's project ID format
    project_id = "041b54b5"  # User's partial project ID
    limit = 10
    
    print(f"📋 Query parameters:")
    print(f"   project_id: {project_id}")
    print(f"   limit: {limit}")
    
    # Find full project ID (since user provided partial)
    with db.get_connection() as conn:
        cursor = conn.execute(
            "SELECT project_id, name FROM projects WHERE project_id LIKE ?",
            (f"{project_id}%",)
        )
        project = cursor.fetchone()
    
    if not project:
        print(f"❌ No project found with ID starting with: {project_id}")
        return
    
    full_project_id = project[0]
    project_name = project[1]
    print(f"✅ Found project: {project_name} (Full ID: {full_project_id})")
    
    # Query semantic events
    try:
        events = db.query_semantic_events(project_id=full_project_id, limit=limit)
        
        print(f"\n📊 Query Results: {len(events)} events found")
        
        for i, event in enumerate(events[:5], 1):  # Show first 5
            print(f"\n{i}. {event['event_type']}")
            print(f"   Node: {event['node_id']}")
            print(f"   Location: {event['location']}")
            print(f"   Details: {event['details']}")
            print(f"   Author: {event['author']}")
            print(f"   Commit: {event['commit_hash'][:8]}...")
            print(f"   Layer: {event['layer']}")
            
        print(f"\n✅ MCP query tools working correctly!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_mcp_query_tools()
