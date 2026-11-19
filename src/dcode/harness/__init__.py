"""
Agent-DCODE Production Agent Harness package.
Provides HarnessConfig, HarnessGuardian, TrajectoryRecorder, HarnessGrader, and AgentHarness.
"""

from dcode.harness.config import HarnessConfig
from dcode.harness.grader import HarnessGrader
from dcode.harness.guardian import (
    BudgetExceededError,
    HarnessGuardian,
    StepCapExceededError,
    TimeoutExceededError,
)
from dcode.harness.runner import AgentHarness
from dcode.harness.trajectory import TrajectoryRecorder

__all__ = [
    "AgentHarness",
    "BudgetExceededError",
    "HarnessConfig",
    "HarnessGrader",
    "HarnessGuardian",
    "StepCapExceededError",
    "TimeoutExceededError",
    "TrajectoryRecorder",
]
