#!/usr/bin/env python3
"""
Test script to check LLM conversational query handling.
"""
import sys
import os

# Change to parent directory so database paths work correctly
os.chdir('..')
sys.path.append('.svcs')

from api import search_semantic_patterns, get_recent_activity, search_events_advanced

def test_performance_queries():
    """Test different ways to find performance optimizations."""
    
    print("=== Testing Different Performance Query Approaches ===\n")
    
    # Test 1: Direct semantic patterns search
    print("1. search_semantic_patterns(pattern_type='performance'):")
    results1 = search_semantic_patterns(pattern_type="performance", limit=5)
    print(f"   Found {len(results1)} results")
    for r in results1[:3]:
        print(f"   - {r.get('event_type', 'unknown')} in {r.get('location', 'unknown')} ({r.get('confidence', 0):.0%})")
    print()
    
    # Test 2: Search by event type
    print("2. search_events_advanced(event_types=['abstract_performance_optimization']):")
    results2 = search_events_advanced(event_types=["abstract_performance_optimization"], limit=5)
    print(f"   Found {len(results2)} results")
    for r in results2[:3]:
        print(f"   - {r.get('event_type', 'unknown')} in {r.get('location', 'unknown')} ({r.get('confidence', 0):.0%})")
    print()
    
    # Test 3: Recent activity with pattern filtering
    print("3. get_recent_activity(days=7) + filtering:")
    recent = get_recent_activity(days=7, limit=20)
    perf_recent = [r for r in recent if 'performance' in r.get('event_type', '').lower() or 'optimization' in r.get('event_type', '').lower()]
    print(f"   Found {len(perf_recent)} performance-related events from recent activity")
    for r in perf_recent[:3]:
        print(f"   - {r.get('event_type', 'unknown')} in {r.get('location', 'unknown')} ({r.get('readable_date', 'unknown')[:16]})")
    print()
    
    # Test 4: Pattern search with broader terms
    print("4. search_semantic_patterns with broader terms:")
    broad_results = []
    for term in ['performance', 'optimization', 'optimized']:
        results = search_semantic_patterns(pattern_type=term, min_confidence=0.6, limit=5)
        broad_results.extend(results)
    
    # Remove duplicates by event_id
    seen_ids = set()
    unique_results = []
    for r in broad_results:
        event_id = r.get('event_id')
        if event_id not in seen_ids:
            seen_ids.add(event_id)
            unique_results.append(r)
    
    print(f"   Found {len(unique_results)} unique results across all optimization terms")
    for r in unique_results[:3]:
        print(f"   - {r.get('event_type', 'unknown')} in {r.get('location', 'unknown')} ({r.get('confidence', 0):.0%})")
    print()
    
    # Test 5: Check what's in the last 7 days specifically
    print("5. All events from last 7 days (to see if date filtering is the issue):")
    import datetime
    seven_days_ago = (datetime.datetime.now() - datetime.timedelta(days=7)).strftime("%Y-%m-%d")
    all_recent = search_events_advanced(since_date=seven_days_ago, limit=50)
    print(f"   Total events in last 7 days: {len(all_recent)}")
    
    perf_in_recent = [r for r in all_recent if 'performance' in r.get('event_type', '').lower() or 'optimization' in r.get('details', '').lower()]
    print(f"   Performance-related events in last 7 days: {len(perf_in_recent)}")
    
    if perf_in_recent:
        print("   Recent performance events:")
        for r in perf_in_recent[:3]:
            date = r.get('readable_date', 'unknown')[:16]
            print(f"   - {r.get('event_type', 'unknown')} on {date} in {r.get('location', 'unknown')}")
    else:
        print("   No performance events found in last 7 days")
        print("   Sample of recent events:")
        for r in all_recent[:5]:
            date = r.get('readable_date', 'unknown')[:16] 
            print(f"   - {r.get('event_type', 'unknown')} on {date}")

if __name__ == "__main__":
    test_performance_queries()
