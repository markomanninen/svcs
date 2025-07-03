#!/usr/bin/env python3
"""
Quick test to investigate the two specific questions:
1. What happened to the original note in central repo
2. What happens when a third user pulls from central repo

This extends the existing successful test.
"""

import os
import sys
import tempfile
import shutil
import subprocess
import time
import json

# Add the parent directory to Python path to import SVCS modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def run_command(command, cwd=None):
    """Run a shell command and return (success, output)"""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            cwd=cwd,
            capture_output=True, 
            text=True,
            timeout=30
        )
        return result.returncode == 0, result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return False, "Command timed out"
    except Exception as e:
        return False, str(e)

def analyze_notes_in_repo(repo_path, repo_name):
    """Analyze semantic notes in a repository"""
    print(f"  🔍 Analyzing semantic notes in {repo_name}...")
    success, output = run_command("git notes --ref=refs/notes/svcs-semantic list", repo_path)
    if success and output.strip():
        lines = output.strip().split('\n')
        notes_list = []
        for line in lines:
            parts = line.strip().split()
            if len(parts) >= 2:
                notes_list.append(parts[1])  # commit_sha is second part
        
        print(f"    ✅ Found {len(notes_list)} semantic notes")
        
        note_details = []
        for i, note_ref in enumerate(notes_list, 1):
            note_success, note_content = run_command(f"git notes --ref=refs/notes/svcs-semantic show {note_ref}", repo_path)
            if note_success and note_content.strip():
                try:
                    note_data = json.loads(note_content)
                    events = note_data.get('semantic_events', [])
                    timestamp = note_data.get('timestamp', 'unknown')
                    commit_hash = note_data.get('commit_hash', note_ref)
                    
                    print(f"      📄 Note {i}: Commit {commit_hash[:8]}, {len(events)} events, {timestamp[:19]}")
                    
                    # Analyze content to determine origin
                    content_lower = note_content.lower()
                    origin = "unknown"
                    if "user" in content_lower and "management" in content_lower:
                        origin = "Dev1 (user management)"
                    elif "api" in content_lower or "endpoint" in content_lower or "flask" in content_lower:
                        origin = "Dev2 (API endpoints)"
                    elif "initial" in content_lower or "setup" in content_lower:
                        origin = "Initial setup"
                    
                    note_details.append({
                        'commit': commit_hash,
                        'events': len(events),
                        'timestamp': timestamp,
                        'origin': origin,
                        'content': note_content
                    })
                    
                    print(f"         Origin: {origin}")
                    for event in events[:2]:  # Show first 2 events
                        print(f"         - {event.get('event_type', 'unknown')}: {event.get('location', 'unknown')}")
                        
                except json.JSONDecodeError:
                    print(f"      📄 Note {i}: Raw content (not JSON)")
                    note_details.append({
                        'commit': note_ref,
                        'events': 0,
                        'timestamp': 'unknown',
                        'origin': 'unknown',
                        'content': note_content
                    })
            else:
                print(f"      ❌ Note {i}: Could not retrieve content")
                
        return note_details
    else:
        print(f"    ❌ No semantic notes found in {repo_name}")
        return []

def test_third_developer_scenario():
    """Test what happens when a third developer joins the project"""
    print("\n🧪 Testing Third Developer Scenario")
    print("=" * 50)
    
    # First, run the existing collaborative test to get a central repo with notes
    print("📋 Step 1: Running the existing collaborative test to set up scenario...")
    
    success, output = run_command("python test_collaborative_semantic_sync.py")
    if not success:
        print(f"❌ Failed to run base test: {output}")
        return
        
    print("✅ Base collaborative test completed")
    
    # Check if we have a semantic notes analysis log
    log_file = "semantic_notes_analysis.log"
    if os.path.exists(log_file):
        print(f"📄 Found semantic notes log: {log_file}")
        with open(log_file, 'r') as f:
            log_content = f.read()
        print("📋 Current semantic notes in central:")
        print(log_content)
    else:
        print("⚠️  No semantic notes log found")
        
    # Now let's simulate what happens when we have a real central repository
    # and a third developer clones it
    
    print("\n📋 Step 2: Simulating third developer joining existing project...")
    
    # For this simulation, let's use the current SVCS repo as our "central" repo
    # and create a temporary clone to simulate a third developer
    
    test_dir = tempfile.mkdtemp(prefix="svcs_third_dev_test_")
    third_dev_repo = os.path.join(test_dir, "third_developer")
    
    try:
        print(f"👤 Creating third developer workspace: {third_dev_repo}")
        
        # Clone the current SVCS repository (which has semantic notes)
        current_repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        success, output = run_command(f"git clone {current_repo} {third_dev_repo}")
        if not success:
            print(f"❌ Failed to clone for third developer: {output}")
            return
            
        # Configure git for third developer
        run_command("git config user.name 'Third Developer'", third_dev_repo)
        run_command("git config user.email 'dev3@example.com'", third_dev_repo)
        
        # Initialize SVCS for third developer
        print("🔬 Initializing SVCS for third developer...")
        sys.path.insert(0, third_dev_repo)
        success, output = run_command("python3 -m svcs.cli --path . init", third_dev_repo)
        if success:
            print("✅ SVCS initialized for third developer")
        else:
            print(f"⚠️  SVCS init had issues: {output}")
            
        # Fetch semantic notes (they should already be there since we cloned)
        print("📥 Checking what semantic notes the third developer can see...")
        third_dev_notes = analyze_notes_in_repo(third_dev_repo, "Third Developer")
        
        # Test SVCS functionality
        print("🧪 Testing SVCS functionality for third developer...")
        success, output = run_command("python3 -m svcs.cli --path . events --limit 5", third_dev_repo)
        if success:
            print("✅ SVCS events query successful for third developer")
            print(f"📊 Recent events visible to third developer:")
            lines = output.strip().split('\n')
            for line in lines[:10]:  # Show first 10 lines
                if line.strip():
                    print(f"    {line}")
        else:
            print(f"❌ SVCS events query failed: {output}")
            
        print(f"\n📊 SUMMARY FOR THIRD DEVELOPER:")
        print(f"   - Can see {len(third_dev_notes)} semantic notes")
        print(f"   - SVCS functionality: {'✅ Working' if success else '❌ Failed'}")
        
        # Analyze the notes by origin
        origins = {}
        for note in third_dev_notes:
            origin = note['origin']
            if origin not in origins:
                origins[origin] = 0
            origins[origin] += 1
            
        print(f"   - Notes by origin:")
        for origin, count in origins.items():
            print(f"     * {origin}: {count} notes")
            
    finally:
        # Cleanup
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)
            print(f"🧹 Cleaned up test directory: {test_dir}")

def investigate_original_notes():
    """Investigate what happened to original notes"""
    print("\n🔍 Investigating Original Notes")
    print("=" * 40)
    
    # Check the current SVCS repository for its semantic notes
    current_repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print(f"🏛️  Analyzing semantic notes in current SVCS repository...")
    
    notes = analyze_notes_in_repo(current_repo, "Current SVCS Repository")
    
    # Look for patterns that might indicate original vs. developer-contributed notes
    print(f"\n📊 Analysis of {len(notes)} notes found:")
    
    origins = {}
    oldest_timestamp = None
    newest_timestamp = None
    
    for note in notes:
        origin = note['origin']
        timestamp = note['timestamp']
        
        # Track origins
        if origin not in origins:
            origins[origin] = []
        origins[origin].append(note)
        
        # Track timestamps
        if timestamp != 'unknown':
            if oldest_timestamp is None or timestamp < oldest_timestamp:
                oldest_timestamp = timestamp
            if newest_timestamp is None or timestamp > newest_timestamp:
                newest_timestamp = timestamp
                
    print(f"\n📋 Notes by origin:")
    for origin, origin_notes in origins.items():
        print(f"   {origin}: {len(origin_notes)} notes")
        if origin_notes:
            timestamps = [n['timestamp'] for n in origin_notes if n['timestamp'] != 'unknown']
            if timestamps:
                print(f"      Timestamps: {min(timestamps)} to {max(timestamps)}")
                
    if oldest_timestamp and newest_timestamp:
        print(f"\n⏰ Overall timestamp range: {oldest_timestamp} to {newest_timestamp}")
        
    # Check if there are any notes that look like they might be "original" setup notes
    original_candidates = []
    for note in notes:
        content_lower = note['content'].lower()
        if any(keyword in content_lower for keyword in ['initial', 'setup', 'readme', 'gitignore']):
            original_candidates.append(note)
            
    print(f"\n🔍 Potential original setup notes: {len(original_candidates)}")
    for candidate in original_candidates:
        print(f"   - Commit {candidate['commit'][:8]}: {candidate['origin']} ({candidate['timestamp'][:19]})")

def main():
    """Main function to run both investigations"""
    print("🚀 Investigating SVCS Collaborative Notes")
    print("=" * 60)
    print("Questions:")
    print("1. What happened to the original note in central repo?")
    print("2. What happens when a third user pulls from central repo?")
    print("=" * 60)
    
    # Question 1: Investigate original notes
    investigate_original_notes()
    
    # Question 2: Test third developer scenario  
    test_third_developer_scenario()
    
    print("\n" + "=" * 60)
    print("🎉 Investigation completed!")

if __name__ == "__main__":
    main()
