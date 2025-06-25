#!/usr/bin/env python3

import sys
sys.path.append('/Users/markomanninen/Documents/GitHub/svcs')

from svcs.semantic_analyzer import SVCSModularAnalyzer

def test_generator_made_function():
    print("🔍 Testing generator_made_function detection...")
    
    # Read the actual test case files
    with open('/Users/markomanninen/Documents/GitHub/svcs/test_cases/javascript/generator_made_function/before.js', 'r') as f:
        before_code = f.read()
    
    with open('/Users/markomanninen/Documents/GitHub/svcs/test_cases/javascript/generator_made_function/after.js', 'r') as f:
        after_code = f.read()
    
    print("📋 Generators should be converted to regular functions")
    
    analyzer = SVCSModularAnalyzer()
    
    # Analyze the changes
    events = analyzer.analyze_file_changes('test.js', before_code, after_code)
    
    print(f"\n📊 Total events detected: {len(events)}")
    
    generator_made_function_events = [e for e in events if e.get('event_type') == 'generator_made_function']
    print(f"🎯 generator_made_function events: {len(generator_made_function_events)}")
    
    for event in generator_made_function_events:
        print(f"   • Details: {event.get('details', 'No details')}")
    
    # Show all events for debugging
    print(f"\n📋 ALL EVENTS:")
    for event in events:
        print(f"   • {event.get('event_type')}: {event.get('details', 'No details')} (Layer {event.get('layer', '?')})")
    
    return len(generator_made_function_events) > 0

if __name__ == "__main__":
    success = test_generator_made_function()
    if success:
        print("\n✅ generator_made_function detection is working!")
    else:
        print("\n❌ generator_made_function detection failed!")
