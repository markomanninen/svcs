# AI Agent Instructions for SVCS Interactive Dashboard

## Overview
This document provides instructions for AI agents working with the SVCS Interactive Dashboard system. The dashboard is a web-based interface for exploring semantic code analysis data.

## Key Files and Components

### Core Dashboard Files
- `svcs_interactive_dashboard.html` - Frontend web interface
- `svcs_web_server.py` - Flask backend server
- `start_dashboard.sh` - Setup and launch script
- `demo_dashboard.py` - Interactive demo with guided tour

### API Integration
- Backend imports functions from `.svcs/api.py`
- All API functions work without `project_path` parameter
- Database queries operate on current working directory

### Fixed API Function Signatures

**Important**: The SVCS API functions do NOT take a `project_path` parameter. Use these correct signatures:

```python
# Semantic Search
search_events_advanced(author=None, event_types=None, layers=None, 
                      min_confidence=None, since_date=None, limit=20)

search_semantic_patterns(pattern_type=None, min_confidence=0.7, 
                        author=None, since_date=None, limit=15)

get_recent_activity(days=7, layers=None, event_types=None, 
                   author=None, limit=20)

# Evolution Tracking  
get_node_evolution(node_id)
get_filtered_evolution(node_id, event_types=None, since_date=None, 
                      until_date=None, min_confidence=None)

# Project Statistics
get_project_statistics(since_date=None, until_date=None, 
                      group_by="event_type")

# Git Integration (these DO work correctly)
get_commit_changed_files(commit_hash)
get_commit_diff(commit_hash, file_path=None)
get_commit_summary(commit_hash)

# Debugging
debug_query_tools(query_description="unspecified query")
```

## Common Issues and Solutions

### 500 API Errors
**Problem**: Flask endpoints returning 500 errors
**Cause**: Incorrect function parameter usage
**Solution**: Ensure API functions are called with correct parameters (no project_path)

### Import Errors
**Problem**: Cannot import flask or api modules
**Cause**: Missing dependencies or wrong working directory
**Solution**: 
```bash
cd /path/to/svcs
source .svcs/venv/bin/activate
pip install Flask Flask-CORS
```

### Database Errors  
**Problem**: No data returned from API calls
**Cause**: SVCS not initialized or no semantic analysis performed
**Solution**: Ensure SVCS has analyzed commits in the current repository

## Troubleshooting Steps

1. **Check Working Directory**: Must be in SVCS root directory
2. **Verify Dependencies**: Flask and Flask-CORS must be installed
3. **Check Database**: Ensure `.svcs/` directory exists with database
4. **Test API Functions**: Test individual functions in Python before web server
5. **Check Logs**: Use browser developer tools and server output

## Development Guidelines

### Adding New Endpoints
```python
@app.route('/api/new_endpoint', methods=['POST'])
def api_new_endpoint():
    try:
        data = request.get_json() or {}
        # Extract parameters
        result = svcs_api_function(correct_parameters)
        return jsonify({'success': True, 'data': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
```

### Frontend API Calls
```javascript
async function callSVCSAPI(endpoint, params = {}) {
    const response = await fetch(`/api/${endpoint}`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(params)
    });
    const result = await response.json();
    if (!result.success) throw new Error(result.error);
    return result.data;
}
```

## Testing and Validation

### Quick API Test
```python
# Test problematic API functions directly
import sys
sys.path.insert(0, '.svcs')
from api import search_semantic_patterns, debug_query_tools

# Test with correct parameters
result = search_semantic_patterns(pattern_type='performance')
debug_info = debug_query_tools('test query')
```

### Server Health Check
```bash
curl http://127.0.0.1:8080/health
```

### Dashboard Functionality Test
1. Start server: `./start_dashboard.sh`
2. Open: `http://127.0.0.1:8080`
3. Test each section for API errors
4. Check browser console for JavaScript errors

## Architecture Notes

### Data Flow
1. Frontend sends POST requests to `/api/*` endpoints
2. Flask server processes parameters and calls SVCS API functions
3. SVCS functions query SQLite database in current directory
4. Results returned as JSON to frontend
5. Frontend displays formatted results

### Security
- Server runs on localhost only (127.0.0.1)
- CORS enabled for development
- All data stays local (no external API calls)

### Performance
- Database queries are optimized with indexes
- Pagination supported in most endpoints
- Results limited by default to prevent overload

## Future Enhancements

When modifying the dashboard:
1. Always test API functions directly before adding endpoints
2. Use consistent error handling patterns
3. Validate input parameters on both frontend and backend
4. Update documentation for new features
5. Test with real SVCS data, not just mock responses

## Support

If issues arise:
1. Check server logs for error details
2. Test API functions in isolation
3. Verify working directory and dependencies
4. Use debug tools in Project Management section
5. Check browser developer console for frontend errors
