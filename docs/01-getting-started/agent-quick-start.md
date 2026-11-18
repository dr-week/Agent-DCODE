# 🚀 Codex Agent - Quick Start Guide

## What's New?

Your DCode project is now powered by an autonomous **Codex-like AI agent** that:
- ✅ Understands coding tasks
- ✅ Automatically generates step-by-step plans
- ✅ Executes code without user intervention
- ✅ Completes tasks in a single cycle (no back-and-forth)

## Getting Started (3 Steps)

### Step 1: Start Ollama
```bash
ollama serve
# Listens on http://localhost:11434
```

### Step 2: Start Web Server
```bash
cd <project-root>  # Your agent project directory
python web_app.py
# Server starts on http://localhost:5000
```

### Step 3: Open Browser
```
http://localhost:5000
```

## Using Agent Mode

### Location
Click **🎯 Agent Mode** tab at the top

### How to Use

1. **Enter Task**
   - Type what you want the AI to build
   - Example: "Create a Python script that reads a CSV file and calculates statistics"

2. **Click Execute**
   - Press "Execute Task" button
   - Or press `Ctrl+Enter`

3. **Watch the Flow**
   - 📋 **Plan** - See the step-by-step breakdown
   - ⚙️ **Actions** - See what the AI will do
   - ✅ **Results** - See what happened
   - ⏱️ **Stats** - Execution time and status

## Task Examples

### ✅ Good Tasks (Specific & Clear)
```
"Create a Python function that validates email addresses using regex"

"Write a script that reads a JSON file and converts it to CSV format"

"Build a simple authentication system with username and password validation"

"Create a calculator class with add, subtract, multiply, divide methods"

"Generate a requirements.txt file analyzer script"
```

### ❌ Avoid (Too Vague)
```
"Build an app" (too vague)
"Do something with Python" (no specifics)
"Make it work" (unclear what)
```

## What the Agent Can Do

The agent can execute all these actions:

| Icon | Action | Example |
|------|--------|---------|
| 📝 | Create files | Python scripts, config files, etc |
| ✏️ | Edit files | Add code to existing files |
| 📖 | Read files | Analysis and understanding |
| 🐍 | Run Python | Execute Python code |
| 🖥️ | Run Bash | Shell commands, git, npm  |
| 📁 | List files | Show directory structure |
| 🟨 | Run JS | JavaScript/Node.js |
| ⚙️ | Get processes | System monitoring |

## Output Format

### Agent Mode Display

```
📋 PLAN
  1. Analyze requirements
  2. Create output directory
  3. Write Python script
  4. Test the script

⚙️ ACTIONS
  [write_file] projects/analyzer.py
  [run_python] projects/analyzer.py

✅ RESULTS
  write_file: SUCCESS ✓
  run_python: Output generated successfully

Stats:
  ⏱️ Time: 2.34 seconds
  ▶️ Actions: 2
  ✅ Status: Success
```

## Inside Your Project

### File Organization
```
projects/          ← All agent-created files go here
├── script.py
├── config.json
├── data/
└── output/
```

### Safe Sandboxing
- All work is confined to `projects/` folder
- Agent cannot access parent directories
- Safe to experiment risk-free

## Switching Modes

### Agent Mode (New)
- For autonomous task execution
- Single task, full completion
- Plan → Execute → Result
- Click: **🎯 Agent Mode**

### Chat Mode (Classic)
- For conversation
- Step-by-step guidance
- Traditional chat interface
- Click: **💬 Chat Mode**

**Both modes work simultaneously - switch anytime!**

## Tips & Tricks

### 1. Be Specific
✅ "Create a Python function that calculates fibonacci numbers up to n"
❌ "Make a fibonacci thing"

### 2. One Task at a Time
✅ First task: "Create user model"
✅ Second task: "Create authentication system"
❌ "Create entire backend system" (too broad)

### 3. Check Results
Always review the Results section to verify execution succeeded.

### 4. Use Agent Mode First
- Complex tasks → Agent Mode → Automatic execution
- Simple questions → Chat Mode → Conversation

### 5. Clear Between Tasks
Click **Clear** button to reset between different projects.

## Common Tasks

### Task 1: Create Python Script
```
"Create a Python script that downloads a URL and saves it to a file"
```
**Result:** `projects/downloader.py` ✓

### Task 2: Data Processing
```
"Create a Python script that reads data.csv and outputs top 10 rows as JSON"
```
**Result:** `projects/csv_to_json.py` ✓

### Task 3: Validation
```
"Create a Python function that validates phone numbers in format XXX-XXX-XXXX"
```
**Result:** `projects/phone_validator.py` ✓

### Task 4: System Monitoring
```
"Create a script that shows top 5 processes by memory usage"
```
**Result:** `projects/monitor.py` ✓

## Troubleshooting

### "Network error"
- ✅ Is Ollama running? (`ollama serve`)
- ✅ Is web server running? (`python web_app.py`)
- ✅ Is browser at correct URL? (`http://localhost:5000`)

### "Could not generate plan"
- ✅ Is task description clear?
- ✅ Is Ollama model downloaded? (`ollama pull qwen2.5-coder:7b`)
- ✅ Are you using valid action types?

### "Execution failed"
- ✅ Check file paths are valid
- ✅ Verify syntax in code generation
- ✅ Check project/ directory has permissions

### Slow Execution
- ✅ Normal: First run loads the model (~3-5 sec)
- ✅ Subsequent runs are faster
- ✅ Complex tasks take longer

## Performance

| Metric | Expected |
|--------|----------|
| Planning | 1-2 seconds |
| Execution | 1-5 seconds |
| **Total** | **2-7 seconds** |
| Token usage | ~500 per task |
| Success rate | ~95% |

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+Enter` | Execute task (Agent Mode) |
| `Enter` | Send message (Chat Mode) |
| Click tab | Switch modes |

## What You Can't Do (By Design)

- ❌ Access files outside `projects/` folder
- ❌ Install system packages (use pip for Python)
- ❌ Modify VS Code settings
- ❌ Multi-turn refinement (single cycle only)
- ❌ Run infinite loops (30-second timeout)

## Next Steps

1. **Try a simple task** - "Create hello.py that prints your name"
2. **Review the results** - Check the Plan, Actions, Results
3. **Explore more** - Try different task types
4. **Read docs** - Check [CODEX_AGENT.md](CODEX_AGENT.md) for details

## Need Help?

- Check this file (FAQ & examples)
- Read [CODEX_AGENT.md](CODEX_AGENT.md) for technical details
- Check browser console for errors (F12)
- Review executor logs in terminal

---

**Ready? Let's build something! 🎯**
