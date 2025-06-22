#!/usr/bin/env python3
"""
Debug confidence filter specifically.
"""

import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def test_confidence_debug():
    """Debug confidence filtering in detail."""
    print("=== Confidence Filter Debug ===")
    
    # Test 1: No confidence filter (baseline)
    response = requests.post(f"{BASE_URL}/api/search_events", json={})
    data = response.json()
    all_results = data['data']
    print(f"Total results (no filter): {len(all_results)}")
    
    confidence_counts = {}
    for result in all_results:
        conf = result.get('confidence')
        if conf is None:
            key = 'None'
        else:
            key = f"{conf:.1f}"
        confidence_counts[key] = confidence_counts.get(key, 0) + 1
    
    print("Confidence distribution:")
    for conf, count in sorted(confidence_counts.items()):
        print(f"  {conf}: {count} results")
    
    # Test 2: High confidence filter
    print(f"\n--- Testing min_confidence: 0.8 ---")
    response = requests.post(f"{BASE_URL}/api/search_events", json={"min_confidence": 0.8})
    data = response.json()
    filtered_results = data['data']
    print(f"Results with min_confidence 0.8: {len(filtered_results)}")
    
    for i, result in enumerate(filtered_results[:5]):  # Show first 5 results
        print(f"  Result {i+1}: confidence={result.get('confidence')}, layer={result.get('layer')}")
    
    # Test 3: Medium confidence filter
    print(f"\n--- Testing min_confidence: 0.6 ---")
    response = requests.post(f"{BASE_URL}/api/search_events", json={"min_confidence": 0.6})
    data = response.json()
    filtered_results = data['data']
    print(f"Results with min_confidence 0.6: {len(filtered_results)}")
    
    for i, result in enumerate(filtered_results[:5]):  # Show first 5 results
        print(f"  Result {i+1}: confidence={result.get('confidence')}, layer={result.get('layer')}")

if __name__ == "__main__":
    test_confidence_debug()
