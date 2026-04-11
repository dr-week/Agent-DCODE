# DCode Usage Examples

This guide shows practical examples of how to use DCode's 10 action types through the web UI and CLI.

## 🎯 Quick Start

### Web UI Chat Examples

The web UI at **http://localhost:5000** is the easiest way to interact with DCode. Simply type your requests and the AI agent will execute the appropriate actions.

---

## 📁 File Operations

### 1. Write Files
**Prompt:** "Create a new Python file called hello_world.py that prints a greeting"

**Generated Action:**
```json
{
  "type": "write_file",
  "path": "projects/hello_world.py",
  "content": "#!/usr/bin/env python3\nprint('Hello, World!')"
}
```

**Output:** `[CREATED] /path/to/projects/hello_world.py`

---

### 2. Append to Files
**Prompt:** "Add a new function to utils.py that calculates factorial"

**Generated Action:**
```json
{
  "type": "append_file",
  "path": "projects/utils.py",
  "content": "def factorial(n):\n    return 1 if n <= 1 else n * factorial(n-1)"
}
```

**Output:** `[APPENDED] /path/to/projects/utils.py`

---

### 3. Read Files
**Prompt:** "Show me the contents of config.json"

**Generated Action:**
```json
{
  "type": "read_file",
  "path": "projects/config.json"
}
```

**UI Display:** File contents shown in a code block with syntax highlighting

---

### 4. List Directory Structure
**Prompt:** "Show me the complete file structure of the projects directory"

**Generated Action:**
```json
{
  "type": "list_files",
  "path": "projects",
  "max_depth": 3
}
```

**Output:**
```
[FILE TREE] /path/to/projects
├── src/
│   ├── main.py
│   └── utils/
│       ├── helpers.py
│       └── validators.py
├── config.json
├── README.md
└── tests/
    ├── test_main.py
    └── test_utils.py
```

**UI Display:** Tree structure rendered in a monospace font with proper formatting

---

## 🐍 Python Code Execution

### 5. Run Python Code
**Prompt:** "Calculate the sum of all numbers from 1 to 100 and show the result"

**Generated Action:**
```json
{
  "type": "run_python",
  "code": "total = sum(range(1, 101))\nprint(f'Sum: {total}')"
}
```

**Output:**
```
Sum: 5050
```

**More Examples:**

**Fibonacci Sequence:**
```
Prompt: "Write and execute Python code that generates the first 10 Fibonacci numbers"

Generated Code:
a, b = 0, 1
fib_list = []
for i in range(10):
    fib_list.append(a)
    a, b = b, a + b
print(f"Fibonacci: {fib_list}")

Output:
Fibonacci: [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
```

**Data Processing:**
```
Prompt: "Create a list of dictionaries with test data and show statistics"

Generated Code:
import json
data = [
    {"name": "Alice", "score": 95},
    {"name": "Bob", "score": 87},
    {"name": "Charlie", "score": 92}
]
avg = sum(d['score'] for d in data) / len(data)
print(f"Average Score: {avg:.1f}")

Output:
Average Score: 91.3
```

---

## 🔧 Bash/Shell Commands

### 6. Run Bash Commands
**Prompt:** "List all files in the projects directory with details"

**Generated Action:**
```json
{
  "type": "run_bash",
  "command": "ls -lah projects/ | head -20"
}
```

**Output:**
```
total 128
drwxr-xr-x   10 user  staff   320 Jan 15 10:30 .
drwxr-xr-x   15 user  staff   480 Jan 15 10:30 ..
-rw-r--r--    1 user  staff   1024 Jan 15 10:30 README.md
```

**More Examples:**

**Find Specific Files:**
```
Prompt: "Find all Python files in the projects directory"

Generated Command:
find projects -name "*.py" -type f

Output:
projects/main.py
projects/utils.py
projects/test.py
```

**File Statistics:**
```
Prompt: "Count the total lines of code in Python files"

Generated Command:
find projects -name "*.py" -exec wc -l {} + | tail -1

Output:
     1524 total
```

**Disk Usage:**
```
Prompt: "Show disk usage of the projects folder"

Generated Command:
du -sh projects/

Output:
45M     projects/
```

---

## 🎨 JavaScript Execution

### 7. Run JavaScript Code
**Prompt:** "Write JavaScript code that creates an array and performs calculations"

**Generated Action:**
```json
{
  "type": "run_js",
  "code": "const nums = [1, 2, 3, 4, 5];\nconst sum = nums.reduce((a, b) => a + b, 0);\nconst avg = sum / nums.length;\nconsole.log(`Sum: ${sum}, Average: ${avg}`);"
}
```

**Output:**
```
Sum: 15, Average: 3
```

**More Examples:**

**JSON Processing:**
```
Prompt: "Parse JSON data and extract specific fields"

Generated Code:
const data = { user: "Alice", age: 25, email: "alice@example.com" };
console.log(JSON.stringify(data, null, 2));

Output:
{
  "user": "Alice",
  "age": 25,
  "email": "alice@example.com"
}
```

**String Manipulation:**
```
Prompt: "Generate an acronym from words"

Generated Code:
const words = "Artificial Intelligence Machine Learning";
const acronym = words.split(" ").map(w => w[0]).join("");
console.log(acronym);

Output:
AIML
```

---

## 💻 System Process Monitoring

### 8. Get Processes
**Prompt:** "Show me the top 5 processes using the most memory"

**Generated Action:**
```json
{
  "type": "get_processes",
  "limit": 5,
  "sort_by": "memory"
}
```

**Output:**
```
[PROCESSES]
PID     Name        CPU%    MEM%
2048    python      45.2    12.3
1024    node        12.5    8.7
512     chrome      5.1     22.4
256     code        8.3     15.1
128     docker      2.1     5.5
```

**UI Display:** Rendered as an interactive table with sortable columns

---

### More Process Examples:**

**CPU-Intensive Processes:**
```
Prompt: "Show the top 10 processes using the most CPU"

Generated Action:
{
  "type": "get_processes",
  "limit": 10,
  "sort_by": "cpu"
}

Output:
PID     Name        CPU%    MEM%
2048    python      78.5    5.2
1024    node        32.1    3.1
...
```

---

## ⏳ Progress Bars

### 9. Show Progress
**Prompt:** "Simulate a 20-step process with a progress bar"

**Generated Action:**
```json
{
  "type": "show_progress",
  "steps": 20,
  "delay": 0.2
}
```

**Output:**
```
[PROGRESS] Running 20 steps...
[██████████████████████████████████████████████░░] 92.0%
[PROGRESS COMPLETE]
```

**UI Display:** Progress bar rendered with color and percentage

---

## 🔄 Running Commands

### 10. Generic Command Execution
**Prompt:** "Run the command to check current directory"

**Generated Action:**
```json
{
  "type": "run_command",
  "command": "pwd"
}
```

**Output:**
```
/Users/username/projects
```

---

## 📊 Complex Multi-Step Scenarios

### Scenario 1: Project Setup
**User Prompt:** "Create a new Python project structure with a main file, utils, and tests"

**Agent Actions (in sequence):**
1. **write_file** - Creates `projects/main.py` with starter code
2. **write_file** - Creates `projects/utils.py` with utility functions
3. **write_file** - Creates `projects/tests/test_main.py` with test skeleton
4. **write_file** - Creates `projects/README.md` with documentation
5. **list_files** - Shows the complete directory structure

---

### Scenario 2: Data Analysis Pipeline
**User Prompt:** "Create and execute a data analysis script"

**Agent Actions:**
1. **write_file** - Creates `projects/analyze.py` with data processing code
2. **run_python** - Executes the script to generate statistics
3. **write_file** - Saves results to `projects/results.json`
4. **list_files** - Shows all generated files

---

### Scenario 3: System Monitoring Report
**User Prompt:** "Generate a system performance report"

**Agent Actions:**
1. **get_processes** - Collects top processes by CPU
2. **get_processes** - Collects top processes by memory
3. **run_bash** - Gets disk usage information
4. **write_file** - Saves report to `projects/system_report.txt`

---

## 🚀 Tips & Best Practices

### 1. File Paths
- Always use paths relative to the `projects/` directory
- Don't include `projects/` prefix in your requests (e.g., say "main.py" not "projects/main.py")
- The agent automatically sandboxes all operations to the `projects/` folder

### 2. Code Execution
- Python and JavaScript code runs with a 30-second timeout for safety
- Standard output is captured and displayed in the chat
- Errors are caught and reported with context

### 3. Long-Running Tasks
- For processes that might take time, use `show_progress` to display updates
- Monitor system resources with `get_processes` to check for bottlenecks

### 4. Chaining Operations
- Ask the agent to perform multiple related tasks in one prompt
- It will intelligently sequence operations (e.g., create then read)

### 5. Safety Guards
- All file operations are confined to the `projects/` directory
- No access to system files or parent directories
- Commands have 30-second timeout limits
- Process monitoring is read-only

---

## 📝 Common Prompts Quick Reference

| Goal | Example Prompt |
|------|---|
| Create Python file | "Create a Python script called `calculator.py` that..." |
| Run code | "Execute Python code that calculates..." |
| Show directory | "List all files in the projects folder" |
| Find files | "Find all `.js` files in the projects directory" |
| Check processes | "What's using the most CPU on my system?" |
| Performance test | "Run a script that tests loop performance" |
| View file | "Show me the contents of `README.md`" |

---

## 🔗 Integration Examples

### With VS Code Extension
1. Open a file in VS Code
2. Use the DCode extension command "Send to AI"
3. Request: "Refactor this function" or "Add error handling"
4. AI sends code to local agent via OpenAI API

### With Web UI
1. Open `http://localhost:5000` in browser
2. Type natural language request
3. See formatted output from each action
4. Chat history is saved automatically

### Via CLI (Direct Python)
```bash
cd ~/path/to/agent
python main.py "Write a function that reverses a string"
```

---

## 🐛 Troubleshooting

**Issue:** "Node.js not installed" error for JS execution
- **Solution:** Install Node.js from nodejs.org, then restart the agent

**Issue:** Commands timeout after 30 seconds
- **Solution:** Break large tasks into smaller steps, or optimize your code

**Issue:** "Blocked path" error for file operations
- **Solution:** Ensure paths are relative to `projects/` directory

**Issue:** Ollama connection failed
- **Solution:** Start Ollama manually: `ollama serve` in a separate terminal

---

For more details, see [README.md](README.md) and [ADVANCED_FEATURES.md](ADVANCED_FEATURES.md).
