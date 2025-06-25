#!/usr/bin/env python3
"""
Repository-Local Semantic Analyzer

This module implements semantic analysis for the repository-local SVCS architecture:
1. Integrates with existing multi-language analyzers
2. Repository-local semantic analysis (no global database dependency)
3. Git commit analysis with file change detection
4. Branch-aware semantic event storage
"""

import logging
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class RepositoryLocalSemanticAnalyzer:
    """Repository-local semantic analyzer integrating with multi-language analysis."""
    
    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path).resolve()
        self.analyzer = None
        self._init_analyzer()
    
    def _init_analyzer(self):
        """Initialize the multi-language analyzer."""
        try:
            # Try to import from the main location first
            sys.path.insert(0, str(self.repo_path))
            from svcs_multilang import MultiLanguageAnalyzer
            self.analyzer = MultiLanguageAnalyzer()
            logger.info("Initialized multi-language semantic analyzer")
        except ImportError:
            try:
                # Try the .svcs location as fallback
                sys.path.insert(0, str(self.repo_path / ".svcs"))
                from svcs_multilang import MultiLanguageAnalyzer
                self.analyzer = MultiLanguageAnalyzer()
                logger.info("Initialized multi-language semantic analyzer from .svcs directory")
            except ImportError:
                logger.warning("Multi-language analyzer not available, using fallback")
                self.analyzer = None
    
    def is_supported_file(self, filepath: str) -> bool:
        """Check if file is supported by semantic analysis."""
        if not self.analyzer:
            # Fallback to basic extension check
            return filepath.endswith(('.py', '.php', '.phtml', '.php3', '.php4', '.php5', '.phps', '.js', '.ts'))
        
        return self.analyzer.get_language(filepath) is not None
    
    def analyze_file_change(self, filepath: str, commit_hash: str) -> List[Dict[str, Any]]:
        """Analyze semantic changes in a specific file for a commit."""
        if not self.is_supported_file(filepath):
            return []
        
        try:
            # Check if this is the initial commit
            is_initial_commit = False
            try:
                subprocess.run(
                    ["git", "rev-parse", f"{commit_hash}~1"],
                    cwd=self.repo_path,
                    capture_output=True,
                    text=True,
                    check=True
                )
            except subprocess.CalledProcessError:
                is_initial_commit = True
            
            # Get file content before and after the commit
            if is_initial_commit:
                before_content = ""  # No previous version in initial commit
            else:
                before_content = self._get_file_content_at_commit(filepath, f"{commit_hash}~1")
                if before_content is None:
                    before_content = ""  # New file
            
            after_content = self._get_file_content_at_commit(filepath, commit_hash)
            
            if after_content is None:
                # File was deleted
                return [{
                    "event_type": "file_deleted",
                    "node_id": f"file:{filepath}",
                    "location": filepath,
                    "details": f"File {filepath} was deleted",
                    "layer": "core",
                    "confidence": 1.0,
                    "reasoning": "File no longer exists in repository"
                }]
            
            # Use multi-language analyzer if available
            if self.analyzer:
                events = self.analyzer.analyze_file_changes(filepath, before_content, after_content)
                
                # Add repository-local metadata
                for event in events:
                    event.setdefault("layer", "core")
                    event.setdefault("confidence", 1.0)
                    event.setdefault("reasoning", "Multi-language AST analysis")
                
                return events
            else:
                # Fallback to basic change detection
                return self._fallback_analysis(filepath, before_content, after_content)
        
        except Exception as e:
            logger.error(f"Error analyzing file {filepath}: {e}")
            return []
    
    def _fallback_analysis(self, filepath: str, before_content: str, after_content: str) -> List[Dict[str, Any]]:
        """Fallback analysis when multi-language analyzer is not available."""
        if before_content == after_content:
            return []
        
        # Basic change detection
        events = []
        
        if not before_content:
            events.append({
                "event_type": "file_added",
                "node_id": f"file:{filepath}",
                "location": filepath,
                "details": f"New file {filepath} was added",
                "layer": "core",
                "confidence": 1.0,
                "reasoning": "File is new (no previous content)"
            })
        else:
            events.append({
                "event_type": "file_modified",
                "node_id": f"file:{filepath}",
                "location": filepath,
                "details": f"File {filepath} was modified",
                "layer": "core",
                "confidence": 1.0,
                "reasoning": "File content changed"
            })
        
        return events
    
    def _get_file_content_at_commit(self, filepath: str, commit_ref: str) -> Optional[str]:
        """Get file content at a specific commit."""
        try:
            result = subprocess.run(
                ["git", "show", f"{commit_ref}:{filepath}"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout
        except subprocess.CalledProcessError:
            # File didn't exist at that commit or other error
            return None
    
    def get_changed_files(self, commit_hash: str) -> List[str]:
        """Get list of files changed in a commit."""
        try:
            # First, check if this is the initial commit
            try:
                subprocess.run(
                    ["git", "rev-parse", f"{commit_hash}~1"],
                    cwd=self.repo_path,
                    capture_output=True,
                    text=True,
                    check=True
                )
                # Parent exists, use normal diff
                cmd = ["git", "diff-tree", "--no-commit-id", "--name-only", "-r", commit_hash]
            except subprocess.CalledProcessError:
                # No parent commit (initial commit), list all files in this commit
                cmd = ["git", "ls-tree", "--name-only", "-r", commit_hash]
            
            result = subprocess.run(
                cmd,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            return [f.strip() for f in result.stdout.strip().split('\n') if f.strip()]
        except subprocess.CalledProcessError as e:
            logger.error(f"Error getting changed files: {e}")
            return []
    
    def analyze_commit(self, commit_hash: str = None) -> List[Dict[str, Any]]:
        """Analyze all semantic changes in a commit."""
        # Get current commit hash if not provided
        if not commit_hash:
            try:
                result = subprocess.run(
                    ["git", "rev-parse", "HEAD"],
                    cwd=self.repo_path,
                    capture_output=True,
                    text=True,
                    check=True
                )
                commit_hash = result.stdout.strip()
            except subprocess.CalledProcessError as e:
                logger.error(f"Could not get current commit hash: {e}")
                return []
        
        # Get changed files
        changed_files = self.get_changed_files(commit_hash)
        if not changed_files:
            return []
        
        # Analyze each changed file
        all_events = []
        for filepath in changed_files:
            file_events = self.analyze_file_change(filepath, commit_hash)
            all_events.extend(file_events)
        
        # Add commit-level metadata to all events
        for event in all_events:
            event["commit_hash"] = commit_hash
            event["created_at"] = int(datetime.now().timestamp())
        
        return all_events
    
    def get_current_branch(self) -> str:
        """Get the current git branch."""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return "main"  # Fallback
    
    def get_commit_info(self, commit_hash: str) -> Dict[str, Any]:
        """Get commit metadata."""
        try:
            # Get commit info
            result = subprocess.run(
                ["git", "show", "--format=%an|%ae|%at|%s", "--no-patch", commit_hash],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            commit_line = result.stdout.strip()
            if commit_line:
                parts = commit_line.split('|', 3)
                if len(parts) == 4:
                    return {
                        "author_name": parts[0],
                        "author_email": parts[1],
                        "timestamp": int(parts[2]),
                        "message": parts[3],
                        "branch": self.get_current_branch()
                    }
        except subprocess.CalledProcessError as e:
            logger.error(f"Error getting commit info: {e}")
        
        return {
            "author_name": "unknown",
            "author_email": "unknown@example.com",
            "timestamp": int(datetime.now().timestamp()),
            "message": "Unknown commit",
            "branch": self.get_current_branch()
        }


def analyze_commit_semantic_changes(repo_path: str, commit_hash: str = None) -> List[Dict[str, Any]]:
    """Convenience function for analyzing commit semantic changes."""
    analyzer = RepositoryLocalSemanticAnalyzer(repo_path)
    return analyzer.analyze_commit(commit_hash)


def demo_repository_local_analyzer():
    """Demonstrate the repository-local semantic analyzer."""
    print("🔍 Repository-Local Semantic Analyzer Demo")
    print("=" * 50)
    
    # Get current directory (assuming it's a git repo)
    current_dir = Path.cwd()
    
    # Initialize analyzer
    analyzer = RepositoryLocalSemanticAnalyzer(current_dir)
    
    print(f"📁 Repository: {current_dir}")
    print(f"🌿 Current branch: {analyzer.get_current_branch()}")
    print(f"🔧 Multi-language analyzer: {'Available' if analyzer.analyzer else 'Fallback mode'}")
    
    if analyzer.analyzer:
        print(f"🌍 Supported languages: {analyzer.analyzer.get_supported_languages()}")
    
    # Analyze latest commit
    print("\n🔍 Analyzing latest commit...")
    events = analyzer.analyze_commit()
    
    if events:
        print(f"✅ Found {len(events)} semantic events:")
        for event in events[:5]:  # Show first 5 events
            print(f"  🎯 {event['event_type']} | {event['node_id']} | {event['location']}")
            print(f"     💬 {event['details']}")
    else:
        print("ℹ️ No semantic changes detected in latest commit")
    
    return analyzer


if __name__ == "__main__":
    demo_repository_local_analyzer()
