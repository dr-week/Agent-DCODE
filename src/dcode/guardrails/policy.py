"""
Guardrail policy validator for agent actions, shell commands, and execution budgets.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Tuple

DEFAULT_BLOCKED_PATTERNS = (
    "rm -rf /",
    "mkfs",
    "dd if=",
    ":(){ :|:& };:",
    "shutdown",
    "reboot",
    "> /dev/sda",
)


@dataclass
class GuardrailPolicy:
    """Enforces safety constraints and step/action budgets on any agent."""

    max_steps: int = 10
    max_actions_per_turn: int = 5
    allow_shell: bool = True
    blocked_patterns: Tuple[str, ...] = field(default_factory=lambda: DEFAULT_BLOCKED_PATTERNS)

    def validate_action(self, action: Dict[str, Any]) -> Tuple[bool, str]:
        action_type = action.get("type", "")
        if action_type in ("run_bash", "run_command", "execute_cmd") and not self.allow_shell:
            return False, f"Shell execution ('{action_type}') is disabled by GuardrailPolicy."

        cmd_or_code = f"{action.get('command', '')} {action.get('code', '')}".lower()
        for pattern in self.blocked_patterns:
            if pattern.lower() in cmd_or_code:
                return False, f"Blocked hazardous pattern detected: '{pattern}'"

        path = action.get("path", "")
        if ".." in path or path.startswith("/etc") or path.startswith("/root"):
            return False, f"Path traversal outside sandbox blocked: '{path}'"

        return True, "Allowed"

    def validate_batch(self, actions: List[Dict[str, Any]]) -> Tuple[bool, str]:
        if len(actions) > self.max_actions_per_turn:
            return False, f"Action count ({len(actions)}) exceeds limit ({self.max_actions_per_turn})"
        for act in actions:
            ok, reason = self.validate_action(act)
            if not ok:
                return False, reason
        return True, "All actions passed guardrails"
