"""
Ephemeral Docker & Subprocess Sandbox Execution Engine.
Executes agent commands in unprivileged containers with local process fallback.
"""

import os
import shutil
import subprocess
from typing import Any, Dict, List, Optional


class DockerSandbox:
    """Executes commands safely inside Docker or an isolated local subprocess."""

    def __init__(self, workspace_dir: str, image: str = "python:3.11-slim"):
        self.workspace_dir = os.path.abspath(workspace_dir)
        self.image = image
        self.docker_bin = shutil.which("docker")

    @property
    def is_docker_available(self) -> bool:
        return self.docker_bin is not None

    def run(
        self, cmd: List[str] | str, timeout: int = 30, env_vars: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Execute command in docker container if available, else local fallback."""
        if self.is_docker_available:
            return self._run_docker(cmd, timeout, env_vars)
        return self._run_local(cmd, timeout, env_vars)

    def _run_docker(self, cmd: List[str] | str, timeout: int, env: Optional[Dict[str, str]]) -> Dict[str, Any]:
        dcmd = [
            self.docker_bin or "docker", "run", "--rm",
            "-v", f"{self.workspace_dir}:/workspace", "-w", "/workspace",
            "--network=none", "--memory=1g", "--cpus=1.0",
        ]
        if env:
            for k, v in env.items():
                dcmd.extend(["-e", f"{k}={v}"])
        dcmd.append(self.image)
        dcmd.extend(cmd if isinstance(cmd, list) else ["sh", "-c", cmd])
        return self._exec(dcmd, timeout=timeout, backend="docker")

    def _run_local(self, cmd: List[str] | str, timeout: int, env: Optional[Dict[str, str]]) -> Dict[str, Any]:
        safe_env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": self.workspace_dir}
        if env:
            safe_env.update(env)
        args = cmd if isinstance(cmd, list) else ["bash", "-c", cmd]
        return self._exec(args, timeout=timeout, backend="local_process", cwd=self.workspace_dir, env=safe_env)

    def _exec(
        self, args: List[str], timeout: int, backend: str, cwd: Optional[str] = None, env: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        try:
            r = subprocess.run(args, cwd=cwd, env=env, capture_output=True, text=True, timeout=timeout)
            return {"stdout": r.stdout, "stderr": r.stderr, "exit_code": r.returncode, "success": r.returncode == 0, "backend": backend}
        except subprocess.TimeoutExpired:
            return {"stdout": "", "stderr": f"Timeout after {timeout}s", "exit_code": -1, "success": False, "backend": backend}
        except Exception as e:
            return {"stdout": "", "stderr": str(e), "exit_code": -2, "success": False, "backend": backend}
