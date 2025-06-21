#!/usr/bin/env python3
"""
Fixed SVCS CLI that actually works
"""

import os
import sys
from pathlib import Path

# Add the SVCS paths
svcs_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(svcs_root))
sys.path.insert(0, str(svcs_root / "svcs_mcp"))
sys.path.insert(0, str(svcs_root / ".svcs"))

import click
from svcs_mcp_server_simple import GlobalSVCSDatabase, process_commit

@click.group()
def main():
    """SVCS - Semantic Version Control System CLI (FIXED VERSION)."""
    pass

@main.command()
@click.argument('project_path', default='.')
def analyze_commit(project_path):
    """Analyze the latest commit for semantic changes."""
    project_path = os.path.abspath(project_path)
    
    try:
        process_commit(project_path)
        print("✅ Semantic analysis completed")
    except Exception as e:
        print(f"❌ Analysis failed: {e}")

@main.command()
def list_projects():
    """List all registered projects."""
    db = GlobalSVCSDatabase()
    projects = db.list_projects()
    
    print(f"📋 SVCS Registered Projects ({len(projects)}):")
    print()
    
    if not projects:
        print("No projects registered with SVCS")
        return
    
    for project in projects:
        print(f"• {project['name']}")
        print(f"  Path: {project['path']}")
        print(f"  ID: {project['project_id'][:8]}...")
        print()

@main.command()
@click.argument('project_path')
@click.argument('name')
def register_project(project_path, name):
    """Register a new project."""
    db = GlobalSVCSDatabase()
    project_path = os.path.abspath(project_path)
    
    try:
        project_id = db.register_project(name, project_path)
        print(f"✅ Project '{name}' registered successfully")
        print(f"Project ID: {project_id}")
    except Exception as e:
        print(f"❌ Registration failed: {e}")

@main.command()
@click.argument('project_id')
def stats(project_id):
    """Show project statistics."""
    db = GlobalSVCSDatabase()
    
    # Get project info
    projects = db.list_projects()
    project = None
    for p in projects:
        if p['project_id'].startswith(project_id) or project_id in p['name']:
            project = p
            break
    
    if not project:
        print(f"❌ Project not found: {project_id}")
        return
    
    project_id = project['project_id']
    
    # Get statistics
    with db.get_connection() as conn:
        cursor = conn.execute("""
            SELECT COUNT(*) FROM semantic_events WHERE project_id = ?
        """, (project_id,))
        total_events = cursor.fetchone()[0]
        
        cursor = conn.execute("""
            SELECT event_type, COUNT(*) as count
            FROM semantic_events 
            WHERE project_id = ?
            GROUP BY event_type
            ORDER BY count DESC
        """, (project_id,))
        event_types = cursor.fetchall()
    
    print(f"📊 Statistics for '{project['name']}':")
    print(f"Total semantic events: {total_events}")
    
    if event_types:
        print("\nEvent breakdown:")
        for event_type, count in event_types:
            print(f"  - {event_type}: {count}")
    else:
        print("\nNo semantic events recorded yet.")

if __name__ == "__main__":
    main()
