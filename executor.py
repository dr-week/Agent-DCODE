import os
import subprocess
import json
import psutil
import time

BASE_DIR = os.path.abspath("projects")

def safe_path(path):
    if path.startswith("projects/"):
        path = path.replace("projects/", "", 1)

    full = os.path.abspath(os.path.join(BASE_DIR, path))

    if not full.startswith(BASE_DIR):
        return None

    return full


def execute_actions(actions):
    for a in actions:
        t = a.get("type")

        if t == "write_file":
            write_file(a)

        elif t == "append_file":
            append_file(a)

        elif t == "read_file":
            read_file(a)

        elif t == "run_command":
            run_cmd(a)

        elif t == "list_files":
            list_files(a)

        elif t == "run_python":
            run_python(a)

        elif t == "run_bash":
            run_bash(a)

        elif t == "run_js":
            run_js(a)

        elif t == "get_processes":
            get_processes(a)

        elif t == "show_progress":
            show_progress(a)

        else:
            print("[UNKNOWN ACTION]", t)


def write_file(a):
    path = a.get("path")
    content = a.get("content", "")

    full = safe_path(path)
    if not full:
        print("[BLOCKED PATH]", path)
        return

    os.makedirs(os.path.dirname(full), exist_ok=True)

    with open(full, "w", encoding="utf-8") as f:
        f.write(content)

    print("[CREATED]", full)


def append_file(a):
    path = a.get("path")
    content = a.get("content", "")

    full = safe_path(path)
    if not full:
        print("[APPEND ERROR]", path)
        return

    # 🔥 fix escaped newline
    content = content.replace("\\n", "\n")

    with open(full, "a", encoding="utf-8") as f:
        f.write("\n" + content.strip())

    print("[APPENDED]", full)

def read_file(a):
    path = a.get("path")

    full = safe_path(path)
    if not full or not os.path.exists(full):
        print("[READ ERROR]", path)
        return

    with open(full, "r", encoding="utf-8") as f:
        content = f.read()

    print("[READ SUCCESS]")
    print(content)


def run_cmd(a):
    cmd = a.get("command")

    cmd = cmd.replace("\\\\", "\\")

    print("[RUN]", cmd)

    try:
        r = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )

        print("[OUT]\n", r.stdout)
        print("[ERR]\n", r.stderr)

    except subprocess.TimeoutExpired:
        print("[TIMEOUT]")


def list_files(a):
    """List directory structure recursively"""
    path = a.get("path", "projects")
    max_depth = a.get("max_depth", 3)

    full = safe_path(path) if path != "projects" else BASE_DIR
    if not full or not os.path.isdir(full):
        print("[LIST ERROR]", path)
        return

    def tree(directory, prefix="", depth=0):
        if depth > max_depth:
            return
        try:
            items = sorted(os.listdir(directory))
            for i, item in enumerate(items):
                if item.startswith('.'):
                    continue
                path = os.path.join(directory, item)
                is_last = i == len(items) - 1
                current_prefix = "└── " if is_last else "├── "
                print(prefix + current_prefix + item)
                if os.path.isdir(path):
                    next_prefix = prefix + ("    " if is_last else "│   ")
                    tree(path, next_prefix, depth + 1)
        except PermissionError:
            pass

    print(f"[FILE TREE] {full}")
    tree(full)


def run_python(a):
    """Execute Python code"""
    code = a.get("code", "")
    if not code:
        print("[PYTHON ERROR] No code provided")
        return

    print("[PYTHON]")
    try:
        exec(code)
    except Exception as e:
        print(f"[PYTHON ERROR] {e}")


def run_bash(a):
    """Execute bash/shell command"""
    cmd = a.get("command", "")
    if not cmd:
        print("[BASH ERROR] No command provided")
        return

    print(f"[BASH] {cmd}")
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print("[STDERR]", result.stderr)
    except subprocess.TimeoutExpired:
        print("[BASH TIMEOUT]")
    except Exception as e:
        print(f"[BASH ERROR] {e}")


def run_js(a):
    """Execute JavaScript code (via Node.js)"""
    code = a.get("code", "")
    if not code:
        print("[JS ERROR] No code provided")
        return

    print("[JAVASCRIPT]")
    try:
        result = subprocess.run(
            ["node", "-e", code],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print("[JS ERROR]", result.stderr)
    except FileNotFoundError:
        print("[JS ERROR] Node.js not installed")
    except subprocess.TimeoutExpired:
        print("[JS TIMEOUT]")
    except Exception as e:
        print(f"[JS ERROR] {e}")


def get_processes(a):
    """Get system process information"""
    sort_by = a.get("sort_by", "memory")  # cpu or memory
    limit = a.get("limit", 10)

    print("[PROCESSES]")
    try:
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        # Sort processes
        if sort_by == "cpu":
            processes.sort(key=lambda x: x.get('cpu_percent', 0), reverse=True)
        else:
            processes.sort(key=lambda x: x.get('memory_percent', 0), reverse=True)

        print(f"PID\tName\tCPU%\tMEM%")
        for p in processes[:limit]:
            print(f"{p['pid']}\t{p['name'][:10]}\t{p.get('cpu_percent', 0):.1f}\t{p.get('memory_percent', 0):.1f}")
    except Exception as e:
        print(f"[PROCESS ERROR] {e}")


def show_progress(a):
    """Show progress bar"""
    steps = a.get("steps", 10)
    delay = a.get("delay", 0.1)

    print(f"[PROGRESS] Running {steps} steps...")
    for i in range(steps + 1):
        percent = (i / steps) * 100
        filled = int(percent / 2)
        bar = "█" * filled + "░" * (50 - filled)
        print(f"\r[{bar}] {percent:.0f}%", end="", flush=True)
        time.sleep(delay)
    print("\n[PROGRESS COMPLETE]")