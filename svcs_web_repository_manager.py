#!/usr/bin/env python3
"""
SVCS Web Repository Manager

Manages multiple SVCS repositories for the web interface.
Uses repository-local semantic.db files with optional central registry at ~/.svcs/repos.db
"""

import os
import sqlite3
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

# Add paths for imports
sys.path.insert(0, str(Path(__file__).parent))

try:
    from svcs_repo_local import RepositoryLocalSVCS
    REPO_LOCAL_AVAILABLE = True
except ImportError:
    REPO_LOCAL_AVAILABLE = False


class SVCSWebRepositoryManager:
    """Manages SVCS repositories for web interface using repository-local architecture."""
    
    def __init__(self):
        self.repositories = {}  # Cache of repository instances
        self.registry_db = Path.home() / ".svcs" / "repos.db"
        self._init_registry()
    
    def _init_registry(self):
        """Initialize central repository registry."""
        try:
            self.registry_db.parent.mkdir(exist_ok=True)
            with sqlite3.connect(self.registry_db) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS repositories (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        path TEXT UNIQUE NOT NULL,
                        db_path TEXT NOT NULL,
                        created_at INTEGER NOT NULL,
                        last_accessed INTEGER
                    )
                """)
                conn.commit()
        except Exception:
            pass
    
    def discover_repositories(self, scan_paths: List[str] = None) -> List[Dict[str, Any]]:
        """Discover SVCS repositories from registry and filesystem scan."""
        repositories = []
        
        # 1. Get from central registry
        registry_repos = self._get_registry_repositories()
        repositories.extend(registry_repos)
        
        # 2. Scan for repository-local installations not in registry
        if scan_paths is None:
            # More focused scan paths to avoid timeouts
            scan_paths = [
                os.getcwd(),  # Current directory
                str(Path.home() / "Documents"),  # Documents folder
                str(Path.home() / "Projects"),   # Common project folder
                str(Path.home() / "GitHub"),     # GitHub folder
                str(Path.home() / "git"),        # Git folder
            ]
            
            # Only add home directory if it's not too large
            home_path = Path.home()
            try:
                # Quick check: if home has too many items, skip it
                if len(list(home_path.iterdir())) < 50:
                    scan_paths.append(str(home_path))
            except (PermissionError, OSError):
                pass
        
        scanned_repos = self._discover_repository_local(scan_paths)
        
        # 3. Remove duplicates based on path
        seen_paths = {repo['path'] for repo in repositories}
        for repo in scanned_repos:
            if repo['path'] not in seen_paths:
                repositories.append(repo)
        
        return repositories
    
    def _discover_repository_local(self, scan_paths: List[str]) -> List[Dict[str, Any]]:
        """Discover repository-local SVCS installations with performance optimization."""
        repositories = []
        max_depth = 3  # Limit search depth to avoid deep scanning
        
        for scan_path in scan_paths:
            try:
                scan_path = Path(scan_path)
                if not scan_path.exists():
                    continue
                
                # Use limited depth search to avoid performance issues
                repositories.extend(self._scan_directory_limited(scan_path, max_depth))
                
            except Exception as e:
                # Log error but continue with other paths
                print(f"Warning: Error scanning {scan_path}: {e}")
                continue
        
        return repositories
    
    def _scan_directory_limited(self, base_path: Path, max_depth: int, current_depth: int = 0) -> List[Dict[str, Any]]:
        """Scan directory with depth limit for performance."""
        repositories = []
        
        if current_depth > max_depth:
            return repositories
        
        try:
            # Check if current directory has .svcs
            svcs_dir = base_path / '.svcs'
            if svcs_dir.exists() and (svcs_dir / 'semantic.db').exists():
                # Verify it's a git repository
                if (base_path / '.git').exists():
                    repo_info = self._get_repository_info(str(base_path))
                    if repo_info:
                        repositories.append(repo_info)
            
            # Only scan subdirectories if we haven't reached max depth
            if current_depth < max_depth:
                for item in base_path.iterdir():
                    if item.is_dir() and not item.name.startswith('.') and item.name not in ['node_modules', '__pycache__', 'venv', 'env']:
                        repositories.extend(self._scan_directory_limited(item, max_depth, current_depth + 1))
                        
        except (PermissionError, OSError):
            # Skip directories we can't access
            pass
        
        return repositories
    
    def _get_registry_repositories(self) -> List[Dict[str, Any]]:
        """Get repositories from central registry."""
        repositories = []
        
        try:
            with sqlite3.connect(self.registry_db) as conn:
                cursor = conn.execute("""
                    SELECT name, path, db_path, created_at, last_accessed 
                    FROM repositories ORDER BY last_accessed DESC
                """)
                
                for name, path, db_path, created_at, last_accessed in cursor.fetchall():
                    # Verify repository still exists and has SVCS data
                    if Path(path).exists() and Path(db_path).exists():
                        repo_info = self._get_repository_info(path)
                        if repo_info:
                            repo_info['name'] = name  # Use registry name
                            repo_info['registered'] = True
                            repositories.append(repo_info)
        except Exception:
            pass
        
        return repositories
    
    def _get_repository_info(self, repo_path: str) -> Optional[Dict[str, Any]]:
        """Get repository information from repository-local SVCS."""
        try:
            if not REPO_LOCAL_AVAILABLE:
                return None
            
            svcs = RepositoryLocalSVCS(repo_path)
            if not svcs.is_git_repository():
                return None
            
            status = svcs.get_repository_status()
            if not status.get('initialized'):
                return None
            
            # Get additional git info
            import subprocess
            try:
                result = subprocess.run(
                    ['git', 'config', 'remote.origin.url'],
                    cwd=repo_path, capture_output=True, text=True
                )
                origin_url = result.stdout.strip() if result.returncode == 0 else None
            except:
                origin_url = None
            
            # Get last activity from git logs
            last_activity = 'unknown'
            try:
                result = subprocess.run(
                    ['git', 'log', '-1', '--format=%cr'],
                    cwd=repo_path, capture_output=True, text=True
                )
                if result.returncode == 0 and result.stdout.strip():
                    last_activity = result.stdout.strip()
            except:
                pass
            
            return {
                'path': repo_path,
                'name': Path(repo_path).name,
                'type': 'repository-local',
                'status': 'active',
                'current_branch': status.get('current_branch'),
                'branch': status.get('current_branch'),  # For dashboard compatibility
                'events_count': status.get('semantic_events_count', 0),
                'event_count': status.get('semantic_events_count', 0),  # For dashboard compatibility
                'commits_count': status.get('commits_analyzed', 0),
                'last_activity': last_activity,
                'origin_url': origin_url,
                'registered': False
            }
        except Exception:
            return None
    
    def get_repository(self, repo_path: str) -> Optional[Any]:
        """Get or create repository instance."""
        repo_path = str(Path(repo_path).resolve())
        
        # Update registry access time
        self.update_registry_access(repo_path)
        
        if repo_path in self.repositories:
            return self.repositories[repo_path]
        
        # Try repository-local
        if REPO_LOCAL_AVAILABLE:
            try:
                svcs = RepositoryLocalSVCS(repo_path)
                if svcs.is_git_repository():
                    status = svcs.get_repository_status()
                    if status.get('initialized'):
                        self.repositories[repo_path] = svcs
                        return svcs
            except Exception:
                pass
        
        return None
    
    def register_repository(self, repo_path: str, name: str = None) -> Dict[str, Any]:
        """Register repository in central registry."""
        if not REPO_LOCAL_AVAILABLE:
            return {'success': False, 'error': 'Repository-local SVCS not available'}
        
        try:
            repo_path = str(Path(repo_path).resolve())
            svcs = RepositoryLocalSVCS(repo_path)
            
            if not svcs.is_git_repository():
                return {'success': False, 'error': 'Not a git repository'}
            
            status = svcs.get_repository_status()
            if not status.get('initialized'):
                return {'success': False, 'error': 'SVCS not initialized. Run svcs init first.'}
            
            if not name:
                name = Path(repo_path).name
            
            db_path = str(Path(repo_path) / '.svcs' / 'semantic.db')
            
            with sqlite3.connect(self.registry_db) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO repositories 
                    (name, path, db_path, created_at, last_accessed)
                    VALUES (?, ?, ?, ?, ?)
                """, (name, repo_path, db_path, int(datetime.now().timestamp()), 
                      int(datetime.now().timestamp())))
                conn.commit()
            
            return {'success': True, 'message': f'Repository "{name}" registered successfully'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def initialize_repository(self, repo_path: str) -> Dict[str, Any]:
        """Initialize SVCS for a repository, creating directory and git repo if needed."""
        if not REPO_LOCAL_AVAILABLE:
            return {'success': False, 'error': 'Repository-local SVCS not available'}
        
        try:
            repo_path = str(Path(repo_path).resolve())
            repo_path_obj = Path(repo_path)
            
            # Create directory if it doesn't exist
            if not repo_path_obj.exists():
                try:
                    repo_path_obj.mkdir(parents=True, exist_ok=True)
                except Exception as e:
                    return {'success': False, 'error': f'Failed to create directory: {str(e)}'}
            
            # Initialize git repository if not already a git repo
            git_dir = repo_path_obj / '.git'
            if not git_dir.exists():
                try:
                    import subprocess
                    result = subprocess.run(['git', 'init'], cwd=repo_path, capture_output=True, text=True)
                    if result.returncode != 0:
                        return {'success': False, 'error': f'Failed to initialize git repository: {result.stderr}'}
                except Exception as e:
                    return {'success': False, 'error': f'Failed to initialize git repository: {str(e)}'}
            
            # Now initialize SVCS
            svcs = RepositoryLocalSVCS(repo_path)
            
            if not svcs.is_git_repository():
                return {'success': False, 'error': 'Failed to create git repository'}
            
            result = svcs.initialize_repository()
            if '✅' in result:
                self.repositories[repo_path] = svcs
                return {'success': True, 'message': result}
            else:
                return {'success': False, 'error': result}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def unregister_repository(self, repo_path: str) -> Dict[str, Any]:
        """Remove repository from central registry."""
        try:
            repo_path = str(Path(repo_path).resolve())
            
            with sqlite3.connect(self.registry_db) as conn:
                cursor = conn.execute("DELETE FROM repositories WHERE path = ?", (repo_path,))
                if cursor.rowcount > 0:
                    conn.commit()
                    # Clear from cache
                    if repo_path in self.repositories:
                        del self.repositories[repo_path]
                    return {'success': True, 'message': f'Repository unregistered: {repo_path}'}
                else:
                    return {'success': False, 'error': 'Repository not found in registry'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_repository_statistics(self, repo_path: str) -> Dict[str, Any]:
        """Get repository statistics."""
        svcs = self.get_repository(repo_path)
        if not svcs:
            return {'error': 'Repository not found or not initialized'}
        
        try:
            status = svcs.get_repository_status()
            
            # Get additional statistics
            events = svcs.get_branch_events(limit=1000)
            
            # Event type distribution
            event_types = {}
            for event in events:
                event_type = event.get('event_type', 'unknown')
                event_types[event_type] = event_types.get(event_type, 0) + 1
            
            return {
                'repository_path': repo_path,
                'current_branch': status.get('current_branch'),
                'total_events': status.get('semantic_events_count', 0),
                'total_commits': status.get('commits_analyzed', 0),
                'event_types': event_types,
                'recent_events': events[:10]  # Last 10 events
            }
        except Exception as e:
            return {'error': str(e)}
    
    def search_events(self, repo_path: str, limit: int = 20, event_type: str = None, 
                     since_days: int = None) -> List[Dict[str, Any]]:
        """Search semantic events in repository."""
        svcs = self.get_repository(repo_path)
        if not svcs:
            return []
        
        try:
            events = svcs.get_branch_events(limit=1000)
            
            # Apply filters
            if event_type:
                events = [e for e in events if e.get('event_type') == event_type]
            
            if since_days:
                cutoff = int((datetime.now() - timedelta(days=since_days)).timestamp())
                events = [e for e in events if e.get('created_at', 0) > cutoff]
            
            return events[:limit]
        except Exception:
            return []
    
    def update_registry_access(self, repo_path: str):
        """Update last accessed timestamp for repository."""
        try:
            repo_path = str(Path(repo_path).resolve())
            with sqlite3.connect(self.registry_db) as conn:
                conn.execute("""
                    UPDATE repositories SET last_accessed = ? WHERE path = ?
                """, (int(datetime.now().timestamp()), repo_path))
                conn.commit()
        except Exception:
            pass

    def auto_register_if_initialized(self, repo_path: str) -> Dict[str, Any]:
        """Automatically register repository if it's SVCS-initialized but not registered."""
        try:
            repo_path = str(Path(repo_path).resolve())
            
            # Check if already registered
            with sqlite3.connect(self.registry_db) as conn:
                cursor = conn.execute("SELECT name FROM repositories WHERE path = ?", (repo_path,))
                if cursor.fetchone():
                    return {'success': True, 'message': 'Repository already registered', 'already_registered': True}
            
            # Check if SVCS is initialized
            if not REPO_LOCAL_AVAILABLE:
                return {'success': False, 'error': 'Repository-local SVCS not available'}
            
            svcs = RepositoryLocalSVCS(repo_path)
            if not svcs.is_git_repository():
                return {'success': False, 'error': 'Not a git repository'}
            
            status = svcs.get_repository_status()
            if not status.get('initialized'):
                return {'success': False, 'error': 'SVCS not initialized'}
            
            # Auto-register with directory name
            name = Path(repo_path).name
            return self.register_repository(repo_path, name)
            
        except Exception as e:
            return {'success': False, 'error': str(e)}


# Global instance for web server
web_repository_manager = SVCSWebRepositoryManager()
