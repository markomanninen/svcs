# SVCS Web Server - New Repository-Local Architecture

Modern Flask-based web server for SVCS using repository-local `semantic.db` files with central registry at `~/.svcs/repos.db`.

## 🏗️ Architecture Overview

**Repository-Local Design:**
- Each repository has its own `.svcs/semantic.db` with branch-specific semantic data
- Central registry at `~/.svcs/repos.db` tracks registered repositories
- No global semantic database - clean separation of concerns
- Web interface can manage multiple repositories simultaneously

## 🚀 Quick Start

### 1. Prerequisites

```bash
# Install required Python packages
pip install flask flask-cors

# Ensure SVCS repository-local module is available
# (should be in the same directory or Python path)
```

### 2. Start the Web Server

```bash
# Start with default settings (localhost:8080)
python3 svcs_web_server_new.py

# Custom host and port
python3 svcs_web_server_new.py --host 0.0.0.0 --port 9000

# Debug mode
python3 svcs_web_server_new.py --debug
```

### 3. Access the Dashboard

Open your browser to: `http://localhost:8080`

## 🛠️ API Endpoints

### Repository Management

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/repositories/discover` | GET/POST | Discover repositories from registry + filesystem |
| `/api/repositories/register` | POST | Register repository in central registry |
| `/api/repositories/unregister` | POST | Remove repository from registry |
| `/api/repositories/initialize` | POST | Initialize SVCS in repository + auto-register |
| `/api/repositories/statistics` | POST | Get repository statistics |

### Semantic Analysis

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/semantic/search_events` | POST | Search semantic events in repository |
| `/api/semantic/recent_activity` | POST | Get recent semantic activity |
| `/api/semantic/commit_summary` | POST | Get commit summary with semantic events |
| `/api/semantic/evolution` | POST | Get evolution history for code element |

### System Information

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check and system status |
| `/api/system/status` | GET | Detailed system information |

## 📝 API Usage Examples

### Register a Repository

```bash
curl -X POST http://localhost:8080/api/repositories/register \
  -H "Content-Type: application/json" \
  -d '{"path": "/path/to/your/project", "name": "My Project"}'
```

### Search Semantic Events

```bash
curl -X POST http://localhost:8080/api/semantic/search_events \
  -H "Content-Type: application/json" \
  -d '{
    "repository_path": "/path/to/your/project",
    "limit": 20,
    "event_type": "function_added",
    "since_days": 7
  }'
```

### Get Repository Statistics

```bash
curl -X POST http://localhost:8080/api/repositories/statistics \
  -H "Content-Type: application/json" \
  -d '{"repository_path": "/path/to/your/project"}'
```

## 🔧 Integration with SVCS Init

### Automatic Registration

The web server includes automatic registration functionality. When you run `svcs init` in a repository, you can automatically register it:

```python
# From svcs init process or post-commit hook
from svcs_registry_integration import register_repository
result = register_repository("/path/to/repo")
```

### CLI Integration Script

```bash
# Register repository
python3 svcs_registry_integration.py register /path/to/repo "Project Name"

# List registered repositories
python3 svcs_registry_integration.py list

# Unregister repository
python3 svcs_registry_integration.py unregister /path/to/repo
```

## 📊 Central Registry Database

**Location**: `~/.svcs/repos.db`

**Schema**:
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

## 🔍 Repository Discovery

The web server discovers repositories from:

1. **Central Registry**: Previously registered repositories
2. **Filesystem Scan**: Automatic discovery of `.svcs/semantic.db` files
3. **Common Locations**: Scans typical project directories

**Default Scan Paths**:
- Current working directory
- User home directory
- `/Users`, `/home`, `/workspace`, `/projects`

## 🧪 Testing

Run the test suite to verify functionality:

```bash
python3 test_new_architecture.py
```

This tests:
- Repository manager functionality
- Registry integration
- Web server module import
- Discovery and statistics

## 🆚 Differences from Legacy Server

| Feature | Legacy Server | New Server |
|---------|---------------|------------|
| **Architecture** | Global database | Repository-local |
| **Project Management** | Single project context | Multi-project registry |
| **Dependencies** | Legacy API imports | Repository manager only |
| **Migration Support** | Complex fallback logic | Clean, simple architecture |
| **Registration** | Manual process | Auto-registration on init |

## 🔒 Security Considerations

- **Local Access**: Server binds to localhost by default
- **Path Validation**: Repository paths are validated and resolved
- **Error Handling**: Comprehensive error handling prevents information leakage
- **Registry Protection**: Central registry is user-specific (`~/.svcs/`)

## 🚧 Future Enhancements

- [ ] Cross-repository semantic search
- [ ] Repository health monitoring
- [ ] Bulk repository operations
- [ ] Export/import repository registry
- [ ] Integration with git hooks for auto-registration
- [ ] MCP server integration (when ready)

## 📄 Files Overview

- **`svcs_web_server_new.py`**: Main Flask web server
- **`svcs_web_repository_manager.py`**: Repository management logic
- **`svcs_registry_integration.py`**: CLI integration for registration
- **`test_new_architecture.py`**: Test suite
- **`WEB_MODERNIZATION_PLAN.md`**: Detailed implementation plan

## 🎉 Benefits

1. **Clean Architecture**: No legacy compatibility burden
2. **Scalable**: Handle unlimited repositories via registry
3. **Fast**: Direct access to repository-local databases  
4. **Simple**: Straightforward API design
5. **Maintainable**: Single source of truth for repository management

---

**Ready to use the new SVCS web architecture!** 🚀
