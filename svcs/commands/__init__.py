#!/usr/bin/env python3
"""
SVCS Commands Package

Modular command handlers for the SVCS CLI.
Each module contains related command functions to improve maintainability.
"""

# Import all command functions to maintain backward compatibility
from .init import cmd_init
from .status import cmd_status, cmd_cleanup
from .events import cmd_events, cmd_process_hook
from .search import cmd_search, cmd_evolution, cmd_compare
from .analytics import cmd_analytics, cmd_quality
from .web import cmd_web, cmd_dashboard
from .ci import cmd_ci
from .discuss import cmd_discuss, cmd_query
from .notes import cmd_notes
from .sync import cmd_sync, cmd_merge_resolve, cmd_auto_fix, cmd_sync_all, cmd_pull, cmd_push, cmd_merge, cmd_config, cmd_config
from .utils import cmd_quick_help, cmd_workflow

# Export all command functions
__all__ = [
    # Core repository management
    'cmd_init',
    'cmd_status', 
    'cmd_cleanup',
    
    # Events and semantic data
    'cmd_events',
    'cmd_process_hook',
    
    # Search and analysis
    'cmd_search',
    'cmd_evolution', 
    'cmd_compare',
    
    # Analytics and quality
    'cmd_analytics',
    'cmd_quality',
    
    # Web interfaces
    'cmd_web',
    'cmd_dashboard',
    
    # CI/CD integration
    'cmd_ci',
    
    # Conversational interfaces
    'cmd_discuss',
    'cmd_query',
    
    # Git notes management
    'cmd_notes',
    
    # Sync and merge operations
    'cmd_sync',
    'cmd_merge_resolve',
    'cmd_auto_fix',
    'cmd_sync_all',
    'cmd_pull',
    'cmd_push',
    'cmd_merge',
    'cmd_config',
    
    # Utilities and help
    'cmd_quick_help',
    'cmd_workflow'
]
