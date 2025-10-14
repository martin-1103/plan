#!/usr/bin/env python3
import json
import sys
import os
import time
import hashlib
import stat
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

def is_lock_valid(lock_path, config):
    """Check if lock file is still valid (not expired or completed)"""
    if not lock_path.exists():
        return False

    try:
        lock_data = json.loads(lock_path.read_text())
        current_time = time.time()
        lock_time = lock_data.get('timestamp', 0)

        # Check if lock has expired
        is_expired = (current_time - lock_time) >= config['lock_timeout']

        # Check if lock is marked as completed (ready for unlock)
        is_completed = lock_data.get('status') == 'completed'

        # Check if lock should be unlocked immediately
        unlock_immediately = lock_data.get('unlock_immediately', False)

        # Lock is invalid if expired or completed and should be unlocked
        if is_expired or (is_completed and unlock_immediately):
            return False

        return True
    except:
        # Invalid lock file, treat as expired
        return False

def can_unlock_immediately(lock_path, session_id):
    """Check if lock can be unlocked immediately (completed status)"""
    if not lock_path.exists():
        return False

    try:
        lock_data = json.loads(lock_path.read_text())

        # Can unlock if:
        # 1. Lock belongs to this session
        # 2. Lock status is 'completed'
        # 3. Not already unlocked
        return (
            lock_data.get('session_id') == session_id and
            lock_data.get('status') == 'completed' and
            lock_data.get('unlock_timestamp') is None
        )
    except:
        return False

def unlock_immediately(lock_path, session_id):
    """Immediately unlock a completed lock"""
    try:
        lock_data = json.loads(lock_path.read_text())

        # Verify ownership
        if lock_data.get('session_id') != session_id:
            return False

        # Update lock data
        lock_data['status'] = 'unlocked'
        lock_data['unlock_timestamp'] = time.time()
        lock_data['unlock_method'] = 'immediate_completion'

        # Remove the lock file
        lock_path.unlink()

        file_path = lock_data.get('file_path', 'unknown')
        print(f"Immediately unlocked completed file: {file_path}")
        return True

    except Exception as e:
        print(f"Failed to immediately unlock: {e}", file=sys.stderr)
        return False

def wait_for_lock(lock_path, config, session_id):
    """Wait for lock to be released or timeout with immediate unlock support"""
    start_time = time.time()
    max_wait = config['max_wait_time']

    while time.time() - start_time < max_wait:
        # Check if lock can be immediately unlocked (completed status)
        if can_unlock_immediately(lock_path, session_id):
            if unlock_immediately(lock_path, session_id):
                return True  # Lock immediately unlocked

        # Check if lock is no longer valid (expired or removed)
        if not is_lock_valid(lock_path, config):
            return True  # Lock released

        # Wait 1 second before checking again
        time.sleep(1)

    return False  # Timeout reached

def cleanup_expired_locks():
    """Clean up expired lock files"""
    config = get_config()
    project_dir = Path(config['project_dir'])
    lock_dir = project_dir / '.claude' / 'lock' / 'files'

    if not lock_dir.exists():
        return

    current_time = time.time()
    for lock_file in lock_dir.glob(f"*{config['lock_file_extension']}"):
        try:
            lock_data = json.loads(lock_file.read_text())
            lock_time = lock_data.get('timestamp', 0)

            # Remove expired locks
            if (current_time - lock_time) >= config['lock_timeout']:
                lock_file.unlink()
        except:
            # Remove invalid lock files
            try:
                lock_file.unlink()
            except:
                pass

def create_lock(file_path, tool_name, session_id):
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

    # Process Read operations (check lock)
    if tool_name == "Read":
        file_path = tool_input.get("file_path", "")
        if not file_path:
            sys.exit(0)

        # Get configuration
        config = get_config()

        # Clean up expired locks periodically
        cleanup_expired_locks()

        # Get lock file path
        lock_path = get_lock_path(file_path)

        # Check if file is locked
        if is_lock_valid(lock_path, config):
            print(f"File is locked, waiting for release: {file_path}", file=sys.stderr)

            # Wait for lock to be released
            if wait_for_lock(lock_path, config, session_id):
                print(f"Lock released, proceeding with read: {file_path}")
            else:
                # Timeout reached, deny the operation
                output = {
                    "hookSpecificOutput": {
                        "hookEventName": "PreToolUse",
                        "permissionDecision": "deny",
                        "permissionDecisionReason": f"File {file_path} is locked and wait timeout exceeded"
                    }
                }
                print(json.dumps(output))
                sys.exit(0)

        # File is not locked, allow the operation
        sys.exit(0)

    # Process Write/Edit operations (create lock)
    elif tool_name in ["Write", "Edit"]:
        file_path = tool_input.get("file_path", "")
        if not file_path:
            sys.exit(0)

        # Get configuration
        config = get_config()

        # Clean up expired locks
        cleanup_expired_locks()

        # Get lock file path
        lock_path = get_lock_path(file_path)

        # Check if file is already locked by another session
        if is_lock_valid(lock_path, config):
            print(f"File is locked, waiting for release: {file_path}", file=sys.stderr)

            # Wait for lock to be released
            if wait_for_lock(lock_path, config, session_id):
                print(f"Lock released, creating new lock for {file_path}")
            else:
                # Timeout reached, deny the operation
                output = {
                    "hookSpecificOutput": {
                        "hookEventName": "PreToolUse",
                        "permissionDecision": "deny",
                        "permissionDecisionReason": f"File {file_path} is locked and wait timeout exceeded"
                    }
                }
                print(json.dumps(output))
                sys.exit(0)

        # Create lock for the file
        if create_lock(file_path, tool_name, session_id):
            # Success - lock created, allow operation
            sys.exit(0)
        else:
            print(f"Failed to create lock for file: {file_path}", file=sys.stderr)
            sys.exit(1)

    else:
        # Other tool types - no action needed
        sys.exit(0)

if __name__ == "__main__":
    main()