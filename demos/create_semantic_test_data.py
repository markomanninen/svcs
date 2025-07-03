#!/usr/bin/env python3
"""
Populate semantic.db with comprehensive test data for API testing.
Creates realistic commits and semantic events to test all API functions.
"""

import os
import sqlite3
import time
import random
import json
from datetime import datetime, timedelta

# Database path
# Use relative path to current repo
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(REPO_ROOT, ".svcs", "semantic.db")

def get_random_commit_hash():
    """Generate a realistic git commit hash."""
    return ''.join(random.choices('0123456789abcdef', k=40))

def get_timestamp(days_ago):
    """Get timestamp for days ago."""
    return int((datetime.now() - timedelta(days=days_ago)).timestamp())

def create_test_data():
    """Create comprehensive test data for semantic analysis."""
    
    # Test data configuration
    authors = ["alice@example.com", "bob@example.com", "charlie@example.com", "diana@example.com"]
    branches = ["main", "feature/user-auth", "feature/api-refactor", "hotfix/security-patch"]
    
    # Event types and patterns
    event_types = [
        "function_added", "function_modified", "function_removed",
        "class_added", "class_modified", "class_removed", 
        "dependency_added", "dependency_removed", "dependency_updated",
        "architecture_change", "performance_improvement", "security_enhancement",
        "bug_fix", "refactor", "test_added", "documentation_updated",
        "api_endpoint_added", "api_endpoint_modified", "database_schema_change"
    ]
    
    layers = [
        ("layer1", "Syntax and Structure"),
        ("layer2", "Data Flow and Dependencies"),
        ("layer3", "Architectural Patterns"),
        ("layer4", "Business Logic and Domain"),
        ("layer5", "AI-Enhanced Semantic Analysis")
    ]
    
    # Node patterns for different languages
    node_patterns = {
        "python": ["func:process_data", "class:UserManager", "func:validate_input", "class:DatabaseConnection"],
        "javascript": ["func:handleClick", "class:ApiClient", "func:formatDate", "func:validateForm"],
        "php": ["func:authenticate_user", "class:PaymentProcessor", "func:sanitize_input"],
        "general": ["config:database", "endpoint:/api/users", "schema:user_table", "package:requests"]
    }
    
    # Location patterns
    locations = [
        "src/main.py:45", "src/api/users.py:123", "src/models/user.py:67",
        "frontend/components/UserForm.js:89", "config/database.yml:12",
        "tests/test_auth.py:156", "docs/api.md:234", "package.json:45",
        "src/controllers/AuthController.php:78", "src/utils/helpers.py:234"
    ]

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        print("🗃️ Creating comprehensive test data for semantic.db...")
        
        # Clear existing data
        cursor.execute("DELETE FROM semantic_events")
        cursor.execute("DELETE FROM commits")
        cursor.execute("DELETE FROM branches")
        cursor.execute("DELETE FROM repository_info")
        
        # Insert repository info
        cursor.execute("""
            INSERT INTO repository_info (repo_path, created_at, last_analyzed, current_branch, config)
            VALUES (?, ?, ?, ?, ?)
        """, (
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            get_timestamp(30),
            get_timestamp(0),
            "main",
            json.dumps({"version": "1.0", "language": "python"})
        ))
        
        # Insert branches
        for i, branch in enumerate(branches):
            cursor.execute("""
                INSERT INTO branches (branch_name, created_at, last_analyzed, parent_branch, semantic_events_count)
                VALUES (?, ?, ?, ?, ?)
            """, (
                branch,
                get_timestamp(25 - i*5),
                get_timestamp(random.randint(0, 5)),
                "main" if branch != "main" else None,
                0  # Will be updated later
            ))
        
        # Generate commits and semantic events
        commit_data = []
        event_data = []
        event_id_counter = 1
        
        # Generate commits over the last 30 days
        for day in range(30, 0, -1):
            # Random number of commits per day (0-3)
            num_commits = random.randint(0, 3)
            
            for _ in range(num_commits):
                commit_hash = get_random_commit_hash()
                author = random.choice(authors)
                branch = random.choice(branches)
                timestamp = get_timestamp(day) + random.randint(0, 86400)  # Random time during the day
                
                messages = [
                    "Add user authentication system",
                    "Fix security vulnerability in login",
                    "Refactor database connection logic", 
                    "Update API documentation",
                    "Improve performance of data processing",
                    "Add comprehensive test coverage",
                    "Implement new payment processing",
                    "Fix bug in user registration",
                    "Add logging and monitoring",
                    "Update dependencies to latest versions"
                ]
                message = random.choice(messages)
                
                commit_data.append((
                    commit_hash, branch, author, timestamp, message, 
                    int(time.time()), False
                ))
                
                # Generate 1-5 semantic events per commit
                num_events = random.randint(1, 5)
                for _ in range(num_events):
                    event_type = random.choice(event_types)
                    layer, layer_desc = random.choice(layers)
                    
                    # Choose node pattern based on file type
                    if "py" in random.choice(locations):
                        node_id = random.choice(node_patterns["python"])
                    elif "js" in random.choice(locations):
                        node_id = random.choice(node_patterns["javascript"])  
                    elif "php" in random.choice(locations):
                        node_id = random.choice(node_patterns["php"])
                    else:
                        node_id = random.choice(node_patterns["general"])
                    
                    location = random.choice(locations)
                    confidence = round(random.uniform(0.6, 0.95), 2)
                    
                    # Generate contextual details and reasoning
                    details_templates = {
                        "function_added": f"New function '{node_id}' implements {random.choice(['validation', 'processing', 'formatting', 'calculation'])} logic",
                        "class_added": f"New class '{node_id}' provides {random.choice(['data management', 'API interface', 'business logic', 'utility functions'])}",
                        "dependency_added": f"Added dependency '{node_id}' for {random.choice(['HTTP requests', 'data validation', 'testing', 'logging'])}",
                        "performance_improvement": f"Optimized {node_id} reducing {random.choice(['memory usage', 'execution time', 'database queries'])} by {random.randint(20, 80)}%",
                        "security_enhancement": f"Enhanced security in {node_id} by adding {random.choice(['input validation', 'authentication', 'encryption', 'access control'])}",
                        "bug_fix": f"Fixed {random.choice(['null pointer', 'race condition', 'memory leak', 'logic error'])} in {node_id}"
                    }
                    
                    details = details_templates.get(event_type, f"Modified {node_id} with {event_type}")
                    
                    reasoning = f"AI analysis detected {event_type} pattern in {location} with {confidence} confidence"
                    
                    impact_levels = ["low", "medium", "high", "critical"]
                    impact = random.choice(impact_levels)
                    
                    event_data.append((
                        f"evt_{event_id_counter:06d}",
                        commit_hash,
                        branch,
                        event_type,
                        node_id,
                        location,
                        details,
                        layer,
                        layer_desc,
                        confidence,
                        reasoning,
                        impact,
                        timestamp + random.randint(0, 3600),  # Event within an hour of commit
                        False
                    ))
                    event_id_counter += 1
        
        # Insert commits
        print(f"📝 Inserting {len(commit_data)} commits...")
        cursor.executemany("""
            INSERT INTO commits (commit_hash, branch, author, timestamp, message, created_at, git_notes_synced)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, commit_data)
        
        # Insert semantic events
        print(f"🔍 Inserting {len(event_data)} semantic events...")
        cursor.executemany("""
            INSERT INTO semantic_events (
                event_id, commit_hash, branch, event_type, node_id, location, 
                details, layer, layer_description, confidence, reasoning, impact, 
                created_at, git_notes_synced
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, event_data)
        
        # Update branch event counts
        for branch in branches:
            cursor.execute("""
                UPDATE branches SET semantic_events_count = (
                    SELECT COUNT(*) FROM semantic_events WHERE branch = ?
                ) WHERE branch_name = ?
            """, (branch, branch))
        
        conn.commit()
        
        # Print summary
        cursor.execute("SELECT COUNT(*) FROM commits")
        commit_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM semantic_events")
        event_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT author) FROM commits")
        author_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT event_type) FROM semantic_events")
        event_type_count = cursor.fetchone()[0]
        
        print(f"\n✅ Test data creation complete!")
        print(f"📊 Summary:")
        print(f"   - {commit_count} commits")
        print(f"   - {event_count} semantic events")
        print(f"   - {author_count} unique authors")
        print(f"   - {len(branches)} branches")
        print(f"   - {event_type_count} event types")
        
        # Show sample data
        print(f"\n🔍 Sample Events:")
        cursor.execute("""
            SELECT event_type, node_id, location, confidence, layer
            FROM semantic_events 
            ORDER BY created_at DESC 
            LIMIT 5
        """)
        
        for row in cursor.fetchall():
            event_type, node_id, location, confidence, layer = row
            print(f"   - {event_type}: {node_id} @ {location} (confidence: {confidence}, {layer})")
            
    except Exception as e:
        print(f"❌ Error creating test data: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    create_test_data()
