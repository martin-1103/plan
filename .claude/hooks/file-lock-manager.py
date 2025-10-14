#!/usr/bin/env python3
import json
import sys
import os
import time
import hashlib
from pathlib import Path

def get_config():
    """Load lock configuration"""
    # Use current working directory for flexibility
    project_dir = Path.cwd()
    config_path = project_dir / '.claude' / 'lock' / 'config.json'
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except:
        return {
            "lock_timeout": 60,
            "max_wait_time": 120,
            "cleanup_interval": 300,
            "lock_file_extension": ".lock"
        }

def get_lock_path(file_path):
    """Generate lock file path for given file"""
    config = get_config()
    project_dir = Path.cwd()

    # Create hash of file path for safe filename
    file_hash = hashlib.md5(str(file_path).encode()).hexdigest()
    lock_dir = project_dir / '.claude' / 'lock' / 'files'

    return lock_dir / f"{file_hash}{config['lock_file_extension']}"

def create_lock(file_path, tool_name, session_id, unlock_immediately=False):
    """Create a lock file for the given file"""
    config = get_config()
    lock_path = get_lock_path(file_path)

    # Ensure lock directory exists
    lock_path.parent.mkdir(parents=True, exist_ok=True)

    # Create enhanced lock data with session tracking
    lock_data = {
        "file_path": str(file_path),
        "tool_name": tool_name,
        "session_id": session_id,
        "timestamp": time.time(),
        "lock_duration": config['lock_timeout'],
        "status": "active",
        "unlock_immediately": unlock_immediately,
        "completion_timestamp": None,
        "unlock_timestamp": None,
        "unlock_method": None
    }

    try:
        # Write lock file
        lock_path.write_text(json.dumps(lock_data, indent=2))
        print(f"Created lock for file: {file_path} (Session: {session_id[:8]}...)")
        return True
    except Exception as e:
        print(f"Failed to create lock file: {e}", file=sys.stderr)
        return False

def mark_lock_completed(file_path, session_id):
    """Mark a lock as completed (ready for immediate unlock)"""
    lock_path = get_lock_path(file_path)

    if not lock_path.exists():
        return False

    try:
        lock_data = json.loads(lock_path.read_text())

        # Check if this lock belongs to the current session
        if lock_data.get('session_id') != session_id:
            return False

        # Update lock status to completed
        lock_data['status'] = 'completed'
        lock_data['completion_timestamp'] = time.time()

        # Write updated lock data
        lock_path.write_text(json.dumps(lock_data, indent=2))
        print(f"Marked lock as completed: {file_path}")
        return True

    except Exception as e:
        print(f"Failed to mark lock as completed: {e}", file=sys.stderr)
        return False

def cleanup_expired_locks():
    """Clean up expired lock files"""
    config = get_config()
    project_dir = Path.cwd()
    lock_dir = project_dir / '.claude' / 'lock' / 'files'

    if not lock_dir.exists():
        return

    current_time = time.time()
    removed_count = 0

    for lock_file in lock_dir.glob(f"*{config['lock_file_extension']}"):
        try:
            lock_data = json.loads(lock_file.read_text())
            lock_time = lock_data.get('timestamp', 0)

            # Remove expired locks
            if (current_time - lock_time) >= config['lock_timeout']:
                lock_file.unlink()
                removed_count += 1
        except:
            # Remove invalid lock files
            try:
                lock_file.unlink()
                removed_count += 1
            except:
                pass

    if removed_count > 0:
        print(f"Cleaned up {removed_count} expired lock files")

def main():
    # Load input from stdin
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON input: {e}", file=sys.stderr)
        sys.exit(1)

    tool_name = input_data.get("tool_name", "")
    tool_input = input_data.get("tool_input", {})
    session_id = input_data.get("session_id", "")

    # Process different tool types
    if tool_name in ["Write", "Edit"]:
        # Create lock after Write/Edit operations
        file_path = tool_input.get("file_path", "")
        if not file_path:
            sys.exit(0)

        # Clean up expired locks
        cleanup_expired_locks()

        # Create lock for the file (unlock_immediately=False by default)
        if create_lock(file_path, tool_name, session_id):
            # Success - lock created
            sys.exit(0)
        else:
            print(f"Failed to create lock for file: {file_path}", file=sys.stderr)
            sys.exit(1)

    elif tool_name == "CompleteEdit":
        # Mark lock as completed (ready for unlock)
        file_path = tool_input.get("file_path", "")
        if not file_path:
            sys.exit(0)

        if mark_lock_completed(file_path, session_id):
            print(f"Marked edit as completed: {file_path}")
            sys.exit(0)
        else:
            print(f"Failed to mark edit as completed: {file_path}", file=sys.stderr)
            sys.exit(1)

    else:
        # Other tool types - no action needed
        sys.exit(0)

if __name__ == "__main__":
    main()