#!/usr/bin/env python3
import json
from pathlib import Path
from typing import Dict, Any


class Config:
    """Centralized configuration management for lock system."""

    DEFAULT_CONFIG = {
        "lock_timeout": 60,
        "max_wait_time": 120,
        "cleanup_interval": 300,
        "lock_file_extension": ".lock",
        "immediate_unlock_enabled": True,
        "session_cleanup_enabled": True,
        "completion_status_timeout": 5,
        "version": "2.0.0"
    }

    def __init__(self, project_dir: Path = None):
        """Initialize config with optional project directory."""
        self.project_dir = project_dir or Path.cwd()
        self._config = None

    @property
    def config(self) -> Dict[str, Any]:
        """Lazy load configuration."""
        if self._config is None:
            self._config = self._load_config()
        return self._config

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or return defaults."""
        config_path = self.project_dir / '.claude' / 'hooks' / 'config.json'
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                # Merge with defaults to ensure all keys exist
                return {**self.DEFAULT_CONFIG, **config}
        except (FileNotFoundError, json.JSONDecodeError):
            return self.DEFAULT_CONFIG.copy()

    def get(self, key: str, default=None):
        """Get configuration value."""
        return self.config.get(key, default)

    def __getitem__(self, key: str):
        """Allow dictionary-style access."""
        return self.config[key]

    def __contains__(self, key: str):
        """Allow 'in' operator."""
        return key in self.config