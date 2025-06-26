# FILE: .svcs/storage.py

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