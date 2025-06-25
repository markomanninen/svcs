# SVCS Legacy Feature Migration Plan
## From Global System to Repository-Local Architecture

This document provides a comprehensive plan for migrating all legacy SVCS features from the global database system (`~/.svcs/global.db`) to the new repository-local, git-integrated architecture (`.svcs/semantic.db`).

## 📋 Executive Summary

**Objective**: Preserve all existing SVCS functionality while transitioning to repository-local architecture
**Approach**: Adaptation and enhancement rather than complete rewriting
**Timeline**: 3 phases over 4-6 weeks
**Code Reuse**: 80%+ of existing logic can be preserved with targeted updates

---

## 🗺️ Feature Migration Mapping

| Legacy Feature | Legacy Module | Repo-Local Status | Migration Type | Code Reuse | Priority |
|----------------|---------------|-------------------|----------------|------------|----------|
| **Analytics Dashboard** | `svcs_analytics.py` | ✅ Adapt | Data Source Update | 90% | HIGH |
| **Quality Analysis** | `svcs_quality.py` | ✅ Adapt | Data Source Update | 85% | HIGH |
| **Static Web Dashboard** | `svcs_web.py` | ✅ Adapt | Data Source Update | 80% | HIGH |
| **Interactive Web Server** | `svcs_web_server.py` | ✅ Adapt | API Update | 75% | MEDIUM |
| **CI/CD Integration** | `svcs_ci.py` | ✅ Enhance | Git Integration | 85% | MEDIUM |
| **MCP Server** | `svcs_mcp/` | 🔄 Hybrid | Architecture Change | 60% | ADVANCED |
| **Project Management** | Global DB | ✅ Replace | Git-Based | 50% | MEDIUM |

---

## 🎯 Phase 1: Core Analytics & Quality (Week 1-2)

### 1.1 Analytics Module Migration (`svcs_analytics.py` → `svcs_repo_analytics.py`)

**Current State**: Reads from `~/.svcs/global.db`, provides cross-project analytics
**Target State**: Reads from `.svcs/semantic.db`, provides git-enhanced repository analytics

#### Changes Required:
```python
# OLD: Global database import
sys.path.insert(0, '.svcs')
from api import get_full_log, get_valid_commit_hashes

# NEW: Repository-local database import  
sys.path.insert(0, '.svcs')
from api import get_full_log, get_valid_commit_hashes, get_git_info
```

#### Enhanced Features:
- **Git Integration**: Correlate semantic events with git commits, branches, authors
- **Branch Analytics**: Compare semantic patterns across git branches
- **Commit Correlation**: Link semantic changes to specific commits and PRs
- **Timeline Enhancement**: Git-aware timeline with commit context

#### Implementation Tasks:
1. ✅ **Update Data Source**: Change database connection to local `.svcs/semantic.db`
2. ✅ **Add Git Correlation**: Enhance existing functions with git commit/branch data
3. ✅ **Branch Comparison**: Add branch-specific analytics functions
4. ✅ **Preserve API**: Maintain compatibility with existing analytics API
5. ✅ **Add CLI Commands**: Update CLI to use new analytics functions

**Code Changes**: ~50 lines modified, ~100 lines added for git integration
**Testing**: Verify analytics on existing repositories with semantic data

---

### 1.2 Quality Analysis Migration (`svcs_quality.py` → `svcs_repo_quality.py`)

**Current State**: `CodeQualityAnalyzer` class with global project analysis
**Target State**: Enhanced analyzer with git integration and branch awareness

#### Enhanced Features:
- **Git Blame Integration**: Correlate quality trends with author contributions
- **Branch Quality Comparison**: Compare code quality across git branches
- **Quality Evolution**: Track quality changes through git history
- **PR Quality Analysis**: Analyze quality impact of pull requests

#### Implementation Tasks:
1. ✅ **Update Database Source**: Adapt to read from local semantic database
2. ✅ **Add Git Integration**: Enhance quality metrics with git context
3. ✅ **Branch Awareness**: Add branch-specific quality analysis
4. ✅ **Author Correlation**: Link quality trends to git authors via git blame
5. ✅ **Preserve Quality Indicators**: Keep existing positive/negative/refactoring event classification

**Code Changes**: ~40 lines modified, ~80 lines added for git features
**Testing**: Validate quality analysis on repositories with known quality patterns

---

## 🎯 Phase 2: Web Dashboard & CI Integration (Week 3-4)

### 2.1 Web Dashboard Migration

#### 2.1.1 Static Dashboard (`svcs_web.py` → `svcs_repo_web.py`)

**Current State**: Generates static HTML with global project data
**Target State**: Repository-focused dashboard with git integration

#### Enhanced Features:
- **Git Branch Selection**: Dashboard filtered by git branch
- **Commit Navigation**: Click-through to specific commits
- **Branch Comparison**: Visual comparison of semantic patterns across branches
- **Git Timeline**: Timeline visualization correlated with git commits

#### Implementation Tasks:
1. ✅ **Update Data Source**: Read from local `.svcs/semantic.db`
2. ✅ **Add Git Context**: Include branch and commit information
3. ✅ **Branch Filtering**: Add branch selection to dashboard UI
4. ✅ **Enhance Visualizations**: Add git-aware timeline and network views
5. ✅ **Preserve UI**: Keep existing Chart.js and D3.js visualizations

**Code Changes**: ~60 lines modified, ~120 lines added for git features

---

#### 2.1.2 Interactive Web Server (`svcs_web_server.py` → `svcs_repo_web_server.py`)

**Current State**: Flask server with API endpoints for global database
**Target State**: Repository-local API server with git integration

#### New API Endpoints:
```python
# Git Integration APIs
@app.route('/api/branches', methods=['GET'])
def api_get_branches():
    """Get available git branches"""

@app.route('/api/branch_comparison', methods=['POST']) 
def api_compare_branches():
    """Compare semantic patterns between branches"""

@app.route('/api/commit_semantic_context', methods=['POST'])
def api_get_commit_semantic_context():
    """Get semantic events for specific commit"""
```

#### Implementation Tasks:
1. ✅ **Update API Endpoints**: Adapt all endpoints to read from local database
2. ✅ **Add Git APIs**: New endpoints for branch and commit operations
3. ✅ **Remove Multi-Project**: Focus on single repository management
4. ✅ **Enhance Project Management**: Manage local repository settings
5. ✅ **Preserve Existing APIs**: Maintain compatibility with existing frontend

**Code Changes**: ~100 lines modified, ~150 lines added for git APIs

---

### 2.2 CI/CD Integration Migration (`svcs_ci.py` → `svcs_repo_ci.py`)

**Current State**: `SVCSCIIntegration` class for pull request analysis
**Target State**: Enhanced CI integration with git hooks and branch awareness

#### Enhanced Features:
- **Git Hook Integration**: Automatic analysis triggered by git hooks
- **Branch-Aware Quality Gates**: Quality checks specific to target branches
- **Semantic PR Analysis**: Enhanced PR analysis with semantic context
- **CI Platform Integration**: Templates for GitHub Actions, Jenkins, etc.

#### Implementation Tasks:
1. ✅ **Update Database Source**: Read from local `.svcs/semantic.db`
2. ✅ **Enhance PR Analysis**: Improve with git branch context
3. ✅ **Add Git Hook Integration**: Connect with existing git hooks
4. ✅ **Create CI Templates**: Provide integration templates for popular CI platforms
5. ✅ **Branch-Aware Gates**: Implement branch-specific quality thresholds

**Code Changes**: ~80 lines modified, ~100 lines added for git integration

---

## 🎯 Phase 3: Advanced Features & MCP Integration (Week 5-6)

### 3.1 MCP Server Hybrid Architecture (`svcs_mcp/` → Enhanced)

**Current State**: `GlobalSVCSDatabase` with centralized multi-project management
**Target State**: Hybrid architecture supporting both local repos and multi-project views

#### Hybrid Architecture Approach:
1. **Local Repository Mode**: Direct access to `.svcs/semantic.db` for single-repo queries
2. **Multi-Repository Mode**: Discovery and aggregation across multiple repositories
3. **Project Registry**: Maintain registry of known repositories for multi-project features
4. **Dynamic Discovery**: Auto-discover SVCS-enabled repositories

#### Implementation Strategy:
```python
class HybridSVCSDatabase:
    """Hybrid database supporting both local and multi-project access."""
    
    def __init__(self, mode="auto"):
        self.mode = mode  # "local", "multi", "auto"
        self.local_db = None
        self.project_registry = {}
        
    def query_local(self, repo_path=None):
        """Query local repository semantic database"""
        
    def query_multi_project(self, query_params):
        """Query across multiple registered repositories"""
        
    def discover_repositories(self, search_paths):
        """Auto-discover SVCS-enabled repositories"""
```

#### Implementation Tasks:
1. ✅ **Design Hybrid Architecture**: Support both local and multi-project modes
2. ✅ **Repository Discovery**: Auto-discover SVCS-enabled repositories
3. ✅ **Multi-Project Aggregation**: Aggregate data across multiple repositories
4. ✅ **Preserve MCP Protocol**: Maintain MCP server compatibility
5. ✅ **Local Repository Priority**: Optimize for single-repository performance

**Code Changes**: ~200 lines modified, ~300 lines added for hybrid architecture

---

### 3.2 Cross-Repository Analytics (Optional Advanced Feature)

**Target State**: Analytics that work across multiple SVCS-enabled repositories

#### Features:
- **Portfolio Analytics**: Cross-project semantic pattern analysis
- **Team Analytics**: Developer contribution patterns across projects
- **Technology Adoption**: Language and framework trends across portfolio
- **Quality Benchmarking**: Compare quality metrics across projects

#### Implementation Approach:
- Use MCP server's multi-project capabilities
- Repository discovery and registration
- Aggregated analytics with project filtering
- Web dashboard with multi-project views

---

## 🔧 Implementation Guidelines

### Database Schema Compatibility
The repository-local database schema is compatible with existing analytics and quality analysis code. Key tables:
- `semantic_events` - Core event data
- `nodes` - Function/class tracking  
- `git_commits` - Git integration data (new)
- `branches` - Branch tracking (new)

### API Compatibility
Preserve existing API functions where possible:
```python
# Preserved APIs (with local database)
get_full_log()
get_recent_activity()  
search_events_advanced()
get_project_statistics()

# Enhanced APIs (with git integration)
get_commit_semantic_context(commit_hash)
get_branch_analytics(branch_name)
compare_branches(branch1, branch2)
```

### Configuration Management
Repository-local configuration in `.svcs/config.yaml`:
```yaml
# Repository-local SVCS configuration
repository:
  name: "project-name"
  initialized: "2024-01-15"
  
analytics:
  quality_thresholds:
    max_complexity_increases: 3
    min_error_handling_ratio: 0.7
    
web_dashboard:
  default_branch: "main"
  theme: "modern"
  
ci_integration:
  enabled: true
  quality_gates: true
```

---

## 🧪 Testing Strategy

### Phase 1 Testing:
- ✅ **Analytics Accuracy**: Verify analytics match between global and local systems
- ✅ **Quality Analysis**: Validate quality metrics consistency
- ✅ **API Compatibility**: Ensure existing scripts continue working

### Phase 2 Testing:
- ✅ **Web Dashboard**: Test all dashboard features with repository data
- ✅ **CI Integration**: Validate CI workflows with semantic analysis
- ✅ **Git Integration**: Test branch comparison and commit correlation

### Phase 3 Testing:
- ✅ **MCP Server**: Test both local and multi-project modes
- ✅ **Cross-Repository**: Validate multi-project analytics
- ✅ **Performance**: Ensure acceptable performance with multiple repositories

---

## 📦 Migration Tools

### Automated Migration Script (`migrate_to_repo_local.py`)
```python
#!/usr/bin/env python3
"""
SVCS Migration Tool - Migrate from global to repository-local system
"""

def migrate_project_data(project_path, global_db_path):
    """Migrate project data from global DB to local repository"""
    
def backup_global_system():
    """Create backup of global system before migration"""
    
def validate_migration(project_path):
    """Validate successful migration"""
```

### Migration Steps:
1. **Backup Global System**: Create full backup of `~/.svcs/`
2. **Initialize Repository**: Run `svcs init` in target repository
3. **Migrate Data**: Copy relevant semantic events to local database
4. **Validate Migration**: Verify data consistency and feature functionality
5. **Update Scripts**: Update any custom scripts to use new APIs

---

## 🚀 Benefits of Migration

### Enhanced Capabilities:
- **Git Integration**: Semantic analysis correlated with git history
- **Branch Awareness**: Analyze and compare semantic patterns across branches
- **Local Performance**: Faster queries on repository-specific data
- **Team Collaboration**: Git-based sharing of semantic insights
- **CI/CD Integration**: Native integration with git-based workflows

### Preserved Functionality:
- **Analytics Dashboard**: All existing analytics with git enhancements
- **Quality Analysis**: Same quality insights with git context
- **Web Interface**: Full web dashboard with repository focus
- **MCP Integration**: AI tool integration with hybrid multi-project support
- **API Compatibility**: Existing scripts and integrations continue working

### New Possibilities:
- **Branch Quality Gates**: Quality checks specific to git branches
- **Semantic Code Review**: PR analysis with semantic context
- **Git-Aware Insights**: Correlate semantic patterns with git events
- **Team Semantic Insights**: Understand team coding patterns through git history

---

## 📈 Success Metrics

### Migration Success Criteria:
- ✅ **Feature Parity**: All legacy features available in repo-local system
- ✅ **Performance**: Equal or better performance than legacy system
- ✅ **API Compatibility**: 90%+ of existing APIs work without changes
- ✅ **Git Integration**: New git-aware features provide additional value
- ✅ **Documentation**: Complete documentation for new architecture

### Quality Metrics:
- ✅ **Code Reuse**: 80%+ of existing code preserved
- ✅ **Test Coverage**: 95%+ test coverage for migrated features
- ✅ **User Experience**: Improved or equivalent user experience
- ✅ **Migration Time**: <1 hour to migrate typical project
- ✅ **Rollback Capability**: Safe rollback to legacy system if needed

---

## 🎯 Conclusion

This migration plan provides a comprehensive roadmap for transitioning all SVCS legacy features to the repository-local architecture while preserving functionality and enhancing capabilities through git integration. The phased approach minimizes risk while maximizing code reuse and ensuring a smooth transition for users.

**Key Success Factors:**
1. **Incremental Migration**: Phase-by-phase implementation reduces risk
2. **Code Preservation**: Maximum reuse of existing, tested logic
3. **Enhanced Value**: Git integration adds capabilities not possible in legacy system
4. **API Compatibility**: Existing integrations continue working
5. **Comprehensive Testing**: Thorough validation ensures reliability

The result will be a more powerful, git-integrated SVCS system that provides all legacy capabilities plus new git-native features for modern development workflows.
