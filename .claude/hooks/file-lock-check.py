#!/usr/bin/env python3
import json
import sys
import time
from pathlib import Path

# Add lib directory to path for imports
sys.path.insert(0, str(Path(__file__).parent / 'lib'))

from lib import LockManager

# Setup logging
LOG_FILE = Path(__file__).parent / 'logs' / 'lock_check.log'
LOG_FILE.parent.mkdir(exist_ok=True)

def log_message(message):
    """Log message to file with timestamp"""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}\n"
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(log_entry)
    print(f"[LOCK-CHECK] {message}")  # Also print to stdout

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

    # Log incoming request
    log_message(f"REQUEST: tool={tool_name}, session={session_id[:8]}...")

    # Only process Read operations
    if tool_name != "Read":
        log_message(f"IGNORED: tool={tool_name} not Read, exiting")
        sys.exit(0)

    file_path = tool_input.get("file_path", "")
    if not file_path:
        log_message(f"EXIT: No file_path provided")
        sys.exit(0)

    log_message(f"PROCESSING: Read request for {file_path}")

    # Initialize lock manager
    lock_manager = LockManager()

    # Clean up expired locks periodically
    lock_manager.utils.cleanup_expired_locks()

    # Get lock file path
    lock_path = lock_manager.utils.get_lock_path(file_path)

    # Check if file is locked
    if lock_manager.is_valid(lock_path):
        log_message(f"LOCKED: File is locked, waiting for release: {file_path}")
        print(f"File is locked, waiting for release or immediate unlock: {file_path}", file=sys.stderr)

        # Wait for lock to be released with immediate unlock support
        if lock_manager.wait_for_release(lock_path, session_id):
            log_message(f"RELEASED: Lock released, proceeding with read: {file_path}")
            print(f"Lock released (may have been immediately unlocked), proceeding with read: {file_path}")
        else:
            # Timeout reached, deny the operation
            log_message(f"TIMEOUT: Lock wait exceeded, denying read: {file_path}")
            output = {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": f"File {file_path} is locked and wait timeout exceeded"
                }
            }
            print(json.dumps(output))
            sys.exit(0)
    else:
        log_message(f"UNLOCKED: File is not locked, allowing read: {file_path}")

    # File is not locked, allow the operation
    log_message(f"ALLOWED: Read operation allowed for: {file_path}")
    sys.exit(0)

if __name__ == "__main__":
    main()