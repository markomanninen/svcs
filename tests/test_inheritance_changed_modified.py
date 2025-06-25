#!/usr/bin/env python3

import sys
sys.path.append('/Users/markomanninen/Documents/GitHub/svcs')

from svcs.semantic_analyzer import SVCSModularAnalyzer

def test_inheritance_changed_modified():
    print("🔍 Testing inheritance_changed detection (modified class)...")
    
    before_code = """class Animal {
    constructor(name) {
        this.name = name;
    }
    
    speak() {
        return `${this.name} makes a sound`;
    }
}

class Dog {
    constructor(name, breed) {
        this.name = name;
        this.breed = breed;
    }
    
    bark() {
        return `${this.name} barks`;
    }
}"""

    after_code = """class Animal {
    constructor(name) {
        this.name = name;
    }
    
    speak() {
        return `${this.name} makes a sound`;
    }
}

class Dog extends Animal {
    constructor(name, breed) {
        super(name);
        this.breed = breed;
    }
    
    speak() {
        return `${this.name} barks`;
    }
    
    bark() {
        return `${this.name} barks`;
    }
}"""
    
    print("📋 Dog class should change from no inheritance to extending Animal")
    
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
    success = test_inheritance_changed_modified()
    if success:
        print("\n✅ inheritance_changed detection is working!")
    else:
        print("\n❌ inheritance_changed detection failed!")
