#!/usr/bin/env python3
"""
Comprehensive API Testing Script with Real Data
Tests all svcs.api functions with the populated semantic.db
"""

import sys
import os
sys.path.append('.')

from svcs.api import *
import json

def print_header(title):
    """Print a formatted header."""
    print(f"\n{'=' * 60}")
    print(f"🧪 {title}")
    print('=' * 60)

def print_results(results, title, limit=5):
    """Print results in a formatted way."""
    print(f"\n📊 {title}:")
    if isinstance(results, list):
        print(f"   Found {len(results)} items")
        for i, item in enumerate(results[:limit]):
            if isinstance(item, dict):
                # Pretty print key fields
                if 'event_type' in item:
                    print(f"   {i+1}. {item.get('event_type', 'N/A')} - {item.get('node_id', 'N/A')} @ {item.get('location', 'N/A')}")
                elif 'commit_hash' in item:
                    print(f"   {i+1}. {item.get('commit_hash', 'N/A')[:8]} by {item.get('author', 'N/A')} - {item.get('message', 'N/A')[:50]}")
                else:
                    print(f"   {i+1}. {str(item)[:100]}")
            else:
                print(f"   {i+1}. {str(item)[:100]}")
        if len(results) > limit:
            print(f"   ... and {len(results) - limit} more")
    elif isinstance(results, dict):
        print(f"   Keys: {list(results.keys())}")
        for key, value in list(results.items())[:3]:
            print(f"   {key}: {str(value)[:80]}")
    else:
        print(f"   Result: {str(results)[:200]}")

def test_all_api_functions():
    """Test all API functions comprehensively."""
    
    print_header("COMPREHENSIVE API TESTING WITH REAL DATA")
    
    # Test 1: Basic query functions
    print_header("1. BASIC QUERY FUNCTIONS")
    
    try:
        commits = get_valid_commit_hashes()
        commits_list = list(commits) if isinstance(commits, set) else commits
        print_results(commits_list, "Valid Commit Hashes", 3)
        sample_commit = commits_list[0] if commits_list else None
    except Exception as e:
        print(f"❌ get_valid_commit_hashes failed: {e}")
        sample_commit = None
    
    try:
        full_log = get_full_log()
        print_results(full_log, "Full Log")
    except Exception as e:
        print(f"❌ get_full_log failed: {e}")
    
    # Test 2: Search functions
    print_header("2. SEARCH FUNCTIONS")
    
    try:
        # Basic search - provide at least one parameter
        events = search_events(event_type="function_added")
        print_results(events, "Function Added Events")
        
        # Search by author
        events_by_author = search_events(author="alice@example.com")
        print_results(events_by_author, "Events by Alice")
        
        # Search by node_id
        events_by_node = search_events(node_id="func:process_data")
        print_results(events_by_node, "Events for func:process_data")
        
    except Exception as e:
        print(f"❌ search_events failed: {e}")
    
    # Test 3: Advanced search
    print_header("3. ADVANCED SEARCH")
    
    try:
        advanced_results = search_events_advanced(
            limit=10,
            min_confidence=0.8,
            event_types=["function_added", "class_added"],
            order_by="confidence",
            order_desc=True
        )
        print_results(advanced_results, "High Confidence Function/Class Additions")
    except Exception as e:
        print(f"❌ search_events_advanced failed: {e}")
    
    # Test 4: Node evolution
    print_header("4. NODE EVOLUTION TRACKING")
    
    try:
        # Find a sample node ID from the data
        sample_events = search_events_advanced(limit=5)
        if sample_events:
            sample_node = sample_events[0].get('node_id')
            if sample_node:
                evolution = get_node_evolution(sample_node)
                print_results(evolution, f"Evolution of {sample_node}")
    except Exception as e:
        print(f"❌ get_node_evolution failed: {e}")
    
    # Test 5: Recent activity
    print_header("5. RECENT ACTIVITY")
    
    try:
        recent = get_recent_activity(days=7, limit=10)
        print_results(recent, "Recent Activity (7 days)")
    except Exception as e:
        print(f"❌ get_recent_activity failed: {e}")
    
    # Test 6: Project statistics
    print_header("6. PROJECT STATISTICS")
    
    try:
        stats = get_project_statistics()
        print_results(stats, "Project Statistics")
    except Exception as e:
        print(f"❌ get_project_statistics failed: {e}")
    
    # Test 7: Semantic patterns
    print_header("7. SEMANTIC PATTERNS")
    
    try:
        patterns = search_semantic_patterns(
            pattern_type="architecture",
            min_confidence=0.7,
            limit=5
        )
        print_results(patterns, "Architecture Patterns")
    except Exception as e:
        print(f"❌ search_semantic_patterns failed: {e}")
    
    # Test 8: Commit-specific functions
    print_header("8. COMMIT-SPECIFIC FUNCTIONS")
    
    # Get a real commit hash from our database
    try:
        real_commits = search_events_advanced(limit=1)
        if real_commits and real_commits[0].get('commit_hash'):
            sample_commit = real_commits[0]['commit_hash']
        
        if sample_commit:
            try:
                commit_details = get_commit_details(sample_commit)
                print_results(commit_details, f"Details for {sample_commit[:8]}")
            except Exception as e:
                print(f"❌ get_commit_details failed: {e}")
            
            try:
                commit_summary = get_commit_summary(sample_commit)
                print_results(commit_summary, f"Summary for {sample_commit[:8]}")
            except Exception as e:
                print(f"❌ get_commit_summary failed: {e}")
        else:
            print("⚠️ No commit hash available for testing")
    except Exception as e:
        print(f"❌ Could not get real commit hash: {e}")
    
    # Test 9: Dependency analysis
    print_header("9. DEPENDENCY ANALYSIS")
    
    try:
        dep_changes = find_dependency_changes("requests")
        print_results(dep_changes, "Changes to 'requests' dependency")
    except Exception as e:
        print(f"❌ find_dependency_changes failed: {e}")
    
    # Test 10: Analytics and quality
    print_header("10. ANALYTICS AND QUALITY")
    
    try:
        analytics = generate_analytics(
            days=30,
            format_type="dict"
        )
        print_results(analytics, "Analytics Report")
    except Exception as e:
        print(f"❌ generate_analytics failed: {e}")
    
    try:
        quality = analyze_quality(verbose=True)
        print_results(quality, "Quality Analysis")
    except Exception as e:
        print(f"❌ analyze_quality failed: {e}")
    
    # Final summary
    print_header("API TESTING COMPLETE")
    print("✅ All API functions have been tested with real semantic data!")
    print("🎯 The semantic database now contains realistic test data for development and testing.")

if __name__ == "__main__":
    test_all_api_functions()
