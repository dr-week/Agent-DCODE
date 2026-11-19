"""
Multi-Agent Consensus & Debate Protocol.
Orchestrates Proposer-Critic-Verifier loops to validate actions before commitment.
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional


@dataclass
class ReviewFeedback:
    reviewer: str
    approved: bool
    score: float
    critique: str


class ConsensusEngine:
    """Coordinates debate and voting among specialized agents to achieve consensus."""

    def __init__(self, threshold: float = 0.66):
        self.threshold = threshold

    def evaluate_proposal(
        self,
        proposal: str,
        critics: List[Callable[[str], ReviewFeedback]],
    ) -> Dict[str, Any]:
        """Collect votes and critiques from an ensemble of review agents."""
        reviews: List[ReviewFeedback] = []
        for critic_fn in critics:
            reviews.append(critic_fn(proposal))

        total_score = sum(r.score for r in reviews) if reviews else 0.0
        avg_score = total_score / len(reviews) if reviews else 0.0
        approvals = sum(1 for r in reviews if r.approved)
        approval_rate = approvals / len(reviews) if reviews else 0.0
        passed = approval_rate >= self.threshold and avg_score >= 0.5

        return {
            "passed": passed,
            "approval_rate": round(approval_rate, 2),
            "average_score": round(avg_score, 2),
            "reviews": [
                {
                    "reviewer": r.reviewer,
                    "approved": r.approved,
                    "score": r.score,
                    "critique": r.critique,
                }
                for r in reviews
            ],
            "consensus": "APPROVED" if passed else "REJECTED_OR_NEEDS_REVISION",
        }
