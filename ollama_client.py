import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "qwen2.5-coder:7b"

SYSTEM_PROMPT = """
Output ONLY JSON.

Schema:
{
  "actions": [
    {"type": "write_file", "path": "projects/test.py", "content": "print('hello')"},
    {"type": "append_file", "path": "projects/test.py", "content": "print('world')"},
    {"type": "read_file", "path": "projects/test.py"},
    {"type": "run_command", "command": ".venv\\Scripts\\python projects/test.py"}
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