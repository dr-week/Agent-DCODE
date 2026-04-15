# File Panel - Quick Reference

## 🎯 What Was Added

### Backend (web_app.py)
```python
# New global variable
current_file_state = {
    "path": None,
    "status": "pending",
    "message": ""
}

# New endpoints
GET  /api/files           # Get project file tree
GET  /api/current-file    # Get current file status
POST /api/current-file    # Update current file status
```

### Frontend (HTML + CSS + JS)

**HTML Structure:**
- Sidebar panel with file tree
- Dynamic file list with status indicators
- Directory expansion/collapse

**CSS Styling:**
- Sidebar layout (220px width)
- File tree styling
- Status indicators (○ ⏳ ✔ ✕)
- Responsive design (hidden on mobile)
- Current file highlight
- Smooth animations

**JavaScript Functionality:**
- Load file tree on init
- Poll current file status every 1s
- Update file indicators
- Handle directory toggling
- Auto-scroll to current file
- Responsive sidebar toggle

---

## 📊 How It Works

### On Page Load
```
1. initFilePanel() called
   ↓
2. loadFileTree()
   - Fetches /api/files
   - Gets recursive file tree
   - Renders HTML
   ↓
3. startFileStatusUpdate()
   - Starts 1s polling interval
   - Fetches /api/current-file regularly
   - Updates UI
```

### When Agent Works on File
```
Backend:
POST /api/current-file with path="src/file.py", status="working"

Frontend:
1. Polls and receives update
2. Finds file element
3. Changes icon: ○ → ⏳
4. Changes color: gray → orange
5. Adds pulsing animation
6. Highlights row with blue background
7. Scrolls into view

When Done:
POST /api/current-file with status="done"

Frontend:
1. Changes icon: ⏳ → ✔
2. Changes color: orange → green
3. Remove pulse animation
```

---

## 🔌 Integration with Your Agent

### Option 1: Simple (No Transparency)
```python
# In your agent code, after processing a file
import requests

requests.post("http://localhost:5000/api/current-file", json={
    "path": "src/myfile.py",
    "status": "working"
})

# ... do processing ...

requests.post("http://localhost:5000/api/current-file", json={
    "path": "src/myfile.py",
    "status": "done"
})
```

### Option 2: With Existing Transparency Tracker
```python
# In transparency.py, add file tracking
tracker.update_file("src/file.py", "working")

# In web_app.py transparency endpoints
@app.route("/api/transparency/file", methods=["POST"])
def transparency_update_file():
    data = request.json
    global current_file_state
    current_file_state = {
        "path": data.get("path"),
        "status": data.get("status", "pending"),
        "message": data.get("message", "")
    }
    return jsonify({"success": True})
```

---

## 📱 UI Features

### Desktop View
```
┌─ 📁 Files ─────────────┐  Full sidebar visible
│ ▶ src/                 │  All items visible
│   ⏳ agent.py         │  Full names displayed
│   ✔ utils.py          │  Status icons clear
│   ▶ tests/            │
│     ○ test_a.py       │
│     ○ test_b.py       │
│ ▶ static/             │
│ ▶ .logs/              │
└────────────────────────┘
```

### Mobile View (Collapsed)
```
┌─ ✕ ─┐  Sidebar hidden by default
│     │  Click ✕ to expand
│     │  Overlay on content
└─────┘
```

---

## 🎯 Status Indicators

| Status | Icon | Color | Animation |
|--------|------|-------|-----------|
| pending | ○ | Gray | None |
| working | ⏳ | Orange | Pulse |
| done | ✔ | Green | None |
| error | ✕ | Red | None |

---

## ⚙️ Configuration Examples

### Disable Auto-Polling
```javascript
// In script.js
// Comment out or modify
// fileStatusUpdateInterval = setInterval(updateFileStatus, 1000);
```

### Change Polling Interval
```javascript
// More frequent (500ms)
fileStatusUpdateInterval = setInterval(updateFileStatus, 500);

// Less frequent (5s)
fileStatusUpdateInterval = setInterval(updateFileStatus, 5000);
```

### Always Expand Directories
```javascript
// In renderFileTree() after rendering
document.querySelectorAll(".file-item.directory").forEach(dir => {
    dir.classList.add("expanded");
});
```

---

## 🔍 Testing Checklist

- [ ] `/api/files` returns valid JSON
- [ ] `/api/current-file` GET returns initial state
- [ ] File tree renders on page load
- [ ] Directories can be expanded/collapsed
- [ ] File type icons display correctly
- [ ] POST to `/api/current-file` updates state
- [ ] Status indicators update (⏳ → ✔)
- [ ] Current file highlights
- [ ] Auto-scroll works
- [ ] Sidebar toggles on mobile
- [ ] Polling continues during task execution

---

## 📊 Response Formats

### GET /api/files
```json
{
    "success": true,
    "files": [
        {"name": "file.py", "path": "file.py", "type": "file", "size": 1234},
        {
            "name": "src", "path": "src", "type": "directory",
            "children": [...]
        }
    ],
    "root": "."
}
```

### GET /api/current-file
```json
{
    "path": "src/file.py",
    "status": "working",
    "message": "Processing..."
}
```

### POST /api/current-file
```json
{
    "success": true,
    "state": {
        "path": "src/file.py",
        "status": "working",
        "message": "Processing..."
    }
}
```

---

## 🚀 Files Modified

| File | Changes |
|------|---------|
| `web_app.py` | Added state variable + 2 endpoints |
| `static/index.html` | Added sidebar HTML (~40 lines) |
| `static/style.css` | Added sidebar styles (~250 lines) |
| `static/script.js` | Added file panel JS (~400 lines) |

---

## 💡 Tips

✅ **Do:**
- Keep update interval reasonably frequent (1-5s)
- Always update status when processing starts/ends
- Use meaningful status messages
- Test endpoints with curl first
- Check browser console for errors

❌ **Don't:**
- Update status too frequently (<100ms)
- Forget to POST status updates
- Leave status as "working" after completion
- Use incorrect file paths
- Mix relative/absolute paths

---

## 🔗 Connected Features

Works with:
- ✅ Codex Control Bar (shows files available)
- ✅ Transparency Tracker (update file status during execution)
- ✅ Agent Execution (real-time file activity)
- ✅ Responsive Design (adapts to screen size)

---

## 📞 Quick Troubleshoot

**File tree not loading?**
- Check if `/api/files` endpoint exists
- Verify endpoint returns valid JSON
- Check browser console for fetch errors

**Status not updating?**
- Verify `/api/current-file` POST is being called
- Check if polling interval is running
- Inspect Network tab for requests

**Sidebar not visible?**
- Check if HTML elements exist
- Verify CSS classes are correct
- Check z-index on mobile

**Icons not showing?**
- Verify emoji support in browser
- Check if getFileIcon() includes extensions
- Try different emoji characters

---

## 📚 Full Documentation
See [FILE_PANEL_GUIDE.md](FILE_PANEL_GUIDE.md) for complete reference
