import os
import subprocess
import json
import psutil
import time
from io import StringIO
import sys

BASE_DIR = os.path.abspath("projects")

# Action type registry for structured mapping
ACTION_HANDLERS = {
    "write_file": "write_file",
    "create_file": "write_file",
    "append_file": "append_file",
    "read_file": "read_file",
    "run_command": "run_cmd",
    "run_bash": "run_bash",
    "list_files": "list_files",
    "run_python": "run_python",
    "run_js": "run_js",
    "get_processes": "get_processes",
    "show_progress": "show_progress",
}


def safe_path(path):
    if path.startswith("projects/"):
        path = path.replace("projects/", "", 1)

    full = os.path.abspath(os.path.join(BASE_DIR, path))

    if not full.startswith(BASE_DIR):
        return None

    return full


def execute_actions(actions):
    """Execute actions and capture output"""
    results = []
    for a in actions:
        t = a.get("type")
        output = ""

        # Map action type to handler
        handler_name = ACTION_HANDLERS.get(t)
        if not handler_name:
            output = f"[UNKNOWN ACTION] {t}"
            print(output)
        else:
            # Call handler function
            handler = globals().get(handler_name)
            if handler:
                try:
                    output = handler(a)
                except Exception as e:
                    output = f"[ERROR in {t}] {str(e)}"
                    print(output)
            else:
                output = f"[HANDLER NOT FOUND] {handler_name}"
        
        # Collect result
        result = a.copy()
        result["output"] = output
        results.append(result)
    
    return results


def write_file(a):
    path = a.get("path")
    content = a.get("content", "")

    full = safe_path(path)
    if not full:
        msg = f"[BLOCKED PATH] {path}"
        print(msg)
        return msg

    os.makedirs(os.path.dirname(full), exist_ok=True)

    with open(full, "w", encoding="utf-8") as f:
        f.write(content)

    msg = f"[CREATED] {full}"
    print(msg)
    return msg


def append_file(a):
    path = a.get("path")
    content = a.get("content", "")

    full = safe_path(path)
    if not full:
        msg = f"[APPEND ERROR] {path}"
        print(msg)
        return msg

    # 🔥 fix escaped newline
    content = content.replace("\\n", "\n")

    with open(full, "a", encoding="utf-8") as f:
        f.write("\n" + content.strip())

    msg = f"[APPENDED] {full}"
    print(msg)
    return msg

def read_file(a):
    path = a.get("path")

    full = safe_path(path)
    if not full or not os.path.exists(full):
        msg = f"[READ ERROR] {path}"
        print(msg)
        return msg

    with open(full, "r", encoding="utf-8") as f:
        content = f.read()

    print("[READ SUCCESS]")
    print(content)
    return content


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

        output = f"{r.stdout}\n{r.stderr}" if r.stderr else r.stdout
        print("[OUT]\n", r.stdout)
        if r.stderr:
            print("[ERR]\n", r.stderr)
        return output

    except subprocess.TimeoutExpired:
        msg = "[TIMEOUT]"
        print(msg)
        return msg


def list_files(a):
    """List directory structure recursively"""
    path = a.get("path", "projects")
    max_depth = a.get("max_depth", 3)

    full = safe_path(path) if path != "projects" else BASE_DIR
    if not full or not os.path.isdir(full):
        msg = f"[LIST ERROR] {path}"
        print(msg)
        return msg

    output_lines = []
    
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
                current_prefix = "+-- " if is_last else "|-- "
                line = prefix + current_prefix + item
                output_lines.append(line)
                try:
                    print(line, flush=True)
                except UnicodeEncodeError:
                    print(line.encode('utf-8', errors='replace').decode('utf-8'), flush=True)
                if os.path.isdir(path):
                    next_prefix = prefix + ("    " if is_last else "|   ")
                    tree(path, next_prefix, depth + 1)
        except PermissionError:
            pass

    header = f"[FILE TREE] {full}"
    print(header)
    output_lines.insert(0, header)
    tree(full)
    
    return "\n".join(output_lines)


def run_python(a):
    """Execute Python code"""
    code = a.get("code", "")
    if not code:
        msg = "[PYTHON ERROR] No code provided"
        print(msg)
        return msg

    print("[PYTHON]")
    output = StringIO()
    old_stdout = sys.stdout
    
    try:
        sys.stdout = output
        exec(code)
        sys.stdout = old_stdout
        result = output.getvalue()
        print(result)
        return result
    except Exception as e:
        sys.stdout = old_stdout
        msg = f"[PYTHON ERROR] {e}"
        print(msg)
        return msg


def run_bash(a):
    """Execute bash/shell command"""
    cmd = a.get("command", "")
    if not cmd:
        msg = "[BASH ERROR] No command provided"
        print(msg)
        return msg

    print(f"[BASH] {cmd}")
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )
        output = f"{result.stdout}"
        if result.stderr:
            output += f"\n[STDERR] {result.stderr}"
        print(output)
        return output
    except subprocess.TimeoutExpired:
        msg = "[BASH TIMEOUT]"
        print(msg)
        return msg
    except Exception as e:
        msg = f"[BASH ERROR] {e}"
        print(msg)
        return msg


def run_js(a):
    """Execute JavaScript code (via Node.js)"""
    code = a.get("code", "")
    if not code:
        msg = "[JS ERROR] No code provided"
        print(msg)
        return msg

    print("[JAVASCRIPT]")
    try:
        result = subprocess.run(
            ["node", "-e", code],
            capture_output=True,
            text=True,
            timeout=10
        )
        output = f"{result.stdout}"
        if result.stderr:
            output += f"\n[JS ERROR] {result.stderr}"
        print(output)
        return output
    except FileNotFoundError:
        msg = "[JS ERROR] Node.js not installed"
        print(msg)
        return msg
    except subprocess.TimeoutExpired:
        msg = "[JS TIMEOUT]"
        print(msg)
        return msg
    except Exception as e:
        msg = f"[JS ERROR] {e}"
        print(msg)
        return msg


def get_processes(a):
    """Get system process information"""
    sort_by = a.get("sort_by", "memory")  # cpu or memory
    limit = a.get("limit", 10)

    print("[PROCESSES]")
    output_lines = ["[PROCESSES]", "PID\tName\tCPU%\tMEM%"]
    
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

        for p in processes[:limit]:
            line = f"{p['pid']}\t{p['name'][:10]}\t{p.get('cpu_percent', 0):.1f}\t{p.get('memory_percent', 0):.1f}"
            output_lines.append(line)
            print(line)
            
        return "\n".join(output_lines)
    except Exception as e:
        msg = f"[PROCESS ERROR] {e}"
        print(msg)
        return msg


def show_progress(a):
    """Show progress bar"""
    steps = a.get("steps", 10)
    delay = a.get("delay", 0.1)

    print(f"[PROGRESS] Running {steps} steps...")
    output_lines = [f"[PROGRESS] Running {steps} steps..."]
    
    for i in range(steps + 1):
        percent = (i / steps) * 100
        filled = int(percent / 2)
        bar = "█" * filled + "░" * (50 - filled)
        line = f"[{bar}] {percent:.0f}%"
        output_lines.append(line)
        print(f"\r{line}", end="", flush=True)
        time.sleep(delay)
    
    print("\n[PROGRESS COMPLETE]")
    output_lines.append("[PROGRESS COMPLETE]")
    return "\n".join(output_lines)