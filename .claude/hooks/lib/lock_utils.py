#!/usr/bin/env python3
import hashlib
import json
import time
from pathlib import Path
from typing import List, Tuple

from .config import Config


class LockUtils:
    """Utility functions for lock file operations."""

    def __init__(self, config: Config = None):
        """Initialize with optional config."""
        self.config = config or Config()

    def get_lock_path(self, file_path: str) -> Path:
        """Generate lock file path for given file."""
        # Create hash of file path for safe filename
        file_hash = hashlib.md5(str(file_path).encode()).hexdigest()
        lock_dir = self.config.project_dir / '.claude' / 'hooks' / 'files'

        return lock_dir / f"{file_hash}{self.config['lock_file_extension']}"

    def cleanup_expired_locks(self) -> int:
        """Clean up expired lock files and return count of removed files."""
        lock_dir = self.config.project_dir / '.claude' / 'hooks' / 'files'

        if not lock_dir.exists():
            return 0

        current_time = time.time()
        removed_count = 0

        for lock_file in lock_dir.glob(f"*{self.config['lock_file_extension']}"):
            try:
                lock_data = json.loads(lock_file.read_text())
                lock_time = lock_data.get('timestamp', 0)

                # Remove expired locks
                if (current_time - lock_time) >= self.config['lock_timeout']:
                    lock_file.unlink()
                    removed_count += 1
            except:
                # Remove invalid lock files
                try:
                    lock_file.unlink()
                    removed_count += 1
                except:
                    pass

        if removed_count > 0:
            print(f"Cleaned up {removed_count} expired lock files")

        return removed_count

    def find_session_locks(self, session_id: str) -> List[Tuple[Path, dict]]:
        """Find all lock files belonging to a specific session."""
        lock_dir = self.config.project_dir / '.claude' / 'hooks' / 'files'
        session_locks = []

        if not lock_dir.exists():
            return session_locks

        for lock_file in lock_dir.glob(f"*{self.config['lock_file_extension']}"):
            try:
                lock_data = json.loads(lock_file.read_text())
                if lock_data.get('session_id') == session_id:
                    session_locks.append((lock_file, lock_data))
            except:
                # Skip invalid lock files
                continue

        return session_locks

    def ensure_lock_directory(self) -> Path:
        """Ensure lock directory exists and return its path."""
        lock_dir = self.config.project_dir / '.claude' / 'hooks' / 'files'
        lock_dir.mkdir(parents=True, exist_ok=True)
        return lock_dir

    def read_lock_data(self, lock_path: Path) -> dict:
        """Read and parse lock file data."""
        try:
            return json.loads(lock_path.read_text())
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def write_lock_data(self, lock_path: Path, lock_data: dict) -> bool:
        """Write lock data to file."""
        try:
            lock_path.write_text(json.dumps(lock_data, indent=2))
            return True
        except Exception:
            return False