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
    
    # Categorize PHP-specific events
    php_categories = {
        'Classes & Objects': ['class:', 'interface:', 'trait:'],
        'Methods & Functions': ['func:'],
        'Properties & Constants': ['prop:', 'const:'],
        'Dependencies': ['namespace:', 'implements:', 'extends:'],
        'Module Changes': ['module:']
    }
    
    print("\n🎯 PHP EVENT CATEGORIES")
    for category, prefixes in php_categories.items():
        category_events = [e for e in php_events 
                         if any(e['node_id'].startswith(prefix) for prefix in prefixes)]
        if category_events:
            print(f"\n📋 {category} ({len(category_events)} events):")
            
            # Group by event type
            event_types = {}
            for event in category_events:
                event_type = event['event_type']
                if event_type not in event_types:
                    event_types[event_type] = []
                event_types[event_type].append(event)
            
            for event_type, type_events in event_types.items():
                print(f"   • {event_type}: {len(type_events)} events")
                for event in type_events[:3]:  # Show first 3 examples
                    node_name = event['node_id'].split(':')[-1]
                    print(f"     - {node_name}")
                if len(type_events) > 3:
                    print(f"     ... and {len(type_events) - 3} more")
    
    # Show PHP-specific patterns detected
    print("\n🔍 PHP-SPECIFIC PATTERNS DETECTED")
    
    patterns = {
        'Namespaces': len([e for e in php_events if 'namespace:' in e.get('details', '')]),
        'Interfaces': len([e for e in php_events if e['node_id'].startswith('interface:')]),
        'Traits': len([e for e in php_events if e['node_id'].startswith('trait:')]),
        'Properties': len([e for e in php_events if e['node_id'].startswith('prop:')]),
        'Constants': len([e for e in php_events if e['node_id'].startswith('const:')]),
        'Interface Implementations': len([e for e in php_events if 'implements:' in e.get('details', '')])
    }
    
    for pattern, count in patterns.items():
        if count > 0:
            print(f"   • {pattern}: {count}")
    
    # Show evolution of specific PHP files
    print("\n📈 PHP FILE EVOLUTION")
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
