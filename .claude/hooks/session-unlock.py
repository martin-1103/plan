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

def unlock_session_files(session_id):
    """Unlock all files locked by specific session"""
    config = get_config()
    project_dir = Path(config['project_dir'])
    lock_dir = project_dir / '.claude' / 'lock' / 'files'

    if not lock_dir.exists():
        return 0

    unlocked_count = 0
    current_time = time.time()

    for lock_file in lock_dir.glob(f"*{config['lock_file_extension']}"):
        try:
            lock_data = json.loads(lock_file.read_text())

            # Check if this lock belongs to the current session
            if lock_data.get('session_id') == session_id:
                # Update lock status to completed/unlocked
                lock_data['status'] = 'unlocked'
                lock_data['unlock_timestamp'] = current_time
                lock_data['unlock_method'] = 'session_end'

                # Remove the lock file (immediate unlock)
                lock_file.unlink()
                unlocked_count += 1

                print(f"Unlocked file: {lock_data.get('file_path', 'unknown')}")

        except Exception as e:
            # Remove invalid lock files
            try:
                lock_file.unlink()
                unlocked_count += 1
                print(f"Removed invalid lock file: {lock_file.name}")
            except:
                pass

    return unlocked_count

def main():
    # Load input from stdin
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON input: {e}", file=sys.stderr)
        sys.exit(1)

    session_id = input_data.get("session_id", "")
    if not session_id:
        print("No session_id provided, skipping unlock", file=sys.stderr)
        sys.exit(0)

    # Unlock all files for this session
    unlocked_count = unlock_session_files(session_id)

    if unlocked_count > 0:
        print(f"Session unlock completed: {unlocked_count} files unlocked")
    else:
        print("No locked files found for this session")

    sys.exit(0)

if __name__ == "__main__":
    main()