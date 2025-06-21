#!/usr/bin/env python3
"""
Integration module for existing SVCS functionality.

This module bridges the existing SVCS codebase with the new MCP server architecture.
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Optional


class SVCSIntegration:
    """Integration layer between MCP server and existing SVCS functionality."""
    
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.svcs_path = self.project_path / '.svcs'
        
        # Add existing SVCS modules to path
        if self.svcs_path.exists():
            sys.path.insert(0, str(self.svcs_path))
    
    def has_existing_svcs(self) -> bool:
        """Check if project has existing SVCS installation."""
        return (self.svcs_path / 'api.py').exists()
    
    def migrate_existing_data(self, global_db, project_id: str) -> bool:
        """Migrate existing SVCS data to global database."""
        if not self.has_existing_svcs():
            return False
        
        local_db = self.svcs_path / 'history.db'
        if not local_db.exists():
            return False
        
        try:
            # Import existing SVCS API
            sys.path.insert(0, str(self.svcs_path))
            from api import _execute_query as local_execute_query
            
            # Get existing data
            commits = local_execute_query("SELECT * FROM commits", ())
            events = local_execute_query("SELECT * FROM semantic_events", ())
            
            # Migrate to global database
            with global_db.get_connection() as conn:
                # Migrate commits
                for commit in commits:
                    conn.execute("""
                        INSERT OR IGNORE INTO commits 
                        (commit_hash, project_id, author, timestamp, message)
                        VALUES (?, ?, ?, ?, ?)
                    """, (
                        commit['commit_hash'], project_id, commit['author'],
                        commit['timestamp'], commit['message']
                    ))
                
                # Migrate events
                for event in events:
                    conn.execute("""
                        INSERT OR IGNORE INTO semantic_events
                        (event_id, project_id, commit_hash, event_type, node_id, 
                         location, details, layer, layer_description, confidence,
                         reasoning, impact, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        f"{project_id}_{event['event_id']}", project_id,
                        event['commit_hash'], event['event_type'], event['node_id'],
                        event['location'], event['details'], event['layer'],
                        event['layer_description'], event['confidence'],
                        event['reasoning'], event['impact'],
                        event.get('created_at', 0)
                    ))
                
                conn.commit()
            
            return True
            
        except Exception as e:
            print(f"Error migrating data: {e}")
            return False
    
    def analyze_commit(self, commit_hash: str, global_db, project_id: str) -> bool:
        """Analyze a commit using existing SVCS logic."""
        if not self.has_existing_svcs():
            return False
        
        try:
            # This would integrate with the existing SVCS analysis pipeline
            # For now, return True to indicate successful processing
            return True
            
        except Exception as e:
            print(f"Error analyzing commit {commit_hash}: {e}")
            return False
    
    def query_evolution(self, query: str, global_db, project_id: str) -> Dict:
        """Query evolution using existing conversational interface."""
        if not self.has_existing_svcs():
            return {
                "error": "No existing SVCS installation found",
                "suggestion": "Project needs semantic analysis setup"
            }
        
        try:
            # This would integrate with the existing svcs_discuss.py
            # conversational interface, modified to work with project_id filtering
            
            # For now, return a placeholder
            return {
                "query": query,
                "project_id": project_id,
                "results": [],
                "message": "Evolution querying will be integrated in next phase"
            }
            
        except Exception as e:
            return {
                "error": f"Query failed: {str(e)}",
                "query": query
            }


def setup_project_analysis(project_path: str, global_db, project_id: str) -> bool:
    """Set up semantic analysis for a project."""
    integration = SVCSIntegration(project_path)
    
    # Check if existing SVCS data can be migrated
    if integration.has_existing_svcs():
        print(f"Found existing SVCS data in {project_path}")
        success = integration.migrate_existing_data(global_db, project_id)
        if success:
            print("✅ Successfully migrated existing SVCS data")
        else:
            print("⚠️ Failed to migrate some existing data")
    
    # TODO: Set up analysis pipeline for this project
    # This would involve:
    # 1. Configuring semantic analyzers for the project's language(s)
    # 2. Setting up background processing for commits
    # 3. Initializing any project-specific settings
    
    return True


def process_commit_for_project(project_path: str, global_db, project_id: str) -> bool:
    """Process the latest commit for semantic analysis."""
    integration = SVCSIntegration(project_path)
    
    # Get latest commit hash
    import subprocess
    try:
        result = subprocess.run(
            ['git', 'rev-parse', 'HEAD'],
            cwd=project_path,
            capture_output=True,
            text=True,
            check=True
        )
        commit_hash = result.stdout.strip()
        
        # Analyze the commit
        return integration.analyze_commit(commit_hash, global_db, project_id)
        
    except subprocess.CalledProcessError:
        return False
