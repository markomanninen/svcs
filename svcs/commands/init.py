#!/usr/bin/env python3
"""
SVCS Init Commands

Commands for initializing SVCS in repositories.
"""

from pathlib import Path
from .base import smart_init_svcs


def cmd_init(args):
    """Initialize SVCS for current repository with smart auto-detection."""
    repo_path = Path(args.path or Path.cwd()).resolve()
    
    # Smart initialization logic
    result = smart_init_svcs(repo_path)
    print(result)
