#!/usr/bin/env python3
"""
SVCS Search and Evolution Commands

Commands for searching semantic events and tracking evolution.
"""

import sys
from datetime import datetime
from pathlib import Path
from .base import RepositoryLocalSVCS, ensure_svcs_initialized, print_svcs_error


def cmd_search(args):
    """Advanced semantic search."""
    repo_path = Path(args.path or Path.cwd()).resolve()
    
    if not ensure_svcs_initialized(repo_path):
        print_svcs_error("SVCS not initialized. Run 'svcs init' first.")
        return
    
    try:
        # Import API functions from centralized location
        sys.path.insert(0, str(repo_path))
        from svcs.api import search_events_advanced, search_semantic_patterns
        
        # Determine search type
        if args.pattern_type:
            # Pattern-based search
            results = search_semantic_patterns(
                pattern_type=args.pattern_type,
                min_confidence=args.confidence,
                since_date=args.since,
                limit=args.limit
            )
            print(f"🎯 {args.pattern_type.title()} Patterns ({len(results)} found)")
        else:
            # Advanced event search
            search_params = {
                'author': args.author,
                'event_types': [args.event_type] if args.event_type else None,
                'min_confidence': args.confidence,
                'since_date': args.since,
                'limit': args.limit,
                'location_pattern': args.location
            }
            # Remove None values
            search_params = {k: v for k, v in search_params.items() if v is not None}
            
            results = search_events_advanced(**search_params)
            print(f"🔍 Search Results ({len(results)} found)")
        
        if not results:
            print("ℹ️ No results found. Try adjusting your search criteria.")
            return
            
        print("=" * 60)
        for result in results:
            timestamp = result.get('created_at', result.get('timestamp', ''))
            if isinstance(timestamp, (int, float)):
                timestamp = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
                
            confidence = result.get('confidence', 1.0)
            if confidence < 1.0:
                confidence_str = f" ({confidence:.1%})"
            else:
                confidence_str = ""
                
            print(f"📊 {result['event_type']}{confidence_str}")
            print(f"   📝 {result.get('commit_hash', 'N/A')[:8]} | {result.get('branch', 'N/A')} | {result.get('author', 'N/A')} | {timestamp}")
            print(f"   🎯 {result.get('node_id', 'N/A')} @ {result.get('location', 'N/A')}")
            if 'details' in result:
                print(f"   💬 {result['details']}")
            if 'reasoning' in result:
                print(f"   🧠 {result['reasoning']}")
            print()
            
    except ImportError:
        print_svcs_error("API functions not available. Ensure SVCS is properly set up.")
    except Exception as e:
        print_svcs_error(f"Error: {e}")


def cmd_evolution(args):
    """Track function/class evolution."""
    repo_path = Path(args.path or Path.cwd()).resolve()
    
    if not ensure_svcs_initialized(repo_path):
        print_svcs_error("SVCS not initialized. Run 'svcs init' first.")
        return
    
    try:
        sys.path.insert(0, str(repo_path))
        from svcs.api import get_filtered_evolution
        
        results = get_filtered_evolution(
            node_id=args.node_id,
            event_types=args.event_types,
            min_confidence=args.confidence,
            since_date=args.since
        )
        
        print(f"📈 Evolution of '{args.node_id}' ({len(results)} events)")
        print("=" * 60)
        
        if not results:
            print("ℹ️ No evolution events found for this node.")
            return
            
        for event in results:
            timestamp = event.get('created_at', event.get('timestamp', ''))
            if isinstance(timestamp, (int, float)):
                timestamp = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
                
            confidence = event.get('confidence', 1.0)
            if confidence < 1.0:
                confidence_str = f" ({confidence:.1%})"
            else:
                confidence_str = ""
                
            print(f"🔄 {event['event_type']}{confidence_str}")
            print(f"   📝 {event.get('commit_hash', 'N/A')[:8]} | {event.get('branch', 'N/A')} | {event.get('author', 'N/A')} | {timestamp}")
            print(f"   📍 {event.get('location', 'N/A')}")
            if 'details' in event:
                print(f"   💬 {event['details']}")
            print()
            
    except ImportError:
        print_svcs_error("API functions not available. Ensure SVCS is properly set up.")
    except Exception as e:
        print_svcs_error(f"Error: {e}")


def cmd_compare(args):
    """Compare semantic events between branches."""
    repo_path = Path(args.path or Path.cwd()).resolve()
    
    if not ensure_svcs_initialized(repo_path):
        print_svcs_error("SVCS not initialized. Run 'svcs init' first.")
        return
    
    svcs = RepositoryLocalSVCS(repo_path)
    comparison = svcs.compare_branches(args.branch1, args.branch2, limit=args.limit)
    
    print(f"🔍 Comparing semantic events between branches: {args.branch1} ↔ {args.branch2}")
    print()
    print(f"🌿 Branch Comparison: {args.branch1} vs {args.branch2}")
    print("=" * 60)
    print(f"📊 Summary:")
    print(f"   {args.branch1}: {comparison['branch1_count']} total events")
    print(f"   {args.branch2}: {comparison['branch2_count']} total events")
    print(f"   Difference: {abs(comparison['branch1_count'] - comparison['branch2_count'])}")
    
    if comparison['branch1_events']:
        print(f"\n🌿 Recent events in '{args.branch1}':")
        for event in comparison['branch1_events'][:5]:
            # Handle different timestamp formats
            timestamp = event.get('created_at', event.get('timestamp', ''))
            if isinstance(timestamp, (int, float)):
                timestamp = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
            elif isinstance(timestamp, str) and len(timestamp) > 19:
                timestamp = timestamp[:19]
            print(f"  📊 {event['event_type']} at {event['location']} ({event['commit_hash'][:8]}) - {timestamp}")
    
    if comparison['branch2_events']:
        print(f"\n🌿 Recent events in '{args.branch2}':")
        for event in comparison['branch2_events'][:5]:
            # Handle different timestamp formats
            timestamp = event.get('created_at', event.get('timestamp', ''))
            if isinstance(timestamp, (int, float)):
                timestamp = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
            elif isinstance(timestamp, str) and len(timestamp) > 19:
                timestamp = timestamp[:19]
            print(f"  📊 {event['event_type']} at {event['location']} ({event['commit_hash'][:8]}) - {timestamp}")
