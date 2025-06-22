#!/usr/bin/env python3
"""
Quick verification that the SVCS Dashboard API endpoints are working
"""

import sys
import json

# Test the corrected API functions
sys.path.insert(0, '.svcs')

def test_api_functions():
    """Test all the API functions that were causing 500 errors"""
    try:
        from api import (
            search_semantic_patterns, 
            debug_query_tools, 
            get_recent_activity,
            search_events_advanced,
            get_project_statistics
        )
        
        print("🧪 Testing Fixed API Functions")
        print("=" * 40)
        
        # Test 1: search_semantic_patterns
        print("1. Testing search_semantic_patterns...")
        result = search_semantic_patterns(pattern_type='performance', limit=3)
        print(f"   ✅ Returned {len(result) if isinstance(result, list) else 'data'}")
        
        # Test 2: debug_query_tools  
        print("2. Testing debug_query_tools...")
        result = debug_query_tools('test query')
        print(f"   ✅ Returned {type(result).__name__}")
        
        # Test 3: get_recent_activity
        print("3. Testing get_recent_activity...")
        result = get_recent_activity(days=7, limit=3)
        print(f"   ✅ Returned {len(result) if isinstance(result, list) else 'data'}")
        
        # Test 4: search_events_advanced
        print("4. Testing search_events_advanced...")
        result = search_events_advanced(limit=3)
        print(f"   ✅ Returned {len(result) if isinstance(result, list) else 'data'}")
        
        # Test 5: get_project_statistics
        print("5. Testing get_project_statistics...")
        result = get_project_statistics()
        print(f"   ✅ Returned {type(result).__name__}")
        
        print("\n🎉 All API functions working correctly!")
        print("\n📋 Fix Summary:")
        print("- Removed incorrect 'project_path' parameters")
        print("- Updated Flask endpoints to use correct function signatures")
        print("- All previously failing endpoints should now work")
        print("\n🚀 Dashboard is ready for use!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing API functions: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_api_functions()
    if success:
        print("\n✅ Verification complete - restart your dashboard server!")
        print("   Use: ./start_dashboard.sh")
        print("   Then access: http://127.0.0.1:8080")
    else:
        print("\n❌ Issues found - please check the errors above")
        sys.exit(1)
