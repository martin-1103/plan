#!/usr/bin/env python3
import json
import sys
import os
import time
import hashlib
from pathlib import Path

def detect_project_dir():
    """Automatically detect project directory"""
    # Try current working directory first
    current_dir = Path.cwd()

    # Check if .claude directory exists in current or parent directories
    search_dir = current_dir
    max_levels = 10  # Prevent infinite loop

    for _ in range(max_levels):
        claude_dir = search_dir / '.claude'
        if claude_dir.exists() and claude_dir.is_dir():
            return search_dir

        # Move to parent directory
        parent = search_dir.parent
        if parent == search_dir:  # Reached root directory
            break
        search_dir = parent

    # Fallback to user home directory
    try:
        import os
        home_dir = Path(os.path.expanduser('~'))
        if home_dir.exists():
            return home_dir
    except:
        pass

    # Last resort - current working directory
    return Path.cwd()

def get_config():
    """Load lock configuration"""
    # Auto-detect project directory
    project_dir = detect_project_dir()
    config_path = project_dir / '.claude' / 'hooks' / 'config.json'
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
            # Ensure project_dir is set in config
            if 'project_dir' not in config:
                config['project_dir'] = str(project_dir)
            return config
    except:
        return {
            "project_dir": str(detect_project_dir()),
            "lock_timeout": 60,
            "max_wait_time": 120,
            "cleanup_interval": 300,
            "lock_file_extension": ".lock"
        }

def get_lock_path(file_path):
    """Generate lock file path for given file"""
    config = get_config()
    project_dir = Path(config['project_dir'])

    # Create hash of file path for safe filename
    file_hash = hashlib.md5(str(file_path).encode()).hexdigest()
    lock_dir = project_dir / '.claude' / 'lock' / 'files'

    return lock_dir / f"{file_hash}{config['lock_file_extension']}"

def unlock_lock(file_path, session_id):
    """Unlock a lock file for the given file"""
    lock_path = get_lock_path(file_path)

    if not lock_path.exists():
        return False

    try:
        lock_data = json.loads(lock_path.read_text())

        # Check if this lock belongs to the current session
        if lock_data.get('session_id') != session_id:
            print(f"Cannot unlock lock - belongs to different session: {file_path}", file=sys.stderr)
            return False

        # Update lock data before removing
        lock_data['status'] = 'unlocked'
        lock_data['unlock_timestamp'] = time.time()
        lock_data['unlock_method'] = 'operation_complete'

        # Remove the lock file
        lock_path.unlink()

        print(f"Unlocked file: {file_path} (Session: {session_id[:8]}...)")
        return True

    except Exception as e:
        print(f"Failed to unlock file: {e}", file=sys.stderr)
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
    project_dir = Path(config['project_dir'])
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
        # Unlock after Write/Edit operations complete
        file_path = tool_input.get("file_path", "")
        if not file_path:
            sys.exit(0)

        # Clean up expired locks
        cleanup_expired_locks()

        # Unlock the file
        if unlock_lock(file_path, session_id):
            # Success - file unlocked
            sys.exit(0)
        else:
            print(f"Failed to unlock file: {file_path}", file=sys.stderr)
            sys.exit(1)

    elif tool_name == "CompleteEdit":
        # This is no longer needed since we unlock directly after Write/Edit
        # But keep for compatibility - just unlock
        file_path = tool_input.get("file_path", "")
        if not file_path:
            sys.exit(0)

        if unlock_lock(file_path, session_id):
            print(f"Unlocked completed edit: {file_path}")
            sys.exit(0)
        else:
            print(f"Failed to unlock completed edit: {file_path}", file=sys.stderr)
            sys.exit(1)

    else:
        # Other tool types - no action needed
        sys.exit(0)

if __name__ == "__main__":
    main()