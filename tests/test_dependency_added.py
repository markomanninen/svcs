#!/usr/bin/env python3

import sys
sys.path.append('/Users/markomanninen/Documents/GitHub/svcs')

from svcs.semantic_analyzer import SVCSModularAnalyzer

def test_dependency_added():
    print("🔍 Testing dependency_added detection...")
    
    # Read the actual test case files
    with open('/Users/markomanninen/Documents/GitHub/svcs/test_cases/javascript/dependency_added/before.js', 'r') as f:
        before_code = f.read()
    
    with open('/Users/markomanninen/Documents/GitHub/svcs/test_cases/javascript/dependency_added/after.js', 'r') as f:
        after_code = f.read()
    
    print("📋 Dependencies should be added: lodash, moment, validator")
    
    analyzer = SVCSModularAnalyzer()
    
    # Analyze the changes
    events = analyzer.analyze_file_changes('test.js', before_code, after_code)
    
    print(f"\n📊 Total events detected: {len(events)}")
    
    dependency_added_events = [e for e in events if e.get('event_type') == 'dependency_added']
    print(f"🎯 dependency_added events: {len(dependency_added_events)}")
    
    for event in dependency_added_events:
        print(f"   • Details: {event.get('details', 'No details')}")
    
    # Show all events for debugging
    print(f"\n📋 ALL EVENTS:")
    for event in events:
        print(f"   • {event.get('event_type')}: {event.get('details', 'No details')} (Layer {event.get('layer', '?')})")
    
    return len(dependency_added_events) > 0

if __name__ == "__main__":
    success = test_dependency_added()
    if success:
        print("\n✅ dependency_added detection is working!")
    else:
        print("\n❌ dependency_added detection failed!")
