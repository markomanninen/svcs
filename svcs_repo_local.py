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
                SELECT event_id, commit_hash, branch, event_type, node_id, location,
                       details, layer, confidence, reasoning, impact, created_at
                FROM semantic_events
                WHERE branch = ?
                ORDER BY created_at DESC
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
            result = subprocess.run([
                "git", "push", remote, self.notes_ref
            ], cwd=self.repo_path, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"Successfully pushed semantic git notes to {remote}")
                return True
            else:
                logger.error(f"Failed to push git notes: {result.stderr}")
                return False
        
        except Exception as e:
            logger.error(f"Error syncing notes to remote: {e}")
            return False
    
    def fetch_notes_from_remote(self, remote: str = "origin") -> bool:
        """Fetch semantic git notes from remote repository."""
        try:
            result = subprocess.run([
                "git", "fetch", remote, f"{self.notes_ref}:{self.notes_ref}"
            ], cwd=self.repo_path, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"Successfully fetched semantic git notes from {remote}")
                return True
            else:
                logger.warning(f"No semantic notes found on remote: {result.stderr}")
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
    
    def analyze_and_store_commit(self, commit_hash: str, semantic_events: List[Dict[str, Any]]) -> Tuple[int, bool]:
        """Analyze a commit and store both locally and as git notes."""
        # Store in local database
        stored_count = 0
        for event_data in semantic_events:
            event_data["commit_hash"] = commit_hash
            self.db.store_semantic_event(event_data)
            stored_count += 1
        
        # Store as git notes for team sharing
        notes_success = self.git_notes.store_semantic_data_as_note(commit_hash, semantic_events)
        
        return stored_count, notes_success
    
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


# Migration tools for moving from global to repository-local architecture
class SVCSMigrator:
    """Tools for migrating from global to repository-local SVCS architecture."""
    
    def __init__(self, global_db_path: str = None):
        if global_db_path is None:
            global_db_path = Path.home() / ".svcs" / "global.db"
        self.global_db_path = Path(global_db_path)
    
    def migrate_project_to_local(self, project_path: str) -> str:
        """Migrate a project from global database to repository-local storage."""
        project_path = Path(project_path).resolve()
        
        if not self.global_db_path.exists():
            return f"❌ Global database not found: {self.global_db_path}"
        
        # Initialize repository-local SVCS
        local_svcs = RepositoryLocalSVCS(project_path)
        result = local_svcs.initialize_repository()
        
        if "❌" in result:
            return result
        
        # Extract data from global database
        try:
            with sqlite3.connect(self.global_db_path) as global_conn:
                # Get project_id
                cursor = global_conn.execute(
                    "SELECT project_id FROM projects WHERE path = ?", (str(project_path),)
                )
                project_result = cursor.fetchone()
                
                if not project_result:
                    return f"⚠️ Project not found in global database: {project_path}"
                
                project_id = project_result[0]
                
                # Get semantic events
                cursor = global_conn.execute("""
                    SELECT commit_hash, event_type, node_id, location, details, 
                           layer, layer_description, confidence, reasoning, impact, created_at
                    FROM semantic_events 
                    WHERE project_id = ?
                    ORDER BY created_at
                """, (project_id,))
                
                events = cursor.fetchall()
                migrated_count = 0
                
                # Group events by commit
                commit_events = {}
                for event in events:
                    commit_hash = event[0]
                    if commit_hash not in commit_events:
                        commit_events[commit_hash] = []
                    
                    event_data = {
                        "event_type": event[1],
                        "node_id": event[2],
                        "location": event[3],
                        "details": event[4],
                        "layer": event[5],
                        "layer_description": event[6],
                        "confidence": event[7],
                        "reasoning": event[8],
                        "impact": event[9],
                        "created_at": event[10]
                    }
                    commit_events[commit_hash].append(event_data)
                
                # Migrate each commit's events
                for commit_hash, semantic_events in commit_events.items():
                    stored_count, notes_success = local_svcs.analyze_and_store_commit(
                        commit_hash, semantic_events
                    )
                    migrated_count += stored_count
                
                return f"✅ Migrated {migrated_count} semantic events to repository-local storage"
        
        except Exception as e:
            return f"❌ Migration failed: {e}"
    
    def list_migratable_projects(self) -> List[Dict[str, Any]]:
        """List projects that can be migrated from global database."""
        if not self.global_db_path.exists():
            return []
        
        try:
            with sqlite3.connect(self.global_db_path) as conn:
                cursor = conn.execute("""
                    SELECT name, path, created_at, status, 
                           (SELECT COUNT(*) FROM semantic_events WHERE project_id = projects.project_id) as event_count
                    FROM projects 
                    WHERE status = 'active'
                    ORDER BY created_at DESC
                """)
                
                columns = [desc[0] for desc in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        except Exception as e:
            logger.error(f"Error listing projects: {e}")
            return []


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
