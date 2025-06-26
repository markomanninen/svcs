#!/usr/bin/env python3
"""
SVCS Package Main Entry Point

This module handles execution when SVCS is run as a package with `python -m svcs`.
It provides clean module loading and prevents import conflicts.
"""

import sys
from pathlib import Path

def main():
    """Main entry point for package execution."""
    # Add the parent directory to path to ensure proper imports
    package_dir = Path(__file__).parent.parent
    if str(package_dir) not in sys.path:
        sys.path.insert(0, str(package_dir))
    
    # Import and run CLI after path setup
    from svcs.cli import main as cli_main
    cli_main()

if __name__ == "__main__":
    main()
