"""
Agent Harness Trajectory Ledger (<100 lines).
Appends execution steps, tool interactions, diffs, and metrics to structured JSONL files.
"""

import json
import os
import time
from typing import Any, Dict, List, Optional
from dcode.config import LOGS_DIR


class TrajectoryRecorder:
    """Manages append-only JSONL execution journals for full agent trajectory replay."""

    def __init__(self, log_path: Optional[str] = None):
        os.makedirs(LOGS_DIR, exist_ok=True)
        self.log_path = log_path or os.path.join(LOGS_DIR, f"trajectory_{int(time.time())}.jsonl")
        self.steps: List[Dict[str, Any]] = []

    def log_step(
        self,
        step_index: int,
        action_name: str,
        input_data: Any,
        output_data: Any,
        diff: str = "",
        tokens: int = 0,
        cost_usd: float = 0.0,
        latency_ms: float = 0.0,
        status: str = "ok",
    ) -> Dict[str, Any]:
        """Record an execution step to memory and append to the JSONL log file."""
        entry = {
            "step": step_index,
            "timestamp": time.time(),
            "action": action_name,
            "input": input_data,
            "output": output_data,
            "diff_lines": len(diff.splitlines()) if diff else 0,
            "tokens": tokens,
            "cost_usd": round(cost_usd, 6),
            "latency_ms": round(latency_ms, 2),
            "status": status,
        }
        self.steps.append(entry)
        try:
            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")
        except Exception:
            pass
        return entry

    def read_trajectory(self) -> List[Dict[str, Any]]:
        """Read back the saved JSONL trajectory."""
        if not os.path.exists(self.log_path):
            return list(self.steps)
        entries = []
        with open(self.log_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    entries.append(json.loads(line))
        return entries
