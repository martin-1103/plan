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

    # Initialize lock manager
    lock_manager = LockManager()

    # Process different tool types
    if tool_name in ["Write", "Edit"]:
        # Create lock after Write/Edit operations
        file_path = tool_input.get("file_path", "")
        if not file_path:
            sys.exit(0)

        # Clean up expired locks
        lock_manager.utils.cleanup_expired_locks()

        # Create lock for the file (unlock_immediately=False by default)
        if lock_manager.create_lock(file_path, tool_name, session_id):
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

        if lock_manager.mark_completed(file_path, session_id):
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