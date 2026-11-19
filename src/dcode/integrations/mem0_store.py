"""
Phase 4: Mem0 Persistent Long-Term Agent Memory Adapter (mem0ai/mem0).
Persists user preferences, codebase conventions, and debugging insights across sessions
using Mem0 or a local SQLite FTS/keyword fallback database.
"""

import os
import sqlite3
import time
from typing import Any, Dict, List, Optional
from dcode.config import LOGS_DIR

try:
    from mem0 import Memory  # type: ignore

    HAS_MEM0 = True
except ImportError:
    Memory = None  # type: ignore
    HAS_MEM0 = False


class Mem0Store:
    """Cross-session semantic memory store wrapping mem0ai with SQLite persistence fallback."""

    def __init__(self, db_path: Optional[str] = None):
        os.makedirs(LOGS_DIR, exist_ok=True)
        self.db_path = db_path or os.path.join(LOGS_DIR, "mem0_memory.sqlite3")
        self.mem0_client = None
        if HAS_MEM0 and Memory is not None:
            try:
                self.mem0_client = Memory()
            except Exception:
                self.mem0_client = None
        self._init_sqlite()

    def _init_sqlite(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """CREATE TABLE IF NOT EXISTS memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    content TEXT NOT NULL,
                    category TEXT DEFAULT 'general',
                    created_at REAL NOT NULL
                )"""
            )

    def remember(self, content: str, user_id: str = "default", category: str = "general") -> Dict[str, Any]:
        """Store a long-term memory entry for a specific user or project."""
        if self.mem0_client is not None:
            try:
                self.mem0_client.add(content, user_id=user_id, metadata={"category": category})
            except Exception:
                pass
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.execute(
                "INSERT INTO memories (user_id, content, category, created_at) VALUES (?, ?, ?, ?)",
                (user_id, content, category, time.time()),
            )
            row_id = cur.lastrowid
        return {"id": row_id, "user_id": user_id, "category": category, "backend": "mem0" if self.mem0_client else "sqlite"}

    def recall(self, query: str, user_id: str = "default", limit: int = 5) -> List[Dict[str, Any]]:
        """Retrieve relevant long-term memories ranked by keyword overlap."""
        terms = [t.lower() for t in query.split() if len(t) > 2]
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT id, content, category, created_at FROM memories WHERE user_id = ? ORDER BY id DESC",
                (user_id,),
            ).fetchall()
        scored = []
        for r_id, text, cat, ts in rows:
            low = text.lower()
            score = sum(1 for t in terms if t in low) if terms else 1
            if score > 0 or not terms:
                scored.append({"id": r_id, "content": text, "category": cat, "score": score, "created_at": ts})
        scored.sort(key=lambda x: (x["score"], x["created_at"]), reverse=True)
        return scored[:limit]
