#!/usr/bin/env python3
"""
Enhanced test script to validate Semantic Search filters after fixes.
This script tests each filter and validates that they actually affect the results.
"""

import requests
import json
import sys

BASE_URL = "http://127.0.0.1:5000"

def test_api_with_validation(endpoint, params, test_name, validation_func=None):
    """Test API endpoint and validate results."""
    print(f"\n=== Testing: {test_name} ===")
    print(f"Parameters: {json.dumps(params, indent=2)}")
    
    try:
        response = requests.post(f"{BASE_URL}{endpoint}", json=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                results = data.get('data', [])
                result_count = len(results)
                print(f"✅ SUCCESS: {result_count} results returned")
                
                # Run validation if provided
                if validation_func and results:
                    validation_result = validation_func(results, params)
                    if validation_result:
                        print(f"✅ VALIDATION PASSED: {validation_result}")
                    else:
                        print(f"❌ VALIDATION FAILED")
                        return False
                
                # Show sample result
                if results:
                    sample = results[0]
                    print(f"Sample: Layer={sample.get('layer')}, Author={sample.get('author')}, Confidence={sample.get('confidence')}")
                
                return True, results
            else:
                print(f"❌ API Error: {data.get('error', 'Unknown error')}")
                return False, []
        else:
            print(f"❌ HTTP Error {response.status_code}: {response.text}")
            return False, []
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return False, []

def validate_author_filter(results, params):
    """Validate that author filter works."""
    author_filter = params.get('author', '').lower()
    if not author_filter:
        return "No author filter to validate"
    
    for result in results:
        result_author = (result.get('author') or '').lower()
        if author_filter not in result_author:
            return None  # Validation failed
    return f"All results contain author '{author_filter}'"

def validate_confidence_filter(results, params):
    """Validate that confidence filter works."""
    min_conf = params.get('min_confidence')
    if min_conf is None:
        return "No confidence filter to validate"
    
    filtered_results = [r for r in results if r.get('confidence') is not None]
    if not filtered_results:
        return "No results with confidence values to validate"
    
    for result in filtered_results:
        conf = result.get('confidence')
        if conf is not None and conf < min_conf:
            return None  # Validation failed
    return f"All results have confidence >= {min_conf}"

def validate_layer_filter(results, params):
    """Validate that layer filter works."""
    layers = params.get('layers', [])
    if not layers:
        return "No layer filter to validate"
    
    for result in results:
        result_layer = result.get('layer')
        if result_layer not in layers:
            return None  # Validation failed
    return f"All results are in layers {layers}"

def validate_limit_filter(results, params):
    """Validate that limit filter works."""
    limit = params.get('limit')
    if not limit:
        return "No limit filter to validate"
    
    if len(results) <= limit:
        return f"Result count {len(results)} <= limit {limit}"
    else:
        return None  # Validation failed

def main():
    """Run comprehensive filter validation tests."""
    print("SVCS Interactive Dashboard - Enhanced Filter Validation")
    print("=" * 60)
    
    # Test 1: Basic search to get baseline
    success, baseline_results = test_api_with_validation(
        "/api/search_events",
        {},
        "Baseline search (no filters)"
    )
    
    baseline_count = len(baseline_results)
    print(f"Baseline result count: {baseline_count}")
    
    # Test 2: Author filter validation
    test_api_with_validation(
        "/api/search_events",
        {"author": "marko"},
        "Author filter validation",
        validate_author_filter
    )
    
    # Test 3: Confidence filter validation
    test_api_with_validation(
        "/api/search_events",
        {"min_confidence": 0.8},
        "High confidence filter validation",
        validate_confidence_filter
    )
    
    # Test 4: Layer filter validation (fixed frontend format)
    test_api_with_validation(
        "/api/search_events",
        {"layers": ["5a"]},
        "Layer 5a filter validation",
        validate_layer_filter
    )
    
    # Test 5: Limit filter validation
    test_api_with_validation(
        "/api/search_events",
        {"limit": 3},
        "Limit filter validation",
        validate_limit_filter
    )
    
    # Test 6: Combined filters validation
    print(f"\n=== Combined Filter Test ===")
    success, combined_results = test_api_with_validation(
        "/api/search_events",
        {
            "author": "marko",
            "layers": ["5a", "5b"],
            "min_confidence": 0.5,
            "limit": 5
        },
        "Combined filters test"
    )
    
    if success:
        # Validate each filter in combination
        valid_author = validate_author_filter(combined_results, {"author": "marko"})
        valid_layer = validate_layer_filter(combined_results, {"layers": ["5a", "5b"]})
        valid_conf = validate_confidence_filter(combined_results, {"min_confidence": 0.5})
        valid_limit = validate_limit_filter(combined_results, {"limit": 5})
        
        print(f"Author validation: {valid_author}")
        print(f"Layer validation: {valid_layer}")
        print(f"Confidence validation: {valid_conf}")
        print(f"Limit validation: {valid_limit}")
    
    # Test 7: Frontend compatibility (layer vs layers)
    print(f"\n=== Frontend Compatibility Test ===")
    success1, results1 = test_api_with_validation(
        "/api/search_events",
        {"layer": "core"},  # Old frontend format
        "Legacy 'layer' parameter (should be handled by backend)"
    )
    
    success2, results2 = test_api_with_validation(
        "/api/search_events",
        {"layers": ["core"]},  # Correct format
        "Correct 'layers' parameter"
    )
    
    if success1 and success2:
        if len(results1) == len(results2):
            print("✅ Backend compatibility: 'layer' and 'layers' produce same results")
        else:
            print("❌ Backend compatibility issue: different result counts")

if __name__ == "__main__":
    print("Starting enhanced filter validation...")
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ SVCS Web Server is running")
            main()
        else:
            print("❌ SVCS Web Server is not responding")
            sys.exit(1)
    except requests.exceptions.RequestException:
        print("❌ Cannot connect to SVCS Web Server")
        sys.exit(1)
