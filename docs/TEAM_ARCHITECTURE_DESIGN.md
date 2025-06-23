# SVCS Team Architecture Design

## Problem Statement

The current SVCS implementation is a single-user system with local database storage (`~/.svcs/global.db`), but the README contains claims about team and organizational capabilities that aren't implemented. This document outlines a hybrid architecture design that will enable true team collaboration while maintaining backward compatibility.

## Design Goals

1. **Backward Compatibility**: Existing single-user installations continue working unchanged
2. **Gradual Adoption**: Teams can migrate projects incrementally 
3. **Offline Capability**: Local database continues to work when team server is unavailable
4. **Flexible Sharing**: Users can choose which projects to share with teams
5. **Security**: Proper authentication and project-level access control

## Proposed Hybrid Architecture

### Phase 1: Enhanced Local Mode (Current + Configuration)

**Current State (Preserved):**
```
~/.svcs/
├── global.db                 # Local SQLite database  
├── hooks/                    # Git hooks directory
│   └── svcs-hook            # Universal git hook script
├── logs/                     # Local logs
├── projects/                 # Per-project metadata
└── cache/                    # Local cache
```

**New Additions:**
```
~/.svcs/
├── config.yaml              # Team server configuration
└── teams/                   # Team-specific local cache
    ├── team1.db             # Cached team data
    └── team2.db             # Cached team data
```

**Configuration Format (`~/.svcs/config.yaml`):**
```yaml
teams:
  my-company:
    server: "https://svcs.mycompany.com"
    token: "jwt_token_here"
    auto_sync: true
    projects:
      - "/path/to/shared/project1"
      - "/path/to/shared/project2"
  
personal:
  projects:
    - "/path/to/personal/project"
```

### Phase 2: Team Server Component

**SVCS Team Server Architecture:**
```
svcs-team-server/
├── api/                     # REST API endpoints
├── auth/                    # Authentication & authorization
├── database/                # PostgreSQL/MySQL backend
├── sync/                    # Synchronization logic
└── web/                     # Team dashboard
```

**Database Schema Extensions:**
```sql
-- Teams and membership
CREATE TABLE teams (
    team_id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP,
    config JSONB DEFAULT '{}'
);

CREATE TABLE team_memberships (
    team_id UUID REFERENCES teams(team_id),
    user_id UUID REFERENCES users(user_id), 
    role VARCHAR(50) NOT NULL, -- 'member', 'admin', 'owner'
    joined_at TIMESTAMP,
    PRIMARY KEY (team_id, user_id)
);

-- Enhanced projects table
ALTER TABLE projects ADD COLUMN team_id UUID REFERENCES teams(team_id);
ALTER TABLE projects ADD COLUMN visibility VARCHAR(20) DEFAULT 'personal'; -- 'personal', 'team', 'public'
ALTER TABLE projects ADD COLUMN last_sync_at TIMESTAMP;

-- Project permissions
CREATE TABLE project_permissions (
    project_id UUID,
    user_id UUID,
    permission VARCHAR(20) NOT NULL, -- 'read', 'write', 'admin'
    granted_at TIMESTAMP,
    PRIMARY KEY (project_id, user_id)
);

-- Sync metadata
CREATE TABLE sync_events (
    sync_id UUID PRIMARY KEY,
    project_id UUID,
    user_id UUID,
    sync_type VARCHAR(20), -- 'push', 'pull', 'conflict'
    events_count INTEGER,
    sync_at TIMESTAMP,
    status VARCHAR(20) -- 'success', 'conflict', 'error'
);
```

### Phase 3: Enhanced CLI with Team Operations

**New CLI Commands:**
```bash
# Team management
svcs team join --server https://svcs.mycompany.com --token abc123
svcs team leave my-company
svcs team list
svcs team info my-company

# Project sharing
svcs share --team my-company /path/to/project
svcs unshare /path/to/project  
svcs project-permissions /path/to/project

# Team synchronization
svcs sync --project /path/to/project     # Sync specific project
svcs sync --team my-company              # Sync all team projects
svcs sync --all                          # Sync all shared projects
svcs sync --dry-run                      # Preview sync operations

# Team-wide queries
svcs team-search --team my-company --query "performance"
svcs team-evolution --team my-company --function process_data
svcs team-analytics --team my-company --since "1 month ago"
svcs team-compare --projects proj1,proj2 --pattern "refactoring"
```

**Enhanced Individual Commands:**
```bash
# Existing commands work unchanged for personal projects
svcs search --query "performance"       # Local search only
svcs evolution func:process_data         # Local evolution only

# New --team flag for team-wide operations  
svcs search --team my-company --query "performance"  
svcs evolution --team my-company func:process_data
```

## Implementation Plan

### Phase 1: Configuration Infrastructure (Week 1-2)
1. Add team configuration support to existing CLI
2. Modify database schema to support team metadata
3. Add team/personal project separation logic
4. Update MCP server to handle team configuration

### Phase 2: Team Server Development (Week 3-6)
1. Design REST API endpoints
2. Implement authentication system (JWT-based)
3. Create team server with PostgreSQL backend
4. Build synchronization protocol
5. Add conflict resolution logic

### Phase 3: CLI Integration (Week 7-8)
1. Implement team management commands
2. Add sync commands with conflict resolution
3. Extend search/evolution commands for team operations
4. Add team-wide analytics capabilities

### Phase 4: Web Dashboard Enhancement (Week 9-10)
1. Add team login/authentication to web dashboard
2. Create team-wide analytics views
3. Add project sharing management interface
4. Build team member management interface

### Phase 5: Testing & Documentation (Week 11-12)
1. Comprehensive testing of sync conflicts
2. Security testing and penetration testing
3. Performance testing with large datasets
4. Documentation and migration guides

## Security Considerations

### Authentication
- JWT-based authentication with refresh tokens
- Support for SSO integration (SAML, OIDC)
- API key authentication for CI/CD systems

### Authorization
- Project-level permissions (read/write/admin)
- Team-level roles (member/admin/owner)
- Audit logging for all team operations

### Data Protection
- HTTPS/TLS for all communication
- Encrypted database connections
- Optional semantic data encryption at rest

## Migration Strategy

### For Existing Users
1. **No Impact**: Existing single-user setups continue working unchanged
2. **Opt-in**: Team features are completely optional
3. **Gradual**: Projects can be migrated to team sharing one by one

### Migration Commands
```bash
# Migrate existing project to team
svcs migrate-to-team --project /path/to/project --team my-company

# Migrate team project back to personal
svcs migrate-to-personal --project /path/to/project

# Bulk migration
svcs migrate-all-to-team --team my-company --exclude personal-proj
```

## Conflict Resolution

### Sync Conflicts
When multiple team members analyze the same commits, conflicts may arise:

1. **Automatic Resolution**: Identical semantic events are deduplicated
2. **Confidence-based**: Higher confidence AI analysis takes precedence  
3. **User Choice**: Manual resolution for genuine conflicts
4. **Audit Trail**: All conflict resolutions are logged

### Conflict Resolution UI
```bash
svcs resolve-conflicts /path/to/project
# Interactive CLI for viewing and resolving sync conflicts

svcs conflicts list                    # Show pending conflicts
svcs conflicts resolve --id conflict123 --strategy merge
```

## Performance Considerations

### Local Performance
- Team data cached locally to maintain offline capability
- Incremental sync to minimize data transfer
- Background sync processes to avoid blocking user operations

### Server Performance  
- Database indexing for team queries
- Connection pooling for concurrent users
- Caching layer for frequently accessed data
- Horizontal scaling support for large teams

## Rollout Strategy

### Beta Phase
1. Deploy to small internal teams (5-10 people)
2. Gather feedback on sync conflicts and performance
3. Iterate on API design and conflict resolution

### Public Release
1. Public documentation and migration guides
2. Video tutorials for team setup
3. Support for popular CI/CD integrations
4. Community feedback and feature requests

## Success Metrics

### Technical Metrics
- Sync conflict rate < 5%
- API response time < 200ms (95th percentile)
- Zero data loss during sync operations
- 99.9% uptime for team servers

### User Experience Metrics
- Time to set up team sharing < 10 minutes
- User satisfaction with conflict resolution
- Adoption rate across different team sizes
- Feature usage analytics

## Future Enhancements

### Advanced Team Features
- Cross-team project sharing
- Organization-wide semantic insights
- Advanced analytics and reporting
- Integration with external tools (Jira, Slack, etc.)

### Scaling Features
- Multi-region server deployment
- Federated team servers
- Advanced caching and CDN integration
- Real-time collaboration features

This architecture provides a clear path from the current single-user system to a fully collaborative team environment while maintaining all the benefits of the local-first design.
