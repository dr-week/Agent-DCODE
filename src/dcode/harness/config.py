"""
Agent Harness Configuration Dataclass (<100 lines).
Defines budget caps, step boundaries, timeouts, and execution policies for agent runs.
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class HarnessConfig:
    """Configuration contract controlling agent execution boundaries and safety policies."""

    max_steps: int = 10
    step_timeout_sec: float = 30.0
    token_budget: int = 25_000
    cost_limit_usd: float = 0.50
    auto_rollback_on_fail: bool = True
    workspace_dir: Optional[str] = None
    test_command: str = "python3 -m unittest"
    allowed_tools: List[str] = field(default_factory=list)
    record_trajectory: bool = True
    trajectory_file: Optional[str] = None

    def validate(self) -> None:
        """Validate safety thresholds."""
        if self.max_steps < 1 or self.max_steps > 100:
            raise ValueError(f"max_steps must be between 1 and 100, got {self.max_steps}")
        if self.step_timeout_sec <= 0:
            raise ValueError(f"step_timeout_sec must be positive, got {self.step_timeout_sec}")
        if self.token_budget <= 0:
            raise ValueError(f"token_budget must be positive, got {self.token_budget}")
        if self.cost_limit_usd <= 0:
            raise ValueError(f"cost_limit_usd must be positive, got {self.cost_limit_usd}")
