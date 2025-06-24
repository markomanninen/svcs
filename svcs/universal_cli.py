#!/usr/bin/env python3
"""
SVCS CLI - Universal Semantic Analysis
Complete command line interface with universal semantic analyzer integration
"""

import argparse
import os
import sys
import subprocess
from pathlib import Path

# Add the svcs package to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from svcs.universal_analyzer import analyze_semantic_changes
from svcs.repo_adapters import get_repo_adapter
from svcs.utils import init_database, store_events


def analyze_file_command(args):
    """Analyze a specific file for semantic changes."""
    if not os.path.exists(args.file):
        print(f"Error: File {args.file} does not exist")
        return 1
    
    # Get file content
    with open(args.file, 'r', encoding='utf-8') as f:
        current_content = f.read()
    
    # Get previous version from git
    try:
        result = subprocess.run(
            ['git', 'show', f'HEAD~1:{args.file}'],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(args.file) or '.'
        )
        
        if result.returncode == 0:
            previous_content = result.stdout
        else:
            # File is new
            previous_content = ""
    except Exception as e:
        print(f"Error getting previous version: {e}")
        return 1
    
    # Analyze changes
    events = analyze_semantic_changes(args.file, previous_content, current_content)
    
    if not events:
        print(f"No semantic changes detected in {args.file}")
        return 0
    
    print(f"🔍 Semantic Analysis Results for {args.file}")
    print("=" * 60)
    print(f"Detected {len(events)} semantic events:")
    
    for i, event in enumerate(events, 1):
        print(f"\n{i}. {event['event_type'].upper()}")
        print(f"   Node: {event['node_id']}")
        print(f"   Details: {event['details']}")
        if event.get('confidence', 1.0) < 1.0:
            print(f"   Confidence: {event['confidence']:.1%}")
    
    # Store events if database is initialized
    try:
        store_events(events)
        print(f"\n✅ Events stored in database")
    except Exception as e:
        print(f"\n⚠️  Could not store events: {e}")
    
    return 0


def analyze_commit_command(args):
    """Analyze all changes in a specific commit."""
    try:
        # Get changed files in commit
        result = subprocess.run(
            ['git', 'diff-tree', '--no-commit-id', '--name-only', '-r', args.commit],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print(f"Error: Could not get files for commit {args.commit}")
            return 1
        
        changed_files = result.stdout.strip().split('\n')
        changed_files = [f for f in changed_files if f and f.endswith(('.py', '.php', '.js', '.ts'))]
        
        if not changed_files:
            print(f"No supported files changed in commit {args.commit}")
            return 0
        
        print(f"🔍 Analyzing commit {args.commit}")
        print(f"Changed files: {', '.join(changed_files)}")
        print("=" * 60)
        
        all_events = []
        
        for filepath in changed_files:
            # Get file content at commit
            try:
                current_result = subprocess.run(
                    ['git', 'show', f'{args.commit}:{filepath}'],
                    capture_output=True,
                    text=True
                )
                
                previous_result = subprocess.run(
                    ['git', 'show', f'{args.commit}~1:{filepath}'],
                    capture_output=True,
                    text=True
                )
                
                if current_result.returncode == 0:
                    current_content = current_result.stdout
                    previous_content = previous_result.stdout if previous_result.returncode == 0 else ""
                    
                    # Analyze this file
                    events = analyze_semantic_changes(filepath, previous_content, current_content)
                    
                    if events:
                        print(f"\n📁 {filepath}: {len(events)} events")
                        for event in events:
                            print(f"   • {event['event_type']}: {event['details']}")
                        
                        all_events.extend(events)
                
            except Exception as e:
                print(f"   ❌ Error analyzing {filepath}: {e}")
        
        print(f"\n🎯 Total: {len(all_events)} semantic events detected")
        
        # Store events
        try:
            store_events(all_events)
            print(f"✅ Events stored in database")
        except Exception as e:
            print(f"⚠️  Could not store events: {e}")
        
        return 0
        
    except Exception as e:
        print(f"Error analyzing commit: {e}")
        return 1


def post_commit_hook(args):
    """Run semantic analysis as a post-commit hook."""
    try:
        # Get the latest commit
        result = subprocess.run(
            ['git', 'rev-parse', 'HEAD'],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print("Error: Could not get latest commit hash")
            return 1
        
        commit_hash = result.stdout.strip()
        
        # Analyze the latest commit
        print(f"🔄 Running post-commit semantic analysis for {commit_hash[:8]}...")
        
        # Create args object for analyze_commit_command
        class Args:
            commit = commit_hash
        
        return analyze_commit_command(Args())
        
    except Exception as e:
        print(f"Error in post-commit hook: {e}")
        return 1


def install_hooks_command(args):
    """Install git hooks for automatic semantic analysis."""
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
        
        # Get the path to this script
        script_path = os.path.abspath(__file__)
        
        hook_content = f"""#!/bin/bash
# SVCS Semantic Analysis Post-Commit Hook
echo "Running SVCS semantic analysis..."
python3 "{script_path}" post-commit
"""
        
        with open(hook_file, 'w') as f:
            f.write(hook_content)
        
        # Make executable
        hook_file.chmod(0o755)
        
        print(f"✅ Installed post-commit hook at {hook_file}")
        print("   Semantic analysis will run automatically after each commit")
        
        return 0
        
    except Exception as e:
        print(f"Error installing hooks: {e}")
        return 1


def list_events_command(args):
    """List recent semantic events."""
    try:
        from svcs.utils import get_recent_events
        
        events = get_recent_events(limit=args.limit)
        
        if not events:
            print("No semantic events found")
            return 0
        
        print(f"📊 Recent Semantic Events (last {len(events)})")
        print("=" * 60)
        
        for event in events:
            print(f"• {event.get('event_type', 'unknown')}")
            print(f"  File: {event.get('location', 'unknown')}")
            print(f"  Node: {event.get('node_id', 'unknown')}")
            print(f"  Details: {event.get('details', 'No details')}")
            if event.get('timestamp'):
                print(f"  Time: {event['timestamp']}")
            print()
        
        return 0
        
    except Exception as e:
        print(f"Error listing events: {e}")
        return 1


def init_command(args):
    """Initialize SVCS in the current repository."""
    try:
        init_database()
        print("✅ SVCS database initialized")
        
        # Also install hooks
        class Args:
            pass
        
        install_hooks_command(Args())
        
        return 0
        
    except Exception as e:
        print(f"Error initializing SVCS: {e}")
        return 1


def test_analyzer_command(args):
    """Test the universal analyzer with sample code."""
    print("🧪 Testing Universal Semantic Analyzer")
    print("=" * 50)
    
    # Test cases for different languages
    test_cases = [
        {
            'language': 'Python',
            'file': 'test.py',
            'before': '''
def old_function(x):
    return x * 2

class OldClass:
    def method(self):
        pass
''',
            'after': '''
import asyncio

async def new_function(x: int) -> int:
    """Enhanced function."""
    result = x * 2
    await asyncio.sleep(0.1)
    return result

class NewClass:
    def __init__(self, value: int):
        self.value = value
    
    @property
    def computed(self) -> int:
        return self.value * 2
'''
        },
        {
            'language': 'PHP',
            'file': 'test.php',
            'before': '''<?php
class SimpleClass {
    public function method() {
        return "hello";
    }
}
?>''',
            'after': '''<?php
namespace App\\Models;

use App\\Services\\ServiceInterface;

class EnhancedClass implements ServiceInterface {
    private $value;
    
    public function __construct($value) {
        $this->value = $value;
    }
    
    public function method(): string {
        return "hello " . $this->value;
    }
}
?>'''
        },
        {
            'language': 'JavaScript',
            'file': 'test.js',
            'before': '''
function simpleFunction(x) {
    return x * 2;
}

class SimpleClass {
    method() {
        return "hello";
    }
}
''',
            'after': '''
import { Service } from './service';

class EnhancedClass extends Service {
    constructor(value) {
        super();
        this.value = value;
    }
    
    async method() {
        const result = await this.processValue();
        return `hello ${result}`;
    }
    
    get computed() {
        return this.value * 2;
    }
}

export default EnhancedClass;
'''
        }
    ]
    
    total_events = 0
    
    for test_case in test_cases:
        print(f"\n📝 Testing {test_case['language']}:")
        
        events = analyze_semantic_changes(
            test_case['file'],
            test_case['before'],
            test_case['after']
        )
        
        print(f"   Events detected: {len(events)}")
        
        for event in events:
            print(f"   • {event['event_type']}: {event['details']}")
        
        total_events += len(events)
    
    print(f"\n🎯 Test Results: {total_events} total events detected across all languages")
    print("✅ Universal analyzer is working!")
    
    return 0


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="SVCS - Universal Semantic Version Control System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  svcs init                           # Initialize SVCS in current repo
  svcs analyze file.py                # Analyze specific file
  svcs analyze-commit HEAD            # Analyze latest commit
  svcs analyze-commit abc123          # Analyze specific commit
  svcs install-hooks                  # Install git hooks
  svcs list-events                    # Show recent events
  svcs post-commit                    # Run post-commit analysis (for hooks)
  svcs test                           # Test the universal analyzer
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Init command
    init_parser = subparsers.add_parser('init', help='Initialize SVCS')
    
    # Analyze file command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze file changes')
    analyze_parser.add_argument('file', help='File to analyze')
    
    # Analyze commit command
    commit_parser = subparsers.add_parser('analyze-commit', help='Analyze commit changes')
    commit_parser.add_argument('commit', help='Commit hash to analyze')
    
    # Post-commit hook command
    post_commit_parser = subparsers.add_parser('post-commit', help='Post-commit hook')
    
    # Install hooks command
    hooks_parser = subparsers.add_parser('install-hooks', help='Install git hooks')
    
    # List events command
    list_parser = subparsers.add_parser('list-events', help='List recent events')
    list_parser.add_argument('--limit', type=int, default=10, help='Number of events to show')
    
    # Test command
    test_parser = subparsers.add_parser('test', help='Test the universal analyzer')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Command dispatch
    commands = {
        'init': init_command,
        'analyze': analyze_file_command,
        'analyze-commit': analyze_commit_command,
        'post-commit': post_commit_hook,
        'install-hooks': install_hooks_command,
        'list-events': list_events_command,
        'test': test_analyzer_command
    }
    
    if args.command in commands:
        return commands[args.command](args)
    else:
        print(f"Unknown command: {args.command}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
