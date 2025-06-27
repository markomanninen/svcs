#!/usr/bin/env python3
"""
Test script to verify MCP server initialization without runtime errors.
This simulates the problematic initialization that was failing in Claude.
"""

import os
import sys
from pathlib import Path

# Simulate Claude's environment where cwd might be /
os.chdir('/')
print(f"Current working directory: {os.getcwd()}")

# Add paths for imports (same as mcp_server.py)
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))
sys.path.insert(0, str(script_dir.parent))

# Add the main SVCS directory to path for new architecture imports
SVCS_ROOT = script_dir.parent / "svcs"
sys.path.insert(0, str(SVCS_ROOT))

def test_initialization():
    """Test the initialization process that was failing."""
    print("Testing imports...")
    
    try:
        # Test new architecture components
        from svcs_repo_local_core import RepositoryLocalMCPServer
        print("✓ New architecture available")
        NEW_ARCH_AVAILABLE = True
    except ImportError as e:
        print(f"✗ New architecture not available: {e}")
        NEW_ARCH_AVAILABLE = False
        return False

    # Test initialization sequence
    if NEW_ARCH_AVAILABLE:
        print("\nTesting new architecture initialization...")
        try:
            mcp_server = RepositoryLocalMCPServer()
            print("✓ RepositoryLocalMCPServer initialized successfully")
            
        except Exception as e:
            print(f"✗ New architecture initialization failed: {e}")
            return False
    else:
        print("✗ No architecture components available")
        return False
        
    print("\n✅ All initialization tests completed successfully!")
    return True

if __name__ == "__main__":
    success = test_initialization()
    if not success:
        sys.exit(1)
