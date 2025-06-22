#!/usr/bin/env python3
"""
Test script to verify the Recent Activity fix for the SVCS Interactive Dashboard.
This script tests that the get_recent_activity API endpoint returns meaningful data.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from svcs_web_server import app
import json

def test_recent_activity_api():
    """Test the get_recent_activity API endpoint directly."""
    print("🔍 Testing Recent Activity API endpoint...")
    
    with app.test_client() as client:
        # Test the get_recent_activity endpoint
        response = client.post('/api/get_recent_activity', 
                             json={'days': 7, 'limit': 20},
                             content_type='application/json')
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.get_json()
            print(f"Response Success: {data.get('success', False)}")
            
            if data.get('success') and data.get('data'):
                activity_data = data['data']
                print(f"Number of recent activities found: {len(activity_data)}")
                
                if activity_data:
                    print("\n📊 Sample recent activity:")
                    for i, activity in enumerate(activity_data[:3]):  # Show first 3
                        print(f"  {i+1}. {activity}")
                    print("✅ Recent Activity API is working and returning data!")
                    return True
                else:
                    print("⚠️  Recent Activity API returned empty data")
                    return False
            else:
                print(f"❌ API response indicates failure: {data}")
                return False
        else:
            print(f"❌ API request failed with status {response.status_code}")
            print(f"Response: {response.get_data(as_text=True)}")
            return False

def test_dashboard_quick_search_logic():
    """Test the logic that would be used by the dashboard's quickSearch function."""
    print("\n🎯 Testing Dashboard Quick Search Logic...")
    
    with app.test_client() as client:
        # Test what quickSearch('recent') would now call
        print("Testing quickSearch('recent') logic...")
        response = client.post('/api/get_recent_activity',
                             json={
                                 'days': 7,
                                 'limit': 20,
                                 'author': None,
                                 'layers': None
                             },
                             content_type='application/json')
        
        if response.status_code == 200:
            data = response.get_json()
            if data.get('success') and data.get('data'):
                print(f"✅ quickSearch('recent') would return {len(data['data'])} activities")
                return True
            else:
                print("❌ quickSearch('recent') would return empty results")
                return False
        else:
            print(f"❌ quickSearch('recent') would fail with status {response.status_code}")
            return False

def main():
    """Run all tests for the Recent Activity fix."""
    print("🚀 Testing Recent Activity Fix for SVCS Interactive Dashboard\n")
    
    # Test the API endpoint
    api_test_passed = test_recent_activity_api()
    
    # Test the dashboard logic
    dashboard_test_passed = test_dashboard_quick_search_logic()
    
    print(f"\n📋 Test Results Summary:")
    print(f"  - Recent Activity API Test: {'✅ PASSED' if api_test_passed else '❌ FAILED'}")
    print(f"  - Dashboard Quick Search Logic Test: {'✅ PASSED' if dashboard_test_passed else '❌ FAILED'}")
    
    if api_test_passed and dashboard_test_passed:
        print("\n🎉 All Recent Activity tests PASSED! The fix is working correctly.")
        return True
    else:
        print("\n⚠️  Some tests FAILED. The Recent Activity feature may still have issues.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
