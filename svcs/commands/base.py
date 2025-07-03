#!/usr/bin/env python3
"""
SVCS Commands Base Module

Common imports, utilities and base functionality for all command modules.
"""

import json
import os
import shutil
import subprocess
import sys
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Import core SVCS modules
try:
    from svcs_repo_local import RepositoryLocalSVCS
    from svcs_repo_hooks import SVCSRepositoryManager
    try:
        from . import utils
    except ImportError:
        pass
except ImportError:
    # Development mode fallback
    current_dir = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(current_dir))
    try:
        from svcs_repo_local import RepositoryLocalSVCS
        from svcs_repo_hooks import SVCSRepositoryManager
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent))
        try:
            import utils
        except ImportError:
            pass
    except ImportError:
        print("❌ Error: SVCS modules not found. Please ensure SVCS is properly installed.")
        sys.exit(1)

# Import smart initialization
try:
    from ..centralized_utils import smart_init_svcs
except ImportError:
    try:
        from centralized_utils import smart_init_svcs
    except ImportError:
        try:
            # Look in parent directory
            sys.path.insert(0, str(Path(__file__).parent.parent))
            from centralized_utils import smart_init_svcs
        except ImportError:
            # Final fallback - inline implementation
            def smart_init_svcs(repo_path):
                """Fallback smart init implementation"""
                from svcs_repo_hooks import SVCSRepositoryManager
                manager = SVCSRepositoryManager(str(repo_path))
                return manager.setup_repository()


def ensure_svcs_initialized(repo_path: Path) -> bool:
    """Check if SVCS is initialized for the repository."""
    return (repo_path / '.svcs' / 'semantic.db').exists()


def print_svcs_error(message: str):
    """Print standardized SVCS error message."""
    print(f"❌ {message}")


def print_svcs_success(message: str):
    """Print standardized SVCS success message."""
    print(f"✅ {message}")


def print_svcs_info(message: str):
    """Print standardized SVCS info message."""
    print(f"ℹ️ {message}")
