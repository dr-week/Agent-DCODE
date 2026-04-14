# 🤖 DCode - Autonomous AI Coding Agent

A **fully offline** AI coding agent with autonomous loop capabilities. Continuously plans, executes, and refines code until goals are complete. No cloud dependencies, no internet required. Works like GitHub Copilot but with your own local models via Ollama.

![Status](https://img.shields.io/badge/Status-Production-green)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Autonomous](https://img.shields.io/badge/Autonomous-Loop-brightgreen)
![License](https://img.shields.io/badge/License-MIT-green)

## 🚀 Autonomous Loop (NEW)

**Completely autonomous coding** — Agent continuously plans, executes, detects errors, and refines until goals are complete.

```
Loop: Plan → Generate Actions → Execute → Check → Iterate
```

- **Auto-Planning**: LLM generates step-by-step plans
- **Error Recovery**: Detects failures and retries with learned context
- **Iteration Control**: Configurable max iterations (default: 10)
- **State Tracking**: Logs all decisions and actions
- **No User Intervention**: Runs start-to-finish autonomously

See [AUTONOMOUS_SYSTEM.md](AUTONOMOUS_SYSTEM.md) for architecture and [AUTONOMOUS_AGENT.md](AUTONOMOUS_AGENT.md) for detailed docs.

---

## 🎯 VS Code Extension

**Agent-DCODE** — Full-featured VS Code extension with model selection and process management.

- **Location:** `vsc-agent/dcode/`
- **Features:** Multi-model support, auto-start Ollama, real-time chat, autonomous mode
- **Models:** Local (Ollama), Gemini, OpenAI (configurable)
- **Setup:** Configure backend URL in VS Code settings
- **Usage:** Chat sidebar, model dropdown, or autonomous agent command
- **Size:** 300+ lines of TypeScript, fully compiled & ready

See [AGENT_DCODE_README.md](vsc-agent/dcode/AGENT_DCODE_README.md) for details.

---

### Prerequisites
- **Python 3.10+**
- **Ollama** (download from [ollama.ai](https://ollama.ai))
- **Local LLM model** (e.g., `qwen2.5-coder:7b`, `mistral`, `codegemma`)

### Installation

1. **Clone/Setup the project**
   ```bash
   cd <project-root>
   python -m venv .venv
   .venv\Scripts\Activate.ps1        # Windows
   source .venv/bin/activate          # macOS/Linux
   pip install -r requirements.txt
   ```

2. **Start Ollama** (in separate terminal)
   ```bash
   ollama serve
   ```

3. **Run the web app**
   ```bash
   python web_app.py
   ```

4. **Open in browser**
   ```
   http://localhost:5000
   ```

---

## 📋 Architecture

### **Autonomous Loop (NEW)**
```
Goal (High-level requirement)
    ↓
[Autonomous Agent Loop]
    ├─ Plan Generation (LLM: What steps?)
    ├─ Action Generation (LLM: What code?)
    ├─ Sandbox Execution (projects/ directory)
    ├─ Error Detection
    ├─ Context Accumulation
    └─ Iterate or Complete?
    ↓
[Return Results + Execution History]
```

### **Backend (Python)**
```
autonomous_agent.py → Autonomous loop controller (NEW)
main.py           → CLI entry point
web_app.py        → Flask web server
ollama_client.py  → Local Ollama integration
parser.py         → JSON extraction
executor.py       → Action execution
logger.py         → State tracking & logging
```

### **Frontend (Web UI + Extension)**
```
static/                 Web UI (Chrome/Firefox)
├── index.html          Chat interface
├── style.css           Styling
└── script.js           Real-time messaging

vsc-agent/dcode/        VS Code Extension
├── extension.ts        Entry point
├── api/backend-api.ts  Unified API client
└── utils/process-manager.ts  Ollama lifecycle
```

### **Request Flow**
```
User Goal
    ↓
Autonomous Agent
├─ LLM Plan (Ollama/Gemini)
├─ LLM Actions (Ollama/Gemini)
├─ Executor (Sandboxed in projects/)
├─ Error Checker
└─ Iterate or Return
    ↓
[Logged Results + Execution History]
---

## ✨ Features

### Autonomous Loop (NEW) 🚀
- **Continuous Planning** — LLM generates 3-5 step plans automatically
- **Auto-Execution** — Converts plans to concrete actions
- **Error Recovery** — Detects failures and retries with learned context
- **Iteration Control** — Configurable max iterations (prevents infinite loops)
- **State Tracking** — Logs all decisions, actions, and results
- **Goal Completion** — Runs until success or max iterations reached
- **No User Intervention** — Fully autonomous start-to-finish execution

### Single-Cycle Agent ✅
- **Web Chat Interface** — Beautiful, responsive UI (works on mobile)
- **Local LLM Integration** — Uses your local Ollama models
- **Code Generation** — Writes Python, JS, and other code
- **File Operations** — Create, read, append files safely
- **Command Execution** — Run shell commands (30s timeout)
- **Error Handling** — 3-retry logic with fallback
- **Status Monitor** — Real-time connection status
- **Path Safety** — Sandboxed to `projects/` directory (prevents breakouts)

### Advanced Execution Features 🚀
- **Python Execution** — Run Python code directly
- **Bash Commands** — Execute shell/bash commands
- **JavaScript Execution** — Run Node.js scripts (requires Node.js)
- **File Browsing** — Display directory structure recursively
- **Process Monitoring** — Get system process info (CPU, memory)
- **Progress Bars** — Visual feedback for long operations

### What Works But Needs Improvement ⚠️
- **JSON Parsing** — Regex-based fallback, sometimes LLM outputs malformed JSON
- **Long Running Tasks** — 30s timeout may cut off complex operations
- **Error Detection** — Heuristic-based (looks for error patterns in output)
- **Autonomous Loop Scope** — Limited to simple coding tasks (file generation, basic logic)

### Known Limitations ❌
- **No Internet Access** — By design (fully offline)
- **Slow on Low-End Hardware** — LLM inference is CPU/memory intensive
- **Bounded Execution** — Max iterations prevent infinite loops but limit complex tasks
- **No Rollback** — No way to undo executed actions
- **Single User** — No multi-user support
- **No Persistent Storage** — Chat history only in session memory
- **No API Keys/Auth** — No security (use on local network only)
- **Action Limit** — Restricted to projects/ directory for safety

---

## 📚 Documentation & Resources

### Autonomous Agent (NEW) ⭐
- **[AUTONOMOUS_SYSTEM.md](AUTONOMOUS_SYSTEM.md)** — Complete system architecture and reference
- **[AUTONOMOUS_AGENT.md](AUTONOMOUS_AGENT.md)** — Usage guide with examples and API reference
- **[AUTONOMOUS_INTEGRATION.md](AUTONOMOUS_INTEGRATION.md)** — Integration patterns (Flask, Extension, clients)

### Getting Started
- **[START_HERE.md](START_HERE.md)** — Quick start guide
- **[INSTALL.md](INSTALL.md)** — Detailed setup for all platforms
- **[TEST_WEB_UI.md](TEST_WEB_UI.md)** — Quick test scenarios ⭐
- **[USAGE_EXAMPLES.md](USAGE_EXAMPLES.md)** — 50+ practical examples ⭐

### Feature Documentation
- **[ADVANCED_FEATURES.md](ADVANCED_FEATURES.md)** — Complete reference for all 10 actions
- **[AGENT_QUICK_START.md](AGENT_QUICK_START.md)** — Quick reference guide
- **[AGENT_DCODE_README.md](vsc-agent/dcode/AGENT_DCODE_README.md)** — VS Code extension guide

### Development & Troubleshooting
- **[DEBUG.md](vsc-agent/dcode/DEBUG.md)** — Debugging VS Code extension
- **[PROJECT_LOG.md](PROJECT_LOG.md)** — Development history and decisions
- **[RELEASE_v1.2.0.md](RELEASE_v1.2.0.md)** — Latest release notes

---

## 🎯 Advanced Features  

The agent now supports powerful actions including file browsing, code execution (Python, Bash, JavaScript), system monitoring, and more!

**See [ADVANCED_FEATURES.md](ADVANCED_FEATURES.md) for complete documentation.**

---

### Example 1: Write Python Code
```
You: "write a fibonacci function that returns first 10 numbers"

DCode:
✓ Created: projects/fibonacci.py
✓ Executed 1 action
```

### Example 2: Create and Run a File
```
You: "create a hello world app in python and run it"

DCode:
✓ Created: projects/hello.py
✓ Executed: python projects/hello.py
Output: Hello, World!
```

### Example 3: Read and Modify Files
```
You: "read projects/test.py and add error handling"

DCode:
✓ Read: projects/test.py
✓ Appended: projects/test.py
Output: Modified successfully
```

---

## 🔧 Configuration

### Change the Model
Edit `ollama_client.py`:
```python
MODEL = "mistral"  # or "codegemma", "neural-chat", etc.
```

### Change the LLM Temperature
Edit `ollama_client.py`:
```python
"temperature": 0  # 0=deterministic, 1=creative
```

### Change Default Port
Edit `web_app.py`:
```python
app.run(host="0.0.0.0", port=8000)  # Changed from 5000
```

### Available Ollama Models
```bash
ollama pull qwen2.5-coder:7b    # Recommended (7B params)
ollama pull mistral              # General purpose
ollama pull codegemma            # Code-focused
ollama pull neural-chat          # Fast
ollama pull llama2               # Large
```

---

## 🐛 Troubleshooting

### "Connection refused" error
- Make sure Ollama is running: `ollama serve`
- Check if port 11434 is available (Ollama default)

### "Could not get valid JSON after 3 attempts"
- Model is generating malformed JSON
- Try a different model
- Increase retry attempts in `main.py`

### "BLOCKED PATH" error
- Tried to create file outside `projects/`
- This is intentional for safety
- All files must be in `projects/` directory

### Web UI shows "Offline"
- Ollama service crashed
- Python backend crashed
- Network issue

### Slow responses
- Your model is too large for your hardware
- Use a smaller model (7B instead of 13B)
- Increase RAM/VRAM

---

## 📁 Project Structure

```
agent/
├── README.md                      # This file
├── requirements.txt               # Python dependencies
│
├── autonomous_agent.py            # Autonomous loop controller (NEW)
├── test_autonomous.py             # Test suite for autonomous agent (NEW)
│
├── main.py                        # CLI entry point
├── web_app.py                     # Flask web server (port 5000)
├── agent.py                       # Single-cycle agent
├── ollama_client.py               # Ollama API integration
├── parser.py                      # JSON extraction
├── executor.py                    # Action executor
├── logger.py                      # Structured logging
├── utils.py                       # Utilities
│
├── static/                        # Web UI
│   ├── index.html                 Chat interface
│   ├── style.css                  Styling
│   └── script.js                  Real-time messaging
│
├── projects/                      # Sandbox directory (AI work)
│   └── test.py                    Example file
│
├── .logs/                         # Execution logs (auto-generated)
│   └── {project_name}/
│
├── colab_agent.py                 # Colab agent (Gemini + ngrok)
├── requirements_colab.txt         # Colab dependencies
│
└── vsc-agent/dcode/               # VS Code Extension
    ├── package.json               Configuration
    ├── src/
    │   ├── extension.ts           Main entry point
    │   ├── api/backend-api.ts     Unified API client
    │   ├── webview/chat.ts        Chat UI
    │   └── utils/process-manager.ts   Ollama lifecycle (NEW)
    └── ...
```

---

## 🚧 Roadmap / Future Improvements

### High Priority
- [x] Autonomous loop system ✅
- [x] Model selection from UI ✅
- [x] VS Code extension integration ✅
- [x] Local model process management ✅
- [ ] Save chat history to database
- [ ] Code syntax highlighting in chat
- [ ] Rollback support
- [ ] File upload/download capability

### Medium Priority
- [ ] Multi-agent collaboration (agents sharing context)
- [ ] Checkpoint/resume for long-running tasks
- [ ] Cost tracking (token usage monitoring)
- [ ] Confidence scoring (agent certainty levels)
- [ ] Custom goal templates
- [ ] Docker containerization

### Future Enhancements
- [ ] Parallel action execution
- [ ] Persistent knowledge base
- [ ] Performance optimization
- [ ] REST API authentication
- [ ] Multi-user support with authentication

---

## 🔐 Security & Safety

⚠️ **Important: This is for LOCAL USE ONLY**

- ✅ All processing is local (no data sent anywhere)
- ✅ Files restricted to `projects/` directory
- ✅ Commands execute with your user permissions
- ⚠️ No input validation on command execution
- ⚠️ No authentication/authorization
- ⚠️ Don't expose on public network

**Best Practices:**
- Use only on personal machines
- Don't run untrusted models
- Review generated code before deployment
- Keep Ollama updated

---

## 🤝 Contributing

Want to improve DCode? Here's what needs work:

1. **Frontend Improvements**
   - Add syntax highlighting (use Prism.js or Highlight.js)
   - Add file browser for `projects/` directory
   - Dark mode toggle

2. **Backend Enhancements**
   - Persistent chat history (SQLite/PostgreSQL)
   - Model configuration UI
   - Better error messages

3. **Testing**
   - Unit tests for executor
   - Integration tests with Ollama
   - UI E2E tests

4. **Documentation**
   - API documentation
   - Video tutorial
   - Troubleshooting guide

---

## 📝 Development Notes

### For the Next Developer

**What's Working Well:**
- Action execution is clean and modular
- JSON parsing has good fallbacks
- Flask integration is straightforward

**What Needs Fixing:**
1. **Hardcoded model name** — Should be config-driven
2. **No database** — Chat history only in memory
3. **Incomplete VS Code extension** — Just a skeleton
4. **No tests** — Add unit tests to executor.py
5. **Error handling** — Too generic, needs better messages

###Testing the Agent Manually
```bash
# Via CLI
python main.py "write a hello world program"

# Or use the web interface
# Go to http://localhost:5000
```

---

## 📞 Support

**Quick Help:**
- Check Flask terminal for errors
- Check Ollama terminal for connection issues
- Browser console (F12) for frontend errors

**Common Issues:**
- See **Troubleshooting** section above
- Check Python version: `python --version` (must be 3.10+)
- Verify Ollama: `ollama list` should show your models

---

## 📄 License

MIT License - Feel free to modify and distribute

---

## 🎯 Key Takeaways

| Feature | Status | Notes |
|---------|--------|-------|
| **Offline LLM** | ✅ Complete | Ollama + local models |
| **Web UI** | ✅ Complete | Beautiful chat interface |
| **Single-Cycle Agent** | ✅ Complete | Plan → Execute → Return |
| **Autonomous Loop** | ✅ Complete | Continuous plan → exec → check → iterate |
| **File Operations** | ✅ Complete | Safe sandbox in projects/ |
| **Command Execution** | ✅ Complete | Python, Bash, JavaScript support |
| **VS Code Extension** | ✅ Complete | Full-featured with model selection |
| **Process Management** | ✅ Complete | Auto-start/stop Ollama |
| **Error Recovery** | ✅ Complete | Detects and retries failures |
| **State Logging** | ✅ Complete | JSON logs with execution history |
| **Persistence** | ⏳ Future | Chat history only in memory |
| **Production Ready** | ✅ Yes | Autonomous mode ready for use |

---

## Quick Start

```bash
# 1. Setup Python environment
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 2. Start Ollama (separate terminal)
ollama serve

# 3. Run autonomous agent
python test_autonomous.py 1

# OR start web server
python web_app.py  # http://localhost:5000
```

---

**Last Updated:** April 15, 2026  
**Current Version:** 1.2.0 (Production)  
**Status:** Autonomous loop ready for deployment  
**Maintained by:** Dishant  

🚀 **Start your autonomous coding journey!**
