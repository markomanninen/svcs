#!/usr/bin/env python3
"""
Simple CLI test for SVCS MCP server functionality.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "svcs_mcp"))

from svcs_mcp_server_simple import GlobalSVCSDatabase, ProjectManager, SVCSQueryEngine

def test_cli():
    """Test CLI functionality."""
    print("🧪 Testing SVCS MCP CLI Interface")
    print("=" * 50)
    
    # Initialize database
    db = GlobalSVCSDatabase()
    print("✅ Database initialized")
    
    # Initialize other components
    project_manager = ProjectManager(db)
    query_engine = SVCSQueryEngine(db)
    print("✅ Components initialized")
    
    # Test project registration (or get existing)
    print("\n📝 Managing test project...")
    current_dir = str(Path.cwd())
    
    # Check if project already exists
    existing_project = db.get_project_by_path(current_dir)
    if existing_project:
        project_id = existing_project['project_id']
        print(f"✅ Found existing project: {project_id[:8]}...")
    else:
        project_id = db.register_project("SVCS Test Project", current_dir)
        print(f"✅ Project registered with ID: {project_id[:8]}...")
    
    # Test project listing
    print("\n📋 Listing all projects...")
    projects = db.list_projects()
    for project in projects:
        print(f"  • {project['name']} ({project['project_id'][:8]}...)")
        print(f"    Path: {project['path']}")
    
    # Test project statistics
    print(f"\n📊 Getting statistics for project {project_id[:8]}...")
    stats = query_engine.get_project_statistics(project_id)
    print(f"  • Project ID: {project_id[:8]}...")
    print(f"  • Statistics: {stats}")
    
    print("\n✨ CLI test completed successfully!")

if __name__ == "__main__":
    test_cli()
