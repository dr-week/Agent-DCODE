# Codex Control Bar - Component Reference

## Overview
The Codex-style input control bar provides a powerful, minimal interface for agent control with file attachment, code context, model selection, environment management, and approval workflows.

**Location:** Between the Mode Selector and Task Input sections

---

## UI Components

### 1. **[+] Add File Button**
- **Function:** Open file picker for multiple file selection
- **Behavior:** 
  - Accepts any file type
  - Multiple files can be attached at once
  - Files are stored in `codexState.files` array
  - Shows indicator badge with file count
- **Data Structure:**
  ```javascript
  {
    name: "filename.ext",
    content: "file_content_string",
    type: "mime/type",
    size: 1234
  }
  ```

### 2. **[<>] Code Context Button**
- **Function:** Fetch code from clipboard or user input
- **Behavior:**
  - Attempts to read from clipboard
  - Falls back to prompt dialog
  - Stores in `codexState.code`
  - Auto-populates task description
- **Use Cases:**
  - Quick code analysis
  - Debugging snippets
  - Code review requests

### 3. **[Model Dropdown]**
- **Options:**
  - 🔵 `local` - Local Ollama instance
  - ✨ `gemini` - Google Gemini
  - 🦙 `ollama` - Ollama server
  - 🤖 `openai` - OpenAI API
- **Default:** `local`
- **State:** `codexState.model`

### 4. **[⚙ Settings] Button**
- **Opens:** Floating settings popup
- **Available Toggles:**
  - `Auto-Execute` - Automatically run tasks
  - `Show Thinking` - Display model reasoning
  - `Safe Mode` - Restrict dangerous operations
- **State:** `codexState.settings` object
- **Persistence:** Values maintained during session

### 5. **[↑] Send Button**
- **Function:** Submit task with all Codex state
- **Behavior:**
  - Validates task is not empty
  - Respects `autoExecute` setting
  - Builds complete request object
  - Sends to `/api/agent/execute` endpoint
- **Hot Key:** Click button or Ctrl+Enter in task

### 6. **[Environment Dropdown]**
- **Options:**
  - 📍 `local` - Local machine
  - ☁️ `colab` - Google Colab
  - 🌐 `remote` - Remote server
- **Default:** `local`
- **State:** `codexState.environment`

### 7. **[Approvals Dropdown]**
- **Modes:**
  - ✓ `auto` - Execute without prompts
  - ⊙ `manual` - Manual approval each step
  - ⚠ `confirm` - Confirm before execution
- **Default:** `auto`
- **State:** `codexState.approvalsMode`

---

## State Management

### Core State Object
```javascript
let codexState = {
    files: [],              // Array of file objects
    code: "",               // Code context string
    model: "local",         // Selected model
    environment: "local",   // Target environment
    approvalsMode: "auto",  // Approval workflow mode
    settings: {
        autoExecute: false,     // Auto-run tasks
        showThinking: false,    // Show model reasoning
        safeMode: true          // Restrict dangerous ops
    }
};
```

### Request Format Sent to Backend
```javascript
{
    task: "user task description",
    code: "pasted or fetched code",
    model: "local|gemini|ollama|openai",
    environment: "local|colab|remote",
    approval_mode: "auto|manual|confirm",
    files: [
        {
            name: "filename.ext",
            content: "file content",
            type: "mime/type",
            size: 1234
        }
    ],
    settings: {
        autoExecute: boolean,
        showThinking: boolean,
        safeMode: boolean
    }
}
```

---

## Event Handlers

### File Operations
```javascript
handleAddFile()           // Opens file picker
handleFileSelection(e)    // Processes selected files
updateFilesIndicator()    // Updates file count badge
```

### Code Context
```javascript
handleCodeContext()       // Fetches code from clipboard/prompt
```

### Settings
```javascript
toggleSettingsPopup()     // Toggle settings visibility
showSettingsPopup()       // Display settings
hideSettingsPopup()       // Hide settings
```

### Task Execution
```javascript
sendCodexTask()          // Send with current Codex state
buildCodexRequest()      // Build request object
```

---

## CSS Classes

### Structure
- `.codex-control-bar` - Main container
- `.control-group` - Grouped controls section
- `.control-btn` - Button styling
- `.control-select` - Dropdown styling
- `.settings-popup` - Floating settings panel
- `.files-indicator` - File count badge

### States
- `:hover` - Interactive feedback
- `:active` - Press feedback
- `:focus` - Focus state
- `disabled` - Disabled state

### Responsive
- `@media (max-width: 768px)` - Tablet adjustments
- `@media (max-width: 600px)` - Mobile adaptations

---

## Usage Examples

### Example 1: Simple Task with Local Model
```javascript
// User enters task and clicks send
// codexState.model = "local"
// codexState.environment = "local"
// codexState.approvalsMode = "auto"
// Request sent to backend
```

### Example 2: File Analysis with Gemini
```javascript
// 1. Click [+] button
// 2. Select file(s)
// 3. File count appears: "2 file(s) attached"
// 4. Select "✨ gemini" from model dropdown
// 5. Enter task description
// 6. Click [↑] button
// Request includes files and uses Gemini model
```

### Example 3: Code Review with Safe Mode
```javascript
// 1. Click [<>] button
// 2. Paste code or select from clipboard
// 3. Click [⚙] button
// 4. Check "Safe Mode"
// 5. Enter review task
// 6. Submit
// Dangerous operations will be restricted
```

### Example 4: Manual Approval Workflow
```javascript
// 1. Select "⊙ manual" from approvals dropdown
// 2. Build task with necessary context
// 3. Set model, environment, etc.
// 4. Click [↑] button
// Agent will pause before each action for approval
```

---

## Integration with Backend

### Expected Endpoint
```
POST /api/agent/execute
Content-Type: application/json

{
    task: string,
    code: string,
    model: string,
    environment: string,
    approval_mode: string,
    files: array,
    settings: object
}
```

### Response Handling
```javascript
{
    success: boolean,
    plan: array,              // [{ step, description }]
    actions: array,
    results: array,
    execution_time: number,
    actions_count: number,
    error?: string
}
```

---

## Customization

### Add New Model
Edit HTML:
```html
<select id="modelSelect" class="control-select">
    <option value="new-model">🎨 new-model</option>
</select>
```

### Add New Toggle Setting
Edit HTML:
```html
<label class="setting-toggle">
    <input type="checkbox" id="newSetting" />
    <span>New Setting</span>
</label>
```

Edit JS:
```javascript
codexState.settings.newSetting = false;
const newSettingCheckbox = document.getElementById("newSetting");
newSettingCheckbox.addEventListener("change", (e) => {
    codexState.settings.newSetting = e.target.checked;
});
```

### Modify Default Environment
```javascript
// In initCodexBar() or at initialization
codexState.environment = "colab";
environmentSelect.value = "colab";
```

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+Enter` / `Cmd+Enter` | Submit task |
| `Tab` | Navigate controls |
| `Space` | Toggle checkbox |
| `Escape` | Close settings popup |

---

## Best Practices

1. **File Management**
   - Clear attached files regularly with Clear button
   - Monitor file count to avoid memory issues
   - Use descriptive filenames

2. **Model Selection**
   - Use `local` for low-latency testing
   - Use `gemini`/`openai` for advanced reasoning
   - Consider cost and latency

3. **Approval Modes**
   - Use `auto` for trusted tasks
   - Use `manual` for critical operations
   - Use `confirm` for learning/debugging

4. **Safe Mode**
   - Enable for untested tasks
   - Disable for production workflows
   - Review restrictions in backend

5. **Settings**
   - Auto-Execute for batch operations
   - Show Thinking for debugging
   - Safe Mode for file operations

---

## Troubleshooting

### File Not Attaching
- Check file size limit
- Verify file format is supported
- Check browser console for errors

### Code Context Not Working
- Grant clipboard permissions
- Use Firefox/Chrome for clipboard API
- Fall back to manual paste in prompt

### Settings Not Persisting
- Settings persist only during session
- Reload page clears state
- Use backend storage for persistence

### Model Not Responding
- Verify model availability
- Check API keys if using remote models
- Test connection to model service

---

## Performance Notes

- **File Storage:** Files stored in memory; large files may impact UI
- **State Size:** Monitor `codexState` object size
- **API Calls:** Each send button click = 1 backend request
- **Popup Rendering:** Settings popup rendered on demand

---

## Browser Support

- Chrome/Chromium 90+
- Firefox 88+
- Safari 14+
- Edge 90+

Requires:
- ES6+ Support
- FileReader API
- Clipboard API (for code context)
- Fetch API
