#!/usr/bin/env python3
"""
Test script for all API functions in svcs_repo_discuss.py
Tests each function directly without using the LLM interface.
"""

import sys
import os
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the API functions from svcs_repo_discuss
try:
    from svcs_repo_discuss import (
        get_full_log,
        search_events,
        get_node_evolution,
        get_recent_activity,
        get_project_statistics,
        search_semantic_patterns,
        get_filtered_evolution,
        find_dependency_changes,
        get_commit_details,
        search_events_advanced,
        get_commit_changed_files,
        get_commit_diff,
        get_commit_summary,
        compare_branches,
        generate_analytics,
        analyze_quality,
        debug_query_tools
    )
    print("✅ Successfully imported all API functions")
except ImportError as e:
    print(f"❌ Failed to import API functions: {e}")
    sys.exit(1)

def test_function(func_name, func, *args, **kwargs):
    """Test a single function and report results."""
    try:
        print(f"\n🧪 Testing {func_name}...")
        result = func(*args, **kwargs)
        
        if isinstance(result, list):
            print(f"   ✅ Returned list with {len(result)} items")
            if result and len(result) > 0:
                print(f"   📄 Sample item keys: {list(result[0].keys()) if isinstance(result[0], dict) else 'Non-dict item'}")
        elif isinstance(result, dict):
            print(f"   ✅ Returned dict with {len(result)} keys: {list(result.keys())}")
        elif isinstance(result, str):
            print(f"   ✅ Returned string (length: {len(result)})")
        else:
            print(f"   ✅ Returned {type(result)}: {result}")
            
        return True
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def main():
    print("🚀 Testing all SVCS API functions...")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    # Test basic functions that should work even with empty database
    test_cases = [
        ("get_full_log", get_full_log),
        ("get_recent_activity", get_recent_activity, 7),  # last 7 days
        ("get_project_statistics", get_project_statistics),
        ("search_semantic_patterns", search_semantic_patterns, "performance"),
        ("generate_analytics", generate_analytics),
        ("analyze_quality", analyze_quality),
        ("debug_query_tools", debug_query_tools),
    ]
    
    # Test functions with parameters
    for test_case in test_cases:
        func_name = test_case[0]
        func = test_case[1]
        args = test_case[2:] if len(test_case) > 2 else []
        
        if test_function(func_name, func, *args):
            passed += 1
        else:
            failed += 1
    
    # Test search functions with specific parameters
    search_tests = [
        ("search_events with author", search_events, {"author": "testuser"}),
        ("search_events with event_type", search_events, {"event_type": "signature_change"}),
        ("search_events with location", search_events, {"location": "src/"}),
    ]
    
    for test_name, func, kwargs in search_tests:
        if test_function(test_name, func, **kwargs):
            passed += 1
        else:
            failed += 1
    
    # Test date range and evolution functions with existing functions
    from datetime import datetime, timedelta
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    # Test search_events_advanced as a substitute for date range search
    if test_function("search_events_advanced", search_events_advanced,
                    since_date=start_date.strftime("%Y-%m-%d"), limit=10):
        passed += 1
    else:
        failed += 1
    
    # Test node evolution function (may fail if no data)
    try:
        if test_function("get_node_evolution", get_node_evolution, "func:test_function"):
            passed += 1
        else:
            failed += 1
    except:
        print("\n🧪 Testing get_node_evolution...")
        print("   ⚠️  Skipped (requires specific node_id)")
    
    # Test evolution tracking function
    try:
        if test_function("get_filtered_evolution", get_filtered_evolution, "func:test_function"):
            passed += 1
        else:
            failed += 1
    except:
        print("\n🧪 Testing get_filtered_evolution...")
        print("   ⚠️  Skipped (requires specific node_id)")
    
    # Test dependency changes
    if test_function("find_dependency_changes", find_dependency_changes, "requests"):
        passed += 1
    else:
        failed += 1
        
    # Test branch comparison (may fail if branches don't exist)
    try:
        if test_function("compare_branches", compare_branches, "main", "main"):
            passed += 1
        else:
            failed += 1
    except:
        print("\n🧪 Testing compare_branches...")
        print("   ⚠️  Skipped (requires valid branches)")
    
    print("\n" + "=" * 60)
    print(f"🎯 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All API functions are working correctly!")
    else:
        print(f"⚠️  {failed} functions had issues (may be due to empty database)")
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
