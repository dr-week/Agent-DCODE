"""
Global thread-safe session management for TransparencyTracker.
"""

import threading
from typing import Optional
from dcode.observability.transparency_tracker import TransparencyTracker

_current_tracker: Optional[TransparencyTracker] = None
_tracker_lock = threading.Lock()


def get_tracker() -> TransparencyTracker:
    """Get or create current tracker."""
    global _current_tracker
    if _current_tracker is None:
        with _tracker_lock:
            if _current_tracker is None:
                _current_tracker = TransparencyTracker()
    return _current_tracker


def create_new_session() -> TransparencyTracker:
    """Create new tracking session."""
    global _current_tracker
    with _tracker_lock:
        _current_tracker = TransparencyTracker()
        return _current_tracker


def reset_tracker() -> None:
    """Reset tracker (for cleanup)."""
    global _current_tracker
    with _tracker_lock:
        _current_tracker = None
