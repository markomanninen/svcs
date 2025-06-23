#!/usr/bin/env python3
"""
SVCS Project Cleanup Utility

A comprehensive script to remove SVCS projects based on various criteria:
- Temporary directories (/tmp/, /private/tmp/, /var/folders/)
- Test projects and directories
- Inactive projects
- Projects by path pattern or status

Usage:
    python3 svcs_cleanup.py --help
    python3 svcs_cleanup.py --temp-dirs          # Remove all temp directory projects
    python3 svcs_cleanup.py --inactive           # Remove all inactive projects
    python3 svcs_cleanup.py --pattern "svcs_*"   # Remove projects matching pattern
    python3 svcs_cleanup.py --path "/tmp/"       # Remove projects in specific path
    python3 svcs_cleanup.py --dry-run            # Preview what would be removed
"""

import argparse
import sqlite3
import sys
import shutil
import os
from pathlib import Path
from typing import List, Tuple, Optional

# Add paths for imports
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / "svcs_mcp"))

# Global SVCS directory
SVCS_HOME = Path.home() / ".svcs"
GLOBAL_DB = SVCS_HOME / "global.db"

class SVCSCleanup:
    """SVCS Project Cleanup Utility"""
    
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.total_projects = 0
        self.total_events = 0
        self.total_commits = 0
        
    def get_projects_by_criteria(self, 
                                temp_dirs: bool = False,
                                inactive: bool = False, 
                                pattern: Optional[str] = None,
                                path_filter: Optional[str] = None) -> List[Tuple]:
        """Get projects matching the specified criteria"""
        
        if not GLOBAL_DB.exists():
            print(f"❌ Database not found: {GLOBAL_DB}")
            return []
            
        conditions = []
        params = []
        
        if temp_dirs:
            conditions.append("""(path LIKE '%/tmp/%' OR path LIKE '%tmp%' 
                                OR path LIKE '%/var/folders/%' 
                                OR path LIKE '%/private/tmp/%'
                                OR path LIKE '%Documents/tmp%')""")
            # Exclude the main SVCS repository
            conditions.append("path NOT LIKE '%/Documents/GitHub/svcs%'")
            
        if inactive:
            conditions.append("status = 'inactive'")
            
        if pattern:
            conditions.append("(name LIKE ? OR path LIKE ?)")
            params.extend([f"%{pattern}%", f"%{pattern}%"])
            
        if path_filter:
            conditions.append("path LIKE ?")
            params.append(f"%{path_filter}%")
            
        if not conditions:
            print("❌ No criteria specified. Use --help for options.")
            return []
            
        query = f"""
            SELECT project_id, name, path, status 
            FROM projects 
            WHERE {' AND '.join(conditions)}
        """
        
        try:
            conn = sqlite3.connect(GLOBAL_DB)
            cursor = conn.execute(query, params)
            projects = cursor.fetchall()
            conn.close()
            return projects
        except Exception as e:
            print(f"❌ Error querying database: {e}")
            return []
    
    def count_project_data(self, project_id: str) -> Tuple[int, int]:
        """Count events and commits for a project"""
        try:
            conn = sqlite3.connect(GLOBAL_DB)
            
            cursor = conn.execute("SELECT COUNT(*) FROM semantic_events WHERE project_id = ?", (project_id,))
            event_count = cursor.fetchone()[0]
            
            cursor = conn.execute("SELECT COUNT(*) FROM commits WHERE project_id = ?", (project_id,))
            commit_count = cursor.fetchone()[0]
            
            conn.close()
            return event_count, commit_count
        except Exception as e:
            print(f"❌ Error counting data for project {project_id}: {e}")
            return 0, 0
    
    def delete_project(self, project_id: str, name: str, path: str) -> bool:
        """Delete a project and all its data"""
        if self.dry_run:
            print(f"   [DRY RUN] Would delete project: {name}")
            return True
            
        try:
            conn = sqlite3.connect(GLOBAL_DB)
            
            # Delete semantic events
            conn.execute("DELETE FROM semantic_events WHERE project_id = ?", (project_id,))
            
            # Delete commits  
            conn.execute("DELETE FROM commits WHERE project_id = ?", (project_id,))
            
            # Delete project
            conn.execute("DELETE FROM projects WHERE project_id = ?", (project_id,))
            
            conn.commit()
            conn.close()
            
            print(f"   ✓ Deleted from database: {name}")
            return True
            
        except Exception as e:
            print(f"   ❌ Error deleting project {name}: {e}")
            return False
    
    def remove_directory(self, path: str) -> bool:
        """Physically remove a directory"""
        if self.dry_run:
            if os.path.exists(path):
                print(f"   [DRY RUN] Would remove directory: {path}")
            return True
            
        if os.path.exists(path):
            try:
                shutil.rmtree(path)
                print(f"   ✓ Physically removed directory: {path}")
                return True
            except Exception as e:
                print(f"   ❌ Error removing directory {path}: {e}")
                return False
        return True
    
    def cleanup_projects(self, projects: List[Tuple]) -> None:
        """Clean up the specified projects"""
        if not projects:
            print("✅ No projects found matching the criteria.")
            return
            
        print(f"\n📋 Found {len(projects)} projects to remove:")
        
        # Show what will be removed
        for project_id, name, path, status in projects:
            event_count, commit_count = self.count_project_data(project_id)
            print(f"  • {name} ({path}) - {status}")
            print(f"    Events: {event_count}, Commits: {commit_count}")
            self.total_events += event_count
            self.total_commits += commit_count
        
        if self.dry_run:
            print(f"\n[DRY RUN] Would delete: {len(projects)} projects, {self.total_events} events, {self.total_commits} commits")
            return
            
        # Confirm deletion
        response = input(f"\n⚠️  Delete {len(projects)} projects? (y/N): ").lower()
        if response != 'y':
            print("❌ Cancelled.")
            return
            
        print("\n🗑️ Starting deletion...")
        
        # Delete each project
        for project_id, name, path, status in projects:
            print(f"\n🗑️ Processing: {name}")
            
            event_count, commit_count = self.count_project_data(project_id)
            print(f"   • Events to delete: {event_count}")
            print(f"   • Commits to delete: {commit_count}")
            
            # Delete from database
            if self.delete_project(project_id, name, path):
                self.total_projects += 1
                
            # Remove physical directory
            self.remove_directory(path)
            
            print("   ---")
        
        print(f"\n🎉 Cleanup completed!")
        print(f"📊 Total deleted: {self.total_projects} projects, {self.total_events} events, {self.total_commits} commits")

def main():
    parser = argparse.ArgumentParser(
        description="SVCS Project Cleanup Utility",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --temp-dirs              # Remove all temp directory projects
  %(prog)s --inactive               # Remove all inactive projects  
  %(prog)s --pattern "svcs_test*"   # Remove projects matching pattern
  %(prog)s --path "/tmp/"           # Remove projects in /tmp/
  %(prog)s --temp-dirs --dry-run    # Preview temp directory cleanup
        """
    )
    
    parser.add_argument('--temp-dirs', action='store_true',
                       help='Remove projects in temporary directories (/tmp/, /var/folders/, etc.)')
    parser.add_argument('--inactive', action='store_true',
                       help='Remove projects with inactive status')
    parser.add_argument('--pattern', type=str,
                       help='Remove projects matching name/path pattern (supports wildcards)')
    parser.add_argument('--path', type=str,
                       help='Remove projects in specific path')
    parser.add_argument('--dry-run', action='store_true',
                       help='Preview what would be removed without actually deleting')
    
    args = parser.parse_args()
    
    # Check if any criteria specified
    if not any([args.temp_dirs, args.inactive, args.pattern, args.path]):
        parser.print_help()
        sys.exit(1)
    
    cleanup = SVCSCleanup(dry_run=args.dry_run)
    
    print("🧹 SVCS Project Cleanup Utility")
    print("=" * 40)
    
    if args.dry_run:
        print("🔍 DRY RUN MODE - No changes will be made")
    
    projects = cleanup.get_projects_by_criteria(
        temp_dirs=args.temp_dirs,
        inactive=args.inactive,
        pattern=args.pattern,
        path_filter=args.path
    )
    
    cleanup.cleanup_projects(projects)

if __name__ == "__main__":
    main()
