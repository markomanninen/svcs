#!/usr/bin/env python3
"""
Test script to verify MCP event storage and query functionality
"""

import sys
import os
from pathlib import Path

# Add the MCP directory to Python path
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))
sys.path.insert(0, str(script_dir.parent / ".svcs"))

# Import MCP tools
from svcs_mcp_server_simple import GlobalSVCSDatabase

def test_event_queries():
    """Test event queries and database content."""
    
    print("🧪 Testing SVCS MCP Event Queries")
    print("=" * 50)
    
    # Initialize database
    db = GlobalSVCSDatabase()
    
    # Get the test project
    project_path = "/Users/markomanninen/Documents/tmp/svcs_new_project"
    project = db.get_project_by_path(project_path)
    
    if not project:
        print("❌ Project not found")
        return
    
    project_id = project['project_id']
    print(f"✅ Project: {project['name']} (ID: {project_id[:8]}...)")
    
    # Test querying events
    print("\n🔍 Querying events...")
    events = db.query_semantic_events(project_id=project_id, limit=10)
    
    print(f"📊 Found {len(events)} events")
    
    for i, event in enumerate(events, 1):
        print(f"\n{i}. Event:")
        print(f"   Type: {event['event_type']}")
        print(f"   Node: {event['node_id']}")
        print(f"   Location: {event['location']}")
        print(f"   Details: {event['details']}")
        print(f"   Layer: {event['layer']}")
        print(f"   Commit: {event['commit_hash'][:8]}...")
        print(f"   Author: {event['author']}")
        
    # Test statistics
    print("\n📈 Statistics:")
    stats = db.get_project_statistics(project_id)
    print(f"   Total events: {stats['total_events']}")
    print(f"   Total commits: {stats['total_commits']}")
    print(f"   Event types: {stats['event_types']}")
    print(f"   Layers: {stats['layers']}")
    
    # Test raw database content
    print("\n🗄️ Raw database check:")
    with db.get_connection() as conn:
        cursor = conn.execute("""
            SELECT event_type, node_id, details, layer 
            FROM semantic_events 
            WHERE project_id = ? 
            ORDER BY created_at DESC 
            LIMIT 5
        """, (project_id,))
        
        raw_events = cursor.fetchall()
        
        for event in raw_events:
            print(f"   Raw: {event}")

if __name__ == "__main__":
    test_event_queries()
