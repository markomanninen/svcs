#!/usr/bin/env python3
"""
SVCS Repository Analytics Dashboard - Git-integrated semantic code evolution insights

This is the repository-local version of svcs_analytics.py, designed to work with
the new .svcs/semantic.db architecture while providing enhanced git integration.

Key Changes from Legacy Version:
- Reads from local .svcs/semantic.db instead of global database
- Enhanced with git commit/branch correlation
- Added branch-specific analytics
- Git-aware timeline visualization
- Preserved all existing analytics functions

Usage:
    python3 svcs_repo_analytics.py
    python3 svcs_repo_analytics.py --branch main
    python3 svcs_repo_analytics.py --export-json
"""

import sys
import os
import sqlite3
import subprocess
from collections import defaultdict, Counter
from datetime import datetime, timedelta
import json
import argparse

# Import from repository-local .svcs/api.py
sys.path.insert(0, 'svcs')
try:
    from api import get_full_log, get_valid_commit_hashes
except ImportError:
    print("❌ Error: Could not import from .svcs/api.py")
    print("   Make sure you're running this from a repository with SVCS initialized")
    print("   Run 'svcs init' first if this is a new repository")
    sys.exit(1)

def get_git_info():
    """Get git repository information."""
    try:
        # Get current branch
        current_branch = subprocess.run(
            ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
            capture_output=True, text=True, check=True
        ).stdout.strip()
        
        # Get all branches
        all_branches = subprocess.run(
            ['git', 'branch', '--format=%(refname:short)'],
            capture_output=True, text=True, check=True
        ).stdout.strip().split('\n')
        
        # Get repository name
        repo_name = subprocess.run(
            ['git', 'rev-parse', '--show-toplevel'],
            capture_output=True, text=True, check=True
        ).stdout.strip().split('/')[-1]
        
        return {
            'current_branch': current_branch,
            'all_branches': [b for b in all_branches if b],
            'repo_name': repo_name
        }
    except subprocess.CalledProcessError:
        return {
            'current_branch': 'unknown',
            'all_branches': [],
            'repo_name': 'unknown'
        }

def get_events_for_branch(branch=None):
    """Get semantic events filtered by git branch."""
    events = get_full_log()
    
    if not branch:
        return events
        
    # Filter events by git commits on the specified branch
    try:
        # Get commits on the specified branch
        branch_commits = subprocess.run(
            ['git', 'rev-list', branch],
            capture_output=True, text=True, check=True
        ).stdout.strip().split('\n')
        branch_commits = set(commit for commit in branch_commits if commit)
        
        # Filter events to only those on this branch
        filtered_events = [
            event for event in events 
            if event.get('commit_hash', '').startswith(tuple(branch_commits)) if branch_commits
        ]
        return filtered_events
        
    except subprocess.CalledProcessError:
        print(f"⚠️  Warning: Could not get commits for branch '{branch}', showing all events")
        return events

def generate_repository_analytics_report(branch=None):
    """Generate comprehensive analytics about semantic code evolution for this repository."""
    
    git_info = get_git_info()
    
    print("🔍 SVCS REPOSITORY SEMANTIC ANALYTICS")
    print("=" * 50)
    print(f"📁 Repository: {git_info['repo_name']}")
    print(f"🌿 Current Branch: {git_info['current_branch']}")
    
    if branch:
        print(f"🎯 Analyzing Branch: {branch}")
        events = get_events_for_branch(branch)
    else:
        print(f"🔍 Analyzing: All branches")
        events = get_full_log()
    
    if not events:
        print("\n❌ No semantic events found.")
        print("   Run some git commits with semantic analysis to see results")
        return
    
    # Basic Statistics
    print(f"\n📊 REPOSITORY STATISTICS")
    print(f"   Total Events: {len(events)}")
    print(f"   Unique Event Types: {len(set(e['event_type'] for e in events))}")
    print(f"   Files Tracked: {len(set(e['location'] for e in events))}")
    print(f"   Contributors: {len(set(e['author'] for e in events))}")
    print(f"   Available Branches: {len(git_info['all_branches'])}")
    
    # Git-Enhanced Statistics
    commit_hashes = set(e.get('commit_hash', '') for e in events if e.get('commit_hash'))
    print(f"   Commits with Semantic Data: {len(commit_hashes)}")
    
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
    for file_path, count in file_counts.most_common(8):
        file_name = file_path.split('/')[-1]
        print(f"   {file_name:<25} {count:>3} changes")
    
    # Git Branch Analysis (if multiple branches available)
    if len(git_info['all_branches']) > 1 and not branch:
        print(f"\n🌿 BRANCH ANALYSIS")
        for branch_name in git_info['all_branches'][:5]:  # Top 5 branches
            branch_events = get_events_for_branch(branch_name)
            print(f"   {branch_name:<15} {len(branch_events):>3} events")
    
    # Temporal Analysis
    analyze_temporal_patterns(events)
    
    # Modern Code Analysis
    analyze_technology_adoption(events)

def analyze_temporal_patterns(events):
    """Analyze temporal patterns in semantic changes."""
    print(f"\n📅 TEMPORAL EVOLUTION PATTERNS")
    
    # Group events by date
    daily_events = defaultdict(list)
    for event in events:
        timestamp = event.get('timestamp', 0)
        if timestamp:
            date = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')
            daily_events[date].append(event)
    
    if not daily_events:
        print("   No temporal data available")
        return
    
    # Recent activity (last 30 days)
    recent_cutoff = datetime.now() - timedelta(days=30)
    recent_events = [
        event for event in events 
        if event.get('timestamp', 0) and 
        datetime.fromtimestamp(event['timestamp']) > recent_cutoff
    ]
    
    print(f"   Last 30 Days: {len(recent_events)} events")
    print(f"   Active Days: {len(daily_events)}")
    
    # Peak activity days
    sorted_days = sorted(daily_events.items(), key=lambda x: len(x[1]), reverse=True)
    print(f"   Most Active Days:")
    for date, day_events in sorted_days[:3]:
        print(f"     {date}: {len(day_events)} events")

def analyze_technology_adoption(events):
    """Analyze adoption of modern Python features and best practices."""
    print(f"\n🚀 TECHNOLOGY & BEST PRACTICES ADOPTION")
    
    modern_patterns = {
        'Type Annotations': ['type_annotations_introduced'],
        'Functional Programming': ['functional_programming_adopted', 'lambda_usage_changed'],
        'Error Handling': ['error_handling_introduced', 'exception_handling_added'],
        'Code Quality': ['decorator_added', 'assertion_usage_changed'],
        'Modern Syntax': ['comprehension_usage_changed', 'f_string_usage']
    }
    
    for category, pattern_types in modern_patterns.items():
        count = sum(1 for event in events if event['event_type'] in pattern_types)
        if count > 0:
            print(f"   {category:<25} {count:>3} improvements")

def generate_git_enhanced_json_report(events, output_file='svcs_analytics.json'):
    """Generate a detailed JSON report with git integration for external analysis."""
    
    git_info = get_git_info()
    
    # Enhance events with git context
    enhanced_events = []
    for event in events:
        enhanced_event = event.copy()
        
        # Add git context
        commit_hash = event.get('commit_hash', '')
        if commit_hash:
            try:
                # Get commit details
                commit_info = subprocess.run(
                    ['git', 'show', '--format=%s|%an|%ae|%ad', '--no-patch', commit_hash],
                    capture_output=True, text=True, check=True
                ).stdout.strip().split('|')
                
                if len(commit_info) >= 4:
                    enhanced_event['git_commit_message'] = commit_info[0]
                    enhanced_event['git_author_name'] = commit_info[1]
                    enhanced_event['git_author_email'] = commit_info[2]
                    enhanced_event['git_commit_date'] = commit_info[3]
                    
            except subprocess.CalledProcessError:
                pass  # Skip git info if not available
                
        enhanced_events.append(enhanced_event)
    
    report_data = {
        'repository_info': git_info,
        'generation_timestamp': datetime.now().isoformat(),
        'total_events': len(events),
        'events': enhanced_events,
        'summary': {
            'event_types': list(Counter(e['event_type'] for e in events).keys()),
            'authors': list(Counter(e['author'] for e in events).keys()),
            'files': list(Counter(e['location'] for e in events).keys()),
            'date_range': {
                'earliest': min((e.get('timestamp', 0) for e in events if e.get('timestamp')), default=0),
                'latest': max((e.get('timestamp', 0) for e in events if e.get('timestamp')), default=0)
            }
        }
    }
    
    with open(output_file, 'w') as f:
        json.dump(report_data, f, indent=2, default=str)
    
    print(f"\n💾 JSON report exported to: {output_file}")
    return report_data

def show_git_enhanced_timeline(branch=None):
    """Show a git-aware timeline of major semantic changes."""
    
    events = get_events_for_branch(branch) if branch else get_full_log()
    
    if not events:
        return
    
    print(f"\n📈 GIT-ENHANCED SEMANTIC EVOLUTION TIMELINE")
    print("-" * 50)
    
    # Group by commit hash for git correlation
    commits_with_events = defaultdict(list)
    for event in events:
        commit_hash = event.get('commit_hash', 'unknown')
        commits_with_events[commit_hash].append(event)
    
    # Sort by timestamp
    sorted_commits = []
    for commit_hash, commit_events in commits_with_events.items():
        if commit_events:
            latest_timestamp = max(e.get('timestamp', 0) for e in commit_events)
            sorted_commits.append((latest_timestamp, commit_hash, commit_events))
    
    sorted_commits.sort(reverse=True)  # Most recent first
    
    # Show recent commits with semantic context
    for i, (timestamp, commit_hash, commit_events) in enumerate(sorted_commits[:10]):
        if timestamp:
            date = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M')
        else:
            date = "Unknown date"
            
        print(f"\n📅 {date} | {commit_hash[:8]}")
        
        # Get git commit message if available
        try:
            commit_msg = subprocess.run(
                ['git', 'show', '--format=%s', '--no-patch', commit_hash],
                capture_output=True, text=True, check=True
            ).stdout.strip()
            print(f"   💬 {commit_msg}")
        except subprocess.CalledProcessError:
            pass
        
        # Show semantic events for this commit
        event_types = Counter(e['event_type'] for e in commit_events)
        for event_type, count in event_types.most_common(3):
            print(f"   🔍 {event_type} ({count}x)")

def compare_branches(branch1, branch2):
    """Compare semantic patterns between two git branches."""
    
    print(f"\n🔀 BRANCH COMPARISON: {branch1} vs {branch2}")
    print("=" * 50)
    
    events1 = get_events_for_branch(branch1)
    events2 = get_events_for_branch(branch2)
    
    print(f"📊 {branch1}: {len(events1)} events")
    print(f"📊 {branch2}: {len(events2)} events")
    
    # Compare event types
    types1 = Counter(e['event_type'] for e in events1)
    types2 = Counter(e['event_type'] for e in events2)
    
    print(f"\n🎯 Event Type Differences:")
    all_types = set(types1.keys()) | set(types2.keys())
    for event_type in sorted(all_types):
        count1 = types1.get(event_type, 0)
        count2 = types2.get(event_type, 0)
        diff = count2 - count1
        if diff != 0:
            direction = "+" if diff > 0 else ""
            print(f"   {event_type:<30} {count1:>3} → {count2:>3} ({direction}{diff})")

def main():
    """Main function with command-line interface."""
    parser = argparse.ArgumentParser(description='SVCS Repository Analytics Dashboard')
    parser.add_argument('--branch', help='Analyze specific git branch')
    parser.add_argument('--export-json', action='store_true', help='Export JSON report')
    parser.add_argument('--compare-branches', nargs=2, metavar=('BRANCH1', 'BRANCH2'),
                       help='Compare two git branches')
    parser.add_argument('--timeline', action='store_true', help='Show git-enhanced timeline')
    
    args = parser.parse_args()
    
    try:
        if args.compare_branches:
            compare_branches(args.compare_branches[0], args.compare_branches[1])
        elif args.timeline:
            show_git_enhanced_timeline(args.branch)
        else:
            generate_repository_analytics_report(args.branch)
            
        if args.export_json:
            events = get_events_for_branch(args.branch) if args.branch else get_full_log()
            generate_git_enhanced_json_report(events)
            
        if not args.compare_branches and not args.timeline:
            show_git_enhanced_timeline(args.branch)
            
    except Exception as e:
        print(f"❌ Error generating analytics: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
