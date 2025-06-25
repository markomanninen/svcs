import os
import shutil
import sqlite3
import subprocess
import tempfile
import time
from pathlib import Path

def run(cmd, cwd):
    result = subprocess.run(cmd, cwd=cwd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Command failed: {cmd}\n{result.stderr}")
    return result.stdout.strip()

def count_events(db_path, branch):
    with sqlite3.connect(db_path) as conn:
        cursor = conn.execute("SELECT COUNT(*) FROM semantic_events WHERE branch = ?", (branch,))
        return cursor.fetchone()[0]

def main():
    tmpdir = tempfile.mkdtemp(prefix="svcs_merge_test_")
    os.chdir(tmpdir)
    print(f"Working in {tmpdir}")

    # Init git repo and SVCS
    run("git init .", tmpdir)
    Path("README.md").write_text("# Test Repo\n")
    run("git add README.md", tmpdir)
    run("git commit -m 'init'", tmpdir)
    run("svcs init", tmpdir)

    # Add a semantic event on main
    db_path = Path(tmpdir) / ".svcs" / "semantic.db"
    with sqlite3.connect(db_path) as conn:
        conn.execute("""
            INSERT INTO semantic_events (
                event_id, commit_hash, branch, event_type, node_id, location,
                details, layer, layer_description, confidence, reasoning, impact, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "main-event-1", run("git rev-parse HEAD", tmpdir), "main", "typeA", "node1", "loc1",
            "main event", "layer1", "desc1", 1.0, "reasoning1", "impact1", int(time.time())
        ))
        conn.commit()

    # Create feature branch and add a semantic event
    run("git checkout -b feature", tmpdir)
    Path("feature.txt").write_text("feature branch\n")
    run("git add feature.txt", tmpdir)
    run("git commit -m 'feature commit'", tmpdir)
    with sqlite3.connect(db_path) as conn:
        conn.execute("""
            INSERT INTO semantic_events (
                event_id, commit_hash, branch, event_type, node_id, location,
                details, layer, layer_description, confidence, reasoning, impact, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "feature-event-1", run("git rev-parse HEAD", tmpdir), "feature", "typeB", "node2", "loc2",
            "feature event", "layer2", "desc2", 1.0, "reasoning2", "impact2", int(time.time())
        ))
        conn.commit()

    # Switch back to main and merge feature
    run("git checkout main", tmpdir)
    run("git merge feature", tmpdir)
    
    # Call SVCS merge logic directly
    from svcs_repo_local import RepositoryLocalSVCS
    svcs = RepositoryLocalSVCS(tmpdir)
    print(svcs.process_merge(source_branch="feature", target_branch="main"))

    # Check events on main
    main_count = count_events(db_path, "main")
    feature_count = count_events(db_path, "feature")
    print(f"Semantic events on main: {main_count}")
    print(f"Semantic events on feature: {feature_count}")

    # Validate both events are present on main
    with sqlite3.connect(db_path) as conn:
        events = conn.execute("SELECT event_type, node_id, branch FROM semantic_events WHERE branch = 'main'").fetchall()
        print("Events on main branch:", events)
        assert ("typeA", "node1", "main") in events, "Main event missing on main"
        assert ("typeB", "node2", "main") in events, "Feature event not transferred to main"

    print("✅ Test passed: All semantic events transferred to main after merge.")

if __name__ == "__main__":
    main()