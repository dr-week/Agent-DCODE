"""
Episodic Memory store for recording and recalling past agent trajectories and error-fix lessons.
"""

from datetime import datetime
import json
from typing import Any, Dict, List
from dcode.config import LOGS_DIR

EPISODIC_FILE = LOGS_DIR / "episodic_memory.json"


class EpisodicMemory:
    """Persists successful task trajectories and learned error recoveries across sessions."""

    def __init__(self, max_episodes: int = 50):
        self.max_episodes = max_episodes

    def _load(self) -> List[Dict[str, Any]]:
        if EPISODIC_FILE.exists():
            try:
                return json.loads(EPISODIC_FILE.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                pass
        return []

    def _save(self, episodes: List[Dict[str, Any]]) -> None:
        EPISODIC_FILE.write_text(json.dumps(episodes[-self.max_episodes:], indent=2), encoding="utf-8")

    def record_episode(
        self, agent_name: str, task: str, outcome: str, success: bool, lesson: str = ""
    ) -> Dict[str, Any]:
        episodes = self._load()
        entry = {
            "timestamp": datetime.now().isoformat(),
            "agent": agent_name,
            "task": task,
            "outcome": outcome,
            "success": success,
            "lesson": lesson,
        }
        episodes.append(entry)
        self._save(episodes)
        return entry

    def recall_similar(self, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        words = {w.lower() for w in query.split() if len(w) > 2}
        scored = []
        for ep in self._load():
            text = f"{ep.get('task', '')} {ep.get('lesson', '')}".lower()
            overlap = sum(1 for w in words if w in text)
            if overlap > 0:
                scored.append((overlap, ep))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [ep for _, ep in scored[:limit]]
