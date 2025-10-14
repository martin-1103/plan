#!/usr/bin/env python3
import json
import sys
import time
from pathlib import Path

# Add lib directory to path for imports
sys.path.insert(0, str(Path(__file__).parent / 'lib'))

from lib import LockManager, Config

# Setup logging from config
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
        'log_file': log_dir / 'lock_check.log'
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
            print(f"[LOCK-CHECK ERROR] Failed to write to log: {e}")

    # Log to console
    if log_config['console_enabled']:
        print(f"[LOCK-CHECK] {message}")

def main():
    # Setup logging from config
    log_config = setup_logging()

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
    log_message(f"REQUEST: tool={tool_name}, session={session_id[:8]}...", log_config)

    # Only process Read operations
    if tool_name != "Read":
        log_message(f"IGNORED: tool={tool_name} not Read, exiting", log_config)
        sys.exit(0)

    file_path = tool_input.get("file_path", "")
    if not file_path:
        log_message(f"EXIT: No file_path provided", log_config)
        sys.exit(0)

    log_message(f"PROCESSING: Read request for {file_path}", log_config)

    # Initialize lock manager
    lock_manager = LockManager()

    # Clean up expired locks periodically
    lock_manager.utils.cleanup_expired_locks()

    # Get lock file path
    lock_path = lock_manager.utils.get_lock_path(file_path)

    # Check if file is locked
    if lock_manager.is_valid(lock_path):
        log_message(f"LOCKED: File is locked, waiting for release: {file_path}", log_config)
        print(f"File is locked, waiting for release or immediate unlock: {file_path}", file=sys.stderr)

        # Wait for lock to be released with immediate unlock support
        if lock_manager.wait_for_release(lock_path, session_id):
            log_message(f"RELEASED: Lock released, proceeding with read: {file_path}", log_config)
            print(f"Lock released (may have been immediately unlocked), proceeding with read: {file_path}")
        else:
            # Timeout reached, deny the operation
            log_message(f"TIMEOUT: Lock wait exceeded, denying read: {file_path}", log_config)
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
        log_message(f"UNLOCKED: File is not locked, allowing read: {file_path}", log_config)

    # File is not locked, allow the operation
    log_message(f"ALLOWED: Read operation allowed for: {file_path}", log_config)
    sys.exit(0)

if __name__ == "__main__":
    main()