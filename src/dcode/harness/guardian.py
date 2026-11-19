"""
Agent Harness Safety & Budget Guardian (<100 lines).
Enforces hard step caps, execution timeouts, token budgets, and cost ceilings.
"""

import time
from typing import Dict
from dcode.harness.config import HarnessConfig


class BudgetExceededError(RuntimeError):
    """Raised when token or dollar budget is exhausted."""


class StepCapExceededError(RuntimeError):
    """Raised when maximum execution steps are reached."""


class TimeoutExceededError(TimeoutError):
    """Raised when turn or total execution timeout is exceeded."""


class HarnessGuardian:
    """Monitors live execution against the active HarnessConfig thresholds."""

    def __init__(self, config: HarnessConfig):
        self.config = config
        self.start_time = time.time()
        self.current_step = 0
        self.total_tokens = 0
        self.total_cost_usd = 0.0

    def tick_step(self, tokens_used: int = 0, cost_used: float = 0.0) -> None:
        """Advance step counter and enforce safety ceilings."""
        self.current_step += 1
        self.total_tokens += tokens_used
        self.total_cost_usd += cost_used

        if self.current_step > self.config.max_steps:
            raise StepCapExceededError(f"Step cap reached: {self.current_step}/{self.config.max_steps}")
        if self.total_tokens > self.config.token_budget:
            raise BudgetExceededError(f"Token budget exceeded: {self.total_tokens}/{self.config.token_budget}")
        if self.total_cost_usd > self.config.cost_limit_usd:
            raise BudgetExceededError(f"Cost limit exceeded: ${self.total_cost_usd:.4f}/${self.config.cost_limit_usd}")

    def check_timeout(self, step_start_time: float) -> None:
        """Verify the current step has not exceeded step_timeout_sec."""
        elapsed = time.time() - step_start_time
        if elapsed > self.config.step_timeout_sec:
            raise TimeoutExceededError(f"Step timed out: {elapsed:.2f}s > {self.config.step_timeout_sec}s")

    def get_metrics(self) -> Dict[str, float]:
        """Return snapshot of execution metrics."""
        return {
            "steps": self.current_step,
            "max_steps": self.config.max_steps,
            "tokens": self.total_tokens,
            "cost_usd": round(self.total_cost_usd, 6),
            "elapsed_sec": round(time.time() - self.start_time, 2),
        }
