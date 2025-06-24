#!/usr/bin/env python3
"""
Targeted Test Runner

This script runs the modular analyzer on the targeted test cases to detect
specific event types that were missing in our main test suite.
"""

import os
import sys
from pathlib import Path

# Add root directory to path
sys.path.insert(0, str(Path(__file__).parent))

from svcs.semantic_analyzer import SVCSModularAnalyzer

def run_test_case(language, test_case, analyzer=None):
    """Run a specific test case and report the events detected."""
    if analyzer is None:
        analyzer = SVCSModularAnalyzer()
        
    test_dir = f"test_cases/{language}/{test_case}"
    
    # Set correct file extension based on language
    if language == "python":
        ext = "py"
    elif language == "javascript":
        ext = "js"
    elif language == "php":
        ext = "php"
    else:
        ext = language
        
    before_file = f"{test_dir}/before.{ext}"
    after_file = f"{test_dir}/after.{ext}"
    
    # Ensure files exist
    if not os.path.exists(before_file) or not os.path.exists(after_file):
        print(f"❌ Test case files not found: {before_file} or {after_file}")
        return []
    
    # Read files
    with open(before_file, 'r') as f:
        before_content = f.read()
    
    with open(after_file, 'r') as f:
        after_content = f.read()
    
    # Run analysis
    file_path = f"test.{ext}"
    events = analyzer.analyze_file_changes(file_path, before_content, after_content)
    
    # Print results
    emoji = {"python": "🐍", "javascript": "🟨", "php": "🐘"}
    print(f"\n{emoji.get(language, '🔍')} {language.upper()}: {test_case}")
    print("=" * 50)
    print(f"📈 Events detected: {len(events)}")
    
    # Get unique event types
    event_types = set(e.get('event_type') for e in events)
    print(f"🎯 Event types: {len(event_types)}")
    print(f"   {sorted(event_types)}")
    
    # Group by layer
    by_layer = {}
    for event in events:
        layer = event.get('layer', 'unknown')
        if layer not in by_layer:
            by_layer[layer] = []
        by_layer[layer].append(event)
    
    for layer in sorted(by_layer.keys()):
        layer_events = by_layer[layer]
        print(f"\n🔍 Layer {layer}: {len(layer_events)} events")
        for event in layer_events:
            print(f"   • {event.get('event_type', 'unknown')}: {event.get('details', '')}")
    
    return events

def main():
    """Run all targeted test cases."""
    print("🎯 TARGETED EVENT TYPE TEST RUNNER")
    print("=" * 60)
    
    analyzer = SVCSModularAnalyzer()
    all_events = []
    all_event_types = set()
    
    # Language-specific events and event types
    language_events = {
        "python": [],
        "javascript": [],
        "php": []
    }
    language_event_types = {
        "python": set(),
        "javascript": set(),
        "php": set()
    }
    
    # Python tests
    python_tests = [
        "comprehensions", 
        "decorators", 
        "lambdas_functional", 
        "augmented_assignment",
        "decorator_removal",
        "yield_pattern",
        "inheritance",
        "default_parameters_added",
        "default_parameters_removed",
        "function_made_async",
        "function_made_generator",
        "function_made_sync",
        "global_scope_changed",
        "nonlocal_scope_changed",
        "file_added",
        "file_removed",
        "assertion_usage",
        "class_attributes",
        "exception_handling_changed",
        "exception_handling_removed",
        "functional_programming_changed",
        "boolean_literal_usage_changed"
    ]
    for test in python_tests:
        events = run_test_case("python", test, analyzer)
        all_events.extend(events)
        all_event_types.update(e.get('event_type') for e in events)
        language_events["python"].extend(events)
        language_event_types["python"].update(e.get('event_type') for e in events)
    
    # JavaScript tests
    js_tests = [
        "functional", 
        "default_parameters",
        "default_parameters_removed",
        "functional_programming_removed",
        "assertion_usage",
        "assignment_pattern",
        "attribute_access",
        "augmented_assignment",
        "class_attributes",
        "comprehension_usage",
        "control_flow",
        "decorator_added",
        "default_parameters_added",
        "dependency_removed",
        "error_handling_introduced",
        "error_handling_removed",
        "exception_handling_added",
        "exception_handling_changed", 
        "exception_handling_removed",
        "function_complexity",
        "function_made_async",
        "function_made_generator",
        "global_scope_changed",
        "inheritance_changed",
        "internal_call_added",
        "lambda_usage",
        "nonlocal_scope_changed",
        "return_pattern",
        "subscript_access",
        "yield_pattern",
        "async_addition",
        "file_added",
        "file_removed"
    ]
    for test in js_tests:
        events = run_test_case("javascript", test, analyzer)
        all_events.extend(events)
        all_event_types.update(e.get('event_type') for e in events)
        language_events["javascript"].extend(events)
        language_event_types["javascript"].update(e.get('event_type') for e in events)
    
    # PHP tests
    php_tests = ["inheritance", "exception_handling"]
    for test in php_tests:
        events = run_test_case("php", test, analyzer)
        all_events.extend(events)
        all_event_types.update(e.get('event_type') for e in events)
        language_events["php"].extend(events)
        language_event_types["php"].update(e.get('event_type') for e in events)
    
    
    # Summary
    print("\n🏆 TARGETED TEST RESULTS:")
    print("=" * 30)
    print(f"📊 Total events detected: {len(all_events)}")
    print(f"🎯 Unique event types: {len(all_event_types)}")
    print(f"📋 Event types detected:")
    for event_type in sorted(all_event_types):
        print(f"   • {event_type}")
    
    # Check for targeted event types
    targeted_types = [
        "comprehension_usage_changed",
        "decorator_added",
        "decorator_removed",
        "lambda_usage_changed",
        "functional_programming_adopted",
        "augmented_assignment_changed",
        "inheritance_changed",
        "yield_pattern_changed"
    ]
    
    detected_targeted = all_event_types.intersection(targeted_types)
    missing_targeted = set(targeted_types) - all_event_types
    
    print(f"\n🎯 TARGETED EVENT TYPES:")
    print(f"✅ Detected: {len(detected_targeted)}")
    for event_type in sorted(detected_targeted):
        print(f"   • {event_type}")
    
    print(f"\n❓ Still missing: {len(missing_targeted)}")
    for event_type in sorted(missing_targeted):
        print(f"   • {event_type}")
        
    # Calculate coverage metrics
    # Get all defined events from event_missing_report.py
    try:
        from pathlib import Path
        import re
        
        layer_dir = Path(__file__).parent / 'svcs' / 'layers'
        defined_types = set()
        pattern = re.compile(r'"event_type":\s*"([\w_]+)"')
        
        for file in layer_dir.glob('layer*.py'):
            text = file.read_text()
            for match in pattern.finditer(text):
                defined_types.add(match.group(1))
        
        # Calculate coverage
        previously_detected = {
            'api_breaking_change', 'assignment_pattern_changed', 'attribute_access_changed',
            'binary_operator_usage_changed', 'class_methods_changed', 'code_complication',
            'comparison_operator_usage_changed', 'concurrency_introduction', 'control_flow_changed',
            'dependency_added', 'error_handling_introduced', 'function_complexity_changed',
            'function_made_sync', 'generator_made_function', 'internal_call_added',
            'internal_call_removed', 'logical_operator_usage_changed', 'node_added',
            'node_removed', 'numeric_literal_usage_changed', 'refactoring_extract_method',
            'return_pattern_changed', 'security_improvement', 'signature_changed',
            'string_literal_usage_changed', 'subscript_access_changed', 'unary_operator_usage_changed'
        }
        
        # Combine previously detected and new detections
        total_detected = previously_detected.union(all_event_types)
        
        # Filter total_detected to only include defined event types
        valid_detected = total_detected.intersection(defined_types)
        
        # Calculate coverage
        coverage_pct = (len(valid_detected) / len(defined_types)) * 100
        
        print("\n📊 EVENT TYPE COVERAGE ANALYSIS:")
        print(f"   • Total defined event types: {len(defined_types)}")
        print(f"   • Previously detected types: {len(previously_detected)}")
        print(f"   • New types detected in targeted tests: {len(all_event_types - previously_detected)}")
        print(f"   • Total detected types (including non-standard): {len(total_detected)}")
        print(f"   • Valid detected types (within defined set): {len(valid_detected)}")
        print(f"   • Overall coverage: {coverage_pct:.1f}%")
        
        # Language-specific coverage
        print("\n🌐 LANGUAGE-SPECIFIC COVERAGE:")
        for lang in ["python", "javascript", "php"]:
            lang_events = language_events[lang]
            lang_types = language_event_types[lang]
            lang_tests = len(python_tests if lang == "python" else js_tests if lang == "javascript" else php_tests)
            lang_valid_types = lang_types.intersection(defined_types)
            lang_coverage = (len(lang_valid_types) / len(defined_types)) * 100 if defined_types else 0
            
            emoji = {"python": "🐍", "javascript": "🟨", "php": "🐘"}[lang]
            print(f"\n{emoji} {lang.upper()} COVERAGE:")
            print(f"   • Test cases: {lang_tests}")
            print(f"   • Events detected: {len(lang_events)}")
            print(f"   • Unique event types (all): {len(lang_types)}")
            print(f"   • Valid event types: {len(lang_valid_types)} ({lang_coverage:.1f}%)")
            print(f"   • Valid event types detected:")
            for event_type in sorted(lang_valid_types):
                print(f"     - {event_type}")
        
        # List newly detected types
        new_types = all_event_types - previously_detected
        if new_types:
            print("\n🎉 NEWLY DETECTED EVENT TYPES:")
            for t in sorted(new_types):
                print(f"   • {t}")
        
        # List remaining missing types
        missing_types = defined_types - total_detected
        if missing_types:
            print("\n❓ REMAINING UNDETECTED EVENT TYPES:")
            for t in sorted(missing_types):
                print(f"   • {t}")
    
    except Exception as e:
        print(f"\n❌ Error calculating coverage: {e}")

if __name__ == "__main__":
    main()
