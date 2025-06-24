#!/usr/bin/env python3
"""
SVCS Modular Semantic Analyzer
Comprehensive 5-layer semantic analysis system with modular architecture

This replaces the old monolithic system with a proper modular structure:
- Parsers: Modular language-specific parsers (Python, PHP, JS)
- Layers: All 5 layers including AI analysis
- Storage: Database integration
- Post-commit hook integration
"""

import os
import sys
import subprocess
import time
from typing import List, Dict, Any, Optional
from pathlib import Path

# Import modular components
from .analyzers.comprehensive_analyzer import ComprehensiveAnalyzer
from .storage import initialize_database, store_commit_events, get_recent_events, get_event_statistics

class SVCSModularAnalyzer:
    """
    Modular semantic analyzer with complete 5-layer analysis system.
    """
    
    def __init__(self, repo_path: str = None):
        """Initialize the analyzer for a specific repository."""
        self.repo_path = repo_path or os.getcwd()
        self.svcs_dir = os.path.join(self.repo_path, '.svcs')
        self.db_path = os.path.join(self.svcs_dir, 'semantic.db')
        
        # Ensure .svcs directory exists
        os.makedirs(self.svcs_dir, exist_ok=True)
        
        # Initialize database
        initialize_database(self.db_path)
        
        # Initialize comprehensive analyzer with all 5 layers
        self.comprehensive_analyzer = ComprehensiveAnalyzer()
    
    def analyze_file_changes(self, filepath: str, before_content: str, after_content: str) -> List[Dict[str, Any]]:
        """
        Analyze changes between two versions of a file using all 5 layers.
        
        Args:
            filepath: Path to the file being analyzed
            before_content: Content of the file before changes
            after_content: Content of the file after changes
            
        Returns:
            List of semantic events detected across all layers
        """
        return self.comprehensive_analyzer.analyze_file_changes(filepath, before_content, after_content)
    
    def analyze_commit(self, commit_hash: str = None) -> List[Dict[str, Any]]:
        """
        Analyze a specific commit for semantic changes using all 5 layers.
        
        Args:
            commit_hash: Git commit hash to analyze (defaults to HEAD)
            
        Returns:
            List of semantic events detected in the commit
        """
        if commit_hash is None:
            commit_hash = self._get_current_commit_hash()
        
        if not commit_hash:
            return []
        
        # Get commit metadata
        commit_metadata = self._get_commit_metadata(commit_hash)
        if not commit_metadata:
            return []
        
        # Use comprehensive analyzer for commit analysis
        all_events = self.comprehensive_analyzer.analyze_commit(commit_hash, self.repo_path)
        
        # Store events in database
        if all_events:
            store_commit_events(self.db_path, commit_hash, commit_metadata, all_events)
        
        return all_events
    
    def get_recent_events(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent semantic events from the database."""
        return get_recent_events(self.db_path, limit)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about stored semantic events."""
        return get_event_statistics(self.db_path)
    
    def get_layer_summary(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get a summary of events by layer."""
        return self.comprehensive_analyzer.get_layer_summary(events)
    
    def install_post_commit_hook(self) -> bool:
        """
        Install a post-commit hook that uses this modular analyzer.
        
        Returns:
            True if hook was installed successfully, False otherwise
        """
        hooks_dir = os.path.join(self.repo_path, '.git', 'hooks')
        if not os.path.exists(hooks_dir):
            print("Error: Not a git repository or hooks directory not found")
            return False
        
        hook_path = os.path.join(hooks_dir, 'post-commit')
        
        # Create the hook script
        hook_content = f'''#!/bin/bash
#
# SVCS Modular Post-Commit Hook
# Uses the complete 5-layer modular semantic analysis system
#

# Get the repository root
REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null)

if [ -z "$REPO_ROOT" ]; then
    echo "❌ SVCS: Not in a git repository"
    exit 1
fi

# Ensure .svcs directory exists for database
mkdir -p "$REPO_ROOT/.svcs"

# Set PYTHONPATH to include SVCS modules
export PYTHONPATH="$REPO_ROOT:$PYTHONPATH"

# Post-commit: Analyze the latest commit for semantic changes
echo "🔍 SVCS: Analyzing semantic changes with 5-layer modular system..."

# Get the latest commit hash
COMMIT_HASH=$(git rev-parse HEAD)

# Run semantic analysis using the modular system
{sys.executable} -c "
import sys
sys.path.insert(0, '$REPO_ROOT')

try:
    from svcs.semantic_analyzer import SVCSModularAnalyzer
    
    analyzer = SVCSModularAnalyzer('$REPO_ROOT')
    events = analyzer.analyze_commit('$COMMIT_HASH')
    
    if events:
        print(f'✅ SVCS: Detected {{len(events)}} semantic events across all layers')
        
        # Show layer summary
        summary = analyzer.get_layer_summary(events)
        print('📊 SVCS: Events by layer:')
        for layer, count in summary['by_layer'].items():
            layer_name = {{
                '1': 'Structural',
                '2': 'Syntactic', 
                '3': 'Semantic',
                '4': 'Behavioral',
                '5a': 'AI Patterns',
                '5b': 'True AI'
            }}.get(layer, layer)
            print(f'   Layer {{layer}} ({{layer_name}}): {{count}} events')
        
        # Show some high-confidence events
        high_conf_events = [e for e in events if e.get('confidence', 1.0) > 0.8]
        if high_conf_events:
            print(f'🎯 SVCS: {{len(high_conf_events)}} high-confidence events detected')
            for event in high_conf_events[:3]:  # Show first 3
                layer = event.get('layer', '?')
                conf = event.get('confidence', 1.0)
                print(f'   Layer {{layer}}: {{event[\"event_type\"]}} ({{conf:.1%}} confidence)')
        
        stats = analyzer.get_statistics()
        print(f'� SVCS: Total events in database: {{stats[\"total_events\"]}}')
    else:
        print('ℹ️ SVCS: No semantic changes detected')
        
except ImportError as e:
    print(f'❌ SVCS: Could not import modular analyzer: {{e}}')
    print('   Make sure the svcs module is properly installed')
except Exception as error:
    print(f'❌ SVCS: Analysis error: {{error}}')
    import traceback
    traceback.print_exc()
"

exit 0
'''
        
        try:
            with open(hook_path, 'w') as f:
                f.write(hook_content)
            
            # Make the hook executable
            os.chmod(hook_path, 0o755)
            
            print(f"✅ SVCS modular 5-layer post-commit hook installed at {hook_path}")
            print("🎯 Hook now includes:")
            print("   • Layer 1: Structural analysis")
            print("   • Layer 2: Syntactic analysis") 
            print("   • Layer 3: Semantic analysis")
            print("   • Layer 4: Behavioral analysis")
            print("   • Layer 5a: AI pattern recognition")
            print("   • Layer 5b: True AI/LLM analysis")
            return True
            
        except Exception as e:
            print(f"❌ Failed to install post-commit hook: {e}")
            return False
    
    def _get_current_commit_hash(self) -> Optional[str]:
        """Get the current commit hash."""
        try:
            result = subprocess.run(
                ['git', 'rev-parse', 'HEAD'],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return None
    
    def _get_commit_metadata(self, commit_hash: str) -> Optional[Dict[str, Any]]:
        """Get metadata for a commit."""
        try:
            result = subprocess.run(
                ['git', 'show', '--format=%an|%at', '--no-patch', commit_hash],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            parts = result.stdout.strip().split('|')
            if len(parts) >= 2:
                return {
                    'author': parts[0],
                    'timestamp': int(parts[1])
                }
        except (subprocess.CalledProcessError, ValueError):
            pass
        
        return None
    
    def _get_changed_files(self, commit_hash: str) -> List[str]:
        """Get list of files changed in a commit."""
        try:
            result = subprocess.run(
                ['git', 'diff-tree', '--no-commit-id', '--name-only', '-r', commit_hash],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            return [f.strip() for f in result.stdout.split('\\n') if f.strip()]
        except subprocess.CalledProcessError:
            return []
    
    def _get_file_contents_for_commit(self, file_path: str, commit_hash: str) -> tuple:
        """Get before and after contents of a file for a commit."""
        # Get the previous commit
        try:
            result = subprocess.run(
                ['git', 'rev-parse', f'{commit_hash}^'],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            parent_hash = result.stdout.strip()
        except subprocess.CalledProcessError:
            parent_hash = None
        
        # Get before content (from parent commit)
        before_content = ""
        if parent_hash:
            try:
                result = subprocess.run(
                    ['git', 'show', f'{parent_hash}:{file_path}'],
                    cwd=self.repo_path,
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    before_content = result.stdout
            except subprocess.CalledProcessError:
                pass
        
        # Get after content (from current commit)
        after_content = ""
        try:
            result = subprocess.run(
                ['git', 'show', f'{commit_hash}:{file_path}'],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            after_content = result.stdout
        except subprocess.CalledProcessError:
            pass
        
        return before_content, after_content
    
    def _should_analyze_file(self, file_path: str) -> bool:
        """Check if a file should be analyzed for semantic changes."""
        # Skip binary files, images, etc.
        skip_extensions = {'.pyc', '.pyo', '.pyd', '.so', '.dll', '.exe', 
                          '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.ico',
                          '.mp3', '.mp4', '.avi', '.mov', '.pdf', '.zip', '.tar', '.gz'}
        
        skip_dirs = {'__pycache__', '.git', '.svn', '.hg', 'node_modules', 
                    '.idea', '.vscode', 'build', 'dist'}
        
        # Check extension
        _, ext = os.path.splitext(file_path)
        if ext.lower() in skip_extensions:
            return False
        
        # Check directory
        path_parts = Path(file_path).parts
        if any(part in skip_dirs for part in path_parts):
            return False
        
        return True

# CLI interface for the modular analyzer
def main():
    """Command-line interface for the SVCS modular analyzer."""
    import argparse
    
    parser = argparse.ArgumentParser(description='SVCS Modular Semantic Analyzer')
    parser.add_argument('--repo', '-r', default='.', 
                       help='Repository path (default: current directory)')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze a commit')
    analyze_parser.add_argument('--commit', '-c', default='HEAD',
                               help='Commit hash to analyze (default: HEAD)')
    
    # Recent command
    recent_parser = subparsers.add_parser('recent', help='Show recent events')
    recent_parser.add_argument('--limit', '-l', type=int, default=20,
                              help='Number of events to show (default: 20)')
    
    # Stats command
    subparsers.add_parser('stats', help='Show statistics')
    
    # Install hook command
    subparsers.add_parser('install-hook', help='Install post-commit hook')
    
    args = parser.parse_args()
    
    analyzer = SVCSModularAnalyzer(args.repo)
    
    if args.command == 'analyze':
        print(f"🔍 Analyzing commit {args.commit}...")
        events = analyzer.analyze_commit(args.commit if args.commit != 'HEAD' else None)
        
        if events:
            print(f"✅ Detected {len(events)} semantic events:")
            for event in events:
                print(f"  • {event['event_type']}: {event.get('details', '')}")
        else:
            print("ℹ️ No semantic changes detected")
    
    elif args.command == 'recent':
        print(f"📋 Recent {args.limit} semantic events:")
        events = analyzer.get_recent_events(args.limit)
        
        if events:
            for event in events:
                print(f"  • {event['event_type']} in {event['location']} ({event['commit_hash'][:8]})")
        else:
            print("ℹ️ No events found")
    
    elif args.command == 'stats':
        stats = analyzer.get_statistics()
        print("📊 SVCS Statistics:")
        print(f"  Total events: {stats['total_events']}")
        print(f"  Total commits: {stats['total_commits']}")
        print("  Event types:")
        for event_type, count in sorted(stats['events_by_type'].items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"    {event_type}: {count}")
    
    elif args.command == 'install-hook':
        success = analyzer.install_post_commit_hook()
        if success:
            print("✅ Post-commit hook installed successfully")
        else:
            print("❌ Failed to install post-commit hook")
    
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
