"""
SVCS - Semantic Version Control System

Repository-local, git-integrated semantic analysis for development teams.
Modular version with proven parser and analyzer architecture.
"""

from .semantic_analyzer import SVCSModularAnalyzer
# Modular parsers available in parsers/ directory
from .storage import initialize_database, store_commit_events, get_recent_events, get_event_statistics

__version__ = "2.0.0"
__author__ = "SVCS Team"
__license__ = "MIT"

__all__ = [
    "SVCSModularAnalyzer",
    "analyze_changes", 
    "analyze_python_changes",
    "analyze_multilang_changes", 
    "parse_code",
    "get_node_details",
    "initialize_database",
    "store_commit_events", 
    "get_recent_events",
    "get_event_statistics"
]

# Import main CLI function for package entry point
from .cli import main

__all__ = ['main']
