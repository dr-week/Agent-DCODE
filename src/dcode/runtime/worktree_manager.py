"""
Ephemeral Git Worktree Isolation Manager.
Spawns isolated temporary git worktrees for safe agent modification without corrupting active branches.
"""

import os
from pathlib import Path
import subprocess
import tempfile
import uuid


class GitWorktreeManager:
    """Manages ephemeral git worktrees for isolated agent execution."""

    def __init__(self, repo_dir: str = "."):
        self.repo_dir = os.path.abspath(repo_dir)

    def create_worktree(self, branch_name: str | None = None) -> Path:
        """Create a temporary worktree detached or on a temporary branch."""
        branch = branch_name or f"dcode-agent-{uuid.uuid4().hex[:8]}"
        tmp_dir = Path(tempfile.mkdtemp(prefix="dcode_wt_"))
        cmd = ["git", "worktree", "add", "-b", branch, str(tmp_dir), "HEAD"]
        res = subprocess.run(cmd, cwd=self.repo_dir, capture_output=True, text=True)
        if res.returncode != 0:
            raise RuntimeError(f"Failed to create worktree: {res.stderr.strip()}")
        return tmp_dir

    def remove_worktree(self, worktree_path: str | Path, delete_branch: bool = True) -> bool:
        """Remove a worktree and optionally prune its temporary branch."""
        wt = Path(worktree_path).resolve()
        branch = None
        if delete_branch:
            res_b = subprocess.run(["git", "branch", "--show-current"], cwd=wt, capture_output=True, text=True)
            if res_b.returncode == 0:
                branch = res_b.stdout.strip()

        res = subprocess.run(["git", "worktree", "remove", "--force", str(wt)], cwd=self.repo_dir, capture_output=True, text=True)
        if delete_branch and branch and branch.startswith("dcode-agent-"):
            subprocess.run(["git", "branch", "-D", branch], cwd=self.repo_dir, capture_output=True, text=True)
        return res.returncode == 0

    def list_worktrees(self) -> list[dict[str, str]]:
        """List active git worktrees for this repository."""
        res = subprocess.run(["git", "worktree", "list", "--porcelain"], cwd=self.repo_dir, capture_output=True, text=True)
        if res.returncode != 0:
            return []
        items = []
        cur: dict[str, str] = {}
        for line in res.stdout.splitlines():
            if line.startswith("worktree "):
                if cur:
                    items.append(cur)
                cur = {"path": line.split(" ", 1)[1]}
            elif line.startswith("branch "):
                cur["branch"] = line.split(" ", 1)[1]
        if cur:
            items.append(cur)
        return items
