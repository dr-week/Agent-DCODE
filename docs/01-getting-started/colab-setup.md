# Minimal Colab Codex Agent

A lightweight Colab-ready Flask agent that uses Google Gemini to generate a single JSON response for `plan`, `actions`, and `result`.

## Files

- `colab_agent.py` — Flask app exposing `POST /agent`
- `requirements_colab.txt` — minimal Colab dependencies

## What it does

- Accepts `task` and optional `code` (max 2000 chars)
- Calls Gemini once
- Returns structured JSON: `plan`, `actions`, `result`
- Starts ngrok automatically for a public URL
- Logs requests, errors, and memory status
- Protects Colab by checking free RAM before each request

## Colab setup cells

1. Install dependencies:

```python
!pip install -q -r requirements_colab.txt
```

2. Set your Google API key and optional model:

```python
import os
os.environ['GOOGLE_API_KEY'] = 'YOUR_GOOGLE_API_KEY'
os.environ['GEMINI_MODEL'] = 'gemini-1.5-pro'
```

3. Run the agent:

```python
!python colab_agent.py
```
```

The notebook output will show a public ngrok URL like `https://xxxxxx.ngrok.app`.

## API usage

Send a single JSON POST to `/agent`:

```python
import requests
url = 'https://xxxxxx.ngrok.app/agent'
payload = {
    'task': 'Create a Python function that reverses a string',
    'code': 'def reverse_string(text):'
}
resp = requests.post(url, json=payload, timeout=30)
print(resp.json())
```

## VS Code fetch example

Use this snippet from a VS Code extension, web app, or JavaScript console:

```js
const url = 'https://xxxxxx.ngrok.app/agent';
const payload = {
  task: 'Create a unit test for the following function',
  code: 'def add(a, b):\n    return a + b'
};

const response = await fetch(url, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(payload),
});
const json = await response.json();
console.log(json);
```

## Example response

```json
{
  "success": true,
  "task": "Create a Python function that reverses a string",
  "model": "gemini-1.5-pro",
  "plan": ["Read the input string", "Return the reversed string"],
  "actions": [
    {"type": "write_file", "path": "projects/reverse.py", "content": "def reverse_string(text):\n    return text[::-1]"}
  ],
  "result": "Created reverse.py with a string reversal function.",
  "runtime_seconds": 2.3
}
```

## Colab limits and safety

- `code` is capped at `2000` characters
- Agent checks for at least `600MB` of free RAM before handling requests
- Gemini request timeout is set to `20` seconds
- The single-call design avoids multiple expensive rounds

## Extending the agent

- Add new action types in the prompt and downstream executor
- Swap in a custom Gemini model with `GEMINI_MODEL`
- Add a `/health` route to inspect runtime status
- Use the returned `plan` and `actions` to drive a separate execution stage
