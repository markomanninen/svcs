#!/usr/bin/env python3
"""
Repository-Local SVCS Database and Git Notes Integration

This module implements the new git-integrated team architecture:
1. Repository-local semantic database (.svcs/semantic.db)
2. Git notes storage for semantic data sync
3. Branch-aware semantic analysis
4. Team collaboration through git workflow
"""

import json
import logging
import os
import sqlite3
import subprocess
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class RepositoryLocalDatabase:
    """Repository-local semantic database stored in .svcs/semantic.db"""
    
    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path).resolve()
        self.svcs_dir = self.repo_path / ".svcs"
        self.db_path = self.svcs_dir / "semantic.db"
        self.ensure_directory()
        self.init_schema()
    
    def ensure_directory(self):
        """Ensure the .svcs directory exists in the repository."""
        self.svcs_dir.mkdir(exist_ok=True)
        
        # Add .svcs/ to .gitignore if not already there
        gitignore_path = self.repo_path / ".gitignore"
        gitignore_entry = ".svcs/"
        
        if gitignore_path.exists():
            with open(gitignore_path, 'r') as f:
                content = f.read()
            if gitignore_entry not in content:
                with open(gitignore_path, 'a') as f:
                    f.write(f"\n# SVCS semantic analysis data (local only)\n{gitignore_entry}\n")
        else:
            with open(gitignore_path, 'w') as f:
                f.write(f"# SVCS semantic analysis data (local only)\n{gitignore_entry}\n")
    
    def get_connection(self):
        """Get database connection."""
        return sqlite3.connect(self.db_path)
    
    def init_schema(self):
        """Initialize the repository-local database schema."""
        with self.get_connection() as conn:
            # Repository info table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS repository_info (
                    id INTEGER PRIMARY KEY,
                    repo_path TEXT NOT NULL,
                    created_at INTEGER NOT NULL,
                    last_analyzed INTEGER,
                    current_branch TEXT,
                    config TEXT DEFAULT '{}'
                )
            """)
            
            # Commits table (branch-aware)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS commits (
                    commit_hash TEXT PRIMARY KEY,
                    branch TEXT,
                    author TEXT,
                    timestamp INTEGER,
                    message TEXT,
                    created_at INTEGER,
                    git_notes_synced BOOLEAN DEFAULT FALSE
                )
            """)
            
            # Semantic events table (branch-aware)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS semantic_events (
                    event_id TEXT PRIMARY KEY,
                    commit_hash TEXT NOT NULL,
                    branch TEXT,
                    event_type TEXT NOT NULL,
                    node_id TEXT,
                    location TEXT,
                    details TEXT,
                    layer TEXT,
                    layer_description TEXT,
                    confidence REAL,
                    reasoning TEXT,
                    impact TEXT,
                    created_at INTEGER NOT NULL,
                    git_notes_synced BOOLEAN DEFAULT FALSE,
                    FOREIGN KEY (commit_hash) REFERENCES commits(commit_hash)
                )
            """)
            
            # Branch tracking table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS branches (
                    branch_name TEXT PRIMARY KEY,
                    created_at INTEGER NOT NULL,
                    last_analyzed INTEGER,
                    parent_branch TEXT,
                    semantic_events_count INTEGER DEFAULT 0
                )
            """)
            
            conn.commit()
    
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
    
    def store_semantic_event(self, event_data: Dict[str, Any]) -> str:
        """Store a semantic event in the repository-local database."""
        event_id = str(uuid.uuid4())
        current_branch = self.get_current_branch()
        created_at = int(datetime.now().timestamp())
        
        with self.get_connection() as conn:
            conn.execute("""
                INSERT INTO semantic_events (
                    event_id, commit_hash, branch, event_type, node_id, location,
                    details, layer, layer_description, confidence, reasoning, impact, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                event_id,
                event_data.get("commit_hash"),
                current_branch,
                event_data.get("event_type"),
                event_data.get("node_id"),
                event_data.get("location"),
                event_data.get("details"),
                event_data.get("layer"),
                event_data.get("layer_description"),
                event_data.get("confidence", 1.0),
                event_data.get("reasoning"),
                event_data.get("impact"),
                created_at
            ))
            conn.commit()
        
        return event_id
    
    def get_branch_events(self, branch: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get semantic events for a specific branch."""
        if branch is None:
            branch = self.get_current_branch()
        
        with self.get_connection() as conn:
            cursor = conn.execute("""
                SELECT se.event_id, se.commit_hash, se.branch, se.event_type, se.node_id, se.location,
                       se.details, se.layer, se.confidence, se.reasoning, se.impact, se.created_at,
                       c.author, c.timestamp as commit_timestamp, c.message as commit_message
                FROM semantic_events se
                LEFT JOIN commits c ON se.commit_hash = c.commit_hash
                WHERE se.branch = ?
                ORDER BY se.created_at DESC
                LIMIT ?
            """, (branch, limit))
            
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]


class GitNotesManager:
    """Manages semantic data storage and sync via git notes."""
    
    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path).resolve()
        self.notes_ref = "refs/notes/svcs-semantic"
    
    def store_semantic_data_as_note(self, commit_hash: str, semantic_events: List[Dict[str, Any]]) -> bool:
        """Store semantic analysis data as a git note attached to a commit."""
        try:
            # Prepare semantic data for storage
            note_data = {
                "version": "1.0",
                "timestamp": datetime.now().isoformat(),
                "semantic_events": semantic_events,
                "analyzer": "svcs",
                "commit_hash": commit_hash
            }
            
            # Convert to JSON
            note_content = json.dumps(note_data, indent=2)
            
            # Store as git note
            result = subprocess.run([
                "git", "notes", "--ref", self.notes_ref, "add", 
                "-m", note_content, commit_hash
            ], cwd=self.repo_path, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"Stored semantic data as git note for commit {commit_hash[:8]}")
                return True
            else:
                # Note might already exist, try to append
                result = subprocess.run([
                    "git", "notes", "--ref", self.notes_ref, "append",
                    "-m", f"\n---\n{note_content}", commit_hash
                ], cwd=self.repo_path, capture_output=True, text=True)
                
                if result.returncode == 0:
                    logger.info(f"Appended semantic data to existing git note for commit {commit_hash[:8]}")
                    return True
                else:
                    logger.error(f"Failed to store git note: {result.stderr}")
                    return False
        
        except Exception as e:
            logger.error(f"Error storing semantic data as git note: {e}")
            return False
    
    def get_semantic_data_from_note(self, commit_hash: str) -> Optional[Dict[str, Any]]:
        """Retrieve semantic analysis data from git note."""
        try:
            result = subprocess.run([
                "git", "notes", "--ref", self.notes_ref, "show", commit_hash
            ], cwd=self.repo_path, capture_output=True, text=True)
            
            if result.returncode == 0:
                # Parse the note content (might contain multiple JSON blocks)
                note_content = result.stdout.strip()
                
                # Try to parse as single JSON first
                try:
                    return json.loads(note_content)
                except json.JSONDecodeError:
                    # Handle multiple JSON blocks separated by ---
                    json_blocks = note_content.split('\n---\n')
                    for block in json_blocks:
                        try:
                            data = json.loads(block.strip())
                            if data.get("commit_hash") == commit_hash:
                                return data
                        except json.JSONDecodeError:
                            continue
            
            return None
        
        except Exception as e:
            logger.error(f"Error retrieving semantic data from git note: {e}")
            return None
    
    def sync_notes_to_remote(self, remote: str = "origin") -> bool:
        """Push semantic git notes to remote repository."""
        try:
            # First check if remote exists
            check_remote = subprocess.run([
                "git", "remote", "get-url", remote
            ], cwd=self.repo_path, capture_output=True, text=True)
            
            if check_remote.returncode != 0:
                logger.warning(f"Remote '{remote}' not configured in repository")
                return False
            
            result = subprocess.run([
                "git", "push", remote, self.notes_ref
            ], cwd=self.repo_path, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"Successfully pushed semantic git notes to {remote}")
                return True
            else:
                logger.error(f"Failed to push git notes to '{remote}': {result.stderr}")
                return False
        
        except Exception as e:
            logger.error(f"Error syncing notes to remote: {e}")
            return False
    
    def fetch_notes_from_remote(self, remote: str = "origin") -> bool:
        """Fetch semantic git notes from remote repository."""
        try:
            # First check if remote exists
            check_remote = subprocess.run([
                "git", "remote", "get-url", remote
            ], cwd=self.repo_path, capture_output=True, text=True)
            
            if check_remote.returncode != 0:
                logger.warning(f"Remote '{remote}' not configured in repository")
                return False
            
            # Check if notes reference exists on remote
            check_notes = subprocess.run([
                "git", "ls-remote", remote, f"refs/notes/svcs-semantic"
            ], cwd=self.repo_path, capture_output=True, text=True)
            
            if check_notes.returncode != 0 or not check_notes.stdout.strip():
                logger.info(f"No semantic git notes found on remote '{remote}'")
                return False
            
            # Fetch the notes - success includes both updates and "already up to date"
            result = subprocess.run([
                "git", "fetch", remote, f"{self.notes_ref}:{self.notes_ref}"
            ], cwd=self.repo_path, capture_output=True, text=True)
            
            # Git fetch returns 0 for both successful updates and "already up to date"
            if result.returncode == 0:
                if result.stderr and "up to date" in result.stderr.lower():
                    logger.info(f"Semantic git notes are already up to date with {remote}")
                else:
                    logger.info(f"Successfully fetched semantic git notes from {remote}")
                return True
            else:
                logger.warning(f"Failed to fetch git notes from '{remote}': {result.stderr}")
                return False
        
        except Exception as e:
            logger.error(f"Error fetching notes from remote: {e}")
            return False


class RepositoryLocalSVCS:
    """Repository-local SVCS coordinator that integrates database and git notes."""
    
    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path).resolve()
        self.db = RepositoryLocalDatabase(repo_path)
        self.git_notes = GitNotesManager(repo_path)
    
    def is_git_repository(self) -> bool:
        """Check if the path is a git repository."""
        return (self.repo_path / ".git").exists()
    
    def initialize_repository(self) -> str:
        """Initialize SVCS for this repository."""
        if not self.is_git_repository():
            return f"❌ Not a git repository: {self.repo_path}"
        
        # Database and directories are created in __init__
        current_branch = self.db.get_current_branch()
        
        with self.db.get_connection() as conn:
            # Check if already initialized
            cursor = conn.execute("SELECT id FROM repository_info WHERE repo_path = ?", (str(self.repo_path),))
            if cursor.fetchone():
                return f"✅ SVCS already initialized for repository at {self.repo_path}"
            
            # Initialize repository info
            created_at = int(datetime.now().timestamp())
            conn.execute("""
                INSERT INTO repository_info (repo_path, created_at, current_branch)
                VALUES (?, ?, ?)
            """, (str(self.repo_path), created_at, current_branch))
            
            # Track current branch
            conn.execute("""
                INSERT OR REPLACE INTO branches (branch_name, created_at)
                VALUES (?, ?)
            """, (current_branch, created_at))
            
            conn.commit()
        
        return f"✅ SVCS initialized for repository at {self.repo_path} (branch: {current_branch})"
    
    def store_commit_metadata(self, commit_hash: str) -> bool:
        """Store commit metadata (author, timestamp, message) in the commits table."""
        try:
            import subprocess
            
            # Get commit info from git
            result = subprocess.run([
                'git', 'show', '--format=%an%n%at%n%s', '--no-patch', commit_hash
            ], cwd=self.repo_path, capture_output=True, text=True, check=True)
            
            lines = result.stdout.strip().split('\n')
            if len(lines) >= 3:
                author = lines[0]
                timestamp = int(lines[1])
                message = lines[2]
                
                current_branch = self.db.get_current_branch()
                created_at = int(datetime.now().timestamp())
                
                with self.db.get_connection() as conn:
                    # Check if commit already exists
                    cursor = conn.execute("SELECT commit_hash FROM commits WHERE commit_hash = ?", (commit_hash,))
                    if cursor.fetchone():
                        return True  # Already exists
                    
                    # Insert new commit
                    conn.execute("""
                        INSERT INTO commits (commit_hash, branch, author, timestamp, message, created_at, git_notes_synced)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (commit_hash, current_branch, author, timestamp, message, created_at, 0))
                    conn.commit()
                    return True
            return False
            
        except Exception as e:
            print(f"Warning: Could not store commit metadata: {e}")
            return False

    def analyze_and_store_commit(self, commit_hash: str, semantic_events: List[Dict[str, Any]]) -> Tuple[int, bool]:
        """Analyze a commit and store both locally and as git notes."""
        # Store commit metadata first
        self.store_commit_metadata(commit_hash)
        
        # Store semantic events in local database
        stored_count = 0
        for event_data in semantic_events:
            event_data["commit_hash"] = commit_hash
            self.db.store_semantic_event(event_data)
            stored_count += 1
        
        # Store as git notes for team sharing
        notes_success = self.git_notes.store_semantic_data_as_note(commit_hash, semantic_events)
        
        return stored_count, notes_success
    
    def get_branch_events(self, branch: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get semantic events for a specific branch."""
        return self.db.get_branch_events(branch, limit)
    
    def get_current_branch(self) -> str:
        """Get current git branch."""
        return self.db.get_current_branch()
    
    def compare_branches(self, branch1: str, branch2: str, limit: int = 100) -> Dict[str, Any]:
        """Compare semantic events between two branches."""
        branch1_events = self.get_branch_events(branch1, limit)
        branch2_events = self.get_branch_events(branch2, limit)
        
        return {
            "branch1": branch1,
            "branch2": branch2,
            "branch1_count": len(branch1_events),
            "branch2_count": len(branch2_events),
            "branch1_events": branch1_events,
            "branch2_events": branch2_events
        }
    
    def get_repository_status(self) -> Dict[str, Any]:
        """Get repository SVCS status."""
        current_branch = self.db.get_current_branch()
        
        with self.db.get_connection() as conn:
            # Get repository info
            cursor = conn.execute("SELECT created_at FROM repository_info WHERE repo_path = ?", (str(self.repo_path),))
            repo_info = cursor.fetchone()
            
            if not repo_info:
                return {"initialized": False}
            
            # Get branch events count
            cursor = conn.execute("SELECT COUNT(*) FROM semantic_events WHERE branch = ?", (current_branch,))
            events_count = cursor.fetchone()[0]
            
            # Get total commits analyzed
            cursor = conn.execute("SELECT COUNT(*) FROM commits")
            commits_count = cursor.fetchone()[0]
            
            return {
                "initialized": True,
                "repository_path": str(self.repo_path),
                "current_branch": current_branch,
                "semantic_events_count": events_count,
                "commits_analyzed": commits_count,
                "created_at": repo_info[0]
            }
    
    def process_merge(self, source_branch: str = None, target_branch: str = None) -> str:
        """Process semantic events after a git merge. Ensures all unique events from source branch are copied to target branch."""
        if target_branch is None:
            target_branch = self.get_current_branch()
        if source_branch is None:
            # Try to detect the merged branch from git (handle both merge commits and fast-forward merges)
            try:
                # First, try to detect from merge commit (non-fast-forward merges)
                result = subprocess.run(
                    ["git", "log", "--merges", "-1", "--pretty=format:%P"],
                    cwd=self.repo_path,
                    capture_output=True,
                    text=True,
                    check=True
                )
                if result.stdout.strip():
                    merge_parents = result.stdout.strip().split()
                    if len(merge_parents) >= 2:
                        # Find the parent that is NOT the current branch tip
                        current_commit = subprocess.run(
                            ["git", "rev-parse", target_branch],
                            cwd=self.repo_path,
                            capture_output=True,
                            text=True,
                            check=True
                        ).stdout.strip()
                        source_commit = [c for c in merge_parents if c != current_commit]
                        if source_commit:
                            source_commit = source_commit[0]
                            # Find branch name for this commit
                            branch_result = subprocess.run(
                                ["git", "branch", "--contains", source_commit],
                                cwd=self.repo_path,
                                capture_output=True,
                                text=True,
                                check=True
                            )
                            branches = [b.strip().replace('* ', '') for b in branch_result.stdout.strip().split('\n')]
                            for branch in branches:
                                if branch != target_branch and not branch.startswith('('):
                                    source_branch = branch
                                    break
                
                # If no merge commit found, try to detect from git reflog (fast-forward merges)
                if not source_branch:
                    reflog_result = subprocess.run(
                        ["git", "reflog", "-1", "--grep=merge", "--pretty=format:%gs"],
                        cwd=self.repo_path,
                        capture_output=True,
                        text=True,
                        check=True
                    )
                    if reflog_result.stdout.strip():
                        # Parse reflog message like "merge feature/branch: Fast-forward"
                        reflog_msg = reflog_result.stdout.strip()
                        if "merge" in reflog_msg.lower():
                            # Extract branch name from reflog message
                            parts = reflog_msg.split()
                            for i, part in enumerate(parts):
                                if part == "merge" and i + 1 < len(parts):
                                    potential_branch = parts[i + 1].rstrip(':')
                                    # Verify this branch exists in our database
                                    with self.db.get_connection() as conn:
                                        cursor = conn.execute("SELECT COUNT(*) FROM semantic_events WHERE branch = ?", (potential_branch,))
                                        if cursor.fetchone()[0] > 0:
                                            source_branch = potential_branch
                                            break
                
                # Alternative approach: check for recently updated branches
                if not source_branch:
                    # Get all branches in the database that have semantic events
                    with self.db.get_connection() as conn:
                        cursor = conn.execute("""
                            SELECT DISTINCT branch FROM semantic_events 
                            WHERE branch != ? AND branch IS NOT NULL
                            ORDER BY created_at DESC
                        """, (target_branch,))
                        potential_branches = [row[0] for row in cursor.fetchall()]
                        
                        # For each potential branch, check if it has events not in target
                        for branch in potential_branches:
                            cursor = conn.execute("""
                                SELECT COUNT(*) FROM (
                                    SELECT event_type, node_id, location FROM semantic_events WHERE branch = ?
                                    EXCEPT
                                    SELECT event_type, node_id, location FROM semantic_events WHERE branch = ?
                                )
                            """, (branch, target_branch))
                            unique_count = cursor.fetchone()[0]
                            if unique_count > 0:
                                source_branch = branch
                                break
                                
            except subprocess.CalledProcessError:
                pass
        if not source_branch:
            return "ℹ️ SVCS: No source branch detected for merge processing"
        with self.db.get_connection() as conn:
            # Find all unique (event_type, node_id, location) in source branch not present in target branch
            cursor = conn.execute("""
                SELECT se1.event_type, se1.node_id, se1.location
                FROM semantic_events se1
                WHERE se1.branch = ?
                EXCEPT
                SELECT se2.event_type, se2.node_id, se2.location
                FROM semantic_events se2
                WHERE se2.branch = ?
            """, (source_branch, target_branch))
            unique_keys = cursor.fetchall()
            if not unique_keys:
                return f"ℹ️ SVCS: No new semantic events to merge from {source_branch} to {target_branch}"
            merged_count = 0
            for event_type, node_id, location in unique_keys:
                # Get the most recent event for this key from the source branch
                event_cursor = conn.execute("""
                    SELECT commit_hash, event_type, node_id, location, details, layer, layer_description, confidence, reasoning, impact, created_at
                    FROM semantic_events
                    WHERE branch = ? AND event_type = ? AND node_id = ? AND location = ?
                    ORDER BY created_at DESC LIMIT 1
                """, (source_branch, event_type, node_id, location))
                event = event_cursor.fetchone()
                if event:
                    new_event_id = str(uuid.uuid4())
                    conn.execute("""
                        INSERT INTO semantic_events 
                        (event_id, commit_hash, branch, event_type, node_id, location,
                        details, layer, layer_description, confidence, reasoning, impact, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        new_event_id,
                        event[0],  # commit_hash
                        target_branch,
                        event[1],  # event_type
                        event[2],  # node_id
                        event[3],  # location
                        event[4],  # details
                        event[5],  # layer
                        event[6],  # layer_description
                        event[7],  # confidence
                        event[8],  # reasoning
                        event[9],  # impact
                        event[10]  # created_at
                    ))
                    merged_count += 1
            conn.commit()
            return f"✅ SVCS: Merged {merged_count} semantic events from {source_branch} to {target_branch}"

    def import_semantic_events_from_notes(self, commit_hashes: List[str] = None) -> int:
        """Import semantic events from git notes for specified commits or recent commits."""
        if commit_hashes is None:
            # Get recent commits that might have notes but no local semantic events
            try:
                result = subprocess.run([
                    "git", "log", "--format=%H", "-10"
                ], cwd=self.repo_path, capture_output=True, text=True, check=True)
                commit_hashes = result.stdout.strip().split('\n')
            except subprocess.CalledProcessError:
                return 0
        
        imported_count = 0
        current_branch = self.get_current_branch()
        
        for commit_hash in commit_hashes:
            if not commit_hash.strip():
                continue
                
            # Check if we already have semantic events for this commit
            with self.db.get_connection() as conn:
                cursor = conn.execute(
                    "SELECT COUNT(*) FROM semantic_events WHERE commit_hash = ?", 
                    (commit_hash,)
                )
                if cursor.fetchone()[0] > 0:
                    continue  # Already have events for this commit
                
                # Try to get semantic data from git notes
                note_data = self.git_notes.get_semantic_data_from_note(commit_hash)
                if note_data and 'semantic_events' in note_data:
                    # Store commit metadata
                    self.store_commit_metadata(commit_hash)
                    
                    # Import semantic events
                    for event_data in note_data['semantic_events']:
                        event_data['commit_hash'] = commit_hash
                        event_id = str(uuid.uuid4())
                        created_at = event_data.get('created_at', int(datetime.now().timestamp()))
                        
                        conn.execute("""
                            INSERT INTO semantic_events (
                                event_id, commit_hash, branch, event_type, node_id, location,
                                details, layer, layer_description, confidence, reasoning, impact, created_at
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            event_id,
                            commit_hash,
                            current_branch,
                            event_data.get("event_type"),
                            event_data.get("node_id"),
                            event_data.get("location"),
                            event_data.get("details"),
                            event_data.get("layer", "core"),
                            event_data.get("layer_description"),
                            event_data.get("confidence", 1.0),
                            event_data.get("reasoning"),
                            event_data.get("impact"),
                            created_at
                        ))
                        imported_count += 1
                    
                    conn.commit()
        
        return imported_count

    def auto_resolve_merge(self) -> str:
        """Automatically resolve common post-merge scenarios and semantic event issues."""
        results = []
        
        # Check if we're in a post-merge state
        try:
            # Check for recent merge in git log
            merge_check = subprocess.run([
                "git", "log", "-1", "--merges", "--pretty=format:%s"
            ], cwd=self.repo_path, capture_output=True, text=True, check=True)
            
            if merge_check.stdout.strip():
                results.append("🔍 Recent merge detected")
                
                # Import semantic events from git notes
                imported = self.import_semantic_events_from_notes()
                if imported > 0:
                    results.append(f"📥 Imported {imported} semantic events from git notes")
                
                # Process merge event transfer
                merge_result = self.process_merge()
                results.append(f"🔄 {merge_result}")
            else:
                # Check for uncommitted merge changes
                status_result = subprocess.run([
                    "git", "status", "--porcelain"
                ], cwd=self.repo_path, capture_output=True, text=True, check=True)
                
                if status_result.stdout.strip():
                    results.append("ℹ️ Uncommitted changes detected - run 'git commit' then 'svcs sync'")
                else:
                    # Just import any missing semantic events
                    imported = self.import_semantic_events_from_notes()
                    if imported > 0:
                        results.append(f"📥 Imported {imported} semantic events from git notes")
                    else:
                        results.append("✅ No pending merge operations or missing events")
        
        except subprocess.CalledProcessError:
            results.append("⚠️ Could not determine git state")
        
        return " | ".join(results) if results else "✅ No issues detected"

    def get_config(self, key: str, default=None):
        """Get a configuration value."""
        with self.db.get_connection() as conn:
            cursor = conn.execute("SELECT config FROM repository_info WHERE repo_path = ?", (str(self.repo_path),))
            result = cursor.fetchone()
            if result and result[0]:
                config = json.loads(result[0])
                return config.get(key, default)
            return default
    
    def set_config(self, key: str, value):
        """Set a configuration value."""
        with self.db.get_connection() as conn:
            cursor = conn.execute("SELECT config FROM repository_info WHERE repo_path = ?", (str(self.repo_path),))
            result = cursor.fetchone()
            
            if result and result[0]:
                config = json.loads(result[0])
            else:
                config = {}
            
            config[key] = value
            
            conn.execute("UPDATE repository_info SET config = ? WHERE repo_path = ?", 
                        (json.dumps(config), str(self.repo_path)))
            conn.commit()
    
    def get_all_config(self) -> Dict[str, Any]:
        """Get all configuration values."""
        with self.db.get_connection() as conn:
            cursor = conn.execute("SELECT config FROM repository_info WHERE repo_path = ?", (str(self.repo_path),))
            result = cursor.fetchone()
            if result and result[0]:
                return json.loads(result[0])
            return {}

    def analyze_current_commit(self) -> bool:
        """Analyze the current/latest commit for semantic events."""
        try:
            # Get the latest commit hash
            result = subprocess.run(['git', 'rev-parse', 'HEAD'], 
                                  cwd=self.repo_path, capture_output=True, text=True, check=True)
            commit_hash = result.stdout.strip()
            
            # Use the PROVEN working modular analyzer system
            from svcs.semantic_analyzer import SVCSModularAnalyzer
            analyzer = SVCSModularAnalyzer(str(self.repo_path))
            
            # Get changed files in this commit
            try:
                cmd = ["git", "diff-tree", "--no-commit-id", "--name-only", "-r", commit_hash]
                result = subprocess.run(cmd, cwd=self.repo_path, capture_output=True, text=True, check=True)
                changed_files = [f.strip() for f in result.stdout.strip().split('\n') if f.strip()]
            except subprocess.CalledProcessError:
                # Try initial commit approach
                cmd = ["git", "ls-tree", "--name-only", "-r", commit_hash]
                result = subprocess.run(cmd, cwd=self.repo_path, capture_output=True, text=True, check=True)
                changed_files = [f.strip() for f in result.stdout.strip().split('\n') if f.strip()]
            
            if not changed_files:
                print("🔍 SVCS: No files changed in this commit")
                return False
            
            # Analyze each changed file
            all_events = []
            for filepath in changed_files:
                # Only analyze supported file types
                if not filepath.endswith(('.py', '.js', '.ts', '.php', '.phtml')):
                    continue
                    
                try:
                    # Get file content before and after
                    try:
                        before_result = subprocess.run(['git', 'show', f'{commit_hash}~1:{filepath}'], 
                                                     cwd=self.repo_path, capture_output=True, text=True, check=True)
                        before_content = before_result.stdout
                    except subprocess.CalledProcessError:
                        before_content = ""  # New file or initial commit
                    
                    after_result = subprocess.run(['git', 'show', f'{commit_hash}:{filepath}'], 
                                                cwd=self.repo_path, capture_output=True, text=True, check=True)
                    after_content = after_result.stdout
                    
                    # Use the working analyzer
                    file_events = analyzer.analyze_changes(filepath, before_content, after_content)
                    
                    # Add commit context to each event
                    for event in file_events:
                        event['commit_hash'] = commit_hash
                        event['file_path'] = filepath
                        
                    all_events.extend(file_events)
                    
                except Exception as e:
                    print(f"⚠️ Error analyzing {filepath}: {e}")
                    continue
            
            if all_events:
                # Store the events using our existing method
                stored_count, notes_success = self.analyze_and_store_commit(commit_hash, all_events)
                print(f"✅ SVCS: Stored {stored_count} semantic events")
                if notes_success:
                    print("📝 SVCS: Semantic data saved as git notes")
                return True
            else:
                print("🔍 SVCS: Analyzing semantic changes...")
                print("ℹ️ SVCS: No semantic events detected in this commit")
                return False
                
        except Exception as e:
            print(f"❌ SVCS: Semantic analysis failed: {e}")
            logger.error(f"Error in analyze_current_commit: {e}")
            return False


def demo_repository_local_svcs():
    """Demonstrate the new repository-local SVCS architecture."""
    print("🚀 Repository-Local SVCS Demo")
    print("=" * 50)
    
    # Get current directory (assuming it's a git repo)
    current_dir = Path.cwd()
    
    # Initialize repository-local SVCS
    local_svcs = RepositoryLocalSVCS(current_dir)
    
    print(f"📁 Repository: {current_dir}")
    print(f"🔍 Git repository: {local_svcs.is_git_repository()}")
    
    # Initialize
    init_result = local_svcs.initialize_repository()
    print(f"🔧 Initialization: {init_result}")
    
    # Get status
    status = local_svcs.get_repository_status()
    print(f"📊 Status: {status}")
    
    return local_svcs


if __name__ == "__main__":
    demo_repository_local_svcs()
