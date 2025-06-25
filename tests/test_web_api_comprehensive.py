#!/usr/bin/env python3
"""
SVCS Web API Comprehensive Test Script

Tests all endpoints in the SVCS web server to ensure they're working correctly.
This script can be used for:
- API validation
- Integration testing  
- Performance monitoring
- CI/CD pipeline verification
"""

import requests
import json
import time
import sys
import os
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

class SVCSWebAPITester:
    """Comprehensive tester for SVCS Web API endpoints."""
    
    def __init__(self, base_url: str = "http://127.0.0.1:8080"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({'Content-Type': 'application/json'})
        
        # Test data
        self.test_repo_path = "/tmp/api-test-repo"
        self.test_repo_name = "api-test-repo"
        
        # Results tracking
        self.results = {
            'total_tests': 0,
            'passed': 0,
            'failed': 0,
            'errors': [],
            'performance': {}
        }
        
    def log(self, message: str, level: str = "INFO"):
        """Log test message with timestamp."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
    
    def measure_performance(self, test_name: str, func, *args, **kwargs):
        """Measure and log performance of a test function."""
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            elapsed = time.time() - start_time
            self.results['performance'][test_name] = elapsed
            self.log(f"{test_name} completed in {elapsed:.2f}s")
            return result
        except Exception as e:
            elapsed = time.time() - start_time
            self.results['performance'][test_name] = elapsed
            self.log(f"{test_name} failed in {elapsed:.2f}s: {e}", "ERROR")
            raise
    
    def test_endpoint(self, test_name: str, method: str, endpoint: str, 
                     data: Dict = None, expected_status: int = 200) -> Dict[str, Any]:
        """Test a single endpoint and track results."""
        self.results['total_tests'] += 1
        
        try:
            url = f"{self.base_url}{endpoint}"
            self.log(f"Testing {test_name}: {method} {endpoint}")
            
            # Make request
            if method.upper() == 'GET':
                response = self.session.get(url, timeout=30)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=data, timeout=30)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            # Check status code
            if response.status_code != expected_status:
                raise Exception(f"Expected status {expected_status}, got {response.status_code}")
            
            # Parse response
            try:
                result = response.json()
            except json.JSONDecodeError:
                result = {'raw_response': response.text}
            
            self.results['passed'] += 1
            self.log(f"✅ {test_name} passed", "SUCCESS")
            return result
            
        except Exception as e:
            self.results['failed'] += 1
            error_msg = f"❌ {test_name} failed: {str(e)}"
            self.log(error_msg, "ERROR")
            self.results['errors'].append({'test': test_name, 'error': str(e)})
            return {'error': str(e)}
    
    def run_health_tests(self):
        """Test basic health and system endpoints."""
        self.log("=== HEALTH & SYSTEM TESTS ===")
        
        # Test health endpoint
        self.measure_performance("health_check", 
            self.test_endpoint, "Health Check", "GET", "/health")
        
        # Test system status
        self.measure_performance("system_status",
            self.test_endpoint, "System Status", "GET", "/api/system/status")
        
        # Test dashboard (should return HTML)
        try:
            self.log("Testing Dashboard: GET /")
            response = self.session.get(f"{self.base_url}/", timeout=10)
            if response.status_code == 200 and 'html' in response.headers.get('content-type', '').lower():
                self.results['passed'] += 1
                self.log("✅ Dashboard passed", "SUCCESS")
            else:
                self.results['failed'] += 1
                self.log(f"❌ Dashboard failed: Status {response.status_code}", "ERROR")
            self.results['total_tests'] += 1
        except Exception as e:
            self.results['failed'] += 1
            self.log(f"❌ Dashboard test error: {e}", "ERROR")
            self.results['total_tests'] += 1
        
        # Test favicon (should return 204)
        self.measure_performance("favicon",
            self.test_endpoint, "Favicon", "GET", "/favicon.ico", None, 204)
    
    def run_repository_discovery_tests(self):
        """Test repository discovery endpoints."""
        self.log("=== REPOSITORY DISCOVERY TESTS ===")
        
        # Test GET discovery
        result = self.measure_performance("discover_get",
            self.test_endpoint, "Discover Repositories (GET)", "GET", "/api/repositories/discover")
        
        # Test POST discovery
        self.measure_performance("discover_post",
            self.test_endpoint, "Discover Repositories (POST)", "POST", "/api/repositories/discover", {})
        
        # Test POST discovery with scan paths
        self.measure_performance("discover_post_paths",
            self.test_endpoint, "Discover with Scan Paths", "POST", "/api/repositories/discover", 
            {"scan_paths": ["/tmp"]})
        
        return result.get('data', {}).get('repositories', [])
    
    def run_repository_management_tests(self):
        """Test repository initialization, registration, and management."""
        self.log("=== REPOSITORY MANAGEMENT TESTS ===")
        
        # Test initialization (creates directory, git repo, and SVCS)
        self.measure_performance("initialize_repo",
            self.test_endpoint, "Initialize Repository", "POST", "/api/repositories/initialize",
            {"path": self.test_repo_path})
        
        # Test repository status
        self.measure_performance("repo_status",
            self.test_endpoint, "Repository Status", "POST", "/api/repositories/status",
            {"path": self.test_repo_path})
        
        # Test repository statistics
        self.measure_performance("repo_statistics",
            self.test_endpoint, "Repository Statistics", "POST", "/api/repositories/statistics",
            {"path": self.test_repo_path})
        
        # Test manual registration (should already be registered from init)
        self.measure_performance("register_repo",
            self.test_endpoint, "Register Repository", "POST", "/api/repositories/register",
            {"path": self.test_repo_path, "name": self.test_repo_name})
    
    def run_semantic_analysis_tests(self):
        """Test semantic analysis endpoints."""
        self.log("=== SEMANTIC ANALYSIS TESTS ===")
        
        # Test search events
        self.measure_performance("search_events",
            self.test_endpoint, "Search Events", "POST", "/api/semantic/search_events",
            {"repository_path": self.test_repo_path, "limit": 10})
        
        # Test advanced search with filters
        self.measure_performance("search_advanced",
            self.test_endpoint, "Advanced Search", "POST", "/api/semantic/search_advanced",
            {
                "repository_path": self.test_repo_path,
                "limit": 10,
                "min_confidence": 0.5,
                "event_types": ["function_added"],
                "order_desc": True
            })
        
        # Test advanced search with date filter
        self.measure_performance("search_advanced_date",
            self.test_endpoint, "Advanced Search with Date", "POST", "/api/semantic/search_advanced",
            {
                "repository_path": self.test_repo_path,
                "limit": 5,
                "since_date": "1 day ago",
                "location_pattern": "*.py"
            })
        
        # Test pattern search
        self.measure_performance("search_patterns",
            self.test_endpoint, "Pattern Search", "POST", "/api/semantic/search_patterns",
            {
                "repository_path": self.test_repo_path,
                "pattern_type": "performance",
                "min_confidence": 0.7,
                "limit": 5
            })
        
        # Test recent activity
        self.measure_performance("recent_activity",
            self.test_endpoint, "Recent Activity", "POST", "/api/semantic/recent_activity",
            {"repository_path": self.test_repo_path, "days": 7})
        
        # Test evolution tracking
        self.measure_performance("evolution_tracking",
            self.test_endpoint, "Evolution Tracking", "POST", "/api/semantic/evolution",
            {"repository_path": self.test_repo_path, "node_id": "test_function"})
        
        # Test commit summary (should work since we created a commit)
        self.measure_performance("commit_summary",
            self.test_endpoint, "Commit Summary", "POST", "/api/semantic/commit_summary",
            {"repository_path": self.test_repo_path, "commit_hash": "5382857"}, 200)
    
    def run_analytics_tests(self):
        """Test analytics and quality analysis endpoints."""
        self.log("=== ANALYTICS & QUALITY TESTS ===")
        
        # Test analytics generation
        self.measure_performance("generate_analytics",
            self.test_endpoint, "Generate Analytics", "POST", "/api/analytics/generate",
            {"repository_path": self.test_repo_path})
        
        # Test quality analysis
        self.measure_performance("quality_analysis",
            self.test_endpoint, "Quality Analysis", "POST", "/api/quality/analyze",
            {"repository_path": self.test_repo_path})
    
    def run_branch_comparison_tests(self):
        """Test branch comparison endpoints."""
        self.log("=== BRANCH COMPARISON TESTS ===")
        
        # Test branch comparison
        self.measure_performance("branch_comparison",
            self.test_endpoint, "Branch Comparison", "POST", "/api/compare/branches",
            {
                "repository_path": self.test_repo_path,
                "branch1": "main",
                "branch2": "main",  # Compare main with itself for testing
                "limit": 5
            })
    
    def run_cleanup_tests(self):
        """Test repository cleanup operations."""
        self.log("=== CLEANUP TESTS ===")
        
        # Test unregistration
        self.measure_performance("unregister_repo",
            self.test_endpoint, "Unregister Repository", "POST", "/api/repositories/unregister",
            {"path": self.test_repo_path})
    
    def run_error_handling_tests(self):
        """Test error handling with invalid requests."""
        self.log("=== ERROR HANDLING TESTS ===")
        
        # Test with non-existent repository
        self.measure_performance("invalid_repo_status",
            self.test_endpoint, "Invalid Repository Status", "POST", "/api/repositories/status",
            {"path": "/nonexistent/path"}, 404)
        
        # Test with missing required parameters
        self.measure_performance("missing_params",
            self.test_endpoint, "Missing Parameters", "POST", "/api/repositories/register",
            {}, 400)
        
        # Test advanced search with missing repository path
        self.measure_performance("advanced_search_missing_repo",
            self.test_endpoint, "Advanced Search Missing Repo", "POST", "/api/semantic/search_advanced",
            {"limit": 5}, 400)
        
        # Test pattern search with missing pattern type
        self.measure_performance("pattern_search_missing_type",
            self.test_endpoint, "Pattern Search Missing Type", "POST", "/api/semantic/search_patterns",
            {"repository_path": self.test_repo_path}, 400)
        
        # Test with invalid JSON
        try:
            url = f"{self.base_url}/api/repositories/register"
            response = self.session.post(url, data="invalid json", timeout=10)
            if response.status_code == 400:
                self.results['passed'] += 1
                self.log("✅ Invalid JSON handling passed", "SUCCESS")
            else:
                self.results['failed'] += 1
                self.log("❌ Invalid JSON handling failed", "ERROR")
        except Exception as e:
            self.results['failed'] += 1
            self.log(f"❌ Invalid JSON test error: {e}", "ERROR")
        
        self.results['total_tests'] += 1
    
    def create_test_data(self):
        """Create some test data for more comprehensive testing."""
        self.log("=== CREATING TEST DATA ===")
        
        # Create a test file to generate some semantic events
        test_file = Path(self.test_repo_path) / "test.py"
        test_content = '''
def hello_world():
    """A simple test function."""
    return "Hello, World!"

class TestClass:
    def __init__(self):
        self.value = 42
    
    def get_value(self):
        return self.value
'''
        
        try:
            test_file.write_text(test_content)
            
            # Add and commit the file to generate git history
            import subprocess
            subprocess.run(['git', 'add', 'test.py'], cwd=self.test_repo_path, check=True)
            subprocess.run(['git', 'commit', '-m', 'Add test file'], cwd=self.test_repo_path, check=True)
            
            self.log("✅ Test data created successfully")
        except Exception as e:
            self.log(f"⚠️ Failed to create test data: {e}", "WARNING")
    
    def cleanup_test_data(self):
        """Clean up test data after testing."""
        self.log("=== CLEANING UP TEST DATA ===")
        
        try:
            import shutil
            if Path(self.test_repo_path).exists():
                shutil.rmtree(self.test_repo_path)
                self.log("✅ Test repository cleaned up")
        except Exception as e:
            self.log(f"⚠️ Failed to cleanup test data: {e}", "WARNING")
    
    def run_all_tests(self, cleanup: bool = True):
        """Run all API tests."""
        self.log("🚀 Starting SVCS Web API Comprehensive Tests")
        self.log(f"📡 Base URL: {self.base_url}")
        
        start_time = time.time()
        
        try:
            # Basic health tests
            self.run_health_tests()
            
            # Repository discovery
            repositories = self.run_repository_discovery_tests()
            
            # Repository management
            self.run_repository_management_tests()
            
            # Create test data for better testing
            self.create_test_data()
            
            # Semantic analysis
            self.run_semantic_analysis_tests()
            
            # Analytics and quality
            self.run_analytics_tests()
            
            # Branch comparison
            self.run_branch_comparison_tests()
            
            # CI/CD integration tests
            self.run_ci_tests()
            
            # Natural language query tests  
            self.run_query_tests()
            
            # Git notes tests
            self.run_notes_tests()
            
            # Enhanced cleanup tests
            self.run_enhanced_cleanup_tests()
            
            # Error handling
            self.run_error_handling_tests()
            
            # Cleanup
            if cleanup:
                self.run_cleanup_tests()
                self.cleanup_test_data()
            
        except KeyboardInterrupt:
            self.log("🛑 Tests interrupted by user")
        except Exception as e:
            self.log(f"💥 Unexpected error during testing: {e}", "ERROR")
        
        # Generate report
        total_time = time.time() - start_time
        self.generate_report(total_time)
    
    def generate_report(self, total_time: float):
        """Generate comprehensive test report."""
        self.log("=" * 60)
        self.log("📊 TEST RESULTS SUMMARY")
        self.log("=" * 60)
        
        # Basic stats
        self.log(f"📈 Total Tests: {self.results['total_tests']}")
        self.log(f"✅ Passed: {self.results['passed']}")
        self.log(f"❌ Failed: {self.results['failed']}")
        self.log(f"⏱️  Total Time: {total_time:.2f}s")
        
        # Success rate
        if self.results['total_tests'] > 0:
            success_rate = (self.results['passed'] / self.results['total_tests']) * 100
            self.log(f"📊 Success Rate: {success_rate:.1f}%")
        
        # Performance summary
        if self.results['performance']:
            self.log("\n🏃 PERFORMANCE SUMMARY:")
            sorted_perf = sorted(self.results['performance'].items(), key=lambda x: x[1], reverse=True)
            for test_name, duration in sorted_perf[:5]:
                self.log(f"  {test_name}: {duration:.2f}s")
        
        # Errors
        if self.results['errors']:
            self.log("\n💥 ERRORS:")
            for error in self.results['errors']:
                self.log(f"  {error['test']}: {error['error']}")
        
        # Overall status
        if self.results['failed'] == 0:
            self.log("\n🎉 ALL TESTS PASSED!")
        else:
            self.log(f"\n⚠️  {self.results['failed']} TESTS FAILED")
        
        # Save detailed report
        self.save_detailed_report(total_time)
    
    def save_detailed_report(self, total_time: float):
        """Save detailed test report to file."""
        report_file = Path(__file__).parent / f"api_test_report_{int(time.time())}.json"
        
        detailed_report = {
            'timestamp': datetime.now().isoformat(),
            'base_url': self.base_url,
            'total_time': total_time,
            'results': self.results,
            'environment': {
                'python_version': sys.version,
                'working_directory': os.getcwd()
            }
        }
        
        try:
            with open(report_file, 'w') as f:
                json.dump(detailed_report, f, indent=2)
            self.log(f"📄 Detailed report saved: {report_file}")
        except Exception as e:
            self.log(f"⚠️ Failed to save report: {e}", "WARNING")

    def run_ci_tests(self):
        """Test CI/CD integration endpoints."""
        self.log("=== CI/CD INTEGRATION TESTS ===")
        
        # Test PR analysis
        self.measure_performance("pr_analysis",
            self.test_endpoint, "PR Analysis (Repository-Local)", "POST", "/api/ci/pr_analysis",
            {
                "repository_path": "/Users/markomanninen/Documents/GitHub/svcs",
                "target_branch": "main"
            })
        
        # Test quality gate
        self.measure_performance("quality_gate",
            self.test_endpoint, "Quality Gate (Repository-Local)", "POST", "/api/ci/quality_gate",
            {
                "repository_path": "/Users/markomanninen/Documents/GitHub/svcs",
                "strict": False
            })
    
    def run_query_tests(self):
        """Test natural language query endpoints."""
        self.log("=== NATURAL LANGUAGE QUERY TESTS ===")
        
        # Test natural language query
        self.measure_performance("natural_query",
            self.test_endpoint, "Natural Language Query", "POST", "/api/query/natural_language",
            {
                "repository_path": "/Users/markomanninen/Documents/GitHub/svcs",
                "query": "show recent changes"
            })
    
    def run_notes_tests(self):
        """Test git notes management endpoints.""" 
        self.log("=== GIT NOTES TESTS ===")
        
        # Test notes sync
        self.measure_performance("notes_sync",
            self.test_endpoint, "Notes Sync", "POST", "/api/notes/sync",
            {"repository_path": "/Users/markomanninen/Documents/GitHub/svcs"})
        
        # Test notes fetch
        self.measure_performance("notes_fetch",
            self.test_endpoint, "Notes Fetch", "POST", "/api/notes/fetch",
            {"repository_path": "/Users/markomanninen/Documents/GitHub/svcs"})
        
        # Test show note
        self.measure_performance("notes_show",
            self.test_endpoint, "Show Note", "POST", "/api/notes/show",
            {
                "repository_path": "/Users/markomanninen/Documents/GitHub/svcs",
                "commit_hash": "HEAD"
            })
    
    def run_enhanced_cleanup_tests(self):
        """Test enhanced repository cleanup endpoints."""
        self.log("=== ENHANCED CLEANUP TESTS ===")
        
        # Test database stats
        self.measure_performance("database_stats",
            self.test_endpoint, "Database Stats", "POST", "/api/cleanup/database_stats",
            {"repository_path": "/Users/markomanninen/Documents/GitHub/svcs"})
        
        # Test orphaned data cleanup
        self.measure_performance("orphaned_cleanup",
            self.test_endpoint, "Orphaned Data Cleanup", "POST", "/api/cleanup/orphaned_data",
            {"repository_path": "/Users/markomanninen/Documents/GitHub/svcs"})
        
        # Test unreachable commits cleanup
        self.measure_performance("unreachable_cleanup", 
            self.test_endpoint, "Unreachable Commits Cleanup", "POST", "/api/cleanup/unreachable_commits",
            {"repository_path": "/Users/markomanninen/Documents/GitHub/svcs"})


def main():
    """Main entry point for the test script."""
    import argparse
    
    parser = argparse.ArgumentParser(description='SVCS Web API Comprehensive Tester')
    parser.add_argument('--url', default='http://127.0.0.1:8080',
                       help='Base URL of SVCS web server (default: http://127.0.0.1:8080)')
    parser.add_argument('--no-cleanup', action='store_true',
                       help='Skip cleanup of test data')
    parser.add_argument('--test-repo', default='/tmp/api-test-repo',
                       help='Path for test repository (default: /tmp/api-test-repo)')
    
    args = parser.parse_args()
    
    # Create tester instance
    tester = SVCSWebAPITester(args.url)
    tester.test_repo_path = args.test_repo
    tester.test_repo_name = Path(args.test_repo).name
    
    # Run tests
    tester.run_all_tests(cleanup=not args.no_cleanup)
    
    # Exit with appropriate code
    if tester.results['failed'] > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()
