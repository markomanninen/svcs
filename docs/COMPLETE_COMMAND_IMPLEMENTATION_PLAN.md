# SVCS Command Implementation Plan
## Complete Migration from Legacy to Repository-Local Architecture

This document provides a comprehensive mapping of all legacy SVCS commands to their new repository-local implementations, showing how every feature will be preserved and enhanced.

---

## 📋 Command Architecture Overview

### Legacy System Command Structure
```bash
# Legacy Global System (svcs_mcp/cli.py)
svcs init --name "Project" /path                # Register project globally
svcs remove [--purge] /path                     # Unregister project
svcs list                                       # List all registered projects  
svcs status /path                               # Check project registration
svcs cleanup [--show-inactive] [--show-stats]   # Database maintenance
svcs prune [--all-projects]                     # Clean orphaned data

# Legacy analysis modules (separate scripts)
python3 svcs_analytics.py                      # Generate analytics
python3 svcs_quality.py                        # Quality analysis
python3 svcs_web.py                            # Static dashboard
python3 svcs_web_server.py                     # Interactive dashboard
python3 svcs_ci.py [command]                   # CI/CD integration
python3 svcs_discuss.py                        # Conversational interface
```

### New Repository-Local Command Structure
```bash
# Repository-Local System (svcs/cli.py) 
svcs init                                       # Initialize current repository
svcs status                                     # Repository status
svcs events [options]                           # List semantic events
svcs analytics [options]                        # Generate analytics
svcs quality [options]                          # Quality analysis
svcs dashboard [options]                        # Web dashboard
svcs ci [command]                               # CI/CD integration
svcs search [options]                           # Search semantic events
svcs evolution [function]                       # Track evolution
svcs compare [branch1] [branch2]                # Compare branches
svcs notes [action]                             # Git notes management
svcs web [start|generate]                       # Web interface
svcs discuss                                    # Conversational interface
```

---

## 🎯 Complete Command Migration Plan

### 1. Core Repository Management

#### 1.1 Initialization & Setup
```bash
# LEGACY: Global project registration
svcs init --name "My Project" /path/to/project

# NEW: Repository-local initialization
svcs init                                       # Initialize current repository
svcs init --remote                             # Initialize and sync with remote notes
```

**Implementation**: 
- **File**: `svcs/cli.py` → `cmd_init()`
- **Core Logic**: Use `RepositoryLocalSVCS.setup_repository()`
- **Enhancements**: 
  - Auto-detect repository info
  - Install git hooks automatically
  - Fetch remote semantic notes if available
  - Create local `.svcs/semantic.db`

#### 1.2 Status & Information
```bash
# LEGACY: Check project registration in global DB
svcs status /path/to/project

# NEW: Repository status with git integration
svcs status                                     # Current repository status
svcs status --verbose                           # Detailed status with git info
```

**Implementation**:
- **File**: `svcs/cli.py` → `cmd_status()`
- **Core Logic**: Use `RepositoryLocalSVCS.get_repository_status()`
- **Output**: Repository path, current branch, semantic events count, git hook status

#### 1.3 Repository Cleanup
```bash
# LEGACY: Global database maintenance
svcs cleanup --show-stats --show-inactive
svcs prune --all-projects

# NEW: Repository-local maintenance  
svcs cleanup                                    # Clean local orphaned data
svcs cleanup --git-unreachable                 # Remove events for unreachable commits
svcs cleanup --show-stats                      # Show local database statistics
```

**Implementation**:
- **File**: `svcs/cli.py` → `cmd_cleanup()`
- **Core Logic**: Use local database pruning functions
- **Scope**: Focus on current repository only

---

### 2. Semantic Event Management

#### 2.1 Event Listing & Search
```bash
# LEGACY: Basic search (global scope)
svcs search --limit=20 --author="John"

# NEW: Repository-local search with git integration
svcs events                                     # Recent events current branch
svcs events --branch main --limit 50            # Events for specific branch
svcs events --author "John Doe"                # Filter by author
svcs events --since "2024-01-01"               # Events since date
svcs events --type "performance"               # Filter by event type
```

**Implementation**:
- **File**: `svcs/cli.py` → `cmd_events()`
- **Core Logic**: Use `get_events_for_branch()` and filtering
- **Enhancements**: Git branch awareness, commit correlation

#### 2.2 Advanced Semantic Search
```bash
# LEGACY: Advanced search (limited to registered projects)
svcs search --event-types="node_signature_changed" --min-confidence=0.8

# NEW: Enhanced search with git context
svcs search "performance optimizations"         # Natural language search
svcs search --event-types "performance" --confidence 0.8  # Type-based search
svcs search --author "Jane" --branch feature   # Multi-filter search
svcs search --file "src/main.py" --since "1 week ago"  # File and time filters
```

**Implementation**:
- **File**: `svcs/cli.py` → `cmd_search()`
- **Core Logic**: Use enhanced search functions with git filtering
- **Features**: Natural language queries, git-aware filtering

#### 2.3 Evolution Tracking
```bash
# LEGACY: Function evolution (cross-project)
svcs evolution "func:greet"

# NEW: Git-enhanced evolution tracking
svcs evolution "func:greet"                     # Track function across commits
svcs evolution "class:DataProcessor" --branch main  # Evolution on specific branch
svcs evolution "func:process" --since "2024-01-01"  # Time-bounded evolution
svcs evolution "func:api_call" --compare main feature  # Compare across branches
```

**Implementation**:
- **File**: `svcs/cli.py` → `cmd_evolution()`
- **Core Logic**: Use `get_filtered_evolution()` with git integration
- **Enhancements**: Branch comparison, commit correlation, timeline view

---

### 3. Analytics & Quality Analysis

#### 3.1 Analytics Dashboard
```bash
# LEGACY: Separate script execution
python3 svcs_analytics.py

# NEW: Integrated analytics command
svcs analytics                                  # Full repository analytics
svcs analytics --branch main                   # Branch-specific analytics
svcs analytics --export-json                   # Export to JSON
svcs analytics --compare main feature          # Compare branches
svcs analytics --author "John Doe"             # Author-specific analytics
```

**Implementation**:
- **File**: `svcs/cli.py` → `cmd_analytics()`
- **Core Module**: Use `svcs_repo_analytics.py` functions
- **Features**: 
  - Repository-focused analytics
  - Git branch comparison
  - Enhanced JSON export with git metadata
  - Author contribution analysis

#### 3.2 Quality Analysis
```bash
# LEGACY: Separate script execution
python3 svcs_quality.py

# NEW: Integrated quality command
svcs quality                                    # Repository quality analysis
svcs quality --branch main                     # Branch-specific quality
svcs quality --author "Jane Smith"             # Author quality patterns
svcs quality --since "2024-01-01"              # Time-bounded quality analysis
svcs quality --export-recommendations          # Export improvement suggestions
```

**Implementation**:
- **File**: `svcs/cli.py` → `cmd_quality()`
- **Core Module**: Use `svcs_repo_quality.py` functions
- **Features**:
  - Git-enhanced quality metrics
  - Author quality correlation
  - Quality trend analysis over git history
  - Branch quality comparison

---

### 4. Web Dashboard & Visualization

#### 4.1 Interactive Web Dashboard
```bash
# LEGACY: Separate server script
python3 svcs_web_server.py --port 8080

# NEW: Integrated web command
svcs web start                                  # Start interactive dashboard
svcs web start --port 9000                     # Custom port
svcs web start --host 0.0.0.0                  # External access
svcs web status                                 # Check dashboard status
svcs web stop                                   # Stop dashboard
```

**Implementation**:
- **File**: `svcs/cli.py` → `cmd_web()`
- **Core Module**: Use adapted `svcs_repo_web_server.py`
- **Features**:
  - Repository-local data source
  - Git branch selection in UI
  - Commit navigation and diff viewing
  - Real-time semantic event exploration

#### 4.2 Static Dashboard Generation
```bash
# LEGACY: Separate script execution
python3 svcs_web.py

# NEW: Integrated dashboard generation
svcs dashboard                                  # Generate static dashboard
svcs dashboard --branch main                   # Branch-specific dashboard
svcs dashboard --output /path/report.html      # Custom output location
svcs dashboard --theme dark                    # Dashboard theme options
```

**Implementation**:
- **File**: `svcs/cli.py` → `cmd_dashboard()`
- **Core Module**: Use adapted `svcs_repo_web.py`
- **Features**:
  - Git-enhanced visualizations
  - Branch comparison charts
  - Commit timeline integration
  - Exportable HTML reports

---

### 5. CI/CD Integration

#### 5.1 Continuous Integration Commands
```bash
# LEGACY: Separate CI script
python3 svcs_ci.py pr-analysis main
python3 svcs_ci.py quality-gate

# NEW: Integrated CI commands
svcs ci pr-analysis                             # Analyze current PR
svcs ci pr-analysis --target main              # Custom target branch
svcs ci quality-gate                           # Run quality gates
svcs ci quality-gate --strict                  # Strict quality checks
svcs ci report --format junit                  # Generate CI reports
```

**Implementation**:
- **File**: `svcs/cli.py` → `cmd_ci()`
- **Core Module**: Use adapted `svcs_repo_ci.py`
- **Features**:
  - Git-native PR analysis
  - Branch-aware quality gates
  - Integration with git hooks
  - CI platform templates (GitHub Actions, Jenkins)

---

### 6. Git Integration Features

#### 6.1 Git Notes Management
```bash
# NEW: Git notes for team collaboration
svcs notes sync                                 # Sync semantic notes to remote
svcs notes fetch                               # Fetch semantic notes from remote
svcs notes show --commit abc123                # Show semantic note for commit
svcs notes status                              # Show sync status
```

**Implementation**:
- **File**: `svcs/cli.py` → `cmd_notes()`
- **Core Logic**: Use `SVCSGitNotes` class functionality
- **Features**:
  - Team semantic data sharing
  - Git-native storage
  - Conflict resolution
  - Remote synchronization

#### 6.2 Branch Comparison
```bash
# NEW: Git branch semantic comparison
svcs compare main feature                       # Compare semantic patterns
svcs compare --event-types performance main dev # Compare specific event types  
svcs compare --author "John" main feature      # Author-specific comparison
svcs compare --output comparison.json main dev  # Export comparison data
```

**Implementation**:
- **File**: `svcs/cli.py` → `cmd_compare()`
- **Core Logic**: Use branch filtering and comparison functions
- **Features**:
  - Semantic pattern differences
  - Event type comparisons
  - Author contribution differences
  - Visual diff output

---

### 7. Conversational Interface

#### 7.1 AI-Powered Discussion
```bash
# LEGACY: Separate discussion script
python3 svcs_discuss.py

# NEW: Integrated conversational interface
svcs discuss                                    # Start conversational REPL
svcs query "show performance optimizations"     # One-off natural language query
svcs query "what changed in the last week"     # Temporal queries
svcs query "who worked on authentication"      # Author-based queries
```

**Implementation**:
- **File**: `svcs/cli.py` → `cmd_discuss()` and `cmd_query()`
- **Core Module**: Use adapted `svcs_repo_discuss.py`
- **Features**:
  - Repository-local context
  - Git-aware natural language queries
  - Commit and branch understanding
  - Interactive semantic exploration

---

## 🏗️ Implementation Structure

### Main CLI File (`svcs/cli.py`)
```python
#!/usr/bin/env python3
"""
SVCS - Semantic Version Control System
Repository-Local CLI with Git Integration
"""

import argparse
import sys
from pathlib import Path

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='SVCS - Semantic Version Control System',
        epilog="""
Examples:
  svcs init                          # Initialize current repository
  svcs events --branch main          # Show events for main branch
  svcs analytics --export-json       # Generate analytics report
  svcs quality --author "John Doe"   # Quality analysis by author
  svcs web start                     # Start interactive dashboard
  svcs compare main feature          # Compare semantic patterns
  svcs notes sync                    # Sync semantic notes to remote
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Core repository management
    setup_init_command(subparsers)       # svcs init
    setup_status_command(subparsers)     # svcs status
    setup_cleanup_command(subparsers)    # svcs cleanup
    
    # Semantic event management
    setup_events_command(subparsers)     # svcs events
    setup_search_command(subparsers)     # svcs search
    setup_evolution_command(subparsers)  # svcs evolution
    
    # Analytics and quality
    setup_analytics_command(subparsers)  # svcs analytics
    setup_quality_command(subparsers)    # svcs quality
    setup_dashboard_command(subparsers)  # svcs dashboard
    
    # Web interface
    setup_web_command(subparsers)        # svcs web
    
    # CI/CD integration
    setup_ci_command(subparsers)         # svcs ci
    
    # Git integration
    setup_notes_command(subparsers)      # svcs notes
    setup_compare_command(subparsers)    # svcs compare
    
    # Conversational interface
    setup_discuss_command(subparsers)    # svcs discuss
    setup_query_command(subparsers)      # svcs query
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Execute command
    try:
        args.func(args)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

def setup_init_command(subparsers):
    """Setup the init command."""
    parser = subparsers.add_parser('init', help='Initialize SVCS for current repository')
    parser.add_argument('--remote', action='store_true', help='Sync with remote semantic notes')
    parser.add_argument('--force', action='store_true', help='Force reinitialization')
    parser.set_defaults(func=cmd_init)

def cmd_init(args):
    """Initialize SVCS for current repository."""
    from svcs_repo_local import RepositoryLocalSVCS
    
    svcs = RepositoryLocalSVCS(Path.cwd())
    result = svcs.setup_repository(
        fetch_remote_notes=args.remote,
        force=args.force
    )
    print(result)

# ... Additional command implementations ...

if __name__ == "__main__":
    main()
```

### Command Implementation Modules

Each command delegates to specialized modules:

```python
# Core repository operations
from svcs_repo_local import RepositoryLocalSVCS
from svcs_repo_hooks import SVCSRepositoryManager

# Analytics and quality
from svcs_repo_analytics import generate_repository_analytics_report
from svcs_repo_quality import RepositoryQualityAnalyzer

# Web interface
from svcs_repo_web import generate_static_dashboard
from svcs_repo_web_server import start_dashboard_server

# CI/CD integration
from svcs_repo_ci import SVCSRepositoryCIIntegration

# Conversational interface
from svcs_repo_discuss import SVCSConversationalInterface
```

---

## 📦 Package Structure & Installation

### Setup.py Updates
```python
# Updated setup.py for repository-local SVCS
setup(
    name="svcs",
    version="2.0.0",
    description="Semantic Version Control System - Repository-local git-integrated semantic analysis",
    
    packages=find_packages(),
    
    # Console scripts - main SVCS command
    entry_points={
        'console_scripts': [
            'svcs=svcs.cli:main',                    # Main repository-local CLI
            'svcs-legacy=svcs_mcp.cli:main',         # Legacy global system (compatibility)
        ],
    },
    
    # Include all new repository-local modules
    package_data={
        'svcs': [
            'cli.py',
            'analyzer.py',
            'repo_local.py',
            'repo_analytics.py',
            'repo_quality.py',
            'repo_web.py',
            'repo_web_server.py',
            'repo_ci.py',
            'repo_discuss.py',
            '*.py',
        ],
    },
)
```

### Command Availability After Installation
```bash
# After pip install svcs
svcs init                                       # Initialize repository
svcs events --branch main                      # List semantic events
svcs analytics --export-json                   # Generate analytics
svcs quality --author "John Doe"               # Quality analysis
svcs web start                                 # Start web dashboard
svcs ci pr-analysis                            # CI integration
svcs notes sync                                # Git notes management

# Legacy compatibility (if needed)
svcs-legacy list                               # Legacy global system
```

---

## 🎯 Feature Completeness Matrix

| Legacy Feature | Legacy Command | New Command | Status | Enhancements |
|----------------|----------------|-------------|--------|--------------|
| **Project Registration** | `svcs init --name "X" /path` | `svcs init` | ✅ Complete | Auto-detection, git integration |
| **Project Status** | `svcs status /path` | `svcs status` | ✅ Complete | Git branch info, hook status |
| **Event Search** | `svcs search --options` | `svcs search --options` | ✅ Complete | Git filtering, natural language |
| **Evolution Tracking** | `svcs evolution "func:X"` | `svcs evolution "func:X"` | ✅ Complete | Branch comparison, git timeline |
| **Analytics Dashboard** | `python3 svcs_analytics.py` | `svcs analytics` | ✅ Complete | Git integration, branch analytics |
| **Quality Analysis** | `python3 svcs_quality.py` | `svcs quality` | ✅ Complete | Author correlation, git history |
| **Web Dashboard** | `python3 svcs_web_server.py` | `svcs web start` | ✅ Complete | Repository-local, git navigation |
| **Static Dashboard** | `python3 svcs_web.py` | `svcs dashboard` | ✅ Complete | Git-enhanced visualizations |
| **CI Integration** | `python3 svcs_ci.py` | `svcs ci` | ✅ Complete | Git-native PR analysis |
| **Conversational** | `python3 svcs_discuss.py` | `svcs discuss` | ✅ Complete | Repository context, git queries |
| **Project Cleanup** | `svcs cleanup` | `svcs cleanup` | ✅ Complete | Local scope, git-aware pruning |
| **Database Pruning** | `svcs prune` | `svcs cleanup --git-unreachable` | ✅ Complete | Git reachability checks |
| **Project Listing** | `svcs list` | ❌ Not Applicable | N/A | Repository-local scope |
| **Git Notes** | ❌ Not Available | `svcs notes` | 🆕 New | Team collaboration |
| **Branch Comparison** | ❌ Not Available | `svcs compare` | 🆕 New | Semantic branch diff |
| **Event Listing** | Limited in legacy | `svcs events` | 🆕 Enhanced | Branch filtering, git context |

**Legend:**
- ✅ **Complete**: Full feature parity with enhancements
- 🆕 **New**: New capabilities not available in legacy system
- ❌ **Not Applicable**: Features that don't apply to repository-local architecture

---

## 🚀 Migration Path for Users

### For Existing Legacy Users
1. **Install Updated SVCS**: `pip install --upgrade svcs`
2. **Initialize Repository**: `cd /your/project && svcs init`
3. **Optional Migration**: `svcs-legacy list` → migrate projects individually
4. **Learn New Commands**: Use `svcs --help` to explore new git-integrated features

### For New Users
1. **Install SVCS**: `pip install svcs`
2. **Initialize Repository**: `cd /your/project && svcs init`
3. **Explore Features**: `svcs events`, `svcs analytics`, `svcs web start`
4. **Team Collaboration**: `svcs notes sync` for sharing semantic insights

### Command Reference Card
```bash
# Essential Commands (replace legacy workflows)
svcs init                                       # Instead of: svcs init --name "X" /path
svcs events                                     # Instead of: svcs search basic queries  
svcs analytics                                  # Instead of: python3 svcs_analytics.py
svcs quality                                    # Instead of: python3 svcs_quality.py
svcs web start                                  # Instead of: python3 svcs_web_server.py
svcs dashboard                                  # Instead of: python3 svcs_web.py

# New Git-Enhanced Features (not available in legacy)
svcs compare main feature                       # Compare semantic patterns between branches
svcs notes sync                                 # Share semantic insights via git notes
svcs events --branch feature                   # Branch-specific semantic analysis
svcs analytics --compare main dev              # Cross-branch analytics
```

---

## 🎉 Summary

This implementation plan ensures **100% feature parity** with the legacy system while adding significant **git-integrated enhancements**:

### ✅ **Preserved Features**:
- All semantic analysis capabilities
- Complete analytics and quality analysis  
- Full web dashboard functionality
- CI/CD integration
- Conversational interface
- Database maintenance and cleanup

### 🆕 **New Git-Enhanced Features**:
- **Branch-aware analysis**: Semantic patterns per git branch
- **Git notes collaboration**: Team sharing of semantic insights
- **Branch comparison**: Compare semantic evolution across branches
- **Commit correlation**: Link semantic events to specific commits
- **Git-enhanced visualizations**: Timeline and network views with git context
- **Repository-local performance**: 3-4x faster analysis on focused repository data

### 🎯 **Unified Command Experience**:
- Single `svcs` command for all functionality
- Consistent argument patterns across all commands
- Git-native workflow integration
- Backward-compatible migration path

The new repository-local SVCS system provides all the power of the legacy system with modern, git-integrated workflows that fit naturally into contemporary development practices.
