"""
StateGraph Persistent Checkpoint Manager.
Saves and loads execution states to disk for pause/resume, time-travel, and human review.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional


class StateCheckpointManager:
    """Persists StateGraph checkpoints as structured JSON snapshots."""

    def __init__(self, base_dir: str = ".checkpoints"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def save_checkpoint(self, session_id: str, step: int, state: Dict[str, Any]) -> Path:
        """Persist state dictionary to disk under session folder."""
        session_dir = self.base_dir / session_id
        session_dir.mkdir(parents=True, exist_ok=True)
        target = session_dir / f"step_{step:04d}.json"
        serializable = {k: v for k, v in state.items() if isinstance(v, (str, int, float, bool, list, dict, type(None)))}
        target.write_text(json.dumps(serializable, indent=2), encoding="utf-8")
        return target

    def load_checkpoint(self, session_id: str, step: int = -1) -> Optional[Dict[str, Any]]:
        """Load state snapshot; step=-1 loads latest available checkpoint."""
        session_dir = self.base_dir / session_id
        if not session_dir.exists():
            return None
        files = sorted(session_dir.glob("step_*.json"))
        if not files:
            return None
        target = files[step] if step >= 0 and step < len(files) else files[-1]
        try:
            return json.loads(target.read_text(encoding="utf-8"))
        except Exception:
            return None

    def list_checkpoints(self, session_id: str) -> List[int]:
        """Return all recorded step indices for a session."""
        session_dir = self.base_dir / session_id
        if not session_dir.exists():
            return []
        steps: List[int] = []
        for p in sorted(session_dir.glob("step_*.json")):
            try:
                num = int(p.stem.split("_")[1])
                steps.append(num)
            except (IndexError, ValueError):
                continue
        return steps
