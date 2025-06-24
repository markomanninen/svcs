#!/usr/bin/env python3
"""
SVCS Universal Semantic Analyzer - Simple CLI
Working implementation for post-commit hooks
"""

import argparse
import os
import sys
import subprocess
import sqlite3
import json
from datetime import datetime
from pathlib import Path

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from universal_analyzer import analyze_semantic_changes


def get_database_path():
    """Get the path to the SVCS database."""
    return Path.cwd() / '.svcs' / 'semantic_events.db'


def init_database():
    """Initialize SVCS database."""
    db_path = get_database_path()
    db_path.parent.mkdir(exist_ok=True)
    
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS semantic_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                node_id TEXT NOT NULL,
                location TEXT NOT NULL,
                details TEXT,
                confidence REAL DEFAULT 1.0,
                layer TEXT DEFAULT 'core',
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                commit_hash TEXT
            )
        ''')
        conn.commit()


def store_events(events, commit_hash=None):
    """Store semantic events in database."""
    if not events:
        return
    
    db_path = get_database_path()
    
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        
        for event in events:
            cursor.execute('''
                INSERT INTO semantic_events 
                (event_type, node_id, location, details, confidence, layer, commit_hash)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                event.get('event_type'),
                event.get('node_id'),
                event.get('location'),
                event.get('details'),
                event.get('confidence', 1.0),
                event.get('layer', 'core'),
                commit_hash
            ))
        
        conn.commit()


def analyze_commit(commit_hash):
    """Analyze all changes in a commit."""
    try:
        # Get changed files
        result = subprocess.run(
            ['git', 'diff-tree', '--no-commit-id', '--name-only', '-r', commit_hash],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            return []
        
        changed_files = result.stdout.strip().split('\n')
        changed_files = [f for f in changed_files if f and f.endswith(('.py', '.php', '.js', '.ts'))]
        
        if not changed_files:
            return []
        
        all_events = []
        
        for filepath in changed_files:
            try:
                # Get file content at commit and previous commit
                current_result = subprocess.run(
                    ['git', 'show', f'{commit_hash}:{filepath}'],
                    capture_output=True,
                    text=True
                )
                
                previous_result = subprocess.run(
                    ['git', 'show', f'{commit_hash}~1:{filepath}'],
                    capture_output=True,
                    text=True
                )
                
                if current_result.returncode == 0:
                    current_content = current_result.stdout
                    previous_content = previous_result.stdout if previous_result.returncode == 0 else ""
                    
                    # Analyze this file
                    events = analyze_semantic_changes(filepath, previous_content, current_content)
                    all_events.extend(events)
                
            except Exception as e:
                print(f"Error analyzing {filepath}: {e}")
        
        return all_events
        
    except Exception as e:
        print(f"Error analyzing commit: {e}")
        return []


def post_commit_hook():
    """Run as post-commit hook."""
    try:
        # Get the latest commit
        result = subprocess.run(
            ['git', 'rev-parse', 'HEAD'],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            return
        
        commit_hash = result.stdout.strip()
        
        # Analyze the commit
        events = analyze_commit(commit_hash)
        
        if events:
            # Initialize database if needed
            init_database()
            
            # Store events
            store_events(events, commit_hash)
            
            print(f"SVCS: Detected {len(events)} semantic events in commit {commit_hash[:8]}")
            for event in events:
                print(f"  • {event['event_type']}: {event['details']}")
        
    except Exception as e:
        print(f"SVCS Error: {e}")


def analyze_file(filepath):
    """Analyze a specific file."""
    if not os.path.exists(filepath):
        print(f"Error: File {filepath} does not exist")
        return
    
    # Get current content
    with open(filepath, 'r', encoding='utf-8') as f:
        current_content = f.read()
    
    # Get previous version from git
    try:
        result = subprocess.run(
            ['git', 'show', f'HEAD~1:{filepath}'],
            capture_output=True,
            text=True
        )
        
        previous_content = result.stdout if result.returncode == 0 else ""
    except:
        previous_content = ""
    
    # Analyze changes
    events = analyze_semantic_changes(filepath, previous_content, current_content)
    
    if not events:
        print(f"No semantic changes detected in {filepath}")
        return
    
    print(f"🔍 Semantic Analysis Results for {filepath}")
    print("=" * 60)
    print(f"Detected {len(events)} semantic events:")
    
    for i, event in enumerate(events, 1):
        print(f"\n{i}. {event['event_type'].upper()}")
        print(f"   Node: {event['node_id']}")
        print(f"   Details: {event['details']}")


def install_hooks():
    """Install git hooks."""
    try:
        git_dir = subprocess.run(
            ['git', 'rev-parse', '--git-dir'],
            capture_output=True,
            text=True
        ).stdout.strip()
        
        hooks_dir = Path(git_dir) / 'hooks'
        hooks_dir.mkdir(exist_ok=True)
        
        # Create post-commit hook
        hook_file = hooks_dir / 'post-commit'
        script_path = os.path.abspath(__file__)
        
        hook_content = f"""#!/bin/bash
# SVCS Universal Semantic Analysis Post-Commit Hook
python3 "{script_path}" post-commit
"""
        
        with open(hook_file, 'w') as f:
            f.write(hook_content)
        
        hook_file.chmod(0o755)
        
        print(f"✅ Installed post-commit hook at {hook_file}")
        print("   Universal semantic analysis will run automatically after each commit")
        
    except Exception as e:
        print(f"Error installing hooks: {e}")


def list_events(limit=10):
    """List recent events."""
    db_path = get_database_path()
    
    if not db_path.exists():
        print("No events database found. Run 'svcs init' first.")
        return
    
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT event_type, location, details, timestamp, commit_hash
            FROM semantic_events 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (limit,))
        
        rows = cursor.fetchall()
        
        if not rows:
            print("No semantic events found")
            return
        
        print(f"📊 Recent Semantic Events (last {len(rows)})")
        print("=" * 60)
        
        for row in rows:
            event_type, location, details, timestamp, commit_hash = row
            print(f"• {event_type}")
            print(f"  File: {location}")
            print(f"  Details: {details}")
            print(f"  Time: {timestamp}")
            if commit_hash:
                print(f"  Commit: {commit_hash[:8]}")
            print()


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="SVCS Universal Semantic Analyzer")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Post-commit hook
    subparsers.add_parser('post-commit', help='Run post-commit analysis')
    
    # Install hooks
    subparsers.add_parser('install-hooks', help='Install git hooks')
    
    # Analyze file
    analyze_parser = subparsers.add_parser('analyze', help='Analyze file')
    analyze_parser.add_argument('file', help='File to analyze')
    
    # List events
    list_parser = subparsers.add_parser('events', help='List recent events')
    list_parser.add_argument('--limit', type=int, default=10, help='Number of events')
    
    # Init
    subparsers.add_parser('init', help='Initialize SVCS')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    if args.command == 'post-commit':
        post_commit_hook()
    elif args.command == 'install-hooks':
        install_hooks()
    elif args.command == 'analyze':
        analyze_file(args.file)
    elif args.command == 'events':
        list_events(args.limit)
    elif args.command == 'init':
        init_database()
        install_hooks()
        print("✅ SVCS Universal Semantic Analyzer initialized")


if __name__ == "__main__":
    main()
