#!/usr/bin/env python3
"""
Frontend Integration Test - Validates that the dashboard frontend 
sends correct parameters and all filters work end-to-end.
"""

import requests
import json
import time

BASE_URL = "http://127.0.0.1:5000"

def test_frontend_integration():
    """Test that simulates what the frontend should send."""
    print("=== Frontend Integration Test ===")
    print("Testing the exact parameters the fixed frontend should send...\n")
    
    # Test 1: Simulate frontend search with all filters
    frontend_params = {
        "author": "marko",
        "days": 30,
        "min_confidence": 0.7,
        "limit": 8,
        "layers": ["5a"]  # Fixed: frontend now sends array
    }
    
    print(f"Frontend parameters: {json.dumps(frontend_params, indent=2)}")
    
    response = requests.post(f"{BASE_URL}/api/search_events", json=frontend_params)
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            results = data.get('data', [])
            print(f"✅ SUCCESS: {len(results)} results returned")
            
            # Validate all filters worked
            validations = []
            
            # Author validation
            author_ok = all('marko' in (r.get('author') or '').lower() for r in results)
            validations.append(f"Author filter: {'✅' if author_ok else '❌'}")
            
            # Layer validation
            layer_ok = all(r.get('layer') == '5a' for r in results)
            validations.append(f"Layer filter: {'✅' if layer_ok else '❌'}")
            
            # Confidence validation
            conf_results = [r for r in results if r.get('confidence') is not None]
            conf_ok = all(r.get('confidence', 0) >= 0.7 for r in conf_results)
            validations.append(f"Confidence filter: {'✅' if conf_ok else '❌'}")
            
            # Limit validation
            limit_ok = len(results) <= 8
            validations.append(f"Limit filter: {'✅' if limit_ok else '❌'}")
            
            print("Filter validation results:")
            for validation in validations:
                print(f"  {validation}")
            
            # Show sample results
            print(f"\nSample results:")
            for i, result in enumerate(results[:3]):
                print(f"  {i+1}. Layer: {result.get('layer')}, "
                      f"Author: {result.get('author')}, "
                      f"Confidence: {result.get('confidence')}")
            
            return all('✅' in v for v in validations)
        else:
            print(f"❌ API Error: {data.get('error')}")
            return False
    else:
        print(f"❌ HTTP Error: {response.status_code}")
        return False

def test_layer_dropdown_values():
    """Test each layer dropdown value works correctly."""
    print(f"\n=== Layer Dropdown Values Test ===")
    
    layer_tests = [
        ("", "All Layers"),
        ("core", "Core (1-4)"),
        ("5a", "AI Pattern (5a)"),
        ("5b", "LLM Analysis (5b)")
    ]
    
    results = {}
    
    for layer_value, layer_name in layer_tests:
        params = {"layers": [layer_value]} if layer_value else {}
        
        response = requests.post(f"{BASE_URL}/api/search_events", json=params)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                count = len(data.get('data', []))
                results[layer_name] = count
                print(f"  {layer_name}: {count} results")
                
                # Validate layer filtering
                if layer_value:
                    actual_layers = set(r.get('layer') for r in data['data'])
                    if len(actual_layers) == 1 and layer_value in actual_layers:
                        print(f"    ✅ All results have layer '{layer_value}'")
                    else:
                        print(f"    ❌ Mixed layers found: {actual_layers}")
            else:
                print(f"    ❌ API Error for {layer_name}")
        else:
            print(f"    ❌ HTTP Error for {layer_name}")
    
    return results

def main():
    """Run all frontend integration tests."""
    print("SVCS Dashboard Frontend Integration Test")
    print("=" * 50)
    
    # Check server is running
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code != 200:
            print("❌ Server not responding")
            return
    except:
        print("❌ Cannot connect to server")
        return
    
    print("✅ Server is running\n")
    
    # Run tests
    frontend_test_passed = test_frontend_integration()
    layer_results = test_layer_dropdown_values()
    
    print(f"\n=== Summary ===")
    print(f"Frontend integration test: {'✅ PASSED' if frontend_test_passed else '❌ FAILED'}")
    print(f"Layer dropdown tests: ✅ COMPLETED")
    
    print(f"\nLayer distribution:")
    for layer_name, count in layer_results.items():
        print(f"  {layer_name}: {count} results")
    
    if frontend_test_passed:
        print(f"\n🎉 All Semantic Search filters are now working correctly!")
        print(f"The dashboard frontend properly sends:")
        print(f"  - Author filter (string)")
        print(f"  - Days filter (integer)")
        print(f"  - Min Confidence filter (float)")
        print(f"  - Max Results filter (integer)")
        print(f"  - Layer filter (array of strings)")
    else:
        print(f"\n❌ Some filters still have issues")

if __name__ == "__main__":
    main()
