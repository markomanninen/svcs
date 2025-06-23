# SVCS Git-Integrated Team Architecture

## Problem Statement

The current SVCS implementation stores semantic data in a global user database (`~/.svcs/global.db`) which doesn't integrate with git's natural team collaboration workflow. When developers push/pull commits, the semantic analysis data doesn't travel with the commits, preventing true team semantic intelligence.

## Solution: Git-Native Team Collaboration

**Core Principle**: Semantic data should follow the exact same workflow as source code through git's existing collaboration mechanisms.

## Architecture Design

### 1. Git Notes Integration

Store semantic analysis as git notes attached to each commit:

```bash
# Post-commit hook stores semantic analysis
git notes --ref=svcs add -m '{
  "events": [
    {"type": "function_added", "name": "process_data", "layer": 2},
    {"type": "performance_optimization", "confidence": 0.85, "layer": "5b"}
  ],
  "analysis_timestamp": 1640995200,
  "svcs_version": "1.0.0"
}' $commit_hash

# Configure automatic sync of semantic notes
git config notes.rewriteRef refs/notes/svcs
git config remote.origin.push '+refs/notes/svcs:refs/notes/svcs'
git config remote.origin.fetch '+refs/notes/svcs:refs/notes/svcs'
```

### 2. Repository-Based Storage

Move from global database to repository-specific storage:

```
project/
├── .svcs/
│   ├── config.yaml           # SVCS configuration for this repo
│   ├── semantic.db           # Local semantic database (branch-aware)
│   ├── cache/                # Analysis cache and temp files
│   ├── logs/                 # SVCS operation logs
│   └── branches/             # Branch-specific metadata
│       ├── main.json         # Main branch semantic state
│       ├── develop.json      # Develop branch semantic state
│       └── feature-x.json    # Feature branch semantic state
├── .git/
│   └── hooks/
│       ├── post-commit       # Analyze commit + store in git notes
│       ├── post-merge        # Merge semantic data from branches
│       ├── post-checkout     # Switch branch semantic context
│       ├── pre-push          # Validate semantic data before push
│       └── post-receive      # Server-side semantic data processing
└── .gitignore                # Include .svcs/cache/, exclude .svcs/semantic.db
```

### 3. Enhanced Git Hooks

#### `post-commit` Hook
```bash
#!/bin/bash
# Run SVCS semantic analysis
cd "$(git rev-parse --show-toplevel)"
.svcs/bin/svcs analyze HEAD

# Store results in git notes
commit_hash=$(git rev-parse HEAD)
semantic_data=$(cat .svcs/cache/latest_analysis.json)
git notes --ref=svcs add -m "$semantic_data" $commit_hash

# Update local semantic database
.svcs/bin/svcs update-db --commit $commit_hash
```

#### `post-merge` Hook
```bash
#!/bin/bash
# Merge semantic data from merged branch
cd "$(git rev-parse --show-toplevel)"
merged_commits=$(git rev-list HEAD^..HEAD)

for commit in $merged_commits; do
    # Import semantic notes from merged commits
    semantic_data=$(git notes --ref=svcs show $commit 2>/dev/null)
    if [ ! -z "$semantic_data" ]; then
        .svcs/bin/svcs import-semantic --commit $commit --data "$semantic_data"
    fi
done

# Rebuild semantic indices for current branch
.svcs/bin/svcs rebuild-indices --branch $(git branch --show-current)
```

#### `post-checkout` Hook
```bash
#!/bin/bash
# Switch semantic context when changing branches
if [ "$3" = "1" ]; then  # Branch checkout, not file checkout
    cd "$(git rev-parse --show-toplevel)"
    new_branch="$2"
    .svcs/bin/svcs switch-branch --branch $new_branch
    .svcs/bin/svcs sync-from-notes --branch $new_branch
fi
```

### 4. Database Schema Changes

#### Repository-Local Database (`.svcs/semantic.db`)
```sql
-- Enhanced projects table (repository-specific)
CREATE TABLE repository_info (
    repo_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    remote_origin TEXT,
    created_at INTEGER,
    last_sync_at INTEGER
);

-- Branch-aware semantic events
CREATE TABLE semantic_events (
    event_id TEXT PRIMARY KEY,
    commit_hash TEXT NOT NULL,
    branch_name TEXT NOT NULL,
    event_type TEXT NOT NULL,
    node_id TEXT,
    location TEXT,
    details TEXT,
    layer TEXT,
    confidence REAL,
    created_at INTEGER,
    source TEXT DEFAULT 'local', -- 'local', 'remote', 'merged'
    git_notes_synced BOOLEAN DEFAULT FALSE
);

-- Branch metadata
CREATE TABLE branches (
    branch_name TEXT PRIMARY KEY,
    base_commit TEXT,
    last_analyzed_commit TEXT,
    semantic_event_count INTEGER DEFAULT 0,
    created_at INTEGER,
    updated_at INTEGER
);

-- Commit metadata with git integration
CREATE TABLE commits (
    commit_hash TEXT PRIMARY KEY,
    branch_name TEXT NOT NULL,
    author TEXT,
    timestamp INTEGER,
    message TEXT,
    parent_commits TEXT, -- JSON array of parent commit hashes
    has_git_notes BOOLEAN DEFAULT FALSE,
    analysis_status TEXT DEFAULT 'pending' -- 'pending', 'analyzed', 'cached'
);

-- Git notes sync tracking
CREATE TABLE git_notes_sync (
    commit_hash TEXT PRIMARY KEY,
    notes_hash TEXT,
    last_sync_at INTEGER,
    sync_status TEXT DEFAULT 'pending' -- 'pending', 'synced', 'conflict'
);
```

## Team Collaboration Workflow

### Scenario: Feature Development with Team Semantic Intelligence

1. **Developer Alice starts feature branch**:
   ```bash
   git checkout -b feature/user-auth
   # SVCS automatically creates branch semantic context
   ```

2. **Alice makes commits with semantic analysis**:
   ```bash
   # Alice commits new authentication code
   git commit -m "Add JWT authentication service"
   # post-commit hook runs SVCS analysis
   # Semantic events stored in git notes + local database
   ```

3. **Alice pushes feature branch**:
   ```bash
   git push origin feature/user-auth
   # Git notes with semantic data automatically included
   ```

4. **Developer Bob fetches and reviews**:
   ```bash
   git fetch origin
   git checkout feature/user-auth
   # post-checkout hook syncs semantic data from git notes
   # Bob can now query Alice's semantic analysis
   svcs search --query "authentication" --branch feature/user-auth
   svcs evolution class:JWTService --branch feature/user-auth
   ```

5. **Feature branch merges to main**:
   ```bash
   git checkout main
   git merge feature/user-auth
   # post-merge hook integrates semantic data into main branch
   # All semantic events from feature branch now part of main history
   ```

6. **Team pulls main branch**:
   ```bash
   git pull origin main
   # All team members automatically get integrated semantic history
   # Can query cross-developer semantic evolution
   svcs team-activity --since "1 week"
   svcs search --author "Alice" --event-type "security_improvement"
   ```

## Enhanced CLI Commands

### Repository Management
```bash
# Initialize SVCS in git repository
svcs init                              # Setup .svcs/ structure + git hooks
svcs status                            # Show SVCS status for current repo
svcs config                            # Configure repository-specific settings

# Git integration
svcs sync-notes                        # Sync semantic data via git notes
svcs pull-semantic                     # Pull semantic data from remote notes
svcs push-semantic                     # Push semantic data to remote notes
```

### Branch-Aware Operations
```bash
# Branch-specific queries
svcs search --branch main              # Search semantic events on main
svcs search --branch feature/auth      # Search on specific feature branch
svcs evolution func:authenticate --branch develop  # Track evolution on branch

# Cross-branch analysis
svcs diff-branches main..feature/auth  # Compare semantic evolution
svcs merge-preview feature/auth        # Preview semantic impact of merge
svcs branch-stats                      # Semantic statistics for current branch
svcs branch-list                       # List all branches with semantic data
```

### Team Collaboration
```bash
# Team-wide semantic intelligence
svcs team-activity --since "2 weeks"   # Recent semantic changes by team
svcs author-stats --branch main        # Semantic contributions by author
svcs cross-author-evolution func:process  # Track function across developers

# Conflict resolution
svcs resolve-semantic-conflicts        # Resolve semantic data merge conflicts
svcs validate-semantic-integrity       # Validate semantic data consistency
```

### Advanced Git Integration
```bash
# Commit-specific operations
svcs analyze-commit SHA                # Analyze specific commit
svcs commit-semantic SHA               # Show semantic analysis for commit
svcs bulk-import --from-notes          # Import semantic data from existing git notes

# Repository maintenance
svcs rebuild-indices                   # Rebuild semantic search indices
svcs cleanup-orphaned                  # Clean semantic data for deleted commits
svcs validate-git-notes                # Validate git notes consistency
```

## Implementation Phases

### Phase 1: Repository-Based Storage (Week 1-2)
1. Redesign database schema for repository-local storage
2. Implement `.svcs/` directory structure
3. Create repository initialization (`svcs init`)
4. Migration tool from global database to repository-specific

### Phase 2: Git Notes Integration (Week 3-4)
1. Implement git notes storage for semantic analysis
2. Create git notes sync commands (`svcs sync-notes`)
3. Build commit-semantic data mapping
4. Add git notes validation and conflict resolution

### Phase 3: Enhanced Git Hooks (Week 5-6)
1. Redesign post-commit hook for git notes storage
2. Implement post-merge hook for branch semantic merging
3. Add post-checkout hook for branch context switching
4. Create pre-push validation for semantic data integrity

### Phase 4: Branch-Aware CLI (Week 7-8)
1. Update all CLI commands for branch awareness
2. Implement branch comparison commands
3. Add cross-branch semantic evolution tracking
4. Create team collaboration commands

### Phase 5: Team Features & Testing (Week 9-10)
1. Comprehensive testing with multi-developer workflows
2. Performance optimization for large repositories
3. Documentation and team setup guides
4. Integration testing with popular git hosting platforms

## Migration Strategy

### For Existing SVCS Users
```bash
# Automatic migration from global database
svcs migrate-to-repository /path/to/project
# ✅ Moves semantic data from ~/.svcs/global.db to project/.svcs/semantic.db
# ✅ Preserves all existing semantic history
# ✅ Sets up git hooks and repository structure
# ✅ Creates git notes for existing commits (where possible)

# Bulk migration for multiple projects
svcs migrate-all-projects
# ✅ Discovers all registered projects
# ✅ Migrates each to repository-based storage
# ✅ Updates global registry to point to new locations
```

### Backward Compatibility
- Global project registry remains for project discovery
- Existing CLI commands work with repository-based storage
- Optional: maintain global database for cross-project queries
- Gradual migration: projects can be migrated individually

## Benefits of Git-Integrated Approach

### For Individual Developers
- **Semantic history travels with code**: Never lose semantic context when cloning
- **Branch-aware analysis**: Understand semantic evolution per feature
- **Automatic backup**: Semantic data backed up via git remotes

### For Development Teams
- **Natural collaboration**: Semantic data follows same workflow as code
- **Shared semantic intelligence**: Everyone sees same analysis without setup
- **Branch merge integration**: Semantic history merges automatically
- **No infrastructure needed**: Works with any git hosting platform

### For Organizations
- **Repository-level insights**: Semantic analysis per project
- **Cross-developer evolution**: Track how features evolve across team members
- **Git hosting integration**: Works with GitHub, GitLab, Bitbucket automatically
- **Audit trail**: Complete semantic history stored in git

## Security and Privacy Considerations

### Git Notes Privacy
- Git notes follow same access control as repository
- Semantic data only shared with developers who have repository access
- Option to exclude sensitive semantic data from git notes

### Repository-Local Storage
- Sensitive analysis data can remain in local `.svcs/semantic.db`
- Git notes store only essential semantic metadata
- Configurable privacy levels per repository

## Performance Considerations

### Git Notes Overhead
- Semantic data stored as JSON in git notes (lightweight)
- Only essential metadata stored in notes, full analysis in local database
- Configurable: can disable git notes for private repositories

### Repository Size Impact
- Git notes add minimal overhead to repository size
- Local `.svcs/semantic.db` excluded from git (in .gitignore)
- Efficient JSON compression for semantic metadata

## Success Metrics

### Technical Metrics
- Semantic data sync success rate > 99%
- Git operations overhead < 100ms additional time
- Cross-developer semantic query response time < 500ms
- Zero semantic data loss during git operations

### Team Adoption Metrics
- Time to see teammate's semantic analysis < 5 minutes (after push/pull)
- Team semantic query usage increase > 50%
- Cross-developer semantic insights discovery
- Reduced time to understand complex changes by 30%

This git-integrated approach transforms SVCS from a single-user tool into a naturally collaborative system that leverages git's existing team workflow mechanisms.
