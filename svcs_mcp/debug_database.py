#!/usr/bin/env python3
"""
Debug script to check database content
"""

import sys
import sqlite3
from pathlib import Path

# Database path
db_path = Path.home() / ".svcs" / "global.db"

def check_database():
    """Check database content for debugging."""
    
    print("🗄️ Database Debug Check")
    print("=" * 40)
    
    if not db_path.exists():
        print("❌ Database not found")
        return
    
    conn = sqlite3.connect(db_path)
    
    # Check projects
    print("\n📁 Projects:")
    cursor = conn.execute("SELECT project_id, name, path FROM projects")
    for row in cursor.fetchall():
        print(f"  {row[0][:8]}... - {row[1]} - {row[2]}")
    
    # Check commits for our project
    print("\n📝 Commits:")
    cursor = conn.execute("""
        SELECT project_id, commit_hash, author, message 
        FROM commits 
        WHERE project_id LIKE '041b54b5%'
        ORDER BY timestamp DESC
        LIMIT 10
    """)
    for row in cursor.fetchall():
        print(f"  {row[1][:8]}... - {row[2]} - {row[3]}")
    
    # Check events with join
    print("\n🔍 Events with Join:")
    cursor = conn.execute("""
        SELECT 
            se.event_type,
            se.node_id,
            se.details,
            c.author,
            c.message
        FROM semantic_events se
        LEFT JOIN commits c ON se.commit_hash = c.commit_hash AND se.project_id = c.project_id
        WHERE se.project_id LIKE '041b54b5%'
        ORDER BY se.created_at DESC
        LIMIT 5
    """)
    for row in cursor.fetchall():
        print(f"  {row[0]} - {row[1]} - {row[3]} - {row[4]}")
    
    conn.close()

if __name__ == "__main__":
    check_database()
