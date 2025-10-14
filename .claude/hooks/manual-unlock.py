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
    config_path = project_dir / '.claude' / 'hooks' / 'config.json'
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
    lock_dir = project_dir / '.claude' / 'hooks' / 'files'

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
    project_dir = Path.cwd()
    lock_dir = project_dir / '.claude' / 'hooks' / 'files'

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