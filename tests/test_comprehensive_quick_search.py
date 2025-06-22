#!/usr/bin/env python3
"""
Comprehensive test to verify all Quick Search functionality in the SVCS Interactive Dashboard.
This tests all quick search buttons to ensure they return meaningful data.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from svcs_web_server import app
import json

def test_quick_search_button(button_type, api_endpoint, params, expected_title):
    """Test a specific quick search button functionality."""
    print(f"🔍 Testing Quick Search: {button_type}")
    
    with app.test_client() as client:
        response = client.post(f'/api/{api_endpoint}', 
                             json=params,
                             content_type='application/json')
        
        print(f"  Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.get_json()
            success = data.get('success', False)
            print(f"  Response Success: {success}")
            
            if success and data.get('data'):
                result_data = data['data']
                count = len(result_data) if isinstance(result_data, list) else 1
                print(f"  Results found: {count}")
                
                if count > 0:
                    print(f"  ✅ {button_type} quick search is working!")
                    return True
                else:
                    print(f"  ⚠️  {button_type} quick search returned empty results")
                    return False
            else:
                print(f"  ❌ {button_type} quick search failed: {data}")
                return False
        else:
            print(f"  ❌ {button_type} quick search failed with status {response.status_code}")
            return False

def test_all_quick_search_buttons():
    """Test all quick search buttons that appear in the dashboard."""
    print("🚀 Testing All Quick Search Buttons\n")
    
    test_results = {}
    
    # Test Recent Activity (now uses get_recent_activity)
    test_results['recent'] = test_quick_search_button(
        'Recent Activity',
        'get_recent_activity',
        {'days': 7, 'limit': 20, 'author': None, 'layers': None},
        'Recent Activity'
    )
    
    # Test Performance Patterns
    test_results['performance'] = test_quick_search_button(
        'Performance Patterns',
        'search_patterns',
        {'pattern_type': 'performance', 'min_confidence': 0.5, 'since_date': '30 days ago', 'limit': 20},
        'Performance patterns'
    )
    
    # Test Architecture Patterns  
    test_results['architecture'] = test_quick_search_button(
        'Architecture Patterns',
        'search_patterns',
        {'pattern_type': 'architecture', 'min_confidence': 0.5, 'since_date': '30 days ago', 'limit': 20},
        'Architecture patterns'
    )
    
    # Test Error Handling Patterns
    test_results['error_handling'] = test_quick_search_button(
        'Error Handling Patterns',
        'search_patterns',
        {'pattern_type': 'error_handling', 'min_confidence': 0.5, 'since_date': '30 days ago', 'limit': 20},
        'Error_handling patterns'
    )
    
    return test_results

def test_dashboard_endpoints_availability():
    """Test that all dashboard-required endpoints are available."""
    print("\n🌐 Testing Dashboard API Endpoints Availability")
    
    endpoints_to_test = [
        '/api/get_recent_activity',
        '/api/search_patterns',
        '/api/search_semantic_patterns',
        '/api/get_filtered_evolution',
        '/api/generate_analytics'
    ]
    
    availability_results = {}
    
    with app.test_client() as client:
        for endpoint in endpoints_to_test:
            # Test with minimal valid data to check availability
            test_data = {}
            if 'get_recent_activity' in endpoint:
                test_data = {'days': 1, 'limit': 1}
            elif 'search_patterns' in endpoint or 'search_semantic_patterns' in endpoint:
                test_data = {'pattern_type': 'performance', 'limit': 1}
            elif 'get_filtered_evolution' in endpoint:
                test_data = {'node_id': 'test'}
            elif 'generate_analytics' in endpoint:
                test_data = {'days': 1}
            
            response = client.post(endpoint, json=test_data, content_type='application/json')
            available = response.status_code != 404
            availability_results[endpoint] = available
            print(f"  {endpoint}: {'✅ Available' if available else '❌ Not Found'}")
    
    return availability_results

def main():
    """Run comprehensive tests for all quick search functionality."""
    print("🎯 Comprehensive Quick Search Test for SVCS Interactive Dashboard\n")
    
    # Test endpoint availability
    endpoint_results = test_dashboard_endpoints_availability()
    
    # Test quick search functionality
    quick_search_results = test_all_quick_search_buttons()
    
    print(f"\n📋 Test Results Summary:")
    print(f"\n🌐 API Endpoint Availability:")
    for endpoint, available in endpoint_results.items():
        print(f"  {endpoint}: {'✅ Available' if available else '❌ Missing'}")
    
    print(f"\n🔍 Quick Search Functionality:")
    for search_type, working in quick_search_results.items():
        print(f"  {search_type}: {'✅ Working' if working else '❌ Not Working'}")
    
    # Overall success check
    all_endpoints_available = all(endpoint_results.values())
    all_searches_working = all(quick_search_results.values())
    
    print(f"\n🏁 Overall Results:")
    print(f"  All Endpoints Available: {'✅ YES' if all_endpoints_available else '❌ NO'}")
    print(f"  All Quick Searches Working: {'✅ YES' if all_searches_working else '❌ NO'}")
    
    if all_endpoints_available and all_searches_working:
        print("\n🎉 All dashboard quick search functionality is working perfectly!")
        return True
    else:
        print("\n⚠️  Some dashboard functionality may have issues.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
