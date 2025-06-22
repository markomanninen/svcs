#!/usr/bin/env python3
"""
Test script to validate and debug Semantic Search filters in the SVCS Interactive Dashboard.
This tests each filter individually and in combination to ensure they work correctly.
"""

import requests
import json
import sys

BASE_URL = "http://127.0.0.1:5000"

def test_api_endpoint(endpoint, params, test_name):
    """Test a specific API endpoint with given parameters."""
    print(f"\n=== Testing: {test_name} ===")
    print(f"Endpoint: {endpoint}")
    print(f"Parameters: {json.dumps(params, indent=2)}")
    
    try:
        response = requests.post(f"{BASE_URL}{endpoint}", json=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                result_count = len(data.get('data', []))
                print(f"✅ SUCCESS: {result_count} results returned")
                
                # Show sample of first result if available
                if result_count > 0:
                    first_result = data['data'][0]
                    print(f"Sample result keys: {list(first_result.keys())}")
                    if 'layer' in first_result:
                        print(f"Layer: {first_result['layer']}")
                    if 'author' in first_result:
                        print(f"Author: {first_result['author']}")
                    if 'confidence' in first_result:
                        print(f"Confidence: {first_result['confidence']}")
                return True
            else:
                print(f"❌ API returned success=False: {data.get('message', 'Unknown error')}")
                return False
        else:
            print(f"❌ HTTP Error {response.status_code}: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False

def main():
    """Run comprehensive filter tests."""
    print("SVCS Interactive Dashboard - Semantic Search Filter Testing")
    print("=" * 60)
    
    # Test basic search without filters
    test_api_endpoint(
        "/api/search_events",
        {},
        "Basic search (no filters)"
    )
    
    # Test Author filter
    test_api_endpoint(
        "/api/search_events",
        {"author": "marko"},
        "Author filter: 'marko'"
    )
    
    # Test Days filter
    test_api_endpoint(
        "/api/search_events",
        {"days": 30},
        "Days filter: 30 days"
    )
    
    # Test Min Confidence filter
    test_api_endpoint(
        "/api/search_events",
        {"min_confidence": 0.7},
        "Min Confidence filter: 0.7"
    )
    
    # Test Max Results filter
    test_api_endpoint(
        "/api/search_events",
        {"limit": 5},
        "Max Results filter: 5"
    )
    
    # Test Layer filter - SINGLE VALUE (current frontend behavior)
    test_api_endpoint(
        "/api/search_events",
        {"layer": "core"},
        "Layer filter: 'core' (SINGLE VALUE - FRONTEND BUG)"
    )
    
    # Test Layer filter - ARRAY (correct backend expectation)
    test_api_endpoint(
        "/api/search_events",
        {"layers": ["core"]},
        "Layers filter: ['core'] (CORRECT ARRAY FORMAT)"
    )
    
    # Test Layer filter - Multiple layers
    test_api_endpoint(
        "/api/search_events",
        {"layers": ["5a", "5b"]},
        "Layers filter: ['5a', '5b'] (Multiple layers)"
    )
    
    # Test combined filters
    test_api_endpoint(
        "/api/search_events",
        {
            "author": "marko",
            "days": 30,
            "min_confidence": 0.5,
            "limit": 10,
            "layers": ["core"]
        },
        "Combined filters: author + days + confidence + limit + layers"
    )
    
    # Test what happens when frontend sends 'layer' instead of 'layers'
    test_api_endpoint(
        "/api/search_events",
        {
            "author": "marko",
            "layer": "core",  # Wrong parameter name
            "min_confidence": 0.5
        },
        "Frontend bug test: layer (singular) instead of layers (plural)"
    )

if __name__ == "__main__":
    print("Starting SVCS Web Server test...")
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ SVCS Web Server is running")
            main()
        else:
            print("❌ SVCS Web Server is not responding correctly")
            sys.exit(1)
    except requests.exceptions.RequestException:
        print("❌ SVCS Web Server is not running. Please start it first with:")
        print("cd /Users/markomanninen/Documents/GitHub/svcs && python svcs_web_server.py")
        sys.exit(1)
