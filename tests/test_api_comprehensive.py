#!/usr/bin/env python3
"""
Comprehensive API Test Suite for SVCS Search Functionality
Tests all search endpoints with various combinations to verify API responses.
"""

import requests
import json
import sys
from typing import Dict, Any, List

# Configuration
BASE_URL = "http://127.0.0.1:8081"
REPO_PATH = "/private/tmp/new-test-repo"

class APITester:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({'Content-Type': 'application/json'})
        
    def test_endpoint(self, endpoint: str, data: Dict[str, Any], test_name: str) -> Dict[str, Any]:
        """Test a single API endpoint and return the result."""
        print(f"\n{'='*60}")
        print(f"TEST: {test_name}")
        print(f"Endpoint: {endpoint}")
        print(f"Request Data: {json.dumps(data, indent=2)}")
        print(f"{'='*60}")
        
        try:
            response = self.session.post(f"{self.base_url}{endpoint}", json=data)
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"Response Success: {result.get('success', 'N/A')}")
                
                if result.get('success'):
                    # Analyze the data structure
                    data_section = result.get('data', {})
                    print(f"Data Keys: {list(data_section.keys())}")
                    
                    # Check for events in different locations
                    events = None
                    events_count = 0
                    
                    if 'events' in data_section:
                        events = data_section['events']
                        events_count = len(events) if events else 0
                        print(f"Events found in 'data.events': {events_count}")
                    elif 'results' in data_section:
                        events = data_section['results']
                        events_count = len(events) if events else 0
                        print(f"Events found in 'data.results': {events_count}")
                    
                    if events and events_count > 0:
                        # Analyze first event structure
                        first_event = events[0]
                        print(f"First Event Keys: {list(first_event.keys())}")
                        print(f"Event Type: {first_event.get('event_type', 'N/A')}")
                        print(f"Location: {first_event.get('location', 'N/A')}")
                        print(f"Author: {first_event.get('author', 'N/A')}")
                        print(f"Timestamp Field: {first_event.get('timestamp', first_event.get('created_at', 'N/A'))}")
                        
                        # Show all event types
                        event_types = list(set(event.get('event_type') for event in events))
                        print(f"Event Types: {event_types}")
                        
                        # Show sample event
                        print(f"Sample Event:")
                        print(json.dumps(first_event, indent=2))
                    else:
                        print("No events found in response")
                        
                else:
                    print(f"API Error: {result.get('error', 'Unknown error')}")
                    
                return result
            else:
                print(f"HTTP Error: {response.text}")
                return {"error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            print(f"Request Error: {str(e)}")
            return {"error": str(e)}

def main():
    """Run comprehensive API tests."""
    
    tester = APITester(BASE_URL)
    
    print("SVCS API Comprehensive Test Suite")
    print(f"Testing repository: {REPO_PATH}")
    print(f"Base URL: {BASE_URL}")
    
    # Test 1: Basic Search - Default
    tester.test_endpoint(
        "/api/semantic/search_events",
        {"repository_path": REPO_PATH},
        "Basic Search - Default (no parameters)"
    )
    
    # Test 2: Basic Search - With Limit
    tester.test_endpoint(
        "/api/semantic/search_events",
        {"repository_path": REPO_PATH, "limit": 5},
        "Basic Search - With Limit (5)"
    )
    
    # Test 3: Basic Search - With Event Type
    tester.test_endpoint(
        "/api/semantic/search_events",
        {"repository_path": REPO_PATH, "limit": 10, "event_type": "node_added"},
        "Basic Search - Filter by Event Type (node_added)"
    )
    
    # Test 4: Basic Search - Since Days
    tester.test_endpoint(
        "/api/semantic/search_events",
        {"repository_path": REPO_PATH, "limit": 10, "since_days": 7},
        "Basic Search - Since 7 Days"
    )
    
    # Test 5: Advanced Search - Default
    tester.test_endpoint(
        "/api/semantic/search_advanced",
        {"repository_path": REPO_PATH},
        "Advanced Search - Default (no parameters)"
    )
    
    # Test 6: Advanced Search - With Limit
    tester.test_endpoint(
        "/api/semantic/search_advanced",
        {"repository_path": REPO_PATH, "limit": 3},
        "Advanced Search - With Limit (3)"
    )
    
    # Test 7: Advanced Search - Order by Event Type
    tester.test_endpoint(
        "/api/semantic/search_advanced",
        {
            "repository_path": REPO_PATH,
            "limit": 10,
            "order_by": "event_type",
            "order_desc": True
        },
        "Advanced Search - Order by Event Type (DESC)"
    )
    
    # Test 8: Advanced Search - Order by Confidence
    tester.test_endpoint(
        "/api/semantic/search_advanced",
        {
            "repository_path": REPO_PATH,
            "limit": 10,
            "order_by": "confidence",
            "order_desc": False
        },
        "Advanced Search - Order by Confidence (ASC)"
    )
    
    # Test 9: Advanced Search - Filter by Event Types
    tester.test_endpoint(
        "/api/semantic/search_advanced",
        {
            "repository_path": REPO_PATH,
            "limit": 10,
            "event_types": ["node_added", "node_logic_changed"]
        },
        "Advanced Search - Filter by Multiple Event Types"
    )
    
    # Test 10: Advanced Search - Filter by Author
    tester.test_endpoint(
        "/api/semantic/search_advanced",
        {
            "repository_path": REPO_PATH,
            "limit": 10,
            "author": "Marko Manninen"
        },
        "Advanced Search - Filter by Author"
    )
    
    # Test 11: Advanced Search - Filter by Confidence
    tester.test_endpoint(
        "/api/semantic/search_advanced",
        {
            "repository_path": REPO_PATH,
            "limit": 10,
            "min_confidence": 0.9
        },
        "Advanced Search - Filter by Min Confidence (0.9)"
    )
    
    # Test 12: Advanced Search - Filter by Location Pattern
    tester.test_endpoint(
        "/api/semantic/search_advanced",
        {
            "repository_path": REPO_PATH,
            "limit": 10,
            "location_pattern": "*.py"
        },
        "Advanced Search - Filter by Location Pattern (*.py)"
    )
    
    # Test 13: Advanced Search - Filter by Layers
    tester.test_endpoint(
        "/api/semantic/search_advanced",
        {
            "repository_path": REPO_PATH,
            "limit": 10,
            "layers": ["core"]
        },
        "Advanced Search - Filter by Layers (core)"
    )
    
    # Test 14: Advanced Search - Since Date
    tester.test_endpoint(
        "/api/semantic/search_advanced",
        {
            "repository_path": REPO_PATH,
            "limit": 10,
            "since_date": "7 days ago"
        },
        "Advanced Search - Since Date (7 days ago)"
    )
    
    # Test 15: Advanced Search - Combined Filters
    tester.test_endpoint(
        "/api/semantic/search_advanced",
        {
            "repository_path": REPO_PATH,
            "limit": 5,
            "event_types": ["node_added", "node_logic_changed"],
            "author": "Marko Manninen",
            "min_confidence": 0.8,
            "order_by": "timestamp",
            "order_desc": True
        },
        "Advanced Search - Combined Filters (event_types + author + confidence + order)"
    )
    
    # Test 16: Recent Activity
    tester.test_endpoint(
        "/api/semantic/recent_activity",
        {
            "repository_path": REPO_PATH,
            "days": 7,
            "limit": 15
        },
        "Recent Activity - 7 days, limit 15"
    )
    
    # Test 17: Advanced Search - Edge Cases
    tester.test_endpoint(
        "/api/semantic/search_advanced",
        {
            "repository_path": REPO_PATH,
            "limit": 0
        },
        "Advanced Search - Edge Case: Limit 0"
    )
    
    # Test 18: Advanced Search - Large Limit
    tester.test_endpoint(
        "/api/semantic/search_advanced",
        {
            "repository_path": REPO_PATH,
            "limit": 1000
        },
        "Advanced Search - Large Limit (1000)"
    )
    
    print(f"\n{'='*60}")
    print("ALL TESTS COMPLETED")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
