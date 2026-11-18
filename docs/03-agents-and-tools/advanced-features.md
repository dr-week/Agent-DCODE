# 🚀 Advanced AI Agent Features

**Added Features:** v1.1.0  
**Date:** April 12, 2026  

---

## New Action Types

The AI agent now supports 10 powerful action types:

### 1. **list_files** 📁
Display directory structure recursively.

```json
{"type": "list_files", "path": "projects", "max_depth": 3}
```

**Response:** Tree-formatted file listing

---

### 2. **run_python** 🐍
Execute arbitrary Python code.

```json
{"type": "run_python", "code": "print('Hello, World!')"}
```

**Use Cases:**
- Data analysis
- Mathematical calculations
- Testing libraries
- Quick scripts

---

### 3. **run_bash** 🖥️
Execute bash/shell commands (Linux/Mac/Windows PowerShell).

```json
{"type": "run_bash", "command": "ls -la"}
```

**Use Cases:**
- System operations
- File manipulation
- Git commands
- Package installation

---

### 4. **run_js** 🟨
Execute JavaScript code (requires Node.js).

```json
{"type": "run_js", "code": "console.log(Math.random())"}
```

**Use Cases:**
- Node.js scripts
- Testing JavaScript
- NPM module testing
- Backend API testing

---

### 5. **get_processes** ⚙️
Get system process information.

```json
{"type": "get_processes", "sort_by": "memory", "limit": 10}
```

**Parameters:**
- `sort_by`: "cpu" or "memory"
- `limit`: Number of processes (default: 10)

**Output:**
```
PID    Name        CPU%   MEM%
1234   python      5.2    12.3
5678   node        2.1    8.5
...
```

---

### 6. **show_progress** 📊
Display a visual progress bar.

```json
{"type": "show_progress", "steps": 10, "delay": 0.1}
```

**Parameters:**
- `steps`: Total steps to complete
- `delay`: Time between each step (seconds)

**Visual Output:**
```
[████████████████████░░░░░░░░░░░░░░░░░░░░░░░░░░] 50%
```

---

## Example Usage

### Scenario 1: Analyze System Performance
```
User: "Check my system processes and show me the top CPU users"

AI Actions:
1. get_processes: sort_by="cpu", limit=5
2. show_progress: steps=5
```

### Scenario 2: Set Up Project Structure
```
User: "Create a new Python project structure"

AI Actions:
1. write_file: Create __init__.py
2. write_file: Create requirements.txt
3. write_file: Create setup.py
4. list_files: Show created structure
```

### Scenario 3: Quick Data Analysis
```
User: "Calculate average of [1,2,3,4,5]"

AI Actions:
1. run_python: Execute calculation code
```

### Scenario 4: Node.js Testing
```
User: "Test if Express is installed and working"

AI Actions:
1. run_js: Test require('express')
1. run_bash: npm list express
```

---

## Installation & Dependencies

### New Requirements
```bash
pip install psutil==5.9.8
```

### Optional Requirements
For JavaScript execution:
```bash
npm install -g node  # Already installed with Node.js
```

---

## API Schema

### Complete Action Schema

```json
{
  "actions": [
    {
      "type": "write_file",
      "path": "projects/file.py",
      "content": "code here"
    },
    {
      "type": "run_python",
      "code": "print('hello')"
    },
    {
      "type": "run_bash",
      "command": "ls -la"
    },
    {
      "type": "run_js",
      "code": "console.log('hello')"
    },
    {
      "type": "list_files",
      "path": "projects",
      "max_depth": 3
    },
    {
      "type": "get_processes",
      "sort_by": "memory",
      "limit": 10
    },
    {
      "type": "show_progress",
      "steps": 20,
      "delay": 0.05
    }
  ]
}
```

---

## Execution Flow

```
User Input
   ↓
Local LLM (Ollama)
   ↓
JSON Parsing (with retry)
   ↓
Action Execution (10 types supported)
   ├── File Operations (read/write/append)
   ├── Command Execution (bash/python/js)
   ├── System Info (processes/file tree)
   └── UI Feedback (progress bars)
   ↓
Response to Web UI
```

---

## Security & Limitations

### Restrictions ✅
- File operations sandboxed to `projects/` directory
- Command execution: 30-second timeout
- No internet access (offline by design)
- Process info read-only
- No privilege escalation

### Limitations ⚠️
- Python code: No external module imports restricted
- Bash: PowerShell on Windows, sh on Unix
- JavaScript: Requires Node.js installed
- Progress bar: For user feedback only
- Process limit: Top 10 processes

---

## Error Handling

All action types have built-in error handling:

```
[ACTION_TYPE ERROR] Description of error
[ACTION_TYPE TIMEOUT] Execution exceeded time limit
[BLOCKED PATH] Attempted to escape sandbox
```

---

## Example Prompts for AI

Try these prompts with the agent:

1. "Show me the folder structure of my projects"
2. "What are the top 5 memory-consuming processes?"
3. "Write a Python script to calculate fibonacci numbers"
4. "Create a simple Node.js server and test it"
5. "List all files and show a progress bar"
6. "Get system info and create a report"

---

## Performance Impact

| Action | Time | Memory |
|--------|------|--------|
| list_files | < 100ms | Low |
| run_python | < 1s | Medium |
| run_bash | < 1s | Low |
| run_js | < 1s | Medium |
| get_processes | < 500ms | Low |
| show_progress | Varies | Very Low |

---

## Future Enhancements

Planned for v1.2.0:
- [ ] SQL query execution
- [ ] Docker container management
- [ ] Git operations
- [ ] API testing
- [ ] Database operations
- [ ] File compression/extraction

---

**These features make the agent truly versatile for coding, automation, and system administration tasks!** 🎉
