# SVCS Web API Comprehensive Test Script

## Overview

`test_web_api_comprehensive.py` is a comprehensive test script that validates all endpoints in the SVCS Web API. It provides automated testing for:

- ✅ **Health & System Endpoints** - Health checks and system status
- ✅ **Repository Discovery** - Finding and listing SVCS repositories  
- ✅ **Repository Management** - Initialize, register, unregister repositories
- ✅ **Semantic Analysis** - Search events, recent activity, evolution tracking
- ✅ **Analytics & Quality** - Generate analytics and quality reports
- ✅ **Branch Comparison** - Compare branches and analyze differences
- ✅ **Error Handling** - Validate proper error responses

## Features

### Comprehensive Coverage
- **22 Different Tests** covering all API endpoints
- **Performance Monitoring** with timing for each test
- **Error Handling Validation** with invalid inputs
- **Test Data Creation** with real repositories and commits

### Smart Testing
- **Auto-cleanup** of test data (optional)
- **Configurable test repositories** and server URLs
- **Detailed reporting** with JSON output
- **Real-time logging** with timestamps

### Performance Tracking
- Individual test timing
- Overall execution time
- Performance summary with slowest tests
- Success rate calculation

## Usage

### Basic Usage
```bash
# Test default server (http://127.0.0.1:8080)
python3 test_web_api_comprehensive.py

# Test custom server
python3 test_web_api_comprehensive.py --url http://localhost:3000

# Skip cleanup (leave test data)
python3 test_web_api_comprehensive.py --no-cleanup

# Custom test repository path
python3 test_web_api_comprehensive.py --test-repo /tmp/my-test-repo
```

### Advanced Usage
```bash
# Full customization
python3 test_web_api_comprehensive.py \
  --url http://production-server:8080 \
  --test-repo /tmp/production-test \
  --no-cleanup
```

## Test Results

### Latest Run (2025-06-25)
```
📊 TEST RESULTS SUMMARY
📈 Total Tests: 22
✅ Passed: 22  
❌ Failed: 0
⏱️  Total Time: 2.09s
📊 Success Rate: 100.0%

🏃 PERFORMANCE SUMMARY:
  discover_post_paths: 0.88s
  system_status: 0.26s
  repo_status: 0.22s
  discover_post: 0.21s
  discover_get: 0.17s
```

### Endpoints Tested

#### Health & System (4 tests)
- `GET /health` - Health check
- `GET /api/system/status` - System information  
- `GET /` - Dashboard HTML
- `GET /favicon.ico` - Favicon handling

#### Repository Discovery (3 tests)  
- `GET /api/repositories/discover` - Discover repositories
- `POST /api/repositories/discover` - Discover with filters
- `POST /api/repositories/discover` - Discover with scan paths

#### Repository Management (4 tests)
- `POST /api/repositories/initialize` - Initialize new repository
- `POST /api/repositories/status` - Get repository status
- `POST /api/repositories/statistics` - Get repository statistics  
- `POST /api/repositories/register` - Register repository

#### Semantic Analysis (4 tests)
- `POST /api/semantic/search_events` - Search semantic events
- `POST /api/semantic/recent_activity` - Get recent activity
- `POST /api/semantic/evolution` - Track code evolution
- `POST /api/semantic/commit_summary` - Analyze commits

#### Analytics & Quality (2 tests)
- `POST /api/analytics/generate` - Generate analytics
- `POST /api/quality/analyze` - Quality analysis

#### Branch Comparison (1 test)
- `POST /api/compare/branches` - Compare branches

#### Error Handling (3 tests)
- Invalid repository paths (404 errors)
- Missing required parameters (400 errors) 
- Invalid JSON handling

#### Cleanup (1 test)
- `POST /api/repositories/unregister` - Unregister repository

## Output Files

### Detailed JSON Report
Each test run generates a detailed JSON report:
```json
{
  "timestamp": "2025-06-25T07:28:25.041494",
  "base_url": "http://127.0.0.1:8080", 
  "total_time": 2.09,
  "results": {
    "total_tests": 22,
    "passed": 22,
    "failed": 0,
    "performance": { ... }
  }
}
```

### Console Output
Real-time colored output with:
- ✅ Success indicators
- ❌ Failure indicators  
- ⏱️ Performance timings
- 📊 Final summary

## Integration

### CI/CD Pipeline
```yaml
# Example GitHub Actions
- name: Test SVCS API
  run: |
    python3 svcs_repo_web_server.py &
    sleep 5
    python3 test_web_api_comprehensive.py
    kill %1
```

### Development Workflow
```bash
# Start server
python3 svcs_repo_web_server.py &

# Run tests
python3 test_web_api_comprehensive.py

# Check results
echo "Exit code: $?"
```

## Requirements

- **Python 3.7+** with `requests` library
- **SVCS Web Server** running and accessible
- **Git** available in PATH for test data creation
- **Write access** to test directory (default: `/tmp`)

## Error Handling

The script handles various error conditions:
- **Server unavailable** - Connection errors
- **Invalid responses** - JSON parsing errors  
- **Permission errors** - File system access issues
- **Network timeouts** - Request timeout handling

Exit codes:
- `0` - All tests passed
- `1` - One or more tests failed

This comprehensive test script ensures the SVCS Web API is functioning correctly across all endpoints and use cases.
