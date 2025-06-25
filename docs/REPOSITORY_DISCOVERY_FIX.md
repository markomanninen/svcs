# SVCS Repository Discovery Fix

## Issue Resolved ✅
**400 Bad Request Error**: Dashboard UI failing to discover repositories due to GET request handling

## Root Cause
The `/api/repositories/discover` endpoint had flawed logic for handling GET requests:
- Dashboard UI calls `discoverRepositories()` without data, triggering GET request
- Server endpoint incorrectly tried to process GET requests as if they had JSON bodies
- This caused "400 Bad Request: The browser (or proxy) sent a request that this server could not understand"

## Solution Applied

### 1. Enhanced Request Method Handling
```python
# Before: Problematic logic
data = request.get_json() if request.is_json else {}
scan_paths = data.get('scan_paths') if data else None

# After: Method-specific handling  
if request.method == 'POST' and request.is_json:
    data = request.get_json() or {}
    scan_paths = data.get('scan_paths')
elif request.method == 'GET':
    scan_paths_param = request.args.get('scan_paths')
    if scan_paths_param:
        scan_paths = scan_paths_param.split(',')
```

### 2. Better Error Handling
- Added proper logging for debugging: `app.logger.error(f"Error in discover_repositories: {e}")`
- More robust handling of edge cases

### 3. Backward Compatibility
- GET requests: Support optional query parameters for scan paths
- POST requests: Continue to work with JSON body containing scan paths
- Both methods now work seamlessly

## Test Results ✅

### Before Fix
```
❌ GET /api/repositories/discover: 400 Bad Request
❌ Dashboard fails to load repositories  
❌ "Failed to discover repositories: 400 Bad Request"
```

### After Fix
```
✅ GET /api/repositories/discover: Success (< 2s)
✅ POST /api/repositories/discover: Success (< 2s)
✅ Dashboard automatically loads repositories
✅ All API integration tests pass
```

## Files Modified
- `svcs_repo_web_server.py`: Enhanced discover endpoint request handling
- `svcs_web_repository_manager.py`: Enhanced initialize_repository to create directories and git repos
- `PERFORMANCE_OPTIMIZATIONS.md`: Updated with fix documentation

## Recent Enhancement - Repository Initialization

### Improvement
The `initialize_repository` method now automatically:
1. **Creates directories**: If the target path doesn't exist, it creates the directory structure
2. **Initializes Git**: If not already a git repository, runs `git init`
3. **Initializes SVCS**: Sets up `.svcs/semantic.db` for semantic tracking
4. **Auto-registers**: Adds the repository to the central registry

### Usage
```bash
# Initialize SVCS in a non-existent directory
curl -X POST "http://localhost:8080/api/repositories/initialize" \
  -H "Content-Type: application/json" \
  -d '{"path": "/tmp/my-new-project"}'
```

### Before vs After
```bash
# Before: Required manual setup
mkdir /tmp/my-project
cd /tmp/my-project
git init
# Then call initialize API

# After: One-step initialization
curl -X POST ".../initialize" -d '{"path": "/tmp/my-project"}'
```

## Impact
- **Dashboard UI**: Now works seamlessly on first load
- **API Robustness**: Better handling of different request methods
- **User Experience**: No more mysterious 400 errors
- **Development**: Improved debugging with better error logging

The repository discovery feature now works reliably for both programmatic API calls and interactive dashboard usage.
