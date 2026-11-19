"""
Composable Harness Workflow Pipeline (<100 lines).
Coordinates multi-stage execution lifecycles: Setup -> Validate -> Execute -> Grade -> Teardown.
"""

from typing import Any, Callable, Dict, List, Optional
from dcode.runtime.git_checkpoint import GitCheckpoint


class PipelineStage:
    """A named step inside a Harness execution pipeline."""

    def __init__(self, name: str, fn: Callable[[Dict[str, Any]], Dict[str, Any]]):
        self.name = name
        self.fn = fn

    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        return self.fn(context)


class HarnessPipeline:
    """Linear & checkpointed workflow manager for running staged agent operations."""

    def __init__(self, workspace_dir: str, auto_rollback: bool = True):
        self.workspace_dir = workspace_dir
        self.auto_rollback = auto_rollback
        self.stages: List[PipelineStage] = []
        self.checkpoint = GitCheckpoint(workspace_dir)

    def add_stage(self, name: str, fn: Callable[[Dict[str, Any]], Dict[str, Any]]) -> "HarnessPipeline":
        self.stages.append(PipelineStage(name, fn))
        return self

    def execute(self, initial_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute all stages sequentially; roll back workspace if any stage fails."""
        ctx = dict(initial_context or {})
        ctx["workspace_dir"] = self.workspace_dir
        snap_id = self.checkpoint.snapshot()
        history: List[Dict[str, Any]] = []

        for stage in self.stages:
            try:
                res = stage.run(ctx)
                ctx.update(res)
                passed = res.get("success", True)
                history.append({"stage": stage.name, "passed": passed, "details": res})
                if not passed:
                    if self.auto_rollback:
                        self.checkpoint.rollback(snap_id)
                    return {"success": False, "failed_stage": stage.name, "history": history, "context": ctx}
            except Exception as exc:
                if self.auto_rollback:
                    self.checkpoint.rollback(snap_id)
                return {"success": False, "failed_stage": stage.name, "error": str(exc), "history": history}

        ctx["diff"] = self.checkpoint.diff_since(snap_id)
        return {"success": True, "history": history, "context": ctx, "diff": ctx["diff"]}
