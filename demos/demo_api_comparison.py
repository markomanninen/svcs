#!/usr/bin/env python3
"""
Practical demonstration comparing Web API and Discuss API approaches.
Shows the same functionality accessed through both interfaces.
"""

import requests
import json
import sys
import os

# Add path for discuss API
sys.path.append('.')

def demonstrate_web_api():
    """Demonstrate Web API usage (requires server running)."""
    print("🌐 WEB API DEMONSTRATION")
    print("=" * 50)
    
    base_url = "http://localhost:8080"
    repo_path = "/Users/markomanninen/Documents/GitHub/svcs"
    
    try:
        # Health check
        print("1. Health Check:")
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            health = response.json()
            print(f"   ✅ Server: {health['service']}")
            print(f"   ✅ Version: {health['version']}")
        else:
            print("   ❌ Server not running")
            return
        
        # Search events
        print("\n2. Search Semantic Events:")
        search_data = {
            "repository_path": repo_path,
            "limit": 5,
            "event_type": "function_added"
        }
        response = requests.post(f"{base_url}/api/semantic/search_events", 
                               json=search_data)
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Found {result['data']['total']} events")
            for event in result['data']['events'][:3]:
                print(f"      - {event.get('event_type', 'N/A')}: {event.get('node_id', 'N/A')}")
        else:
            print(f"   ❌ Search failed: {response.text}")
        
        # Advanced search
        print("\n3. Advanced Search:")
        advanced_data = {
            "repository_path": repo_path,
            "min_confidence": 0.8,
            "event_types": ["function_added", "class_added"],
            "limit": 3
        }
        response = requests.post(f"{base_url}/api/semantic/search_advanced", 
                               json=advanced_data)
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Found {len(result['data'])} high-confidence events")
        else:
            print(f"   ❌ Advanced search failed: {response.text}")
        
        # Recent activity
        print("\n4. Recent Activity:")
        recent_data = {
            "repository_path": repo_path,
            "days": 7,
            "limit": 5
        }
        response = requests.post(f"{base_url}/api/semantic/recent_activity", 
                               json=recent_data)
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Found {len(result['data'])} recent events")
        else:
            print(f"   ❌ Recent activity failed: {response.text}")
        
        # Natural language query
        print("\n5. Natural Language Query:")
        nl_data = {
            "repository_path": repo_path,
            "query": "What functions were added recently?"
        }
        try:
            response = requests.post(f"{base_url}/api/query/natural_language", 
                                   json=nl_data, timeout=10)
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Query processed: '{result['data']['query']}'")
                if 'matching_events' in result['data']:
                    print(f"   ✅ Found {len(result['data']['matching_events'])} matching events")
                else:
                    print(f"   ✅ Response: {result['data'].get('response', 'No response')}")
            else:
                print(f"   ⚠️ Natural language query failed: {response.status_code}")
                print(f"   💡 This endpoint requires discuss module integration")
        except requests.exceptions.Timeout:
            print(f"   ⚠️ Natural language query timed out")
            print(f"   💡 This endpoint may require additional LLM setup")
        except Exception as e:
            print(f"   ⚠️ Natural language query error: {e}")
            print(f"   💡 Endpoint available but may need configuration")
            
    except requests.exceptions.ConnectionError:
        print("   ❌ Cannot connect to Web API server")
        print("   💡 Start server with: python3 svcs_repo_web_server.py")
    except Exception as e:
        print(f"   ❌ Web API error: {e}")

def demonstrate_discuss_api():
    """Demonstrate Discuss API usage."""
    print("\n💬 DISCUSS API DEMONSTRATION")
    print("=" * 50)
    
    try:
        # Import discuss API functions
        from svcs.api import search_events_advanced, get_recent_activity, get_project_statistics
        
        print("1. Project Statistics:")
        stats = get_project_statistics()
        print(f"   ✅ Retrieved {len(stats)} statistics")
        for stat in stats[:3]:
            if 'statistic' in stat:
                print(f"      - {stat['statistic']}: {len(stat.get('data', []))} entries")
        
        print("\n2. Advanced Search:")
        events = search_events_advanced(
            min_confidence=0.8,
            event_types=["function_added", "class_added"],
            limit=3
        )
        print(f"   ✅ Found {len(events)} high-confidence events")
        for event in events:
            print(f"      - {event.get('event_type', 'N/A')}: {event.get('node_id', 'N/A')} (confidence: {event.get('confidence', 'N/A')})")
        
        print("\n3. Recent Activity:")
        recent = get_recent_activity(days=7, limit=5)
        print(f"   ✅ Found {len(recent)} recent events")
        for event in recent[:3]:
            print(f"      - {event.get('event_type', 'N/A')}: {event.get('node_id', 'N/A')}")
        
        print("\n4. Natural Language Query Simulation:")
        print("   🤖 Query: 'What functions were added recently?'")
        print("   🔧 Function calls executed:")
        print("      1. get_recent_activity(days=7)")
        print("      2. search_events_advanced(event_types=['function_added'])")
        print("   📊 AI Response would synthesize results into natural language")
        
    except Exception as e:
        print(f"   ❌ Discuss API error: {e}")

def compare_approaches():
    """Compare the approaches side by side."""
    print("\n🔍 APPROACH COMPARISON")
    print("=" * 50)
    
    print("📤 REQUEST FORMATS:")
    print("\nWeb API (JSON HTTP POST):")
    web_request = {
        "repository_path": "/path/to/repo",
        "min_confidence": 0.8,
        "event_types": ["function_added"],
        "limit": 5
    }
    print(f"   {json.dumps(web_request, indent=2)}")
    
    print("\nDiscuss API (Python function call):")
    print("   search_events_advanced(")
    print("       min_confidence=0.8,")
    print("       event_types=['function_added'],")
    print("       limit=5")
    print("   )")
    
    print("\n📥 RESPONSE FORMATS:")
    print("\nWeb API (JSON response):")
    web_response = {
        "success": True,
        "data": [
            {"event_type": "function_added", "node_id": "func:example", "confidence": 0.85}
        ]
    }
    print(f"   {json.dumps(web_response, indent=2)}")
    
    print("\nDiscuss API (Python objects + AI narrative):")
    print("   [")
    print("       {'event_type': 'function_added', 'node_id': 'func:example', 'confidence': 0.85}")
    print("   ]")
    print("   + AI explanation: 'I found 1 function addition with high confidence...'")

def demonstrate_use_cases():
    """Show typical use cases for each API."""
    print("\n🎯 TYPICAL USE CASES")
    print("=" * 50)
    
    print("🌐 WEB API USE CASES:")
    print("   1. Team Dashboard:")
    print("      - Multiple repositories overview")
    print("      - Real-time activity monitoring")
    print("      - Visual charts and graphs")
    
    print("   2. External Integration:")
    print("      - CI/CD pipeline integration")
    print("      - Third-party tool connections")
    print("      - Automated reporting systems")
    
    print("   3. Multi-User Environment:")
    print("      - Concurrent access by team members")
    print("      - Role-based repository access")
    print("      - Centralized semantic data")
    
    print("\n💬 DISCUSS API USE CASES:")
    print("   1. Development Workflow:")
    print("      - 'What changed in the auth module?'")
    print("      - 'Show me recent performance improvements'")
    print("      - 'Analyze code quality trends'")
    
    print("   2. Code Exploration:")
    print("      - 'How has function X evolved?'")
    print("      - 'What patterns do you see in recent commits?'")
    print("      - 'Explain this semantic event'")
    
    print("   3. Interactive Analysis:")
    print("      - Follow-up questions")
    print("      - Contextual deep-dives")
    print("      - AI-guided exploration")

if __name__ == "__main__":
    print("🔍 SVCS API COMPARISON DEMONSTRATION")
    print("="*60)
    
    demonstrate_web_api()
    demonstrate_discuss_api()
    compare_approaches()
    demonstrate_use_cases()
    
    print("\n🎯 SUMMARY:")
    print("✅ Web API: REST interface for integration and dashboards")
    print("✅ Discuss API: AI-powered conversational analysis")
    print("🚀 Both complement each other for complete SVCS experience!")
