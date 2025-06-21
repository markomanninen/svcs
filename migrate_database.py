#!/usr/bin/env python3
"""
Database migration script to add AI analysis fields to existing SVCS database
"""

import sqlite3
import os

def migrate_database():
    """Add AI analysis fields to the semantic_events table"""
    db_path = ".svcs/history.db"
    
    if not os.path.exists(db_path):
        print("❌ No database found, skipping migration")
        return
    
    print("🔄 Migrating SVCS database to include AI analysis fields...")
    
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        
        # Check if the new columns already exist
        cursor.execute("PRAGMA table_info(semantic_events)")
        columns = [column[1] for column in cursor.fetchall()]
        
        new_columns = ['layer', 'layer_description', 'confidence', 'reasoning', 'impact']
        
        for column in new_columns:
            if column not in columns:
                print(f"  ➕ Adding column: {column}")
                if column == 'confidence':
                    cursor.execute(f"ALTER TABLE semantic_events ADD COLUMN {column} REAL")
                else:
                    cursor.execute(f"ALTER TABLE semantic_events ADD COLUMN {column} TEXT")
            else:
                print(f"  ✅ Column already exists: {column}")
        
        conn.commit()
        
        # Verify the migration
        cursor.execute("PRAGMA table_info(semantic_events)")
        final_columns = [column[1] for column in cursor.fetchall()]
        
        print("📊 Final database schema:")
        for i, col in enumerate(final_columns, 1):
            print(f"  {i}. {col}")
        
        print("✅ Database migration completed successfully!")

if __name__ == "__main__":
    migrate_database()
