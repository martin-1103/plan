#!/usr/bin/env python3
"""
Shared library for Claude file lock system.

This module provides centralized lock management functionality
to reduce code duplication and improve maintainability.
"""

from .config import Config
from .lock_utils import LockUtils
from .lock_manager import LockManager

__all__ = ['Config', 'LockUtils', 'LockManager']