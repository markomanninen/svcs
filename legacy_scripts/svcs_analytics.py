#!/usr/bin/env python3
"""
SVCS Analytics Dashboard - Visual insights into semantic code evolution
"""

import sys
import os
import sqlite3
from collections import defaultdict, Counter
from datetime import datetime, timedelta
import json

sys.path.insert(0, '.svcs')
from api import get_full_log, get_valid_commit_hashes

def generate_analytics_report():
    """Generate comprehensive analytics about semantic code evolution."""
    
    print("🔍 SVCS SEMANTIC ANALYTICS DASHBOARD")
    print("=" * 50)
    
    events = get_full_log()
    
    if not events:
        print("No semantic events found.")
        return
    
    # Basic Statistics
    print(f"\n📊 BASIC STATISTICS")
    print(f"   Total Events: {len(events)}")
    print(f"   Unique Event Types: {len(set(e['event_type'] for e in events))}")
    print(f"   Files Tracked: {len(set(e['location'] for e in events))}")
    print(f"   Contributors: {len(set(e['author'] for e in events))}")
    
    # Event Type Distribution
    print(f"\n🎯 EVENT TYPE DISTRIBUTION")
    event_counts = Counter(e['event_type'] for e in events)
    for event_type, count in event_counts.most_common(10):
        percentage = (count / len(events)) * 100
        bar = "█" * int(percentage / 2)
        print(f"   {event_type:<30} {count:>3} {bar} {percentage:.1f}%")
    
    # Author Activity
    print(f"\n👥 AUTHOR ACTIVITY")
    author_counts = Counter(e['author'] for e in events)
    for author, count in author_counts.most_common(5):
        percentage = (count / len(events)) * 100
        print(f"   {author:<20} {count:>3} events ({percentage:.1f}%)")
    
    # File Evolution Hotspots
    print(f"\n🔥 FILE EVOLUTION HOTSPOTS")
    file_counts = Counter(e['location'] for e in events)
    for filepath, count in file_counts.most_common(10):
        print(f"   {filepath:<40} {count:>3} changes")
    
    # Temporal Analysis
    print(f"\n📈 TEMPORAL ANALYSIS")
    analyze_temporal_patterns(events)
    
    # Complexity Evolution
    print(f"\n🧠 COMPLEXITY EVOLUTION")
    analyze_complexity_trends(events)
    
    # Technology Adoption
    print(f"\n🚀 TECHNOLOGY ADOPTION")
    analyze_technology_adoption(events)
    
    # Generate JSON report
    generate_json_report(events)

def analyze_temporal_patterns(events):
    """Analyze temporal patterns in semantic changes."""
    
    # Group events by day
    daily_activity = defaultdict(int)
    for event in events:
        date = datetime.fromtimestamp(event['timestamp']).date()
        daily_activity[date] += 1
    
    if daily_activity:
        most_active_day = max(daily_activity.items(), key=lambda x: x[1])
        print(f"   Most Active Day: {most_active_day[0]} ({most_active_day[1]} events)")
        
        recent_days = [date for date in daily_activity.keys() 
                      if date >= datetime.now().date() - timedelta(days=7)]
        if recent_days:
            recent_activity = sum(daily_activity[date] for date in recent_days)
            print(f"   Last 7 Days: {recent_activity} events")

def analyze_complexity_trends(events):
    """Analyze complexity-related events and trends."""
    
    complexity_events = [e for e in events if 'complexity' in e['event_type']]
    error_events = [e for e in events if 'error_handling' in e['event_type'] or 'exception' in e['event_type']]
    fp_events = [e for e in events if 'functional_programming' in e['event_type']]
    
    print(f"   Complexity Changes: {len(complexity_events)} events")
    print(f"   Error Handling Evolution: {len(error_events)} events")
    print(f"   Functional Programming Adoption: {len(fp_events)} events")
    
    # Analyze complexity direction
    complexity_increases = [e for e in complexity_events if 'increased' in e.get('details', '')]
    complexity_decreases = [e for e in complexity_events if 'decreased' in e.get('details', '')]
    
    if complexity_increases or complexity_decreases:
        print(f"   Complexity Increases: {len(complexity_increases)}")
        print(f"   Complexity Decreases: {len(complexity_decreases)}")

def analyze_technology_adoption(events):
    """Analyze adoption of modern Python features."""
    
    tech_patterns = {
        'async_programming': ['async', 'await'],
        'type_annotations': ['type_annotations'],
        'decorators': ['decorator'],
        'comprehensions': ['comprehension'],
        'error_handling': ['error_handling', 'exception_handling'],
        'functional_programming': ['lambda', 'functional_programming']
    }
    
    for tech, keywords in tech_patterns.items():
        count = sum(1 for e in events if any(kw in e['event_type'] for kw in keywords))
        if count > 0:
            print(f"   {tech.replace('_', ' ').title()}: {count} events")

def generate_json_report(events):
    """Generate a detailed JSON report for external analysis."""
    
    report = {
        'generated_at': datetime.now().isoformat(),
        'summary': {
            'total_events': len(events),
            'unique_event_types': len(set(e['event_type'] for e in events)),
            'files_tracked': len(set(e['location'] for e in events)),
            'contributors': len(set(e['author'] for e in events))
        },
        'event_type_distribution': dict(Counter(e['event_type'] for e in events)),
        'author_activity': dict(Counter(e['author'] for e in events)),
        'file_hotspots': dict(Counter(e['location'] for e in events)),
        'recent_events': [
            {
                'event_type': e['event_type'],
                'node_id': e['node_id'],
                'location': e['location'],
                'author': e['author'],
                'timestamp': e['timestamp'],
                'details': e['details']
            }
            for e in sorted(events, key=lambda x: x['timestamp'], reverse=True)[:20]
        ]
    }
    
    with open('svcs_analytics_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n💾 DETAILED REPORT")
    print(f"   JSON report saved to: svcs_analytics_report.json")

def show_evolution_timeline():
    """Show a timeline of major semantic changes."""
    
    events = get_full_log()
    
    # Group by commit and show major changes
    commit_events = defaultdict(list)
    for event in events:
        commit_events[event['commit_hash']].append(event)
    
    print(f"\n🕐 EVOLUTION TIMELINE (Recent Commits)")
    print("-" * 50)
    
    for commit_hash in sorted(commit_events.keys(), 
                             key=lambda c: max(e['timestamp'] for e in commit_events[c]),
                             reverse=True)[:5]:
        
        events_in_commit = commit_events[commit_hash]
        timestamp = max(e['timestamp'] for e in events_in_commit)
        author = events_in_commit[0]['author']
        date_str = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M')
        
        print(f"\n📅 {date_str} - {commit_hash[:7]} by {author}")
        
        # Group by event type
        by_type = defaultdict(int)
        for event in events_in_commit:
            by_type[event['event_type']] += 1
        
        for event_type, count in sorted(by_type.items()):
            print(f"   • {event_type}: {count}")

if __name__ == "__main__":
    try:
        generate_analytics_report()
        show_evolution_timeline()
    except Exception as e:
        print(f"Error generating analytics: {e}")
        import traceback
        traceback.print_exc()
