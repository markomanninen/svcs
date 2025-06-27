#!/usr/bin/env python3
"""
SVCS MCP Server Management Commands

Provides commands for starting, stopping, and managing the MCP server.
"""

import os
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional


def get_mcp_server_path() -> Path:
    """Get the path to the MCP server script."""
    # Try to find the MCP server relative to this file
    current_dir = Path(__file__).parent.parent.parent
    mcp_server_path = current_dir / "svcs_mcp" / "mcp_server.py"
    
    if mcp_server_path.exists():
        return mcp_server_path
    
    # Fallback: look in package installation
    import svcs
    package_dir = Path(svcs.__file__).parent.parent
    mcp_server_path = package_dir / "svcs_mcp" / "mcp_server.py"
    
    if mcp_server_path.exists():
        return mcp_server_path
    
    raise FileNotFoundError("MCP server script not found")


def get_mcp_server_pids() -> list:
    """Get PIDs of running MCP server processes."""
    try:
        result = subprocess.run(
            ["pgrep", "-f", "svcs_mcp/mcp_server.py"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            return [int(pid.strip()) for pid in result.stdout.strip().split('\n') if pid.strip()]
        return []
    except (subprocess.SubprocessError, FileNotFoundError):
        # Fallback to ps command
        try:
            result = subprocess.run(
                ["ps", "aux"],
                capture_output=True,
                text=True
            )
            pids = []
            for line in result.stdout.split('\n'):
                if "svcs_mcp/mcp_server.py" in line and "grep" not in line:
                    parts = line.split()
                    if len(parts) > 1:
                        try:
                            pids.append(int(parts[1]))
                        except ValueError:
                            continue
            return pids
        except subprocess.SubprocessError:
            return []


def get_default_log_file() -> Path:
    """Get default log file path."""
    if sys.platform == "darwin":  # macOS
        return Path.home() / "Library" / "Logs" / "Claude" / "mcp-server-svcs.log"
    elif sys.platform.startswith("linux"):
        return Path.home() / ".local" / "share" / "svcs" / "mcp-server.log"
    else:  # Windows
        return Path.home() / "AppData" / "Local" / "SVCS" / "mcp-server.log"


def cmd_mcp_start(args):
    """Start the MCP server."""
    try:
        # Check if already running
        pids = get_mcp_server_pids()
        if pids:
            print(f"🔄 MCP server already running (PID: {', '.join(map(str, pids))})")
            print("   Use 'svcs mcp restart' to restart or 'svcs mcp stop' to stop")
            return

        # Get server path
        server_path = get_mcp_server_path()
        
        # Set up log file
        log_file = Path(args.log_file) if args.log_file else get_default_log_file()
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        print(f"🚀 Starting SVCS MCP server...")
        print(f"📄 Server script: {server_path}")
        print(f"📝 Log file: {log_file}")
        
        if args.background:
            # Start in background
            with open(log_file, 'a') as log:
                process = subprocess.Popen(
                    [sys.executable, str(server_path)],
                    stdout=log,
                    stderr=log,
                    start_new_session=True
                )
            
            # Give it a moment to start
            time.sleep(2)
            
            # Check if it's actually running
            if process.poll() is None:
                print(f"✅ MCP server started successfully in background (PID: {process.pid})")
                print(f"📡 Server ready for IDE connections")
                print(f"📄 View logs: tail -f {log_file}")
            else:
                print(f"❌ Failed to start MCP server (process exited)")
                print(f"📄 Check logs: {log_file}")
        else:
            # Start in foreground
            print(f"📡 Server ready for IDE connections")
            print(f"⏹️  Press Ctrl+C to stop")
            subprocess.run([sys.executable, str(server_path)])
            
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        print("   Make sure SVCS is properly installed")
    except Exception as e:
        print(f"❌ Error starting MCP server: {e}")


def cmd_mcp_stop(args):
    """Stop the MCP server."""
    pids = get_mcp_server_pids()
    
    if not pids:
        print("🔍 No MCP server processes found")
        return
    
    print(f"🛑 Stopping MCP server (PID: {', '.join(map(str, pids))})")
    
    stopped_count = 0
    for pid in pids:
        try:
            os.kill(pid, signal.SIGTERM)
            stopped_count += 1
            print(f"   ✅ Stopped process {pid}")
        except ProcessLookupError:
            print(f"   ⚠️  Process {pid} not found (already stopped)")
        except PermissionError:
            print(f"   ❌ Permission denied stopping process {pid}")
        except Exception as e:
            print(f"   ❌ Error stopping process {pid}: {e}")
    
    if stopped_count > 0:
        print(f"✅ Stopped {stopped_count} MCP server process(es)")
    else:
        print("❌ No processes were stopped")


def cmd_mcp_status(args):
    """Check MCP server status."""
    pids = get_mcp_server_pids()
    
    if not pids:
        print("🔴 MCP server is not running")
        print("   Start with: svcs mcp start")
        return
    
    print(f"🟢 MCP server is running")
    for pid in pids:
        try:
            # Get process info
            result = subprocess.run(
                ["ps", "-p", str(pid), "-o", "pid,ppid,lstart,etime,command"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1:
                    print(f"   PID: {pid}")
                    # Parse ps output for additional info
                    parts = lines[1].split()
                    if len(parts) >= 5:
                        etime = parts[4] if len(parts) > 4 else "unknown"
                        print(f"   Uptime: {etime}")
        except Exception as e:
            print(f"   PID: {pid} (details unavailable: {e})")
    
    # Show log file location
    log_file = get_default_log_file()
    if log_file.exists():
        print(f"📄 Log file: {log_file}")
        print(f"   View logs: svcs mcp logs")
    else:
        print(f"📄 Log file: {log_file} (not found)")


def cmd_mcp_restart(args):
    """Restart the MCP server."""
    print("🔄 Restarting MCP server...")
    
    # Stop first
    cmd_mcp_stop(args)
    
    # Wait a moment
    time.sleep(1)
    
    # Start again
    cmd_mcp_start(args)


def cmd_mcp_logs(args):
    """Show MCP server logs."""
    log_file = get_default_log_file()
    
    if not log_file.exists():
        print(f"📄 Log file not found: {log_file}")
        print("   The MCP server may not have been started yet")
        return
    
    try:
        if args.follow:
            # Follow logs (like tail -f)
            print(f"📄 Following MCP server logs: {log_file}")
            print("⏹️  Press Ctrl+C to stop")
            subprocess.run(["tail", "-f", str(log_file)])
        else:
            # Show last N lines
            result = subprocess.run(
                ["tail", "-n", str(args.lines), str(log_file)],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print(f"📄 Last {args.lines} lines from MCP server logs:")
                print("=" * 60)
                print(result.stdout)
            else:
                # Fallback to reading file directly
                with open(log_file, 'r') as f:
                    lines = f.readlines()
                    last_lines = lines[-args.lines:] if len(lines) > args.lines else lines
                    print(f"📄 Last {len(last_lines)} lines from MCP server logs:")
                    print("=" * 60)
                    print(''.join(last_lines))
                    
    except FileNotFoundError:
        print("❌ 'tail' command not found. Showing file contents:")
        try:
            with open(log_file, 'r') as f:
                content = f.read()
                lines = content.split('\n')
                last_lines = lines[-args.lines:] if len(lines) > args.lines else lines
                print('\n'.join(last_lines))
        except Exception as e:
            print(f"❌ Error reading log file: {e}")
    except KeyboardInterrupt:
        print("\n⏹️  Stopped following logs")
    except Exception as e:
        print(f"❌ Error reading logs: {e}")
