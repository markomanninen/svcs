#!/usr/bin/env python3
"""
Test MCP query tools via the new SVCS API
"""

import sys
import os
from pathlib import Path

# Add the SVCS directory to Python path
script_dir = Path(__file__).parent
svcs_root = script_dir.parent
sys.path.insert(0, str(svcs_root))

# Import new SVCS API
from svcs.api import search_events_advanced, get_recent_activity

def test_mcp_query_tools():
    """Test MCP query tools exactly as the user would use them via the new API."""
    
    print("🔧 Testing MCP Query Tools via New API")
    print("=" * 40)
    
    # Test recent activity (works with current directory)
    print(f"\n📊 Recent Activity (last 7 days):")
    try:
        recent_events = get_recent_activity(days=7, limit=10)
        
        print(f"Found {len(recent_events)} recent events")
        
        for i, event in enumerate(recent_events[:5], 1):  # Show first 5
            print(f"\n{i}. {event['event_type']}")
            print(f"   Location: {event['location']}")
            print(f"   Author: {event['author']}")
            print(f"   Date: {event['timestamp']}")
            if 'details' in event:
                print(f"   Details: {event['details']}")
                
    except Exception as e:
        print(f"❌ Error getting recent activity: {e}")
        return
    
    # Test advanced search
    print(f"\n🔍 Advanced Event Search:")
    try:
        search_results = search_events_advanced(limit=5)
        
        print(f"Found {len(search_results)} events via advanced search")
        
        for i, event in enumerate(search_results[:3], 1):  # Show first 3
            print(f"\n{i}. {event['event_type']}")
            print(f"   Location: {event['location']}")
            print(f"   Layer: {event.get('layer', 'N/A')}")
            if 'node_id' in event:
                print(f"   Node: {event['node_id']}")
                
    except Exception as e:
        print(f"❌ Error in advanced search: {e}")
        return
        
    print(f"\n✅ MCP query tools working correctly via new API!")

if __name__ == "__main__":
    test_mcp_query_tools()
