#!/usr/bin/env python3
import json
import sys
from pathlib import Path

# Add lib directory to path for imports
sys.path.insert(0, str(Path(__file__).parent / 'lib'))

from lib import LockManager

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

    # Only process Read operations
    if tool_name != "Read":
        sys.exit(0)

    file_path = tool_input.get("file_path", "")
    if not file_path:
        sys.exit(0)

    # Initialize lock manager
    lock_manager = LockManager()

    # Clean up expired locks periodically
    lock_manager.utils.cleanup_expired_locks()

    # Get lock file path
    lock_path = lock_manager.utils.get_lock_path(file_path)

    # Check if file is locked
    if lock_manager.is_valid(lock_path):
        print(f"File is locked, waiting for release or immediate unlock: {file_path}", file=sys.stderr)

        # Wait for lock to be released with immediate unlock support
        if lock_manager.wait_for_release(lock_path, session_id):
            print(f"Lock released (may have been immediately unlocked), proceeding with read: {file_path}")
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

if __name__ == "__main__":
    main()