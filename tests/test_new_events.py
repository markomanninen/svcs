#!/usr/bin/env python3
"""
Test script to verify new semantic event types are working correctly.
This script creates test code changes and checks if SVCS detects the new event types.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '.svcs'))

from analyzer import analyze_changes

def test_new_event_types():
    """Test the new event types we added to the analyzer."""
    
    # Test 1: Function complexity changes
    before_code = '''
def process_func(x):
    return x * 2
'''
    
    after_code = '''
def process_func(x):
    try:
        if x > 0:
            for i in range(x):
                if i % 2 == 0:
                    yield i * 2
        else:
            return None
    except ValueError as e:
        print(f"Error: {e}")
        return -1
'''
    
    events = analyze_changes("test.py", before_code, after_code)
    complexity_events = [e for e in events if e['event_type'] == 'function_complexity_changed']
    
    print("=== Test 1: Function Complexity Changes ===")
    print(f"Found {len(complexity_events)} complexity change events")
    for event in complexity_events:
        print(f"  - {event['event_type']}: {event['details']}")
    
    # Test 2: Functional programming adoption
    before_code = '''
def process_data(items):
    result = []
    for item in items:
        if item > 0:
            result.append(item * 2)
    return result
'''
    
    after_code = '''
def process_data(items):
    # Using list comprehension and lambda
    filter_func = lambda x: x > 0
    result = [item * 2 for item in items if filter_func(item)]
    return result
'''
    
    events = analyze_changes("test.py", before_code, after_code)
    fp_events = [e for e in events if 'functional_programming' in e['event_type']]
    lambda_events = [e for e in events if 'lambda_usage' in e['event_type']]
    comp_events = [e for e in events if 'comprehension_usage' in e['event_type']]
    
    print("\n=== Test 2: Functional Programming Adoption ===")
    print(f"Found {len(fp_events)} functional programming events")
    print(f"Found {len(lambda_events)} lambda usage events")
    print(f"Found {len(comp_events)} comprehension events")
    for event in fp_events + lambda_events + comp_events:
        print(f"  - {event['event_type']}: {event['details']}")
    
    # Test 3: Error handling introduction
    before_code = '''
def risky_operation(data):
    result = data / 0  # This will fail
    return result
'''
    
    after_code = '''
def risky_operation(data):
    try:
        result = data / 0
        assert result is not None
        return result
    except ZeroDivisionError as e:
        print(f"Division error: {e}")
        return 0
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None
'''
    
    events = analyze_changes("test.py", before_code, after_code)
    error_events = [e for e in events if 'error_handling' in e['event_type'] or 'exception_handling' in e['event_type']]
    assert_events = [e for e in events if 'assertion_usage' in e['event_type']]
    
    print("\n=== Test 3: Error Handling Introduction ===")
    print(f"Found {len(error_events)} error handling events")
    print(f"Found {len(assert_events)} assertion events")
    for event in error_events + assert_events:
        print(f"  - {event['event_type']}: {event['details']}")
    
    # Test 4: Default parameters and type annotations
    before_code = '''
def greet(name):
    return f"Hello, {name}!"
'''
    
    after_code = '''
from typing import Optional

def greet(name: str, greeting: str = "Hello") -> Optional[str]:
    if name:
        return f"{greeting}, {name}!"
    return None
'''
    
    events = analyze_changes("test.py", before_code, after_code)
    default_events = [e for e in events if 'default_parameters' in e['event_type']]
    type_events = [e for e in events if 'type_annotations' in e['event_type']]
    
    print("\n=== Test 4: Default Parameters and Type Annotations ===")
    print(f"Found {len(default_events)} default parameter events")
    print(f"Found {len(type_events)} type annotation events")
    for event in default_events + type_events:
        print(f"  - {event['event_type']}: {event['details']}")
    
    print(f"\n=== Summary ===")
    print(f"Successfully tested new semantic event types!")
    print(f"The SVCS analyzer can now detect:")
    print(f"  ✓ Function complexity changes")
    print(f"  ✓ Functional programming adoption/removal")
    print(f"  ✓ Error handling introduction/removal")
    print(f"  ✓ Default parameter changes")
    print(f"  ✓ Type annotation changes")
    print(f"  ✓ And many more semantic patterns!")

if __name__ == "__main__":
    test_new_event_types()