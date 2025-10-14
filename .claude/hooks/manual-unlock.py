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

    session_id = input_data.get("session_id", "")
    if not session_id:
        print("No session_id provided", file=sys.stderr)
        sys.exit(1)

    # Initialize lock manager
    lock_manager = LockManager()

    # Check if this is a specific file unlock or all files
    tool_name = input_data.get("tool_name", "")
    tool_input = input_data.get("tool_input", {})

    if tool_name == "Unlock" and tool_input.get("file_path"):
        # Unlock specific file
        file_path = tool_input.get("file_path")
        success, message = lock_manager.unlock_file(file_path, session_id, "manual")

        if success:
            print(message)
            sys.exit(0)
        else:
            print(f"Unlock failed: {message}", file=sys.stderr)
            sys.exit(1)
    else:
        # Unlock all files for this session
        unlocked_count = lock_manager.unlock_session_files(session_id)

        if unlocked_count > 0:
            print(f"Manual unlock completed: {unlocked_count} files unlocked")
        else:
            print("No files to unlock for this session")

    sys.exit(0)

if __name__ == "__main__":
    main()