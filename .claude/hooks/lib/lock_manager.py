#!/usr/bin/env python3
import json
import time
from pathlib import Path
from typing import Tuple, Optional

from .config import Config
from .lock_utils import LockUtils


class LockManager:
    """Core lock management operations."""

    def __init__(self, config: Config = None):
        """Initialize with optional config."""
        self.config = config or Config()
        self.utils = LockUtils(self.config)

    def create_lock(self, file_path: str, tool_name: str, session_id: str,
                   unlock_immediately: bool = False) -> bool:
        """Create a lock file for the given file."""
        lock_path = self.utils.get_lock_path(file_path)

        # Ensure lock directory exists
        self.utils.ensure_lock_directory()

        # Create enhanced lock data with session tracking
        lock_data = {
            "file_path": str(file_path),
            "tool_name": tool_name,
            "session_id": session_id,
            "timestamp": time.time(),
            "lock_duration": self.config['lock_timeout'],
            "status": "active",
            "unlock_immediately": unlock_immediately,
            "completion_timestamp": None,
            "unlock_timestamp": None,
            "unlock_method": None
        }

        if self.utils.write_lock_data(lock_path, lock_data):
            print(f"Created lock for file: {file_path} (Session: {session_id[:8]}...)")
            return True
        else:
            print(f"Failed to create lock file: {file_path}", file='stderr')
            return False

    def mark_completed(self, file_path: str, session_id: str) -> bool:
        """Mark a lock as completed (ready for immediate unlock)."""
        lock_path = self.utils.get_lock_path(file_path)

        if not lock_path.exists():
            return False

        lock_data = self.utils.read_lock_data(lock_path)
        if not lock_data:
            return False

        # Check if this lock belongs to the current session
        if lock_data.get('session_id') != session_id:
            return False

        # Update lock status to completed
        lock_data['status'] = 'completed'
        lock_data['completion_timestamp'] = time.time()

        if self.utils.write_lock_data(lock_path, lock_data):
            print(f"Marked lock as completed: {file_path}")
            return True
        else:
            print(f"Failed to mark lock as completed: {file_path}", file='stderr')
            return False

    def is_valid(self, lock_path: Path) -> bool:
        """Check if lock file is still valid (not expired or completed)."""
        if not lock_path.exists():
            return False

        lock_data = self.utils.read_lock_data(lock_path)
        if not lock_data:
            return False

        current_time = time.time()
        lock_time = lock_data.get('timestamp', 0)

        # Check if lock has expired
        is_expired = (current_time - lock_time) >= self.config['lock_timeout']

        # Check if lock is marked as completed and should be unlocked immediately
        is_completed = lock_data.get('status') == 'completed'
        unlock_immediately = lock_data.get('unlock_immediately', False)

        # Lock is invalid if expired or completed and should be unlocked
        return not (is_expired or (is_completed and unlock_immediately))

    def can_unlock_immediately(self, lock_path: Path, session_id: str) -> bool:
        """Check if lock can be unlocked immediately (completed status)."""
        if not lock_path.exists():
            return False

        lock_data = self.utils.read_lock_data(lock_path)
        if not lock_data:
            return False

        # Can unlock if:
        # 1. Lock belongs to this session
        # 2. Lock status is 'completed'
        # 3. Not already unlocked
        return (
            lock_data.get('session_id') == session_id and
            lock_data.get('status') == 'completed' and
            lock_data.get('unlock_timestamp') is None
        )

    def unlock_immediately(self, lock_path: Path, session_id: str) -> bool:
        """Immediately unlock a completed lock."""
        lock_data = self.utils.read_lock_data(lock_path)
        if not lock_data:
            return False

        # Verify ownership
        if lock_data.get('session_id') != session_id:
            return False

        # Update lock data
        lock_data['status'] = 'unlocked'
        lock_data['unlock_timestamp'] = time.time()
        lock_data['unlock_method'] = 'immediate_completion'

        # Remove the lock file
        try:
            lock_path.unlink()
            file_path = lock_data.get('file_path', 'unknown')
            print(f"Immediately unlocked completed file: {file_path}")
            return True
        except Exception as e:
            print(f"Failed to immediately unlock: {e}", file='stderr')
            return False

    def wait_for_release(self, lock_path: Path, session_id: str) -> bool:
        """Wait for lock to be released or timeout with immediate unlock support."""
        start_time = time.time()
        max_wait = self.config['max_wait_time']

        while time.time() - start_time < max_wait:
            # Check if lock can be immediately unlocked (completed status)
            if self.can_unlock_immediately(lock_path, session_id):
                if self.unlock_immediately(lock_path, session_id):
                    return True  # Lock immediately unlocked

            # Check if lock is no longer valid (expired or removed)
            if not self.is_valid(lock_path):
                return True  # Lock released

            # Wait 1 second before checking again
            time.sleep(1)

        return False  # Timeout reached

    def unlock_file(self, file_path: str, session_id: str,
                   unlock_method: str = "manual") -> Tuple[bool, str]:
        """Unlock a specific file."""
        lock_path = self.utils.get_lock_path(file_path)

        if not lock_path.exists():
            return False, "No lock file found"

        lock_data = self.utils.read_lock_data(lock_path)
        if not lock_data:
            return False, "Invalid lock file"

        # Check if this lock belongs to the current session
        if lock_data.get('session_id') != session_id:
            return False, "Lock belongs to different session"

        # Update lock status before removal
        lock_data['status'] = 'unlocked'
        lock_data['unlock_timestamp'] = time.time()
        lock_data['unlock_method'] = unlock_method

        # Remove the lock file (immediate unlock)
        try:
            lock_path.unlink()
            print(f"Manually unlocked file: {file_path}")
            return True, f"Successfully unlocked: {file_path}"
        except Exception as e:
            return False, f"Error unlocking file: {e}"

    def unlock_session_files(self, session_id: str) -> int:
        """Unlock all files locked by specific session."""
        session_locks = self.utils.find_session_locks(session_id)
        unlocked_count = 0
        current_time = time.time()

        for lock_file, lock_data in session_locks:
            try:
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