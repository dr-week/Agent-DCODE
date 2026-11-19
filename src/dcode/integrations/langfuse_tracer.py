"""
Phase 4: Langfuse & SQLite Telemetry / Observability Adapter (langfuse/langfuse).
Records agent state transitions, LLM spans, token counts, cost in USD, and latency
to Langfuse Cloud/Self-Hosted plus a local SQLite audit database.
"""

import os
import sqlite3
import time
import uuid
from typing import Any, Dict, List, Optional
from dcode.config import LOGS_DIR

try:
    from langfuse import Langfuse  # type: ignore

    HAS_LANGFUSE = True
except ImportError:
    Langfuse = None  # type: ignore
    HAS_LANGFUSE = False


class LangfuseTracer:
    """Production LLM trace logger wrapping langfuse/langfuse with local SQLite span storage."""

    def __init__(self, db_path: Optional[str] = None):
        os.makedirs(LOGS_DIR, exist_ok=True)
        self.db_path = db_path or os.path.join(LOGS_DIR, "telemetry_traces.sqlite3")
        self.lf = None
        if HAS_LANGFUSE and Langfuse is not None and os.environ.get("LANGFUSE_PUBLIC_KEY"):
            try:
                self.lf = Langfuse()
            except Exception:
                self.lf = None
        self._init_db()

    def _init_db(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """CREATE TABLE IF NOT EXISTS spans (
                    span_id TEXT PRIMARY KEY,
                    trace_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    model TEXT,
                    tokens INTEGER DEFAULT 0,
                    cost_usd REAL DEFAULT 0.0,
                    latency_ms REAL DEFAULT 0.0,
                    status TEXT DEFAULT 'ok',
                    created_at REAL NOT NULL
                )"""
            )

    def record_span(
        self,
        name: str,
        trace_id: Optional[str] = None,
        model: str = "ollama/qwen2.5-coder:7b",
        tokens: int = 0,
        cost_usd: float = 0.0,
        latency_ms: float = 0.0,
        status: str = "ok",
    ) -> Dict[str, Any]:
        """Record an agent execution or LLM generation span."""
        t_id = trace_id or uuid.uuid4().hex[:12]
        s_id = uuid.uuid4().hex[:12]
        if self.lf is not None:
            try:
                trace = self.lf.trace(id=t_id, name=name)
                trace.generation(name=name, model=model, usage={"total": tokens})
            except Exception:
                pass
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO spans VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (s_id, t_id, name, model, tokens, cost_usd, latency_ms, status, time.time()),
            )
        return {"span_id": s_id, "trace_id": t_id, "name": name, "tokens": tokens, "cost_usd": cost_usd}

    def summary(self) -> Dict[str, Any]:
        """Return aggregate token, cost, and latency metrics across all recorded runs."""
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT COUNT(*), COALESCE(SUM(tokens),0), COALESCE(SUM(cost_usd),0.0), COALESCE(AVG(latency_ms),0.0) FROM spans"
            ).fetchone()
        return {
            "backend": "langfuse+sqlite" if self.lf else "sqlite-otel",
            "total_spans": row[0],
            "total_tokens": row[1],
            "total_cost_usd": round(float(row[2]), 6),
            "avg_latency_ms": round(float(row[3]), 2),
        }
