#!/usr/bin/env python3
"""
Comprehensive test to verify all API endpoints exist that the dashboard expects.
"""

import sys
import os

def test_all_api_endpoints():
    """Test that all expected API endpoints exist."""
    
    print("🔧 Testing All Dashboard API Endpoints")
    print("=" * 45)
    
    # List of endpoints the dashboard expects
    expected_endpoints = [
        'search_events',
        'search_patterns', 
        'get_commit_changed_files',
        'get_commit_diff',
        'get_commit_summary',
        'get_recent_activity',
        'get_node_evolution',
        'get_filtered_evolution',
        'search_semantic_patterns',  # This was missing
        'get_logs',
        'list_projects',
        'get_project_statistics',
        'register_project',
        'debug_query_tools',
        'generate_analytics',
        'quality_analysis',
        'export_data'
    ]
    
    print(f"📋 Checking {len(expected_endpoints)} API endpoints...")
    
    # Import the web server
    sys.path.insert(0, '.svcs')
    try:
        import svcs_web_server
        app = svcs_web_server.app
        
        # Get all API routes
        api_routes = []
        for rule in app.url_map.iter_rules():
            if rule.rule.startswith('/api/'):
                endpoint_name = rule.rule.replace('/api/', '')
                api_routes.append(endpoint_name)
        
        print(f"✅ Found {len(api_routes)} API routes in web server")
        
        # Check each expected endpoint
        missing_endpoints = []
        for endpoint in expected_endpoints:
            if endpoint in api_routes:
                print(f"✅ {endpoint}")
            else:
                print(f"❌ {endpoint} - MISSING")
                missing_endpoints.append(endpoint)
        
        if missing_endpoints:
            print(f"\n❌ Missing {len(missing_endpoints)} endpoints:")
            for endpoint in missing_endpoints:
                print(f"   - {endpoint}")
            return False
        else:
            print(f"\n🎉 All {len(expected_endpoints)} expected endpoints found!")
            return True
            
    except Exception as e:
        print(f"❌ Error importing web server: {e}")
        return False

if __name__ == "__main__":
    success = test_all_api_endpoints()
    if success:
        print("\n✅ All API endpoints are available")
        print("Dashboard should work without 404 errors!")
    else:
        print("\n❌ Some API endpoints are missing")
    
    sys.exit(0 if success else 1)
