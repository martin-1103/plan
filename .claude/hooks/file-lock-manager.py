#!/usr/bin/env python3
import json
import sys
import time
import argparse
from pathlib import Path

# Add lib directory to path for imports
sys.path.insert(0, str(Path(__file__).parent / 'lib'))

from lib import LockManager

# Setup logging from config
from lib import Config

def setup_logging():
    """Setup logging based on config."""
    config = Config()
    log_config = config.get('logging', {})

    if not log_config.get('enabled', True):
        return None

    log_dir = Path(__file__).parent / log_config.get('log_dir', 'logs')
    log_dir.mkdir(exist_ok=True)

    return {
        'file_enabled': log_config.get('log_to_file', True),
        'console_enabled': log_config.get('log_to_console', True),
        'log_file': log_dir / 'lock_manager.log'
    }

def log_message(message, log_config=None):
    """Log message to file and/or console based on config."""
    if log_config is None:
        log_config = setup_logging()

    if log_config is None:
        return  # Logging disabled

    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}\n"

    # Log to file
    if log_config['file_enabled']:
        try:
            with open(log_config['log_file'], 'a', encoding='utf-8') as f:
                f.write(log_entry)
        except Exception as e:
            # Fallback to console if file logging fails
            print(f"[LOCK-MANAGER ERROR] Failed to write to log: {e}")

    # Log to console
    if log_config['console_enabled']:
        print(f"[LOCK-MANAGER] {message}")

def main():
    # Setup logging from config
    log_config = setup_logging()

    # Parse command line arguments
    parser = argparse.ArgumentParser(description='File lock manager')
    parser.add_argument('--event', type=str, help='Hook event (PreToolUse, PostToolUse, CompleteEdit)')
    args = parser.parse_args()

    hook_event = args.event or "UNKNOWN"

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
    log_message(f"REQUEST: tool={tool_name}, event={hook_event}, session={session_id[:8]}...", log_config)

    # Initialize lock manager
    lock_manager = LockManager()

    # Process different tool types based on hook event
    if tool_name in ["Write", "Edit"]:
        file_path = tool_input.get("file_path", "")
        if not file_path:
            log_message(f"EXIT: No file_path provided", log_config)
            sys.exit(0)

        log_message(f"PROCESSING: file={file_path}, action={hook_event}", log_config)

        # Clean up expired locks
        lock_manager.utils.cleanup_expired_locks()

        if hook_event == "PreToolUse":
            # PRE-TOOL: Create lock BEFORE edit operation
            log_message(f"PRE-TOOL: Attempting to create lock for {file_path}")
            if lock_manager.create_lock(file_path, tool_name, session_id, unlock_immediately=False):
                log_message(f"SUCCESS: Lock created for {file_path}")
                print(f"Created lock before edit: {file_path}")
                sys.exit(0)
            else:
                log_message(f"PRE-TOOL: Lock creation failed for {file_path}, checking if file already locked")
                # If lock already exists, check if we can proceed
                lock_path = lock_manager.utils.get_lock_path(file_path)
                if lock_manager.is_valid(lock_path):
                    log_message(f"PRE-TOOL: File already locked, waiting for release: {file_path}")
                    print(f"File already locked, waiting before edit: {file_path}", file=sys.stderr)
                    # Wait for lock to be released (with timeout)
                    if lock_manager.wait_for_release(lock_path, session_id):
                        log_message(f"PRE-TOOL: Lock released, creating new lock: {file_path}")
                        # Lock released, create new lock
                        if lock_manager.create_lock(file_path, tool_name, session_id, unlock_immediately=False):
                            log_message(f"SUCCESS: Lock created after wait: {file_path}")
                            print(f"Created lock after wait: {file_path}")
                            sys.exit(0)
                        else:
                            log_message(f"FAILED: Could not create lock after wait: {file_path}")
                            print(f"Failed to create lock after wait: {file_path}", file=sys.stderr)
                            sys.exit(1)
                    else:
                        log_message(f"TIMEOUT: Wait exceeded for locked file: {file_path}")
                        # Timeout reached, deny the edit operation
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
                    log_message(f"PRE-TOOL: Lock invalid, proceeding to create new lock: {file_path}")
                    # Lock is not valid, proceed to create new lock
                    if lock_manager.create_lock(file_path, tool_name, session_id, unlock_immediately=False):
                        log_message(f"SUCCESS: Lock created (invalid cleared): {file_path}")
                        print(f"Created lock (invalid lock cleared): {file_path}")
                        sys.exit(0)
                    else:
                        log_message(f"FAILED: Could not create lock: {file_path}")
                        print(f"Failed to create lock: {file_path}", file=sys.stderr)
                        sys.exit(1)

        elif hook_event == "PostToolUse":
            # POST-TOOL: Immediately unlock lock AFTER edit operation
            log_message(f"POST-TOOL: Attempting to unlock file: {file_path}")
            success, message = lock_manager.unlock_file(file_path, session_id, "edit_completed")
            if success:
                log_message(f"SUCCESS: File unlocked after edit: {file_path}")
                print(f"Immediately unlocked after edit: {file_path}")
                sys.exit(0)
            else:
                log_message(f"FAILED: Unlock failed: {file_path} - {message}")
                print(f"Failed to unlock after edit: {file_path} - {message}", file=sys.stderr)
                # Try to mark as completed as fallback
                if lock_manager.mark_completed(file_path, session_id):
                    log_message(f"FALLBACK: Marked as completed: {file_path}")
                    print(f"Marked edit as completed (fallback): {file_path}")
                    sys.exit(0)
                else:
                    log_message(f"FAILED: Both unlock and complete failed: {file_path}")
                    print(f"Failed both unlock and complete: {file_path}", file=sys.stderr)
                    sys.exit(1)

    elif tool_name == "CompleteEdit":
        # Mark lock as completed (ready for unlock)
        file_path = tool_input.get("file_path", "")
        if not file_path:
            log_message(f"COMPLETE: No file_path provided")
            sys.exit(0)

        log_message(f"COMPLETE: Marking edit as completed: {file_path}")
        if lock_manager.mark_completed(file_path, session_id):
            log_message(f"SUCCESS: Edit marked as completed: {file_path}")
            print(f"Marked edit as completed: {file_path}")
            sys.exit(0)
        else:
            log_message(f"FAILED: Could not mark edit as completed: {file_path}")
            print(f"Failed to mark edit as completed: {file_path}", file=sys.stderr)
            sys.exit(1)

    else:
        # Other tool types - no action needed
        log_message(f"IGNORED: tool={tool_name} not handled")
        sys.exit(0)

if __name__ == "__main__":
    main()