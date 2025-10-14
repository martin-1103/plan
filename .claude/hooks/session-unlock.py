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
        print("No session_id provided, skipping unlock", file=sys.stderr)
        sys.exit(0)

    # Initialize lock manager
    lock_manager = LockManager()

    # Unlock all files for this session
    unlocked_count = lock_manager.unlock_session_files(session_id)

    if unlocked_count > 0:
        print(f"Session unlock completed: {unlocked_count} files unlocked")
    else:
        print("No locked files found for this session")

    sys.exit(0)

if __name__ == "__main__":
    main()