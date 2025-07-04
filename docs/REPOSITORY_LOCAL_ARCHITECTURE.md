# SVCS Repository-Local Architecture

## Overview

SVCS provides a repository-local, git-integrated semantic code analysis system. Each repository maintains its own semantic database and shares insights through git notes for team collaboration.

## Core Architecture

### Repository-Local Database

Each repository stores semantic analysis data in `.svcs/semantic.db` within the repository directory.

**Key Features**:
- Branch-aware semantic event storage  
- Git commit correlation for all semantic events
- Local performance optimization
- Git notes synchronization for team collaboration

### Git Integration

SVCS integrates deeply with git workflows:
- Automatic analysis on commits via git hooks
- Branch-aware semantic tracking
- Git notes for sharing semantic insights with team members
- Commit-correlated semantic events

## Core Components

### 1. RepositoryLocalDatabase (`svcs_repo_local.py`)

Repository-local semantic database stored in `.svcs/semantic.db` within each git repository.

**Key Features**:
- Branch-aware semantic event storage
- Git commit correlation
- Team collaboration via git notes
- Local caching for performance

**Database Schema**:
```sql
-- Core semantic events table
CREATE TABLE semantic_events (
    id INTEGER PRIMARY KEY,
    commit_hash TEXT,
    event_type TEXT,
    node_id TEXT,
    location TEXT,
    details TEXT,
    layer INTEGER,
    layer_description TEXT,
    confidence REAL,
    reasoning TEXT,
    impact TEXT,
    created_at TIMESTAMP,
    branch TEXT,
    author TEXT
);

-- Git notes metadata table  
CREATE TABLE git_notes (
    commit_hash TEXT PRIMARY KEY,
    notes_ref TEXT,
    last_sync TIMESTAMP,
    sync_status TEXT
);
```

### 2. Git Hooks Manager (`svcs_repo_hooks.py`)

Manages git hooks for automatic semantic analysis and team synchronization.

**Supported Hooks**:
- `post-commit`: Analyze new commits automatically
- `post-merge`: Handle merge semantic analysis  
- `pre-push`: Sync semantic insights to team via git notes
- `post-receive`: Update local analysis from team notes

### 3. Semantic Analysis Engine (`svcs.semantic_analyzer.SVCSModularAnalyzer`)

Multi-language semantic analysis engine for repository-local analysis.

**Supported Languages**:
- Python: AST-based analysis with scope tracking
- JavaScript/TypeScript: Babel parser integration
- Java: Tree-sitter based analysis
- C/C++: Clang AST integration
- Go: Go AST parser
- Rust: Tree-sitter Rust grammar
- PHP: PHP-Parser integration

### 4. CLI Interface (`svcs/cli.py`)

Repository-focused command line interface.

**Core Commands**:
```bash
# Repository Management
svcs init                          # Initialize SVCS for current repository
svcs status                        # Repository status with git integration
svcs cleanup                       # Repository maintenance

# Semantic Analysis
svcs events                        # List semantic events with git context
svcs search <query>                # Search semantic events
svcs evolution <node>              # Track evolution of functions/classes
svcs compare <branch1> <branch2>   # Compare semantic patterns

# Team Collaboration  
svcs sync                          # Sync semantic insights with team
svcs notes                         # Manage git notes for semantic data
```

## Team Collaboration

### Git Notes Integration

SVCS uses git notes to share semantic insights across team members:

**Notes Organization**:
- `refs/notes/svcs-semantic`: Semantic analysis results
- `refs/notes/svcs-quality`: Code quality insights  
- `refs/notes/svcs-patterns`: AI-detected patterns

**Team Workflow**:
1. Developer commits code with automatic semantic analysis
2. SVCS stores analysis in local database
3. On push, semantic insights are shared via git notes
4. Team members pull notes to get semantic context
5. Semantic insights enhance code review and collaboration

### Synchronization

**Push Workflow**:
```bash
git push                           # Pushes code + semantic notes
# SVCS automatically:
# 1. Analyzes new commits  
# 2. Updates git notes with semantic insights
# 3. Pushes notes to remote repository
```

**Pull Workflow**:
```bash
git pull                           # Pulls code + semantic notes  
# SVCS automatically:
# 1. Fetches semantic notes from team
# 2. Updates local semantic database
# 3. Provides enhanced context for development
```

## Performance Optimizations

### Local Database Benefits
- **Faster Queries**: No network latency for local analysis
- **Branch Awareness**: Efficient branch-specific filtering
- **Git Integration**: Native git command integration
- **Incremental Analysis**: Only analyze changed files

### Caching Strategy
- **AST Caching**: Cache parsed ASTs for unchanged files
- **Git Object Caching**: Cache git metadata for performance
- **Analysis Caching**: Cache semantic analysis results
- **Notes Caching**: Local cache of team semantic insights

## API Integration

### Repository-Local APIs

The repository-local system provides APIs for integration:

```python
from svcs_repo_local import RepositoryLocalSVCS

# Initialize repository-local SVCS
repo = RepositoryLocalSVCS('/path/to/repository')
repo.initialize_repository()

# Get semantic events
events = repo.get_semantic_events(branch='main', limit=100)

# Search semantic patterns
results = repo.search_events_advanced(
    query="function complexity",
    event_types=['complexity_increase'],
    since_date='7 days ago'
)

# Get git-integrated analytics
analytics = repo.get_repository_analytics()
quality = repo.get_quality_metrics()
```

### MCP Server Integration

The Model Context Protocol (MCP) server provides AI integration:

**Features**:
- Natural language semantic queries
- AI-powered pattern detection
- Intelligent code analysis
- Team collaboration insights

## Development Workflow

### Repository Setup

1. **Initialize Repository**:
   ```bash
   cd your-repository
   svcs init
   ```

2. **Automatic Analysis**:
   - SVCS automatically analyzes commits via git hooks
   - Semantic events stored in local database
   - Git notes shared with team

3. **Team Collaboration**:
   - Team members get semantic context automatically
   - Enhanced code review with semantic insights
   - Shared understanding of code evolution

### Quality Integration

**Branch-Aware Quality Gates**:
```bash
# Quality analysis for current branch
svcs quality --branch main

# Compare quality between branches  
svcs quality --compare feature/new-ui main

# Set quality thresholds for CI/CD
svcs quality --gate --max-complexity 10
```

## Configuration

### Repository Configuration

SVCS configuration stored in `.svcs/config.yaml`:

```yaml
# Repository-local SVCS configuration
repository:
  name: "my-project"
  initialized: "2024-01-15"
  
analysis:
  languages: ["python", "javascript", "typescript"]
  quality_thresholds:
    max_complexity_increases: 3
    min_error_handling_ratio: 0.7
    
collaboration:
  git_notes_enabled: true
  auto_sync: true
  team_sharing: true
  
performance:
  cache_enabled: true
  incremental_analysis: true
```

### Git Hooks Configuration

SVCS automatically configures git hooks during initialization:

```bash
# Hooks installed in .git/hooks/
post-commit          # Automatic semantic analysis
post-merge           # Merge semantic analysis
pre-push             # Sync semantic notes  
post-receive         # Update from team notes
```

## Benefits

### Developer Experience
- **Automatic Analysis**: No manual intervention required
- **Git-Native**: Integrates seamlessly with existing git workflow  
- **Team Collaboration**: Shared semantic insights enhance teamwork
- **Performance**: Fast local queries and analysis

### Code Quality
- **Continuous Monitoring**: Track code quality over time
- **Branch Awareness**: Quality analysis per branch
- **Pattern Detection**: AI-powered detection of code patterns
- **Team Insights**: Learn from team coding patterns

### Team Collaboration  
- **Shared Context**: Team semantic insights via git notes
- **Enhanced Reviews**: Semantic context for code reviews
- **Knowledge Sharing**: Understand team coding evolution
- **Onboarding**: New team members get semantic context

This repository-local architecture provides a modern, git-integrated approach to semantic code analysis with powerful team collaboration features while maintaining excellent performance through local optimization.
