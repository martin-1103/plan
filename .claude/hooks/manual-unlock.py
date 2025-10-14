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

def unlock_file(file_path, session_id, unlock_method="manual"):
    """Unlock a specific file"""
    lock_path = get_lock_path(file_path)

    if not lock_path.exists():
        return False, "No lock file found"

    try:
        lock_data = json.loads(lock_path.read_text())

        # Check if this lock belongs to the current session
        if lock_data.get('session_id') != session_id:
            return False, "Lock belongs to different session"

        # Update lock status before removal
        lock_data['status'] = 'unlocked'
        lock_data['unlock_timestamp'] = time.time()
        lock_data['unlock_method'] = unlock_method

        # Remove the lock file (immediate unlock)
        lock_path.unlink()

        print(f"Manually unlocked file: {file_path}")
        return True, f"Successfully unlocked: {file_path}"

    except Exception as e:
        return False, f"Error unlocking file: {e}"

def unlock_all_session_files(session_id):
    """Unlock all files locked by specific session"""
    config = get_config()
    project_dir = Path(config['project_dir'])
    lock_dir = project_dir / '.claude' / 'lock' / 'files'

    if not lock_dir.exists():
        return 0, "Lock directory not found"

    unlocked_count = 0
    errors = []

    for lock_file in lock_dir.glob(f"*{config['lock_file_extension']}"):
        try:
            lock_data = json.loads(lock_file.read_text())

            if lock_data.get('session_id') == session_id:
                file_path = lock_data.get('file_path', '')
                success, message = unlock_file(file_path, session_id, "manual_all")
                if success:
                    unlocked_count += 1
                else:
                    errors.append(f"{file_path}: {message}")

        except Exception as e:
            errors.append(f"{lock_file.name}: {e}")

    return unlocked_count, "\n".join(errors) if errors else "All files unlocked successfully"

def main():
    # Load input from stdin
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON input: {e}", file=sys.stderr)
        sys.exit(1)

    session_id = input_data.get("session_id", "")
    if not session_id:
        print("No session_id provided", file=sys.stderr)
        sys.exit(1)

    # Check if this is a specific file unlock or all files
    tool_name = input_data.get("tool_name", "")
    tool_input = input_data.get("tool_input", {})

    if tool_name == "Unlock" and tool_input.get("file_path"):
        # Unlock specific file
        file_path = tool_input.get("file_path")
        success, message = unlock_file(file_path, session_id)

        if success:
            print(message)
            sys.exit(0)
        else:
            print(f"Unlock failed: {message}", file=sys.stderr)
            sys.exit(1)
    else:
        # Unlock all files for this session
        unlocked_count, status_message = unlock_all_session_files(session_id)

        if unlocked_count > 0:
            print(f"Manual unlock completed: {unlocked_count} files unlocked")
        else:
            print(f"No files to unlock: {status_message}")

    sys.exit(0)

if __name__ == "__main__":
    main()