#!/usr/bin/env python3
"""
SVCS Repository Adapters

Adapters for repository-local and centralized SVCS operations.
"""

from pathlib import Path
from typing import Dict, Any, Optional


class RepositoryAdapter:
    """Base adapter for repository-local SVCS operations."""
    
    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path).resolve()
        self.svcs_dir = self.repo_path / '.svcs'
        self.db_path = self.svcs_dir / 'semantic.db'
        
    def ensure_svcs_initialized(self):
        """Ensure SVCS is initialized for this repository."""
        if not self.db_path.exists():
            raise FileNotFoundError(f"SVCS not initialized for {self.repo_path}. Run 'svcs init' first.")
