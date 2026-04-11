import os
import subprocess

BASE_DIR = os.path.abspath("projects")

def safe_path(path):
    # remove leading "projects/" if model already added it
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

        elif t == "run_command":
            run_cmd(a)

        elif t == "read_file":
            read_file(a)

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

def run_cmd(a):
    cmd = a.get("command")

    # normalize slashes
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