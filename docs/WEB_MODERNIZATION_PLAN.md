# SVCS Web Interface Modernization Plan

## 🎯 **Architecture Overview**

**New Simplified Architecture:**
- **Repository-Local**: Each repository has `.svcs/semantic.db` with branch-specific data
- **Central Registry**: `~/.svcs/repos.db` contains pointers to registered repositories
- **No Legacy Support**: Clean break from old global database approach
- **No MCP Dependencies**: Focus on repository-local web interface

## 📋 **Implementation Tasks**

### **Phase 1: Core Web Server Updates**

#### 1.1 Update Web Server API Endpoints

**File**: `svcs_web_server.py`

**New Repository Management Endpoints:**
```python
# Replace existing repository endpoints
GET  /api/repositories/discover        # Discover repos from registry + scan
POST /api/repositories/register        # Register repo in central registry  
POST /api/repositories/unregister      # Remove repo from registry
POST /api/repositories/initialize      # Initialize SVCS in repository
GET  /api/repositories/list            # List registered repositories
POST /api/repositories/statistics      # Get repository statistics
```

**Updated Semantic Analysis Endpoints:**
All existing semantic endpoints need `repository_path` parameter:
```python
POST /api/semantic/search_events       # Requires repository_path
POST /api/semantic/recent_activity     # Requires repository_path
POST /api/semantic/commit_summary      # Requires repository_path
POST /api/semantic/evolution           # Requires repository_path
# ... etc for all semantic operations
```

#### 1.2 Replace Legacy API Calls

**Current Issue**: Web server imports from `.svcs/api.py` and legacy modules
**Solution**: Use only `SVCSWebRepositoryManager` for all operations

**Changes Required:**
1. Remove all legacy imports
2. Update all endpoints to use repository manager
3. Add proper error handling for missing repositories
4. Add repository selection validation

### **Phase 2: Frontend/UI Modernization**

#### 2.1 Add Repository Selection Interface

**File**: `svcs_interactive_dashboard.html`

**New UI Components:**
```html
<!-- Repository Selection Header -->
<div class="repository-selector">
    <h3>📂 Current Repository</h3>
    <select id="current-repository" class="form-control">
        <option value="">Select repository...</option>
    </select>
    <button onclick="refreshRepositories()">🔄 Refresh</button>
    <button onclick="showRegisterDialog()">➕ Register New</button>
</div>

<!-- Repository Management Panel -->
<div id="repository-management" class="tool-section">
    <h2>🗂️ Repository Management</h2>
    
    <!-- Discovery and Registration -->
    <div class="form-group">
        <button onclick="discoverRepositories()">🔍 Discover Repositories</button>
        <button onclick="registerRepository()">📝 Register Repository</button>
    </div>
    
    <!-- Repository List -->
    <div id="repository-list" class="repository-grid">
        <!-- Dynamic repository cards -->
    </div>
</div>
```

#### 2.2 Update All Forms and API Calls

**Changes Required:**
1. Add repository selection to every semantic operation form
2. Update all JavaScript API calls to include `repository_path`
3. Add repository validation before operations
4. Show repository context in all result displays

#### 2.3 Repository Dashboard View

**New Feature**: Multi-repository overview
```html
<!-- Repository Overview Cards -->
<div class="repository-overview">
    <div class="repo-card" data-path="/path/to/repo1">
        <h4>Project Name</h4>
        <div class="repo-stats">
            <span>📊 123 events</span>
            <span>🔄 45 commits</span>
            <span>🌿 main branch</span>
        </div>
        <button onclick="selectRepository('/path/to/repo1')">Select</button>
    </div>
</div>
```

### **Phase 3: Backend Integration**

#### 3.1 Create Unified API Service

**New File**: `svcs_web_api_service.py`
```python
class SVCSWebAPIService:
    """Unified API service for repository-local SVCS operations."""
    
    def __init__(self):
        self.repo_manager = web_repository_manager
    
    def execute_semantic_operation(self, operation: str, repository_path: str, **params):
        """Execute semantic operation on specific repository."""
        
    def get_all_repositories(self):
        """Get all discovered and registered repositories."""
        
    def validate_repository(self, repository_path: str):
        """Validate repository exists and is SVCS-enabled."""
```

#### 3.2 Standardize Endpoint Pattern

**New Route Structure:**
```python
@app.route('/api/<category>/<operation>', methods=['POST'])
def api_handler(category, operation):
    """Unified API handler with repository validation."""
    data = request.get_json()
    repository_path = data.get('repository_path')
    
    if not repository_path:
        return jsonify({'error': 'repository_path required'}), 400
    
    try:
        result = api_service.execute_operation(category, operation, repository_path, **data)
        return jsonify({'success': True, 'data': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
```

### **Phase 4: Enhanced Features**

#### 4.1 Repository Discovery and Auto-Registration

**Features:**
- Scan common directories for SVCS repositories
- Show discovered vs. registered repositories
- One-click registration for discovered repositories
- Validation of repository health

#### 4.2 Cross-Repository Analysis

**Future Enhancement:**
- Search across multiple repositories
- Compare evolution patterns between repositories
- Aggregate statistics across all repositories

#### 4.3 Repository Health Monitoring

**Features:**
- Show repository status (initialized, healthy, errors)
- Display last analysis date
- Monitor for repository issues

## 🔧 **Technical Implementation Details**

### **Database Changes**

**Central Registry** (`~/.svcs/repos.db`):
```sql
CREATE TABLE repositories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    path TEXT UNIQUE NOT NULL,
    db_path TEXT NOT NULL,
    created_at INTEGER NOT NULL,
    last_accessed INTEGER
);
```

**Repository-Local** (`.svcs/semantic.db`):
- No changes required - existing branch-specific structure

### **API Response Format Standardization**

```json
{
    "success": true,
    "data": {
        "repository_path": "/path/to/repo",
        "repository_name": "Project Name",
        "results": [...]
    },
    "meta": {
        "timestamp": "2025-06-25T12:00:00Z",
        "operation": "search_events",
        "total_results": 42
    }
}
```

### **Error Handling Strategy**

```python
class RepositoryError(Exception):
    """Repository-related errors."""
    pass

class RepositoryNotFound(RepositoryError):
    """Repository not found or not initialized."""
    pass

class RepositoryNotRegistered(RepositoryError):
    """Repository not in central registry."""
    pass
```

## 📊 **Implementation Priority**

1. **High Priority**: Update `svcs_web_server.py` to use repository manager only
2. **High Priority**: Add repository selection UI component
3. **Medium Priority**: Update all existing endpoints to require repository_path
4. **Medium Priority**: Add repository management interface
5. **Low Priority**: Cross-repository analysis features

## 🎉 **Benefits of New Architecture**

1. **Simplified**: No complex migration or fallback logic
2. **Scalable**: Can handle unlimited repositories via registry
3. **Fast**: Direct access to repository-local databases
4. **Clean**: Fresh start without legacy compatibility burden
5. **Maintainable**: Single source of truth for repository management

## 🚀 **Next Steps**

1. Complete `svcs_web_repository_manager.py` implementation ✅
2. Update web server endpoints to use repository manager
3. Add repository selection UI to dashboard
4. Test with multiple repositories
5. Deploy and iterate

This plan provides a clean, modern architecture that leverages the new repository-local approach without the complexity of backwards compatibility.
