#!/usr/bin/env python3
"""
SVCS CLI Test Suite
Comprehensive testing of all unified CLI commands

This script validates that all commands are properly implemented
and provides basic functionality testing.
"""

import subprocess
import sys
import os
from pathlib import Path
import tempfile
import json


class SVCSCLITester:
    """Test harness for SVCS CLI commands."""
    
    def __init__(self):
        self.test_results = []
        self.passed = 0
        self.failed = 0
        
    def run_command(self, cmd, expect_success=True, cwd=None):
        """Run a command and capture output."""
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                cwd=cwd,
                timeout=30
            )
            
            success = (result.returncode == 0) if expect_success else (result.returncode != 0)
            
            return {
                'success': success,
                'returncode': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'command': cmd
            }
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'returncode': -1,
                'stdout': '',
                'stderr': 'Command timed out',
                'command': cmd
            }
        except Exception as e:
            return {
                'success': False,
                'returncode': -1,
                'stdout': '',
                'stderr': str(e),
                'command': cmd
            }
    
    def test_command(self, name, cmd, expect_success=True, cwd=None):
        """Test a single command and record results."""
        print(f"🧪 Testing: {name}")
        print(f"   Command: {cmd}")
        
        result = self.run_command(cmd, expect_success, cwd)
        
        if result['success']:
            print(f"   ✅ PASSED")
            self.passed += 1
        else:
            print(f"   ❌ FAILED")
            print(f"   Return code: {result['returncode']}")
            if result['stderr']:
                print(f"   Error: {result['stderr'][:200]}...")
            self.failed += 1
        
        self.test_results.append({
            'name': name,
            'result': result,
            'status': 'PASSED' if result['success'] else 'FAILED'
        })
        print()
    
    def run_basic_cli_tests(self):
        """Run basic CLI functionality tests."""
        print("=" * 60)
        print("🚀 SVCS CLI Test Suite")
        print("=" * 60)
        print()
        
        # Test help command
        self.test_command(
            "Help Command",
            "python3 svcs/cli.py --help",
            expect_success=True
        )
        
        # Test command listing
        self.test_command(
            "Command Listing", 
            "python3 svcs/cli.py",
            expect_success=True
        )
        
        # Test individual command help
        commands = [
            'init', 'status', 'events', 'search', 'evolution', 
            'analytics', 'quality', 'dashboard', 'web', 'ci',
            'discuss', 'query', 'notes', 'compare', 'cleanup'
        ]
        
        for cmd in commands:
            self.test_command(
                f"{cmd.title()} Help",
                f"python3 svcs/cli.py {cmd} --help",
                expect_success=True
            )
    
    def run_repository_tests(self):
        """Run tests that require a git repository."""
        print("🔧 Repository-based Tests")
        print("-" * 40)
        
        # Create temporary git repository
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir) / "test_repo"
            repo_path.mkdir()
            
            # Initialize git repository
            self.run_command("git init", cwd=repo_path)
            self.run_command("git config user.name 'Test User'", cwd=repo_path)
            self.run_command("git config user.email 'test@example.com'", cwd=repo_path)
            
            # Create a test file
            (repo_path / "test.py").write_text("""
def hello_world():
    print("Hello, World!")
    
if __name__ == "__main__":
    hello_world()
""")
            
            self.run_command("git add test.py", cwd=repo_path)
            self.run_command("git commit -m 'Initial commit'", cwd=repo_path)
            
            # Test SVCS initialization
            self.test_command(
                "SVCS Init",
                "python3 " + str(Path.cwd() / "svcs" / "cli.py") + " init",
                expect_success=True,
                cwd=repo_path
            )
            
            # Test status command
            self.test_command(
                "SVCS Status",
                "python3 " + str(Path.cwd() / "svcs" / "cli.py") + " status",
                expect_success=True,
                cwd=repo_path
            )
            
            # Test events command (may have no events yet)
            self.test_command(
                "SVCS Events",
                "python3 " + str(Path.cwd() / "svcs" / "cli.py") + " events --limit 5",
                expect_success=True,
                cwd=repo_path
            )
    
    def run_error_handling_tests(self):
        """Test error handling for invalid scenarios."""
        print("⚠️ Error Handling Tests")
        print("-" * 40)
        
        # Test SVCS commands in non-git directory
        with tempfile.TemporaryDirectory() as temp_dir:
            self.test_command(
                "Init in Non-Git Dir",
                "python3 svcs/cli.py init",
                expect_success=False,
                cwd=temp_dir
            )
            
            self.test_command(
                "Status in Non-SVCS Dir",
                "python3 svcs/cli.py status",
                expect_success=False,
                cwd=temp_dir
            )
    
    def generate_report(self):
        """Generate test report."""
        print("=" * 60)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 60)
        print(f"✅ Passed: {self.passed}")
        print(f"❌ Failed: {self.failed}")
        print(f"📈 Success Rate: {(self.passed / (self.passed + self.failed) * 100):.1f}%")
        print()
        
        if self.failed > 0:
            print("❌ FAILED TESTS:")
            for test in self.test_results:
                if test['status'] == 'FAILED':
                    print(f"   • {test['name']}")
            print()
        
        # Export detailed results
        report_path = Path("svcs_cli_test_results.json")
        with open(report_path, 'w') as f:
            json.dump({
                'summary': {
                    'passed': self.passed,
                    'failed': self.failed,
                    'total': self.passed + self.failed,
                    'success_rate': self.passed / (self.passed + self.failed) * 100
                },
                'tests': self.test_results
            }, f, indent=2)
        
        print(f"📄 Detailed results saved to: {report_path}")
        
        return self.failed == 0


def main():
    """Run all CLI tests."""
    tester = SVCSCLITester()
    
    # Check if CLI file exists
    cli_path = Path("svcs/cli.py")
    if not cli_path.exists():
        print(f"❌ Error: CLI file not found at {cli_path}")
        sys.exit(1)
    
    try:
        # Run test suites
        tester.run_basic_cli_tests()
        tester.run_repository_tests()
        tester.run_error_handling_tests()
        
        # Generate final report
        success = tester.generate_report()
        
        if success:
            print("🎉 All tests passed! SVCS CLI is ready for use.")
            sys.exit(0)
        else:
            print("⚠️ Some tests failed. Please review the results.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⏹️ Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Testing error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
