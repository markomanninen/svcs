#!/usr/bin/env python3
"""
SVCS Repository-Local MCP Server Core

Updated MCP server that works with the new centralized architecture:
- Uses repository-local databases (.svcs/semantic.db)
- Integrates with git notes for team collaboration
- Supports multiple repositories simultaneously
- Compatible with the new multi-language analyzer
- Uses centralized initialization and registry system
"""

import asyncio
import json
import logging
import os
import sqlite3
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import subprocess

# Import the new repository-local modules
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import new centralized architecture modules
try:
    from svcs.centralized_utils import smart_init_svcs
    from svcs_repo_local import RepositoryLocalSVCS, RepositoryLocalDatabase, GitNotesManager
    from svcs_repo_analyzer import RepositoryLocalSemanticAnalyzer
    from svcs_repo_hooks import SVCSRepositoryManager
    from svcs_web_repository_manager import web_repository_manager
    NEW_ARCH_AVAILABLE = True
except ImportError as e:
    logging.warning(f"New architecture modules not available: {e}")
    # Fallback to legacy imports
    from svcs_repo_local import RepositoryLocalSVCS, RepositoryLocalDatabase, GitNotesManager
    from svcs_repo_analyzer import RepositoryLocalSemanticAnalyzer
    NEW_ARCH_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("svcs-repo-local-mcp")


class RepositoryManager:
    """Manages multiple repository-local SVCS instances."""
    
    def __init__(self):
        self.repositories: Dict[str, RepositoryLocalSVCS] = {}
        self.analyzers: Dict[str, RepositoryLocalSemanticAnalyzer] = {}
    
    def register_repository(self, repo_path: str, name: str = None) -> Dict[str, Any]:
        """Register a repository for SVCS tracking using new centralized architecture."""
        repo_path = Path(repo_path).resolve()
        
        if not repo_path.exists():
            return {"success": False, "error": f"Repository path does not exist: {repo_path}"}
        
        if not (repo_path / ".git").exists():
            return {"success": False, "error": f"Not a git repository: {repo_path}"}
        
        repo_id = str(repo_path)
        if name is None:
            name = repo_path.name
        
        try:
            if NEW_ARCH_AVAILABLE:
                # Use new centralized initialization
                result = smart_init_svcs(repo_path)
                
                if "❌" in result:
                    return {"success": False, "error": result}
                
                # Register in central registry
                try:
                    registry_result = web_repository_manager.register_repository(str(repo_path), name)
                    if not registry_result.get('success'):
                        logger.warning(f"Registry registration failed: {registry_result.get('error')}")
                except Exception as e:
                    logger.warning(f"Registry registration failed: {e}")
                
                # Initialize SVCS instance for MCP operations
                svcs = RepositoryLocalSVCS(repo_path)
                analyzer = RepositoryLocalSemanticAnalyzer(repo_path)
                
                # Store references
                self.repositories[repo_id] = svcs
                self.analyzers[repo_id] = analyzer
                
                return {
                    "success": True,
                    "repo_id": repo_id,
                    "name": name,
                    "path": str(repo_path),
                    "message": result
                }
            else:
                # Fallback to legacy initialization
                svcs = RepositoryLocalSVCS(repo_path)
                result = svcs.initialize_repository()
                
                if "❌" in result:
                    return {"success": False, "error": result}
                
                # Initialize semantic analyzer
                analyzer = RepositoryLocalSemanticAnalyzer(repo_path)
                
                # Store references
                self.repositories[repo_id] = svcs
                self.analyzers[repo_id] = analyzer
                
                return {
                    "success": True,
                    "repo_id": repo_id,
                    "name": name,
                    "path": str(repo_path),
                    "message": result
                }
                
        except Exception as e:
            return {"success": False, "error": f"Failed to register repository: {str(e)}"}
    
    def list_repositories(self) -> List[Dict[str, Any]]:
        """List all registered repositories using new architecture."""
        if NEW_ARCH_AVAILABLE:
            try:
                # Use new registry system
                repos = web_repository_manager.discover_repositories()
                return repos
            except Exception as e:
                logger.warning(f"Failed to list from registry: {e}")
                # Fallback to MCP-tracked repositories
                pass
        
        # Fallback to MCP-tracked repositories
        repos = []
        for repo_id, svcs in self.repositories.items():
            try:
                status = svcs.get_repository_status()
                repos.append({
                    "repo_id": repo_id,
                    "path": status.get("repository_path", repo_id),
                    "name": Path(repo_id).name,
                    "current_branch": status.get("current_branch", "unknown"),
                    "events_count": status.get("semantic_events_count", 0),
                    "commits_analyzed": status.get("commits_analyzed", 0),
                    "initialized": status.get("initialized", False),
                    "type": "repository-local"
                })
            except Exception as e:
                repos.append({
                    "repo_id": repo_id,
                    "path": repo_id,
                    "name": Path(repo_id).name,
                    "error": str(e)
                })
        return repos
    
    def get_repository(self, repo_path: str) -> Optional[RepositoryLocalSVCS]:
        """Get a repository SVCS instance."""
        repo_path = str(Path(repo_path).resolve())
        return self.repositories.get(repo_path)
    
    def get_analyzer(self, repo_path: str) -> Optional[RepositoryLocalSemanticAnalyzer]:
        """Get a repository analyzer instance."""
        repo_path = str(Path(repo_path).resolve())
        return self.analyzers.get(repo_path)


class RepositoryLocalMCPServer:
    """MCP Server for repository-local SVCS architecture."""
    
    def __init__(self):
        self.repo_manager = RepositoryManager()
    
    # Repository Management Tools
    
    async def list_projects(self) -> List[Dict[str, Any]]:
        """List all registered SVCS repositories."""
        return self.repo_manager.list_repositories()
    
    async def register_project(self, path: str, name: str) -> Dict[str, Any]:
        """Register a new repository for SVCS tracking."""
        return self.repo_manager.register_repository(path, name)
    
    async def unregister_project(self, path: str) -> Dict[str, Any]:
        """Unregister a repository (remove from active tracking)."""
        repo_path = str(Path(path).resolve())
        if repo_path in self.repo_manager.repositories:
            del self.repo_manager.repositories[repo_path]
            if repo_path in self.repo_manager.analyzers:
                del self.repo_manager.analyzers[repo_path]
            return {"success": True, "message": f"Repository {path} unregistered"}
        return {"success": False, "error": f"Repository {path} not found"}
    
    async def get_project_statistics(self, project_path: str) -> Dict[str, Any]:
        """Get semantic statistics for a repository."""
        svcs = self.repo_manager.get_repository(project_path)
        if not svcs:
            return {"error": f"Repository not found: {project_path}"}
        
        status = svcs.get_repository_status()
        if not status.get("initialized"):
            return {"error": f"Repository not initialized: {project_path}"}
        
        # Get detailed statistics
        with svcs.db.get_connection() as conn:
            # Event type distribution
            cursor = conn.execute("""
                SELECT event_type, COUNT(*) as count
                FROM semantic_events
                GROUP BY event_type
                ORDER BY count DESC
            """)
            event_types = [{"type": row[0], "count": row[1]} for row in cursor.fetchall()]
            
            # Recent activity
            cursor = conn.execute("""
                SELECT DATE(created_at, 'unixepoch') as date, COUNT(*) as count
                FROM semantic_events
                WHERE created_at > ?
                GROUP BY date
                ORDER BY date DESC
                LIMIT 30
            """, (int((datetime.now() - timedelta(days=30)).timestamp()),))
            daily_activity = [{"date": row[0], "count": row[1]} for row in cursor.fetchall()]
            
            # Branch statistics
            cursor = conn.execute("""
                SELECT branch, COUNT(*) as count
                FROM semantic_events
                GROUP BY branch
                ORDER BY count DESC
            """)
            branch_stats = [{"branch": row[0], "count": row[1]} for row in cursor.fetchall()]
        
        return {
            "repository": status,
            "event_types": event_types,
            "daily_activity": daily_activity,
            "branch_statistics": branch_stats
        }
    
    # Semantic Analysis Tools
    
    async def query_semantic_events(self, project_path: str = None, event_type: str = None, 
                                   limit: int = 10) -> List[Dict[str, Any]]:
        """Query semantic events with filtering."""
        if project_path:
            svcs = self.repo_manager.get_repository(project_path)
            if not svcs:
                return [{"error": f"Repository not found: {project_path}"}]
            
            # Query from specific repository
            with svcs.db.get_connection() as conn:
                query = """
                    SELECT event_id, commit_hash, branch, event_type, node_id, location,
                           details, layer, confidence, reasoning, impact, created_at
                    FROM semantic_events
                """
                params = []
                
                if event_type:
                    query += " WHERE event_type = ?"
                    params.append(event_type)
                
                query += " ORDER BY created_at DESC LIMIT ?"
                params.append(limit)
                
                cursor = conn.execute(query, params)
                columns = [desc[0] for desc in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
        else:
            # Query from all repositories
            all_events = []
            for repo_path, svcs in self.repo_manager.repositories.items():
                events = await self.query_semantic_events(repo_path, event_type, limit)
                for event in events:
                    if "error" not in event:
                        event["repository"] = repo_path
                        all_events.append(event)
            
            # Sort by timestamp and limit
            all_events.sort(key=lambda x: x.get("created_at", 0), reverse=True)
            return all_events[:limit]
    
    async def get_recent_activity(self, project_path: str, days: int = 7, limit: int = 15,
                                 author: str = None, layers: List[str] = None) -> List[Dict[str, Any]]:
        """Get recent semantic activity for a repository."""
        svcs = self.repo_manager.get_repository(project_path)
        if not svcs:
            return [{"error": f"Repository not found: {project_path}"}]
        
        since_timestamp = int((datetime.now() - timedelta(days=days)).timestamp())
        
        with svcs.db.get_connection() as conn:
            query = """
                SELECT event_id, commit_hash, branch, event_type, node_id, location,
                       details, layer, confidence, reasoning, created_at
                FROM semantic_events
                WHERE created_at > ?
            """
            params = [since_timestamp]
            
            if layers:
                placeholders = ",".join(["?" for _ in layers])
                query += f" AND layer IN ({placeholders})"
                params.extend(layers)
            
            query += " ORDER BY created_at DESC LIMIT ?"
            params.append(limit)
            
            cursor = conn.execute(query, params)
            columns = [desc[0] for desc in cursor.description]
            events = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            # Add author information if requested
            if author:
                # Filter by author using git log
                filtered_events = []
                for event in events:
                    try:
                        result = subprocess.run([
                            "git", "log", "--format=%an", "-1", event["commit_hash"]
                        ], cwd=project_path, capture_output=True, text=True)
                        if result.returncode == 0 and author.lower() in result.stdout.lower():
                            event["author"] = result.stdout.strip()
                            filtered_events.append(event)
                    except:
                        continue
                events = filtered_events
            
            return events
    
    # Advanced Analysis Tools
    
    async def analyze_current_commit(self, project_path: str) -> Dict[str, Any]:
        """Analyze the current/latest commit for semantic changes."""
        analyzer = self.repo_manager.get_analyzer(project_path)
        if not analyzer:
            return {"error": f"Repository not found: {project_path}"}
        
        try:
            events = analyzer.analyze_commit()
            return {
                "success": True,
                "events_detected": len(events),
                "events": events
            }
        except Exception as e:
            return {"error": f"Analysis failed: {e}"}
    
    async def get_commit_summary(self, project_path: str, commit_hash: str) -> Dict[str, Any]:
        """Get comprehensive summary of a commit including metadata and semantic events."""
        svcs = self.repo_manager.get_repository(project_path)
        if not svcs:
            return {"error": f"Repository not found: {project_path}"}
        
        # Get commit metadata
        try:
            result = subprocess.run([
                "git", "show", "--format=%H|%an|%ae|%at|%s", "--no-patch", commit_hash
            ], cwd=project_path, capture_output=True, text=True, check=True)
            
            commit_info = result.stdout.strip().split("|")
            metadata = {
                "hash": commit_info[0],
                "author": commit_info[1],
                "email": commit_info[2],
                "timestamp": int(commit_info[3]),
                "message": commit_info[4]
            }
            
            # Get changed files
            result = subprocess.run([
                "git", "diff-tree", "--no-commit-id", "--name-only", "-r", commit_hash
            ], cwd=project_path, capture_output=True, text=True, check=True)
            
            changed_files = [f.strip() for f in result.stdout.strip().split('\n') if f.strip()]
            
            # Get semantic events
            with svcs.db.get_connection() as conn:
                cursor = conn.execute("""
                    SELECT event_type, node_id, location, details, layer, confidence, reasoning
                    FROM semantic_events
                    WHERE commit_hash = ?
                    ORDER BY created_at
                """, (commit_hash,))
                
                columns = [desc[0] for desc in cursor.description]
                semantic_events = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            return {
                "metadata": metadata,
                "changed_files": changed_files,
                "semantic_events": semantic_events,
                "summary": {
                    "files_changed": len(changed_files),
                    "semantic_events_count": len(semantic_events)
                }
            }
            
        except subprocess.CalledProcessError as e:
            return {"error": f"Git command failed: {e}"}
        except Exception as e:
            return {"error": f"Analysis failed: {e}"}
    
    # Branch Comparison Tools (NEW)
    
    async def compare_branches(self, project_path: str, branch1: str, branch2: str) -> Dict[str, Any]:
        """Compare semantic changes between two branches."""
        svcs = self.repo_manager.get_repository(project_path)
        if not svcs:
            return {"error": f"Repository not found: {project_path}"}
        
        with svcs.db.get_connection() as conn:
            # Get events from both branches
            cursor = conn.execute("""
                SELECT branch, event_type, node_id, COUNT(*) as count
                FROM semantic_events
                WHERE branch IN (?, ?)
                GROUP BY branch, event_type, node_id
            """, (branch1, branch2))
            
            branch_events = {}
            for row in cursor.fetchall():
                branch = row[0]
                event_key = f"{row[1]}:{row[2]}"
                if branch not in branch_events:
                    branch_events[branch] = {}
                branch_events[branch][event_key] = row[3]
            
            # Calculate differences
            branch1_events = branch_events.get(branch1, {})
            branch2_events = branch_events.get(branch2, {})
            
            all_events = set(branch1_events.keys()) | set(branch2_events.keys())
            
            differences = []
            for event_key in all_events:
                count1 = branch1_events.get(event_key, 0)
                count2 = branch2_events.get(event_key, 0)
                if count1 != count2:
                    differences.append({
                        "event": event_key,
                        f"{branch1}_count": count1,
                        f"{branch2}_count": count2,
                        "difference": count2 - count1
                    })
            
            return {
                "branch1": branch1,
                "branch2": branch2,
                "differences": differences,
                "summary": {
                    f"{branch1}_total_events": sum(branch1_events.values()),
                    f"{branch2}_total_events": sum(branch2_events.values()),
                    "differences_count": len(differences)
                }
            }


# Convenience functions for MCP integration

async def mcp_list_projects() -> List[Dict[str, Any]]:
    """MCP tool: List all registered SVCS projects."""
    server = RepositoryLocalMCPServer()
    return await server.list_projects()

async def mcp_register_project(path: str, name: str) -> Dict[str, Any]:
    """MCP tool: Register a new project for SVCS tracking."""
    server = RepositoryLocalMCPServer()
    return await server.register_project(path, name)

async def mcp_query_semantic_events(project_path: str = None, event_type: str = None, 
                                   limit: int = 10) -> List[Dict[str, Any]]:
    """MCP tool: Query semantic events from repositories."""
    server = RepositoryLocalMCPServer()
    return await server.query_semantic_events(project_path, event_type, limit)

async def mcp_get_recent_activity(project_path: str, days: int = 7, limit: int = 15) -> List[Dict[str, Any]]:
    """MCP tool: Get recent activity from a repository."""
    server = RepositoryLocalMCPServer()
    return await server.get_recent_activity(project_path, days, limit)

async def mcp_analyze_current_commit(project_path: str) -> Dict[str, Any]:
    """MCP tool: Analyze the current commit for semantic changes."""
    server = RepositoryLocalMCPServer()
    return await server.analyze_current_commit(project_path)

async def mcp_compare_branches(project_path: str, branch1: str, branch2: str) -> Dict[str, Any]:
    """MCP tool: Compare semantic changes between branches."""
    server = RepositoryLocalMCPServer()
    return await server.compare_branches(project_path, branch1, branch2)


if __name__ == "__main__":
    # Test the repository-local MCP server
    async def test_server():
        server = RepositoryLocalMCPServer()
        
        print("🧪 Testing Repository-Local MCP Server")
        print("=" * 50)
        
        # Test repository registration
        current_repo = str(Path.cwd())
        result = await server.register_project(current_repo, "test-repo")
        print(f"📁 Repository registration: {result}")
        
        # Test project listing
        projects = await server.list_projects()
        print(f"📋 Projects: {len(projects)} found")
        
        # Test semantic events query
        events = await server.query_semantic_events(current_repo, limit=5)
        print(f"🔍 Recent events: {len(events)} found")
        
        # Test statistics
        stats = await server.get_project_statistics(current_repo)
        print(f"📊 Statistics: {stats.get('repository', {}).get('semantic_events_count', 0)} events")
    
    asyncio.run(test_server())
