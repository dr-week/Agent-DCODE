# Quick Start: Testing New Web UI Features

This guide walks you through setting up and testing the enhanced web UI with rich action output formatting.

## Prerequisites

- Python 3.10+
- Ollama running locally (`ollama serve`)
- Dependencies installed (`pip install -r requirements.txt`)

## Setup (3 Steps)

### 1. Start Ollama Server
```bash
ollama serve
# Ollama will listen on http://localhost:11434
```

### 2. Start Flask Web App
```bash
cd /path/to/agent
.venv/Scripts/python web_app.py   # Windows
# or
.venv/bin/python web_app.py       # Linux/Mac
```

Server will start on **http://localhost:5000**

### 3. Open in Browser
```
http://localhost:5000
```

## Testing Scenarios

### Test 1: File Operations (2 min)
```
Prompt: "Create a file called test.py that prints hello world"

Expected Output:
- Chat message from AI
- System action showing "[CREATED] /..../projects/test.py"
- Blue-bordered box with action details
```

### Test 2: Directory Listing (2 min)
```
Prompt: "Show me the structure of the projects folder"

Expected Output:
- File tree displayed in monospace font
- Proper indentation with ├── and └── characters
- All subdirectories and files listed
```

### Test 3: Python Execution (2 min)
```
Prompt: "Write and run Python code that calculates 2^10"

Expected Output:
- Code is executed
- Result displayed in code block with dark background
- Shows: 1024
```

### Test 4: Process Monitoring (2 min)
```
Prompt: "Show me the top 5 processes using the most memory"

Expected Output:
- Results displayed as HTML table
- Columns: PID, Name, CPU%, MEM%
- Top memory consumers listed
- Alternating row colors
```

### Test 5: Bash Commands (2 min)
```
Prompt: "Run the pwd command and show the result"

Expected Output:
- Command shown in box with green border
- Output displayed below
- Clear [OUT] section formatting
```

## Visual Elements to Check

### ✅ Action Output Container
- [ ] Each action has colored left border (4px)
- [ ] Header shows emoji icon + ACTION TYPE in uppercase
- [ ] Content area has proper padding (12px)
- [ ] Background is light gray (#f5f5f5)

### ✅ File Tree Display
- [ ] Tree characters (├──, └──, │) render correctly
- [ ] Indentation is consistent
- [ ] Monospace font is applied
- [ ] No weird line breaks

### ✅ Code Blocks
- [ ] Dark background (#2d2d2d) for code
- [ ] Light text (#f8f8f2) for readability
- [ ] Scrollbar appears for long content
- [ ] Text wraps at container edge

### ✅ Process Table
- [ ] Blue header with white text
- [ ] Columns properly aligned (PID, Name, CPU%, MEM%)
- [ ] Alternating row colors (fafafa/white)
- [ ] Hover effect on rows (light gray)
- [ ] Data is readable and not cut off

### ✅ Progress Bars
- [ ] Filled blocks (█) and empty blocks (░)
- [ ] Percentage shown at end
- [ ] Colors are distinct from other elements
- [ ] Animation/progression is smooth

## Common Issues & Fixes

### Issue: "Cannot connect to Ollama"
**Fix:** Make sure `ollama serve` is running in a separate terminal
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags
```

### Issue: Web UI loads but chat doesn't work
**Fix:** Check browser console for errors (F12)
```bash
# Also check server logs in terminal running web_app.py
```

### Issue: Actions execute but no output appears
**Fix:** Action output formatting might have a JS error. Check:
1. Browser console for JavaScript errors
2. Server logs for Python errors
3. Verify renderActionOutput() function in script.js

### Issue: Text bleed-through in dark code blocks
**Fix:** CSS might not be loading. Hard refresh browser:
```
Windows: Ctrl+Shift+Delete
Mac: Command+Shift+Delete
```

## Rollback (Old Behavior)

To revert to simple action list display without rich formatting:

```bash
git diff HEAD~1 static/script.js
git checkout HEAD~1 -- static/script.js
# Refresh browser
```

## Performance Notes

- Large file trees (500+ files) may take 1-2 seconds to render
- Process table updates are fast (<500ms)
- Python/JS code execution timeout: 30 seconds
- Progress bars are simulated (no real background tasks yet)

## Next Steps

1. **Test all scenarios** above with different inputs
2. **Try complex prompts** like: "Create a project structure with tests"
3. **Monitor performance** in DevTools Network tab
4. **Provide feedback** on UI/UX improvements

## Feature Checklist

- [x] Executor returns output instead of just printing
- [x] Web app passes action output to frontend
- [x] JavaScript has renderActionOutput() function
- [x] CSS has styling for all action types
- [x] File tree rendering works
- [x] Code block syntax highlighting ready
- [x] Process table HTML generation works
- [x] Progress bar display works
- [x] Documentation created (USAGE_EXAMPLES.md)
- [x] Git commit saved

## Support

For issues or questions:
1. Check [USAGE_EXAMPLES.md](USAGE_EXAMPLES.md) for prompt examples
2. Review [ADVANCED_FEATURES.md](ADVANCED_FEATURES.md) for feature details
3. Check server logs: `tail -f web_app.py` output
4. Check browser console: F12 → Console tab

---

**Ready to test?** Start services and open http://localhost:5000 🚀
