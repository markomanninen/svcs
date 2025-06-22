#!/usr/bin/env python3
"""
PHP Language Support Demo for SVCS
Demonstrates tracking of PHP-specific semantic patterns
"""

import sys
import os

sys.path.insert(0, '.svcs')
from api import get_full_log

def demonstrate_php_support():
    """Demonstrate PHP language support in SVCS."""
    
    print("🐘 PHP LANGUAGE SUPPORT DEMONSTRATION")
    print("=" * 50)
    
    # Get all events
    events = get_full_log()
    
    # Filter PHP events
    php_events = [e for e in events if e['location'].endswith('.php')]
    
    if not php_events:
        print("❌ No PHP events found. Make sure to commit some PHP files!")
        return
    
    print(f"📊 Total PHP Events: {len(php_events)}")
    print(f"📁 PHP Files Tracked: {len(set(e['location'] for e in php_events))}")
    
    # Enhanced categorization for new event types
    print("\n🎯 DETAILED PHP EVENT CATEGORIES & EXAMPLES")
    print("Note: The richness of detected events depends on the underlying PHP parser.")
    print("If using fallback regex parser, many detailed events may not appear.")

    detailed_event_types = {
        "PHP Structure Changes": [
            "node_added", "node_removed",
            "php_namespace_changed", # Assuming this might be an event type
            "php_use_statement_added", "php_use_statement_removed"
        ],
        "PHP Function/Method Changes": [
            "php_node_signature_changed", "php_return_type_changed",
            "php_node_logic_changed", "php_visibility_changed",
            "php_static_modifier_changed", "php_abstract_modifier_changed",
            "php_final_modifier_changed"
        ],
        "PHP Class/Interface/Trait Changes": [
            "php_inheritance_changed", "php_interface_extends_changed",
            "php_trait_usage_changed", # Placeholder for future
            "php_abstract_modifier_changed", "php_final_modifier_changed"
            # node_added/removed for methods/properties are covered by general structure
        ],
        "PHP Property Changes": [
            "php_typed_property_changed", "php_property_default_value_changed",
            # php_visibility_changed, php_static_modifier_changed (covered above)
        ],
        "PHP Constant Changes": [
            "php_constant_value_changed",
            # php_visibility_changed (covered above)
        ],
        "PHP Metadata Changes": [
            "php_attribute_added", "php_attribute_removed", "php_docstring_changed"
        ],
        "Basic Fallback Events": [ # Events more likely from regex fallback
             "variable_usage_changed", "dependency_added", "dependency_removed"
        ]
    }

    for category, event_type_list in detailed_event_types.items():
        category_events_found = []
        for event_type_name in event_type_list:
            typed_events = [e for e in php_events if e['event_type'] == event_type_name]
            if typed_events:
                if not category_events_found: # Print category header only if events exist
                    print(f"\n📋 {category}:")
                category_events_found.extend(typed_events)
                print(f"   Events of type '{event_type_name}': {len(typed_events)}")
                for event in typed_events[:2]: # Show first 2 examples
                    node_name = event['node_id']
                    details = event.get('details', 'No details')
                    if len(details) > 120: details = details[:117] + "..."
                    print(f"     - Node: {node_name}, Details: {details}")
                if len(typed_events) > 2:
                    print(f"     ... and {len(typed_events) - 2} more.")

    # Highlight some specific advanced changes if present
    print("\n🔍 HIGHLIGHTING SPECIFIC ADVANCED PATTERNS")
    advanced_highlights = {
        "Attribute Changes": ["php_attribute_added", "php_attribute_removed"],
        "Signature Changes": ["php_node_signature_changed"],
        "Return Type Changes": ["php_return_type_changed"],
        "Inheritance Changes": ["php_inheritance_changed", "php_interface_extends_changed"],
        "Typed Property Changes": ["php_typed_property_changed"]
    }
    has_advanced_highlights = False
    for desc, types_to_check in advanced_highlights.items():
        count = sum(1 for e in php_events if e['event_type'] in types_to_check)
        if count > 0:
            has_advanced_highlights = True
            print(f"   • {desc} detected: {count} instance(s)")
    if not has_advanced_highlights:
        print("   No specific advanced patterns (from the highlight list) detected in this set of events.")


    # Show evolution of specific PHP files (remains useful)
    print("\n📈 PHP FILE EVOLUTION (Summary)")
    php_files = set(e['location'] for e in php_events)
    
    for php_file in sorted(php_files):
        file_events = [e for e in php_events if e['location'] == php_file]
        print(f"\n📄 {php_file} ({len(file_events)} events)")
        
        # Show recent events
        recent_events = sorted(file_events, key=lambda x: x['timestamp'], reverse=True)[:5]
        for event in recent_events:
            node_name = event['node_id'].split(':')[-1]
            print(f"   • {event['event_type']}: {node_name}")
    
    print(f"\n✅ PHP language support is working! SVCS can now track semantic changes in PHP files.")
    print(f"🎯 Supported file extensions: .php, .phtml, .php3, .php4, .php5, .phps")

if __name__ == "__main__":
    demonstrate_php_support()
