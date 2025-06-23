#!/usr/bin/env python3
"""
SVCS Semantic Analysis Integration

This module integrates the existing SVCS 5-layer semantic analysis 
with the new global MCP architecture.
"""

import subprocess
import sys
import os
from pathlib import Path
from typing import List, Dict, Any, Optional

# Add the original SVCS directory to path
ORIGINAL_SVCS_DIR = Path(__file__).parent.parent.parent / ".svcs"
sys.path.insert(0, str(ORIGINAL_SVCS_DIR))

# Add the parent directory for relative imports
PARENT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(PARENT_DIR))

try:
    from svcs_complete_5layer import SVCSComplete5LayerAnalyzer
    from storage import store_commit_events
    SEMANTIC_ANALYSIS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import SVCS analysis components: {e}")
    # Try alternative import paths
    try:
        import sys
        from pathlib import Path
        
        # Add multiple possible paths
        svcs_dir = Path(__file__).parent.parent.parent / ".svcs"
        if svcs_dir.exists():
            sys.path.insert(0, str(svcs_dir))
            from svcs_complete_5layer import SVCSComplete5LayerAnalyzer
            from storage import store_commit_events
            SEMANTIC_ANALYSIS_AVAILABLE = True
        else:
            SEMANTIC_ANALYSIS_AVAILABLE = False
    except ImportError:
        SEMANTIC_ANALYSIS_AVAILABLE = False

try:
    from svcs_core import GlobalSVCSDatabase
except ImportError:
    # Fallback import path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from svcs_core import GlobalSVCSDatabase


class GlobalSemanticAnalyzer:
    """Integrates SVCS semantic analysis with global database."""
    
    def __init__(self, global_db: GlobalSVCSDatabase = None):
        self.global_db = global_db or GlobalSVCSDatabase()
        self.analyzer = SVCSComplete5LayerAnalyzer() if SEMANTIC_ANALYSIS_AVAILABLE else None
    
    def analyze_commit(self, project_path: str, commit_hash: str = None) -> Dict[str, Any]:
        """Analyze a git commit for semantic changes."""
        if not SEMANTIC_ANALYSIS_AVAILABLE:
            return {"error": "Semantic analysis components not available"}
        
        project_path = Path(project_path).resolve()
        
        # Check if project is registered
        project = self.global_db.get_project_by_path(str(project_path))
        if not project:
            return {"error": f"Project not registered: {project_path}"}
        
        project_id = project['project_id']
        
        # Get current commit hash if not provided
        if not commit_hash:
            try:
                result = subprocess.run(
                    ['git', 'rev-parse', 'HEAD'], 
                    cwd=project_path, 
                    capture_output=True, 
                    text=True, 
                    check=True
                )
                commit_hash = result.stdout.strip()
            except subprocess.CalledProcessError as e:
                return {"error": f"Could not get commit hash: {e}"}
        
        # Get changed files
        changed_files = self._get_changed_files(project_path, commit_hash)
        if not changed_files:
            return {"message": "No files changed", "events_stored": 0}
        
        # Analyze each changed file
        all_events = []
        for file_path in changed_files:
            file_events = self._analyze_file_change(project_path, file_path, commit_hash)
            all_events.extend(file_events)
        
        # Store events in global database
        stored_count = self._store_events_global(project_id, commit_hash, all_events)
        
        return {
            "project_id": project_id,
            "commit_hash": commit_hash,
            "files_analyzed": len(changed_files),
            "events_generated": len(all_events), 
            "events_stored": stored_count,
            "message": f"Analyzed {len(changed_files)} files, generated {len(all_events)} semantic events"
        }
    
    def _get_changed_files(self, project_path: Path, commit_hash: str) -> List[str]:
        """Get list of files changed in a commit."""
        try:
            # Get parent commit
            parent_result = subprocess.run(
                ['git', 'rev-parse', f'{commit_hash}~1'],
                cwd=project_path,
                capture_output=True,
                text=True
            )
            
            if parent_result.returncode == 0:
                # Compare with parent commit
                parent_hash = parent_result.stdout.strip()
                cmd = ['git', 'diff', '--name-only', parent_hash, commit_hash]
            else:
                # Initial commit, list all files
                cmd = ['git', 'ls-tree', '-r', '--name-only', commit_hash]
            
            result = subprocess.run(cmd, cwd=project_path, capture_output=True, text=True, check=True)
            return [f.strip() for f in result.stdout.split('\n') if f.strip()]
            
        except subprocess.CalledProcessError as e:
            print(f"Error getting changed files: {e}")
            return []
    
    def _analyze_file_change(self, project_path: Path, file_path: str, commit_hash: str) -> List[Dict[str, Any]]:
        """Analyze semantic changes in a specific file."""
        if not self.analyzer:
            return []
        
        full_file_path = project_path / file_path
        
        # Skip non-Python files for now (could extend to other languages)
        if not file_path.endswith('.py'):
            return []
        
        try:
            # Get file content before and after
            before_content = self._get_file_content_at_commit(project_path, file_path, f"{commit_hash}~1")
            after_content = self._get_file_content_at_commit(project_path, file_path, commit_hash)
            
            if before_content is None:
                before_content = ""  # New file
            
            if after_content is None:
                return []  # File deleted or inaccessible
            
            # Run 5-layer analysis
            events = self.analyzer.analyze_complete(file_path, before_content, after_content)
            
            # Add commit context to each event
            for event in events:
                event['commit_hash'] = commit_hash
                event['file_path'] = file_path
                
            return events
            
        except Exception as e:
            print(f"Error analyzing file {file_path}: {e}")
            return []
    
    def _get_file_content_at_commit(self, project_path: Path, file_path: str, commit_ref: str) -> Optional[str]:
        """Get file content at a specific commit."""
        try:
            result = subprocess.run(
                ['git', 'show', f'{commit_ref}:{file_path}'],
                cwd=project_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                return result.stdout
            else:
                return None  # File doesn't exist at this commit
                
        except subprocess.CalledProcessError:
            return None
    
    def _store_events_global(self, project_id: str, commit_hash: str, events: List[Dict[str, Any]]) -> int:
        """Store semantic events in the global database."""
        if not events:
            return 0
        
        # Convert events to global database format
        global_events = []
        for event in events:
            global_event = {
                'project_id': project_id,
                'commit_hash': commit_hash,
                'event_type': event.get('event_type', 'unknown'),
                'node_id': event.get('node_id', ''),
                'location': event.get('location', ''),
                'details': str(event.get('details', '')),
                'layer': str(event.get('layer', 1)),
                'confidence': event.get('confidence', 1.0),
                'file_path': event.get('file_path', ''),
                'timestamp': event.get('timestamp', None)
            }
            global_events.append(global_event)
        
        # Store in global database
        try:
            with self.global_db.get_connection() as conn:
                for event in global_events:
                    conn.execute("""
                        INSERT INTO semantic_events (
                            event_id, project_id, commit_hash, event_type, 
                            node_id, location, details, layer, confidence,
                            timestamp
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                    """, (
                        f"{project_id}_{commit_hash}_{len(global_events)}_{hash(str(event))}",
                        event['project_id'],
                        event['commit_hash'], 
                        event['event_type'],
                        event['node_id'],
                        event['location'],
                        event['details'],
                        event['layer'],
                        event['confidence']
                    ))
                
                conn.commit()
                return len(global_events)
                
        except Exception as e:
            print(f"Error storing events in global database: {e}")
            return 0


def analyze_commit_cli(project_path: str, *args) -> None:
    """CLI entry point for commit analysis (called by git hooks)."""
    analyzer = GlobalSemanticAnalyzer()
    result = analyzer.analyze_commit(project_path)
    
    if "error" in result:
        print(f"❌ SVCS Analysis Error: {result['error']}")
    else:
        print(f"🔍 SVCS: {result['message']}")
        if result['events_stored'] > 0:
            print(f"✅ Stored {result['events_stored']} semantic events")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python semantic_analyzer.py <project_path>")
        sys.exit(1)
    
    analyze_commit_cli(sys.argv[1])
