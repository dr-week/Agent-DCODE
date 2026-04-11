import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "qwen2.5-coder:7b"

SYSTEM_PROMPT = """
Output ONLY JSON. Available actions:

1. write_file: Create new file
   {"type": "write_file", "path": "projects/file.py", "content": "code here"}

2. append_file: Append to existing file
   {"type": "append_file", "path": "projects/file.py", "content": "more code"}

3. read_file: Read file contents
   {"type": "read_file", "path": "projects/file.py"}

4. run_command: Execute shell command
   {"type": "run_command", "command": "command here"}

5. list_files: Show directory tree
   {"type": "list_files", "path": "projects", "max_depth": 3}

6. run_python: Execute Python code
   {"type": "run_python", "code": "print('hello')"}

7. run_bash: Execute bash command
   {"type": "run_bash", "command": "ls -la"}

8. run_js: Execute JavaScript (requires Node.js)
   {"type": "run_js", "code": "console.log('hello')"}

9. get_processes: Get system processes
   {"type": "get_processes", "sort_by": "memory", "limit": 10}

10. show_progress: Show progress bar
    {"type": "show_progress", "steps": 10, "delay": 0.1}

Return JSON with "actions" array. Example:
{
  "actions": [
    {"type": "write_file", "path": "projects/test.py", "content": "print('hello')"},
    {"type": "list_files", "path": "projects"},
    {"type": "get_processes", "sort_by": "cpu"}
  ]
}
"""

def ask_llm(user_input):
    prompt = SYSTEM_PROMPT + "\\nUser: " + user_input

    res = requests.post(OLLAMA_URL, json={
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "format": "json",
        "options": {
            "temperature": 0
        }
    })

    return res.json()["response"]