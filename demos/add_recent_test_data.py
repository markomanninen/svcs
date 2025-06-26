#!/usr/bin/env python3
"""
Add recent test data and fix API testing issues.
"""

import sqlite3
import time
import random
from datetime import datetime, timedelta

DB_PATH = "/Users/markomanninen/Documents/GitHub/svcs/.svcs/semantic.db"

def add_recent_data():
    """Add some recent events for testing recent activity API."""
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        print("🕒 Adding recent test data...")
        
        # Get current timestamp
        now = int(time.time())
        
        # Create recent commits (last 3 days)
        recent_commits = []
        for day in range(3, 0, -1):
            timestamp = now - (day * 24 * 3600) + random.randint(0, 86400)
            commit_hash = ''.join(random.choices('0123456789abcdef', k=40))
            author = random.choice(["alice@example.com", "bob@example.com"])
            branch = "main"
            message = f"Recent commit {4-day}: Add new features"
            
            recent_commits.append((
                commit_hash, branch, author, timestamp, message, now, False
            ))
        
        # Insert recent commits
        cursor.executemany("""
            INSERT INTO commits (commit_hash, branch, author, timestamp, message, created_at, git_notes_synced)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, recent_commits)
        
        # Add recent events for these commits
        event_id = 500  # Start from 500 to avoid conflicts
        recent_events = []
        
        for commit_hash, branch, author, timestamp, message, _, _ in recent_commits:
            for i in range(2):  # 2 events per recent commit
                event_type = random.choice(["function_added", "bug_fix", "performance_improvement"])
                node_id = random.choice(["func:new_feature", "class:RecentUpdate", "func:optimize_code"])
                location = random.choice(["src/recent.py:10", "src/features/new.py:25"])
                confidence = round(random.uniform(0.7, 0.95), 2)
                
                recent_events.append((
                    f"evt_{event_id:06d}",
                    commit_hash,
                    branch,
                    event_type,
                    node_id,
                    location,
                    f"Recent {event_type} in {node_id}",
                    "layer3",
                    "Architectural Patterns",
                    confidence,
                    f"Recent AI analysis detected {event_type}",
                    "medium",
                    timestamp + random.randint(0, 1800),
                    False
                ))
                event_id += 1
        
        # Insert recent events
        cursor.executemany("""
            INSERT INTO semantic_events (
                event_id, commit_hash, branch, event_type, node_id, location, 
                details, layer, layer_description, confidence, reasoning, impact, 
                created_at, git_notes_synced
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, recent_events)
        
        conn.commit()
        
        # Get a sample commit hash from our data
        cursor.execute("SELECT commit_hash FROM commits LIMIT 1")
        sample_commit = cursor.fetchone()
        
        print(f"✅ Added {len(recent_commits)} recent commits and {len(recent_events)} recent events")
        if sample_commit:
            print(f"📋 Sample commit hash for testing: {sample_commit[0]}")
        
        return sample_commit[0] if sample_commit else None
        
    except Exception as e:
        print(f"❌ Error adding recent data: {e}")
        conn.rollback()
        return None
    finally:
        conn.close()

if __name__ == "__main__":
    add_recent_data()
