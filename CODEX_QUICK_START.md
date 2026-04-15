# Codex Control Bar - Quick Reference

## 🎯 Quick Start
1. Open web UI
2. Use Codex Control Bar above task input
3. Select model, environment, approvals
4. Attach files or code context
5. Click [↑] to send task

## 🔘 Controls at a Glance

| Control | Icon | Action | States |
|---------|------|--------|--------|
| Add File | **[+]** | Open file picker | Files count indicator |
| Code Context | **[<>]** | Fetch code from clipboard | Code preview |
| Model | **[🔵]** | Select AI model | local, gemini, ollama, openai |
| Settings | **[⚙]** | Toggle options | Auto-Execute, Show Thinking, Safe Mode |
| Send Task | **[↑]** | Submit to backend | Sends full request object |
| Environment | **[📍]** | Choose runtime | local, colab, remote |
| Approvals | **[✓]** | Approval workflow | auto, manual, confirm |

## 💾 State Structure
```javascript
{
  task: "description",
  code: "pasted code",
  model: "local|gemini|ollama|openai",
  environment: "local|colab|remote",
  approval_mode: "auto|manual|confirm",
  files: [{name, content, type, size}],
  settings: {autoExecute, showThinking, safeMode}
}
```

## ⌨️ Keyboard Shortcuts
- **Ctrl/Cmd + Enter** - Send task
- **Tab** - Navigate controls
- **Space** - Toggle checkbox
- **Esc** - Close settings popup

## 🎪 Common Workflows

### Quick Local Task
```
1. Enter task → Click [↑]
```

### File Analysis
```
1. Click [+] → Select file(s) → Enter task → Click [↑]
```

### Code Review
```
1. Click [<>] → Paste code → Select model → Click [↑]
```

### Safe Execution
```
1. Click [⚙] → Check "Safe Mode" → Enter task → Click [↑]
```

### Remote Execution
```
1. Select [☁️ colab] → Click [↑]
```

## 📝 Request Format Sent
```json
{
  "task": "user input",
  "code": "code snippet",
  "model": "local",
  "environment": "local",
  "approval_mode": "auto",
  "files": [],
  "settings": {
    "autoExecute": false,
    "showThinking": false,
    "safeMode": true
  }
}
```

## 🎨 Visual Cues
- **File indicator:** Shows when files attached
- **Settings popup:** Appears below ⚙ button
- **Button states:** Hover blue tint, active darker
- **Send button:** Purple gradient, always visible

## 💡 Tips & Tricks

✅ **Do:**
- Use Safe Mode for experimental tasks
- Enable Show Thinking for debugging
- Use Gemini/OpenAI for complex reasoning
- Select Colab for heavy computation

❌ **Don't:**
- Attach massive files (memory limits)
- Change model mid-execution
- Use random approval modes without testing
- Leave Safe Mode disabled for untrusted tasks

## 🔧 Integration Checklist

For backend developers:
- [ ] Update `/api/agent/execute` endpoint
- [ ] Parse all 7 request fields
- [ ] Validate file content encoding
- [ ] Handle approval_mode logic
- [ ] Implement safe_mode restrictions
- [ ] Return success/error responses

## 📍 Location in UI
```
┌──────────────────────┐
│   Header             │
├──────────────────────┤
│   Mode Selector      │
├──────────────────────┤
│ 🔴 CODEX BAR HERE    │  ← You are here
├──────────────────────┤
│ Task Textarea        │
├──────────────────────┤
│ Workflow/Results     │
└──────────────────────┘
```

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Files not attaching | Check console, verify format |
| Code context fails | Grant clipboard permission |
| Model selector unresponsive | Refresh page |
| Settings not saving | Use localStorage (add feature) |
| Send button disabled | Clear invalid task text |

## 📚 Documentation Files
- **[CODEX_CONTROL_BAR.md](CODEX_CONTROL_BAR.md)** - Full reference
- **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** - Implementation details

## 🎓 Learning Path
1. **Beginner:** Use local model, no settings
2. **Intermediate:** Add files, try different models
3. **Advanced:** Use approval modes, safe mode, remote environments
4. **Expert:** Batch tasks, automation, custom settings

## 🚀 Next: Backend Integration

Update your `/api/agent/execute` endpoint to:

```python
@app.post("/api/agent/execute")
async def execute_agent(request: CodexRequest):
    # 1. Extract fields
    task = request.task
    files = request.files  # Array of file objects
    model = request.model
    environment = request.environment
    approval_mode = request.approval_mode
    settings = request.settings
    
    # 2. Initialize agent with model + environment
    agent = Agent(model=model, env=environment)
    
    # 3. Load files if any
    for f in files:
        agent.add_file(f.name, f.content)
    
    # 4. Set options
    agent.safe_mode = settings.safeMode
    agent.auto_execute = settings.autoExecute
    agent.show_thinking = settings.showThinking
    
    # 5. Execute
    if approval_mode == "auto":
        result = agent.execute(task)
    elif approval_mode == "manual":
        result = agent.execute_with_approval(task)
    else:  # confirm
        await agent.confirm_each_step(task)
    
    return result
```

## 📞 Need Help?
Check the documentation files for detailed explanations of each component.
