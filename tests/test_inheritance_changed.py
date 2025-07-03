#!/usr/bin/env python3

import sys
sys.path.append('os.path.dirname(os.path.dirname(os.path.abspath(__file__)))')

from svcs.semantic_analyzer import SVCSModularAnalyzer

def test_inheritance_changed():
    print("🔍 Testing inheritance_changed detection...")
    
    # Read the actual test case files
    with open('os.path.dirname(os.path.dirname(os.path.abspath(__file__)))/test_cases/javascript/inheritance_changed/before.js', 'r') as f:
        before_code = f.read()
    
    with open('os.path.dirname(os.path.dirname(os.path.abspath(__file__)))/test_cases/javascript/inheritance_changed/after.js', 'r') as f:
        after_code = f.read()
    
    print("📋 Dog class should extend Animal")
    
    analyzer = SVCSModularAnalyzer()
    
    # Analyze the changes
    events = analyzer.analyze_file_changes('test.js', before_code, after_code)
    
    print(f"\n📊 Total events detected: {len(events)}")
    
    inheritance_changed_events = [e for e in events if e.get('event_type') == 'inheritance_changed']
    print(f"🎯 inheritance_changed events: {len(inheritance_changed_events)}")
    
    for event in inheritance_changed_events:
        print(f"   • Details: {event.get('details', 'No details')}")
    
    # Show all events for debugging
    print(f"\n📋 ALL EVENTS:")
    for event in events:
        print(f"   • {event.get('event_type')}: {event.get('details', 'No details')} (Layer {event.get('layer', '?')})")
    
    return len(inheritance_changed_events) > 0

if __name__ == "__main__":
    success = test_inheritance_changed()
    if success:
        print("\n✅ inheritance_changed detection is working!")
    else:
        print("\n❌ inheritance_changed detection failed!")
