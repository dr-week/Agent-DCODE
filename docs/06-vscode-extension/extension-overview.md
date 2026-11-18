# DCODE Agent Integration - VS Code Extension

## Overview

The DCODE extension now connects to your local **Codex-like Agent API** at `http://localhost:5000/api/agent/execute`.

## Features

✨ **Agent Mode** - Autonomous task execution with plan → execute → result  
🔗 **Local API Connection** - Single fetch call to agent  
📝 **Minimal UI** - Text-only interface, no heavy styling  
⚡ **Loading & Error States** - Real-time feedback  
✏️ **Code Changes** - Auto-apply file changes via WorkspaceEdit  

## Setup

### 1. Start Local Agent
```bash
# Terminal 1: Ollama
ollama serve

# Terminal 2: Agent Web Server
cd <project-root>  # Your agent project directory
python web_app.py
# Server starts on http://localhost:5000
```

### 2. Start VS Code Extension
```bash
# Terminal 3: Extension dev mode
cd vsc-agent/dcode
npm run watch
# Opens extension test window

# Or compile for production:
npm run package
```

## Usage

### Open Agent Mode
1. Press `Ctrl+Shift+P`
2. Type "DCODE Agent" or search "Open Agent Mode"
3. Click "DCODE: Open Agent Mode"
4. A new webview panel opens

### Execute a Task

1. **Enter Task**
   - Type: "Create a Python script that validates email addresses"
   - Or paste existing code context

2. **Execute** (Ctrl+Enter or click button)
   - Shows loading state: "⏳ Executing task..."
   - Fetches from `http://localhost:5000/api/agent/execute`

3. **View Results**
   - 📋 **PLAN** - Step-by-step breakdown
   - ⚙️ **ACTIONS** - What the agent will do
   - ✅ **RESULTS** - Output from each action
   - Stats: Time, action count, status

### Auto-Apply Code Changes
When agent creates/modifies files:
- File changes are automatically applied to your workspace
- Shows notification: "✅ Task completed. Files updated."
- You can undo with Ctrl+Z if needed

## API Integration

### Request
```json
POST http://localhost:5000/api/agent/execute

{
  "task": "Create a login system",
  "selected_code": "optional code snippet"
}
```

### Response
```json
{
  "success": true,
  "task": "Create a login system",
  "plan": [
    {"step": 1, "description": "Design database schema"},
    {"step": 2, "description": "Create user model"},
    {"step": 3, "description": "Create authentication"}
  ],
  "actions": [
    {"type": "write_file", "path": "projects/user_model.py", "content": "..."},
    {"type": "write_file", "path": "projects/auth.py", "content": "..."}
  ],
  "results": [
    {"type": "write_file", "output": "[CREATED] ...", "success": true},
    {"type": "write_file", "output": "[CREATED] ...", "success": true}
  ],
  "actions_count": 2,
  "execution_time": 2.34,
  "error": null
}
```

## Architecture

### Files Structure
```
src/
├── extension.ts            ← Main extension logic
├── api/
│   ├── openai.ts          ← Chat mode (OpenAI)
│   └── agent-api.ts       ← Agent mode (Local API) ⭐ NEW
└── webview/
    ├── chat.ts            ← Chat UI
    └── agent.ts           ← Agent UI ⭐ NEW
```

### Key Components

#### `agent-api.ts` - API Handler
```typescript
export async function executeAgentTask(task: string, code?: string): Promise<AgentResponse>
export async function applyCodeChanges(results: Array<any>)
```

#### `agent.ts` - Webview UI
- Textarea for task input
- Execute & Clear buttons
- Plan/Actions/Results display
- Real-time stats

#### `extension.ts` - Main Logic
- Registers `dcode.agent` command
- Handles selected code extraction
- Applies code changes via WorkspaceEdit
- Shows success/error notifications

## Code Examples

### Task: Create Validator
```
Input Task: 
"Create a Python function that validates email using regex"

Output:
📋 PLAN
  1. Design email regex pattern
  2. Create validation function
  3. Add test cases

⚙️ ACTIONS
  write_file - projects/email_validator.py - [50 chars...]
  run_python - projects/test_email.py - [50 chars...]

✅ RESULTS
  write_file: ✓ OK
  run_python: ✓ All tests passed

Stats: ⏱️ 2.45s | Actions: 2 | Status: ✅ Success
```

### Task: Fix Code
```
Select code in editor → Open Agent → Task: "Fix this code"

Agent automatically includes:
- selected_code: <your selected code>
- Shows plan for fixes
- Applies changes automatically
```

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+Shift+P` → "Agent" | Open Agent Mode |
| `Ctrl+Enter` | Execute task (in agent panel) |
| `Ctrl+Z` | Undo auto-applied changes |

## Error Handling

### Connection Error
```
❌ Failed to execute task: Failed to fetch
→ Ensure http://localhost:5000 is running
```

### API Error
```
❌ API error: 500 Internal Server Error
→ Check server logs
```

### Task Error
```
❌ <error message from agent>
→ Review task description
→ Try simpler task first
```

## Performance

| Operation | Time |
|-----------|------|
| Task → Plan | ~1-2s |
| Plan → Execute | ~1-5s |
| Auto-apply | <100ms |
| **Total** | **~2-7s** |

## Files Created/Modified

### New Files
- `src/api/agent-api.ts` - Agent API handler
- `src/webview/agent.ts` - Agent UI webview

### Modified Files
- `src/extension.ts` - Added agent command & handler
- `package.json` - Added `dcode.agent` command

## Limitations

- ❌ Cannot apply changes outside workspace
- ❌ Only plain text UI (by design - minimal)
- ❌ No styling customization (uses VS Code themes)
- ❌ Single task execution (no history)
- ❌ Requires agent server running on localhost:5000

## Troubleshooting

### Agent panel doesn't open
- Ensure extension is activated
- Run command palette: `dcode.agent`
- Check browser console (F12) for errors

### Changes not applying
- Check file paths are valid
- Ensure workspace has write permissions
- Check VS Code status bar for errors

### Slow execution
- First run loads model (~3-5s) - normal
- Subsequent runs faster
- Complex tasks take longer

## Development

### Build
```bash
npm run compile      # Development
npm run watch        # Watch mode
npm run package      # Production
```

### Test
```bash
npm run check-types  # Type check
```

### Debug
```bash
# In extension, press F5
# Opens debug window with extension running
# Check browser console (F12) for webview logs
```

## Next Steps

1. Test with simple task: "Create hello.py"
2. Try code selection: Select code → Open Agent → Task
3. Check file changes in workspace Explorer
4. Review console logs for debugging

---

**Ready to build autonomously! 🚀**
