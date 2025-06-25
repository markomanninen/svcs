# SVCS Web API Feature Coverage

## Overview

The SVCS web server (`svcs_repo_web_server.py`) now provides comprehensive API coverage for most CLI features, making it a complete alternative for web-based interactions.

## How to Access

### Via CLI
```bash
# Start the web server
svcs web start

# With custom host/port
svcs web start --host 0.0.0.0 --port 9000

# In debug mode
svcs web start --debug

# In background
svcs web start --background
```

### Direct Access
```bash
# Run the web server directly
python svcs_repo_web_server.py

# With options
python svcs_repo_web_server.py --port 9000 --host 0.0.0.0 --debug
```

## API Endpoints vs CLI Features

| CLI Command | API Endpoint | Status | Description |
|-------------|--------------|--------|-------------|
| `svcs init` | `POST /api/repositories/initialize` | ✅ Complete | Initialize SVCS in repository |
| `svcs status` | `POST /api/repositories/status` | ✅ Complete | Get detailed repository status |
| `svcs events` | `POST /api/semantic/search_events` | ✅ Complete | List and filter semantic events |
| `svcs search` | `POST /api/semantic/search_events` | ✅ Complete | Advanced semantic search |
| `svcs evolution` | `POST /api/semantic/evolution` | ✅ Complete | Track function/class evolution |
| `svcs analytics` | `POST /api/analytics/generate` | ✅ Complete | Generate analytics reports |
| `svcs quality` | `POST /api/quality/analyze` | ✅ Complete | Quality analysis and metrics |
| `svcs compare` | `POST /api/compare/branches` | ✅ Complete | Compare branches semantically |
| `svcs web` | Built-in web server | ✅ Complete | Interactive web dashboard |
| `svcs dashboard` | `GET /` | ✅ Complete | Static dashboard generation |
| `svcs ci` | `POST /api/ci/*` | 🚧 Partial | CI/CD integration endpoints |
| `svcs discuss` | `POST /api/query/natural` | 🚧 Partial | Conversational interface |
| `svcs query` | `POST /api/query/natural` | 🚧 Partial | Natural language queries |
| `svcs notes` | `POST /api/notes/*` | 🚧 Partial | Git notes management |
| `svcs cleanup` | `POST /api/cleanup/repository` | 🚧 Partial | Repository maintenance |

## Core Repository Management

### Discovery and Registration
- `GET /api/repositories/discover` - Find SVCS repositories
- `POST /api/repositories/register` - Register repository in central registry
- `POST /api/repositories/unregister` - Remove from central registry
- `POST /api/repositories/initialize` - Initialize SVCS for new repository
- `POST /api/repositories/status` - Get detailed status information
- `POST /api/repositories/statistics` - Get repository statistics

### Semantic Analysis
- `POST /api/semantic/search_events` - Search and filter semantic events
- `POST /api/semantic/recent_activity` - Get recent activity summary
- `POST /api/semantic/commit_summary` - Get commit-specific semantic events
- `POST /api/semantic/evolution` - Track evolution of specific code elements

### Analytics and Quality
- `POST /api/analytics/generate` - Generate comprehensive analytics reports
- `POST /api/quality/analyze` - Perform quality analysis with metrics
- `POST /api/compare/branches` - Compare semantic patterns between branches

### System Information
- `GET /health` - Health check and basic server info
- `GET /api/system/status` - System status and capabilities
- `GET /` - Interactive dashboard

## Example API Usage

### Get Repository Status
```bash
curl -X POST http://localhost:8080/api/repositories/status \
  -H "Content-Type: application/json" \
  -d '{"repository_path": "/path/to/repo"}'
```

### Search Events
```bash
curl -X POST http://localhost:8080/api/semantic/search_events \
  -H "Content-Type: application/json" \
  -d '{"repository_path": "/path/to/repo", "limit": 50, "event_type": "function_created"}'
```

### Generate Analytics
```bash
curl -X POST http://localhost:8080/api/analytics/generate \
  -H "Content-Type: application/json" \
  -d '{"repository_path": "/path/to/repo"}'
```

### Track Evolution
```bash
curl -X POST http://localhost:8080/api/semantic/evolution \
  -H "Content-Type: application/json" \
  -d '{"repository_path": "/path/to/repo", "node_id": "func:process_data"}'
```

## Architecture Benefits

### Repository-Local Design
- **No Global State**: Each repository maintains its own `.svcs/semantic.db`
- **Central Registry**: `~/.svcs/repos.db` tracks available repositories
- **Scalable**: Can manage multiple repositories simultaneously
- **Isolated**: Repository data is completely separate

### Modern Web Stack
- **Flask-based**: Lightweight, fast web server
- **RESTful APIs**: Clean, standard HTTP endpoints
- **JSON Responses**: Machine-readable data format
- **CORS Enabled**: Frontend-friendly for web applications

### Easy Integration
- **CLI Integration**: `svcs web start` launches the server
- **Standalone**: Can run independently with `python svcs_repo_web_server.py`
- **Development Mode**: Supports debug mode for development
- **Background Mode**: Can run as a service

## Feature Completeness

### ✅ Fully Implemented
- Repository management (init, status, discover, register)
- Semantic analysis (events, search, evolution)
- Analytics and quality analysis
- Branch comparison
- System status and health checks

### 🚧 Partially Implemented
- CI/CD integration endpoints (basic structure ready)
- Natural language query processing
- Git notes management
- Repository cleanup operations

### 🎯 Implementation Notes
The web API now covers ~80% of CLI functionality with the core features fully implemented. The remaining features (CI/CD, natural language queries, notes, cleanup) have endpoint stubs and can be easily expanded based on specific needs.

## Usage Recommendations

1. **Development**: Use `svcs web start --debug` for local development
2. **Production**: Use `svcs web start --host 0.0.0.0 --port 8080` for team access
3. **Integration**: Use the REST APIs for custom tooling and dashboards
4. **Monitoring**: Use `/health` and `/api/system/status` for monitoring

The web server now provides a comprehensive alternative to CLI usage while maintaining the same repository-local architecture and data isolation principles.
