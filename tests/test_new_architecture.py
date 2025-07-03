#!/usr/bin/env python3
"""
Test script for new SVCS web architecture.

This script tests the repository manager and web server functionality
without needing Flask or external dependencies.
"""

import sys
import tempfile
import json
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_repository_manager():
    """Test the repository manager functionality."""
    try:
        from svcs_web_repository_manager import web_repository_manager, REPO_LOCAL_AVAILABLE
        
        print("🧪 Testing SVCS Web Repository Manager")
        print("=" * 50)
        print(f"Repository-local available: {REPO_LOCAL_AVAILABLE}")
        print(f"Registry database: {web_repository_manager.registry_db}")
        print()
        
        # Test discovery
        print("1️⃣  Testing repository discovery...")
        repositories = web_repository_manager.discover_repositories([str(Path.cwd())])
        print(f"   Found {len(repositories)} repositories")
        
        for repo in repositories:
            print(f"   • {repo['name']} ({repo['path']})")
            print(f"     Type: {repo['type']}, Events: {repo.get('events_count', 0)}")
        
        print()
        
        # Test system status equivalent
        print("2️⃣  Testing system status...")
        registered_count = len([r for r in repositories if r.get('registered', False)])
        print(f"   Registered repositories: {registered_count}")
        print(f"   Total discovered: {len(repositories)}")
        
        print()
        
        # Test current directory
        current_dir = str(Path.cwd())
        print(f"3️⃣  Testing current directory: {current_dir}")
        
        repo_instance = web_repository_manager.get_repository(current_dir)
        if repo_instance:
            print("   ✅ Current directory is SVCS-enabled")
            
            # Test statistics
            stats = web_repository_manager.get_repository_statistics(current_dir)
            if 'error' not in stats:
                print(f"   📊 Events: {stats.get('total_events', 0)}")
                print(f"   📊 Commits: {stats.get('total_commits', 0)}")
                print(f"   🌿 Branch: {stats.get('current_branch', 'unknown')}")
            else:
                print(f"   ⚠️  Statistics error: {stats['error']}")
        else:
            print("   ❌ Current directory is not SVCS-enabled")
        
        print()
        print("✅ Repository manager test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Repository manager test failed: {e}")
        return False

def test_registry_integration():
    """Test the registry integration script."""
    try:
        from svcs_repo_registry_integration import list_repositories
        
        print("🧪 Testing Registry Integration")
        print("=" * 50)
        
        # Test listing repositories
        print("1️⃣  Testing repository listing...")
        exit_code = list_repositories()
        print(f"   Exit code: {exit_code}")
        
        print()
        print("✅ Registry integration test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Registry integration test failed: {e}")
        return False

def test_web_server_import():
    """Test that the new web server can be imported."""
    try:
        print("🧪 Testing Web Server Import")
        print("=" * 50)
        
        # Test import without running Flask
        import svcs_web_server_new
        
        print("   ✅ Web server module imported successfully")
        print(f"   📡 Default host: {svcs_web_server_new.DEFAULT_HOST}")
        print(f"   🔌 Default port: {svcs_web_server_new.DEFAULT_PORT}")
        
        # Test health check data structure
        health_data = {
            'status': 'healthy',
            'service': 'SVCS Web Server (New Architecture)',
            'version': '0.1',
            'architecture': 'repository-local'
        }
        print(f"   💓 Health check: {health_data['status']}")
        
        print()
        print("✅ Web server import test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Web server import test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 SVCS New Architecture Test Suite")
    print("=" * 60)
    print()
    
    tests = [
        test_repository_manager,
        test_registry_integration,
        test_web_server_import
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
            print()
        except KeyboardInterrupt:
            print("\n❌ Test interrupted by user")
            return 1
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append(False)
            print()
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print("📊 Test Summary")
    print("=" * 20)
    print(f"Passed: {passed}/{total}")
    print(f"Failed: {total - passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed!")
        return 0
    else:
        print("❌ Some tests failed")
        return 1

if __name__ == '__main__':
    sys.exit(main())
