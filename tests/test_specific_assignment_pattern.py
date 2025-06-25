#!/usr/bin/env python3

import sys
sys.path.append('/Users/markomanninen/Documents/GitHub/svcs')

from svcs.semantic_analyzer import SVCSModularAnalyzer

def test_specific_assignment_pattern():
    print("🔍 Testing specific assignment pattern case...")
    
    # Read the actual test case files
    with open('/Users/markomanninen/Documents/GitHub/svcs/test_cases/javascript/assignment_pattern/before.js', 'r') as f:
        before_code = f.read()
    
    with open('/Users/markomanninen/Documents/GitHub/svcs/test_cases/javascript/assignment_pattern/after.js', 'r') as f:
        after_code = f.read()
    
    print("📋 BEFORE CODE:")
    print(before_code)
    print("\n📋 AFTER CODE:")
    print(after_code)
    
    analyzer = SVCSModularAnalyzer()
    
    # Analyze the changes
    events = analyzer.analyze_file_changes('test.js', before_code, after_code)
    
    print(f"\n📊 Total events detected: {len(events)}")
    
    assignment_pattern_events = [e for e in events if e.get('event_type') == 'assignment_pattern_changed']
    print(f"🎯 assignment_pattern_changed events: {len(assignment_pattern_events)}")
    
    for event in assignment_pattern_events:
        print(f"   • Node: {event.get('node_id', 'Unknown')}")
        print(f"   • Layer: {event.get('layer', 'Unknown')}")
        print(f"   • Details: {event.get('details', 'No details')}")
    
    # Show all events for debugging
    print(f"\n📋 ALL EVENTS:")
    for event in events:
        print(f"   • {event.get('event_type')}: {event.get('details', 'No details')} (Layer {event.get('layer', '?')})")
    
    return len(assignment_pattern_events) > 0

if __name__ == "__main__":
    success = test_specific_assignment_pattern()
    if success:
        print("\n✅ assignment_pattern_changed detection is working!")
    else:
        print("\n❌ assignment_pattern_changed detection failed!")
