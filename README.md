# 🤖 DCode - Offline AI Coding Agent

A **fully offline** AI coding assistant that runs local models. No cloud dependencies, no internet required. Works like GitHub Copilot but with your own local models via Ollama.

![Status](https://img.shields.io/badge/Status-Beta-yellow)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)

## 🎯 VS Code Extension (NEW)

**Agent-DCODE** — Minimal VS Code extension for sending code to OpenAI.

- **Location:** `vsc-agent/dcode/`
- **Setup:** Get OpenAI API key → Add to VS Code settings (`dcode.apiKey`)
- **Usage:** Select code → "Send to DCODE AI" or use sidebar chat
- **Size:** ~300 lines of TypeScript, fully compiled & ready

See [AGENT_DCODE_README.md](vsc-agent/dcode/AGENT_DCODE_README.md) for details.

---

### Prerequisites
- **Python 3.10+**
- **Ollama** (download from [ollama.ai](https://ollama.ai))
- **Local LLM model** (e.g., `qwen2.5-coder:7b`, `mistral`, `codegemma`)

### Installation

1. **Clone/Setup the project**
   ```bash
   cd c:\Users\disha\Documents\CODES\001\agent
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
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

### **Backend (Python)**
```
main.py           → CLI entry point (legacy)
ollama_client.py  → Connects to local Ollama API
parser.py         → Extracts JSON from LLM responses
executor.py       → Executes file/command actions
web_app.py        → Flask web server (NEW)
```

### **Frontend (Web UI)**
```
static/
├── index.html     → Chat UI
├── style.css      → Beautiful gradient styling
└── script.js      → Real-time message handling
```

### **How It Works Flow**
```
User Input
    ↓
[Flask API: /api/ask]
    ↓
[Ollama Local LLM]
    ↓
[JSON Parser]
    ↓
[Action Executor]
    ├─ Write File
    ├─ Append File
    ├─ Read File
    └─ Run Command
    ↓
[Response Back to Chat UI]
```

---

## ✨ Features

### Currently Working ✅
- **Web Chat Interface** — Beautiful, responsive UI (works on mobile)
- **Local LLM Integration** — Uses your local Ollama models
- **Code Generation** — Writes Python, JS, and other code
- **File Operations** — Create, read, append files safely
- **Command Execution** — Run shell commands (30s timeout)
- **Chat History** — Messages persist in session
- **Error Handling** — 3-retry logic with fallback
- **Status Monitor** — Real-time connection status
- **Path Safety** — Sandboxed to `projects/` directory (prevents breakouts)

### Advanced Features (NEW) 🚀
- **List Files** — Display directory structure recursively
- **Python Execution** — Run Python code directly
- **Bash Commands** — Execute shell/bash commands
- **JavaScript Execution** — Run Node.js scripts (requires Node.js)
- **Process Monitoring** — Get system process info (CPU, memory)
- **Progress Bars** — Visual feedback for long operations

### What Works But Needs Improvement ⚠️
- **JSON Parsing** — Regex-based fallback, sometimes LLM outputs malformed JSON
- **Long Running Tasks** — 30s timeout may cut off complex operations
- **Error Messages** — User-facing errors could be more helpful
- **Model Selection** — Hardcoded to `qwen2.5-coder:7b` (should be configurable)

### Known Limitations ❌
- **No Internet Access** — By design (fully offline)
- **Slow on Low-End Hardware** — LLM inference is CPU/memory intensive
- **No Code Syntax Highlighting** — Chat shows raw code
- **No File Diff Preview** — Can't preview changes before execution
- **No Rollback** — No way to undo executed actions
- **No Code Review** — Model output not vetted before execution
- **Single User** — No multi-user support
- **No Persistent Storage** — Chat history only in session memory
- **Limited Model Support** — Only tested with qwen2.5-coder
- **No API Keys/Auth** — No security (use on local network only)

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
├── README.md                 # This file
├── requirements.txt          # Python dependencies
├── main.py                   # CLI entry point (legacy)
├── web_app.py               # Flask web server
├── ollama_client.py         # Ollama API integration
├── parser.py                # JSON extraction
├── executor.py              # Action executor
├── utils.py                 # Empty (for future use)
├── static/
│   ├── index.html           # Chat UI
│   ├── style.css            # Styling
│   └── script.js            # Chat logic
├── projects/                # Sandbox directory (AI writes here)
│   └── test.py              # Example file
└── vsc-agent/               # VS Code extension (incomplete)
    └── dcode/
        ├── package.json
        ├── src/extension.ts
        └── ...
```

---

## 🚧 Roadmap / Future Improvements

### High Priority
- [ ] Save chat history to database
- [ ] Configurable model selection from UI
- [ ] Code syntax highlighting in chat
- [ ] Error recovery and rollback support
- [ ] File upload/download capability

### Medium Priority
- [ ] Multi-user support with authentication
- [ ] Conversation memory (context window)
- [ ] Code review before execution
- [ ] Model selection dropdown
- [ ] Command preview before execution

### Low Priority
- [ ] VS Code extension integration (currently incomplete)
- [ ] Docker containerization
- [ ] REST API authentication
- [ ] File versioning/history
- [ ] Performance profiling

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

**File Location:** `c:\Users\disha\Documents\CODES\001\agent\`

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

| What | Status | Notes |
|------|--------|-------|
| **Offline LLM** | ✅ Working | Uses Ollama + local models |
| **Web UI** | ✅ Working | Beautiful chat interface |
| **Code Generation** | ✅ Working | JSON-based action system |
| **File Operations** | ✅ Working | Safe sandbox in projects/ |
| **Persistence** | ❌ Not yet | Chat history only in memory |
| **Syntax Highlighting** | ❌ Not yet | Raw text in chat |
| **VS Code Extension** | 🚧 WIP | Skeletal, needs integration |
| **Production Ready** | ❌ No | Beta stage, for local use only |

---

**Last Updated:** April 11, 2026  
**Current Version:** 1.0.0 (Beta)  
**Maintained by:** Dishant  

🚀 **Happy coding with your offline AI agent!**
