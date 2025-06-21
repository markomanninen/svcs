#!/usr/bin/env python3
"""
Test script to verify the conversational interface improvements.
This simulates how the LLM should handle performance optimization queries.
"""
import sys
import os

# Change to parent directory so database paths work correctly
os.chdir('..')
sys.path.append('.svcs')

from api import (
    search_semantic_patterns, 
    get_recent_activity, 
    search_events_advanced,
    debug_query_tools
)

def simulate_llm_conversation():
    """Simulate how the LLM should handle a performance optimization query."""
    
    print("🤖 SIMULATED LLM CONVERSATION TEST")
    print("=" * 50)
    
    # Simulate user query: "Show me performance optimizations from the last 7 days"
    print("\n👤 User: \"Show me performance optimizations from the last 7 days\"")
    print("\n🤖 Assistant: Let me search for performance optimizations in the recent activity.")
    
    # Step 1: Try the primary approach
    print("\n🔍 Step 1: Using search_semantic_patterns(pattern_type='performance')...")
    perf_results = search_semantic_patterns(pattern_type="performance", min_confidence=0.6, limit=10)
    print(f"Found {len(perf_results)} performance optimization results")
    
    if perf_results:
        print("\n✅ SUCCESS: Found performance optimizations!")
        for i, result in enumerate(perf_results[:3], 1):
            location = result.get('location', 'unknown')
            confidence = result.get('confidence', 0)
            date = result.get('readable_date', 'unknown')[:16]
            details = result.get('details', 'No details')[:100]
            print(f"{i}. **{location}** (confidence: {confidence:.0%}, date: {date})")
            print(f"   {details}...")
            print()
        return True
    
    print("❌ No results from semantic patterns search")
    
    # Step 2: Try alternative approach  
    print("\n🔍 Step 2: Using search_events_advanced with specific event types...")
    advanced_results = search_events_advanced(
        event_types=["abstract_performance_optimization"],
        since_date="2025-06-14",  # 7 days ago from current date
        limit=10
    )
    print(f"Found {len(advanced_results)} results with advanced search")
    
    if advanced_results:
        print("\n✅ SUCCESS: Found performance optimizations with advanced search!")
        for result in advanced_results[:3]:
            location = result.get('location', 'unknown')
            confidence = result.get('confidence', 0)
            date = result.get('readable_date', 'unknown')[:16]
            print(f"• **{location}** (confidence: {confidence:.0%}, date: {date})")
        return True
    
    print("❌ No results from advanced search")
    
    # Step 3: Use debug tool to understand what's available
    print("\n🔍 Step 3: Using debug_query_tools to understand available data...")
    debug_info = debug_query_tools("performance optimizations in last 7 days")
    
    print(f"📊 Debug Information:")
    print(f"   Total events in database: {debug_info.get('total_events', 0)}")
    print(f"   Recent events (7 days): {debug_info.get('recent_events', 0)}")
    print(f"   Performance events (7 days): {debug_info.get('performance_events', 0)}")
    print(f"   AI events (7 days): {debug_info.get('ai_events', 0)}")
    
    approaches = debug_info.get('approaches', {})
    print(f"   Different search approaches found:")
    for approach, count in approaches.items():
        print(f"     - {approach}: {count} results")
    
    # Step 4: Suggest alternatives based on debug info
    print(f"\n🤖 Assistant: Based on the available data, I found:")
    
    total_perf = debug_info.get('performance_events', 0)
    if total_perf > 0:
        print(f"✅ {total_perf} performance-related events in the last 7 days.")
        print("Let me try with a lower confidence threshold...")
        
        # Try with lower confidence
        lower_conf_results = search_semantic_patterns(pattern_type="performance", min_confidence=0.5, limit=10)
        if lower_conf_results:
            print(f"Found {len(lower_conf_results)} results with lower confidence threshold:")
            for result in lower_conf_results[:3]:
                location = result.get('location', 'unknown') 
                confidence = result.get('confidence', 0)
                print(f"• **{location}** (confidence: {confidence:.0%})")
            return True
    else:
        print("❌ No performance-related events found in the last 7 days.")
        print("Let me check what types of events are available:")
        sample_types = debug_info.get('sample_recent_event_types', [])
        print("Recent event types:", ', '.join(sample_types[:5]))
    
    return False

def test_direct_api_calls():
    """Test the API functions directly to ensure they work."""
    print("\n" + "=" * 50)
    print("🔧 DIRECT API FUNCTION TESTS")
    print("=" * 50)
    
    # Test 1: search_semantic_patterns
    print("\n1. Testing search_semantic_patterns(pattern_type='performance'):")
    results1 = search_semantic_patterns(pattern_type="performance", min_confidence=0.5)
    print(f"   Results: {len(results1)}")
    if results1:
        print(f"   Sample: {results1[0].get('event_type')} in {results1[0].get('location')} ({results1[0].get('confidence', 0):.0%})")
    
    # Test 2: search_events_advanced
    print("\n2. Testing search_events_advanced with performance event types:")
    results2 = search_events_advanced(event_types=["abstract_performance_optimization"])
    print(f"   Results: {len(results2)}")
    if results2:
        print(f"   Sample: {results2[0].get('event_type')} in {results2[0].get('location')} ({results2[0].get('confidence', 0):.0%})")
    
    # Test 3: get_recent_activity
    print("\n3. Testing get_recent_activity(days=7):")
    results3 = get_recent_activity(days=7)
    perf_in_recent = [r for r in results3 if 'performance' in r.get('event_type', '').lower()]
    print(f"   Total recent: {len(results3)}, Performance-related: {len(perf_in_recent)}")
    
    # Test 4: debug_query_tools
    print("\n4. Testing debug_query_tools:")
    debug_info = debug_query_tools("test query")
    print(f"   Total events: {debug_info.get('total_events', 0)}")
    print(f"   Recent events: {debug_info.get('recent_events', 0)}")
    print(f"   Performance events: {debug_info.get('performance_events', 0)}")

if __name__ == "__main__":
    # Run the simulated conversation
    success = simulate_llm_conversation()
    
    # Run direct API tests
    test_direct_api_calls()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ SIMULATION SUCCESSFUL: The LLM should be able to find performance optimizations")
    else:
        print("❌ SIMULATION FAILED: Need to investigate further")
    print("=" * 50)
