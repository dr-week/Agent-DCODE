# Structured Logging System

A file-based JSON logging system for tracking agent actions, decisions, and progress across multiple sub-projects.

## Overview

- **File-based**: No external database required
- **Per-project logs**: Each project gets its own `.logs/{project_name}.json`
- **Automatic pruning**: Keeps last 20 entries per project
- **Resumable**: Agent can read last state and context to resume interrupted tasks

## Files

- `logger.py` — Core logging module
- `.logs/` — Directory containing all project logs
- `example_logging.py` — Usage examples

## Log Format

Each project's log is a JSON array:

```json
[
  {
    "timestamp": "2026-04-14T10:23:45.123456",
    "task": "Generate Python function",
    "action": "llm_call",
    "status": "success",
    "details": "Created function with 42 lines"
  },
  {
    "timestamp": "2026-04-14T10:24:12.654321",
    "task": "Build API endpoint",
    "action": "execute",
    "status": "fail",
    "details": "Port 5000 already in use"
  }
]
```

## Functions

### `write_log(project, task, action, status, details="")`

Append a new log entry.

```python
from logger import write_log

write_log(
    project="my_agent",
    task="Parse user input",
    action="tokenize",
    status="success",
    details="Tokenized 150 words"
)
```

### `read_logs(project)`

Read all logs for a project.

```python
from logger import read_logs

logs = read_logs("my_agent")
for entry in logs:
    print(f"{entry['timestamp']}: {entry['action']} - {entry['status']}")
```

### `get_last_state(project)`

Get the most recent log entry (useful for resuming tasks).

```python
from logger import get_last_state

last = get_last_state("my_agent")
if last and last["status"] == "fail":
    print(f"Last action failed: {last['details']}")
    # Resume task here
```

### `get_context_for_project(project, limit=5)`

Get last N entries for context.

```python
from logger import get_context_for_project

context = get_context_for_project("my_agent", limit=3)
# Use context to understand what the agent was doing
```

### `format_log_summary(project)`

Get a readable summary of logs.

```python
from logger import format_log_summary

summary = format_log_summary("my_agent")
print(summary)
# Output:
# 📋 my_agent - 5 entries:
#   10:23 ✅ Parse user input
#   10:24 ❌ Build API endpoint
#   10:25 ✅ Generate response
```

### `clear_logs(project=None)`

Clear logs for a project or all projects.

```python
from logger import clear_logs

clear_logs("my_agent")  # Clear specific project
clear_logs()             # Clear all logs
```

## Integration Examples

### Agent Resumption

```python
from logger import get_last_state, write_log

def execute_task(task_name, project="my_agent"):
    # Check if task was interrupted
    last = get_last_state(project)
    
    if last and last["task"] == task_name and last["status"] == "fail":
        print(f"Resuming: {last['details']}")
        # Resume from where it left off
        ...
    
    # Execute task
    try:
        result = do_work()
        write_log(project, task_name, "execute", "success", result)
    except Exception as e:
        write_log(project, task_name, "execute", "fail", str(e))
```

### Multi-Project Tracking

```python
from logger import read_logs, write_log

projects = ["frontend", "backend", "ml_model"]

for project in projects:
    write_log(project, "Daily sync", "update", "success", "All systems OK")
    logs = read_logs(project)
    print(f"{project}: {len(logs)} entries")
```

### Web API Endpoints

Web API provides REST access to logs:

- `GET /api/logs/<project>` — Get all logs for a project
- `GET /api/logs/<project>/summary` — Get formatted summary
- `GET /api/logs` — List all projects

```bash
curl http://localhost:5000/api/logs/web_api
curl http://localhost:5000/api/logs/agent/summary
curl http://localhost:5000/api/logs
```

## Projects Currently Logging

- `agent` — Main agent execution
- `web_api` — Web API calls
- `colab_agent` — Colab-specific agent

## Storage

Logs are stored in `.logs/` directory:

```
.logs/
├── agent.json
├── web_api.json
└── colab_agent.json
```

Each file contains up to 20 entries (old entries are removed).

## Tips

1. **Use descriptive actions**: "llm_call", "execute", "file_write", "memory_error"
2. **Keep details concise**: Include key info but not raw output
3. **Always include status**: "success" or "fail"
4. **Check logs before resuming**: Use `get_last_state()` to understand context

## Example Output

```
📋 agent - 5 entries:
  14:23 ✅ Generate Python function
  14:24 ❌ Build API endpoint
  14:25 ✅ Process user input
  14:26 ✅ Return result
  14:27 ❌ Save to database
```
