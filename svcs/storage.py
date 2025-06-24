# SVCS Modular Storage - Extracted from .svcs/storage.py
# Database operations for storing semantic events

import sqlite3

def initialize_database(db_path):
    """Creates the database and tables if they don't already exist."""
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        # Create commits table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS commits (
                commit_hash TEXT PRIMARY KEY,
                author TEXT NOT NULL,
                timestamp INTEGER NOT NULL
            )
        """)
        # Create semantic_events table with AI analysis fields
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS semantic_events (
                event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                commit_hash TEXT NOT NULL,
                event_type TEXT NOT NULL,
                node_id TEXT,
                location TEXT,
                details TEXT,
                layer TEXT,
                layer_description TEXT,
                confidence REAL,
                reasoning TEXT,
                impact TEXT,
                FOREIGN KEY (commit_hash) REFERENCES commits (commit_hash)
            )
        """)
        conn.commit()

def store_commit_events(db_path, commit_hash, commit_metadata, events):
    """Stores the analysis results for a single commit in the database."""
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        
        # Insert the commit record, ignoring if it already exists
        cursor.execute("""
            INSERT OR IGNORE INTO commits (commit_hash, author, timestamp)
            VALUES (?, ?, ?)
        """, (commit_hash, commit_metadata["author"], commit_metadata["timestamp"]))
        
        # Insert all semantic events for this commit with AI analysis fields
        events_to_store = [
            (
                commit_hash,
                event.get("event_type"),
                event.get("node_id"),
                event.get("location"),
                event.get("details"),
                event.get("layer"),
                event.get("layer_description"),
                event.get("confidence"),
                event.get("reasoning"),
                event.get("impact"),
            )
            for event in events
        ]
        
        cursor.executemany("""
            INSERT INTO semantic_events (commit_hash, event_type, node_id, location, details, layer, layer_description, confidence, reasoning, impact)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, events_to_store)
        
        conn.commit()

def get_recent_events(db_path, limit=20):
    """Retrieve recent semantic events from the database."""
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT e.event_type, e.node_id, e.location, e.details, 
                   c.commit_hash, c.author, c.timestamp
            FROM semantic_events e
            JOIN commits c ON e.commit_hash = c.commit_hash
            ORDER BY c.timestamp DESC
            LIMIT ?
        """, (limit,))
        
        results = cursor.fetchall()
        events = []
        for row in results:
            events.append({
                'event_type': row[0],
                'node_id': row[1],
                'location': row[2],
                'details': row[3],
                'commit_hash': row[4],
                'author': row[5],
                'timestamp': row[6]
            })
        return events

def get_event_statistics(db_path):
    """Get statistics about stored semantic events."""
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        
        # Total events
        cursor.execute("SELECT COUNT(*) FROM semantic_events")
        total_events = cursor.fetchone()[0]
        
        # Events by type
        cursor.execute("""
            SELECT event_type, COUNT(*) 
            FROM semantic_events 
            GROUP BY event_type 
            ORDER BY COUNT(*) DESC
        """)
        events_by_type = cursor.fetchall()
        
        # Total commits analyzed
        cursor.execute("SELECT COUNT(*) FROM commits")
        total_commits = cursor.fetchone()[0]
        
        return {
            'total_events': total_events,
            'total_commits': total_commits,
            'events_by_type': dict(events_by_type)
        }
