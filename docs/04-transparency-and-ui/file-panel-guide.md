# File Structure Panel - Implementation Guide

## 📋 Overview
A live file structure panel has been added to the web UI, displaying the project file tree with real-time AI activity indicators showing which file the agent is currently working on.

---

## 🔌 Backend Endpoints

### 1. GET `/api/files`
**Purpose:** Fetch project file tree structure

**Response:**
```json
{
    "success": true,
    "files": [
        {
            "name": "agent.py",
            "path": "agent.py",
            "type": "file",
            "size": 2048
        },
        {
            "name": "src",
            "path": "src",
            "type": "directory",
            "children": [
                {
                    "name": "module.py",
                    "path": "src/module.py",
                    "type": "file",
                    "size": 1024
                }
            ]
        }
    ],
    "root": "."
}
```

**Features:**
- Recursively builds file tree
- Filters ignored directories (.git, __pycache__, .venv, node_modules, .logs)
- Includes file sizes
- Nested children for directories
- Handles permission errors gracefully

### 2. GET `/api/current-file`
**Purpose:** Get current file being processed by agent

**Response:**
```json
{
    "path": "src/module.py",
    "status": "working",
    "message": "Processing file..."
}
```

**Status Values:**
- `pending` - File queued, not started
- `working` - Currently processing (⏳)
- `done` - Processing complete (✔)
- `error` - Error occurred (✕)

### 3. POST `/api/current-file`
**Purpose:** Update current file status (called by agent/transparency tracker)

**Request:**
```json
{
    "path": "src/module.py",
    "status": "working",
    "message": "Building class structure..."
}
```

**Response:**
```json
{
    "success": true,
    "state": {
        "path": "src/module.py",
        "status": "working",
        "message": "Building class structure..."
    }
}
```

---

## 🎨 Frontend UI

### Layout Structure
```
┌─────────────────────────────────────────┐
│          Header                         │
├──────────┬──────────────────────────────┤
│          │                              │
│  📁      │      Main Content            │
│  Files   │                              │
│  Sidebar │      Mode Selector           │
│          │      Codex Bar               │
│          │      Task Area               │
│          │      Results                 │
│          │                              │
└──────────┴──────────────────────────────┘
```

### Sidebar Features

**Header:**
- Title: "📁 Files"
- Close/Toggle button (✕)

**File Tree:**
- Recursive tree structure
- Expandable/collapsible directories (▶ →)
- File type icons (based on extension)
- Status indicators:
  - `pending` → ○ (gray)
  - `working` → ⏳ (orange, pulsing)
  - `done` → ✔ (green)
  - `error` → ✕ (red)

**Current File:**
- Highlighted with light blue background
- Blue dot indicator on right
- Auto-scrolls into view
- Bold text styling

### File Type Icons
```
.py       → 🐍 Python
.js       → 📜 JavaScript
.ts       → 📘 TypeScript
.jsx/.tsx → ⚛️ React
.json     → {} JSON
.html     → 🌐 HTML
.css      → 🎨 CSS
.md       → 📝 Markdown
.txt      → 📄 Text
.yml/.yaml→ ⚙️ YAML
.sh/.bash → 💻 Shell
.sql      → 💾 SQL
default   → 📄 Generic
```

---

## 🚀 Frontend Implementation

### JavaScript State
```javascript
// File sidebar data
let fileTreeData = [];
let currentFileState = {
    path: null,
    status: "pending"
};
let fileStatusUpdateInterval = null;
```

### Core Functions

#### `initFilePanel()`
Initialize file panel on page load
- Calls `loadFileTree()`
- Starts file status polling
- Sets up window resize handler

#### `loadFileTree()`
Fetch file tree from `/api/files` and render
- Handles errors gracefully
- Shows "Loading files..." initially
- Updates `fileTreeData`

#### `renderFileTree()`
Convert file data to HTML tree structure
- Creates `<ul>` for root
- Calls `renderFileItem()` for each file

#### `renderFileItem(item, level)`
Render individual file/directory with:
- File icon based on extension
- Clickable name
- Status indicator
- Toggle functionality for directories
- Nested children

#### `startFileStatusUpdate()`
Begin polling `/api/current-file` every 1 second
- Updates file highlight
- Updates status indicators
- Auto-expands parent directories
- Scrolls to current file

#### `updateFileStatus()`
Fetch current file status and update UI
- Compare with previous state
- Update indicators if changed
- Handle transitions

#### `highlightCurrentFile()`
Visually highlight the current file:
- Add `.current` class
- Expand parent directories
- Scroll into view

#### `updateFileStatusIndicator(filePath, status)`
Update status icon and color for a file:
- Map status to icon
- Apply color class
- Animate if working

### CSS Classes

**Container:**
- `.main-layout` - Flex container for sidebar + content
- `.file-sidebar` - Sidebar container
- `.main-content` - Main content area

**Header:**
- `.sidebar-header` - Header styling
- `.sidebar-toggle` - Close button

**File Tree:**
- `.file-tree` - Root list
- `.file-item` - List item
- `.file-item-content` - Clickable content area
- `.file-item-icon` - Icon styling
- `.file-item-status` - Status indicator

**States:**
- `.current` - Current file highlight
- `.expanded` - Directory expanded
- `.directory` - Directory styling

**Status Colors:**
- `.pending` - Gray (#999)
- `.working` - Orange (#f59e0b) with pulse
- `.done` - Green (#4ade80)
- `.error` - Red (#ef4444)

---

## 🔗 Integration Points

### With Transparency Tracker
When agent processes file, call POST endpoint:

```python
# After/during file processing
response = requests.post("/api/current-file", json={
    "path": "src/file.py",
    "status": "working",
    "message": "Analyzing structure..."
})

# When complete
response = requests.post("/api/current-file", json={
    "path": "src/file.py",
    "status": "done",
    "message": "Modifications complete"
})
```

### With Codex Control Bar
Files panel complements Codex control bar:
- See all files available in project
- Understand what agent is currently working on
- Context for code attachment

### With Agent Execution
File panel updates in real-time:
1. Agent starts → File marked "working"
2. Agent processes actions → Status updates
3. Agent error → File marked "error"
4. Agent completes → File marked "done"

---

## 📱 Responsive Design

### Desktop (800px+)
- Sidebar always visible (220px)
- Full tree structure
- All icons and indicators visible

### Tablet (600-768px)
- Sidebar narrower (180px)
- Smaller font sizes
- Same functionality

### Mobile (<600px)
- Sidebar hidden by default
- Toggle button shows/hides
- Full-width when expanded
- Overlay effect over content

---

## 🎯 Usage Workflow

### As End User
1. Open web UI
2. See file tree in left sidebar
3. Submit task via Codex control
4. Watch file sidebar update:
   - Files change color to orange ⏳ when being worked on
   - Turn green ✔ when done
   - Show red ✕ if error
   - Current file is highlighted

### As Developer (Transparency Integration)
```python
# 1. When starting to process a file
agent.update_current_file("src/api.py", "working")

# 2. During processing
agent.update_current_file("src/api.py", "working", "Building endpoints...")

# 3. When complete
agent.update_current_file("src/api.py", "done", "5 endpoints created")

# 4. On error
agent.update_current_file("src/api.py", "error", "Failed to parse imports")
```

---

## 🔧 Customization

### Change Sidebar Width
**CSS:**
```css
.file-sidebar {
    width: 250px;  /* Change from 220px */
}
```

### Add More File Icons
**JavaScript:**
```javascript
function getFileIcon(filename) {
    const icons = {
        'rs': '🦀',      // Rust
        'go': '🐹',      // Go
        'java': '☕',    // Java
        'cpp': '⚙️',     // C++
    };
    // ... existing code
}
```

### Change Update Interval
**JavaScript:**
```javascript
// Currently 1000ms (1 second)
fileStatusUpdateInterval = setInterval(updateFileStatus, 5000);  // 5 seconds
```

### Customize Status Icons
**JavaScript:**
```javascript
const icons = {
    "pending": "⌛",    // Different icon
    "working": "▶",
    "done": "✓",
    "error": "⚠"
};
```

---

## 📊 Performance

- **File Tree Loading:** Recursive scan, typically <500ms
- **Status Polling:** 1 request per second (minimal overhead)
- **Rendering:** Lazy loaded directories (only visible ones)
- **Memory:** ~10-50KB for tree data

---

## 🐛 Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| Files not showing | `/api/files` endpoint not implemented | Verify endpoint returns correct format |
| Status not updating | Polling not started | Check console for init errors |
| Status stuck on ⏳ | Never marked as done | POST to update status when complete |
| Sidebar doesn't toggle | Element selectors mismatch | Verify HTML IDs match JS |
| Icons not showing | Font support issue | Use proper emoji characters |
| Tree not expanding | Event handler failing | Check browser console for errors |

---

## ✨ Future Enhancements

1. **File Search**
   - Quick file finder
   - Fuzzy matching
   - Keyboard shortcuts

2. **File Preview**
   - Show file content on hover
   - Syntax highlighting
   - Line numbers

3. **File Editing**
   - Direct edit support
   - In-UI code editor
   - Diff view

4. **File Operations**
   - Create/delete files
   - Rename functionality
   - Move between directories

5. **Extended Indicators**
   - File size display
   - Last modified date
   - Modification count
   - Dependencies

6. **Context Menu**
   - Right-click operations
   - File-specific actions
   - Copy path to clipboard

---

## 📝 Files Modified

### Backend
- `web_app.py` - Added `current_file_state` variable and two endpoints

### Frontend
- `static/index.html` - Added sidebar HTML structure
- `static/style.css` - Added ~250 lines for sidebar styling
- `static/script.js` - Added ~400 lines for file panel functionality

---

## 🔍 API Testing

### Test `/api/files`
```bash
curl http://localhost:5000/api/files | jq
```

### Test `/api/current-file` (GET)
```bash
curl http://localhost:5000/api/current-file | jq
```

### Test `/api/current-file` (POST)
```bash
curl -X POST http://localhost:5000/api/current-file \
  -H "Content-Type: application/json" \
  -d '{"path":"src/main.py","status":"working","message":"Processing..."}'
```

---

## 📞 Support

For issues or questions:
1. Check endpoint responses with API testing
2. Verify HTML element IDs match JavaScript
3. Check browser console for errors
4. Check server logs for backend issues
