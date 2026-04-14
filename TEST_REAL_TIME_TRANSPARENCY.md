# Testing Real-Time Transparency Integration

**Goal**: Verify that the autonomous agent loop updates VS Code Transparency UI in real-time

---

## Prerequisites

- ✅ autonomous_agent.py with transparency integration
- ✅ transparency.py module (250 lines)
- ✅ Flask backend (web_app.py with 12 transparency endpoints)
- ✅ VS Code Extension with Transparency tab
- ✅ Virtual environment activated

---

## Test Procedure

### Step 1: Start the Backend

```bash
# Terminal 1
cd c:\Users\disha\Documents\CODES\001\agent

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Start Flask server
python web_app.py
```

**Expected Output:**
```
 * Serving Flask app...
 * Running on http://127.0.0.1:5000
 * Press CTRL+C to quit
```

---

### Step 2: Open VS Code Transparency Tab

1. Open VS Code
2. Go to Extensions → DCODE AI (or search for "dcode")
3. Click on the **Transparency** tab (should be empty initially)
4. Keep this tab visible

**Expected**: Empty dashboard ready to receive data

---

### Step 3: Run the Agent

```bash
# Terminal 2 (keep Terminal 1 running!)
cd c:\Users\disha\Documents\CODES\001\agent

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Run agent with a simple task
python -c "
from autonomous_agent import AutonomousAgent
agent = AutonomousAgent(max_iterations=3)
result = agent.run('Create a simple Python calculator with add and multiply functions')
print(f'\n✅ RESULT: {result}')
"
```

---

### Step 4: Monitor the UI

As the agent runs, watch the VS Code Transparency panel for updates:

#### What You Should See

**T+0s - Initialization:**
- Status: "⬤ Initializing..."
- Progress: 0%
- All panels empty but ready

**T+2s - Planning Start:**
- Step indicator: "Plan - Iteration 1"
- Status: "🔄 Planning..."
- Progress: ~15%

**T+4s - Plan Complete:**
- Thinking panel: Shows plan steps
- Status: "✓ Plan complete"
- Progress: ~20%

**T+6s - Action Generation:**
- Step indicator: "Generate Actions - Iteration 1"
- Status: "⟳ Generating..."
- Progress: ~25%

**T+8s - Execution Start:**
- Actions panel: Shows ◯ for each action
- Step indicator: "Execute Actions - Iteration 1"
- Status: "⟳ Executing..."
- Progress: ~30%

**T+10-15s - Execution:**
- Actions: Icons change from ◯ to ⟳ to ✓
- Output snippets visible
- Status bar advancing

**T+16s - Verification:**
- Step indicator: "Verify - Iteration 1"
- Status: "🔍 Verifying..."
- Progress: ~40%

**T+20s - Complete (if successful):**
- Status: "✅ Complete!"
- Progress: 100%
- All panels show final state

---

## Success Indicators

### Visual Checklist

- [ ] Status bar progresses from 0% to 100%
- [ ] Step indicator updates through all 4 steps
- [ ] Thinking panel shows plan steps
- [ ] Actions panel shows action list with status icons
- [ ] Icons animate (◯ → ⟳ → ✓)
- [ ] Progress updates every iteration
- [ ] No errors in browser console

### Console Output (Terminal 2)

Expected to see:
```
🔄 [Iteration 1/3]
📋 Plan: X steps
⚙️  Actions: Y to execute
✅ Goal completed at iteration Z
```

### Backend Output (Terminal 1)

Expected to see Flask requests:
```
GET /api/transparency/state - 200
GET /api/transparency/actions - 200
POST /api/transparency/error - 200
```

---

## What Each Component Shows

### Thinking Panel 🧠
- **Shows**: Plan steps from iteration
- **Updates**: After planning step completes
- **Example**:
  - ✓ Analyze requirements
  - ✓ Design functions
  - ⟳ Generate code
  - ○ Test code

### Actions Panel ▶️
- **Shows**: Each action with status
- **Updates**: As each action executes
- **Status Icons**:
  - ◯ = Waiting
  - ⟳ = Running
  - ✓ = Complete
  - ✕ = Failed
- **Example**:
  ```
  ✓ Create add function (output: def add(a, b)...)
  ✓ Create multiply function (output: def mul(a, b)...)
  ⟳ Test functions
  ```

### Status Panel ●
- **Shows**: Current step and progress
- **Updates**: Every iteration
- **Example**:
  ```
  Status: ⟳ Executing...
  Step: Execute Actions - Iteration 1
  Progress: ████░░░░░░ 40%
  Time: 1m 23s
  ```

### Errors Panel ⚠️
- **Shows**: Any errors that occur
- **Updates**: Immediately on error
- **Visible**: Error message + context + timestamp
- **Example**:
  ```
  ⚠️ ModuleNotFoundError
  Context: During import in generated code
  Time: 14:32:16
  ```

---

## Test Scenarios

### Scenario 1: Simple Success (Easiest)

```python
# Terminal 2
from autonomous_agent import AutonomousAgent
agent = AutonomousAgent(max_iterations=2)
result = agent.run("Create a simple greeting function")
```

**Expected**: 
- Completes in 1-2 iterations
- No errors
- All panels populate
- Status → ✅ Complete

**Watch for**:
- Smooth progress bar
- Clear plan steps
- Action execution
- Final success message

---

### Scenario 2: Multi-Iteration (Medium)

```python
# Terminal 2
from autonomous_agent import AutonomousAgent
agent = AutonomousAgent(max_iterations=5)
result = agent.run("Build a to-do list application with add, remove, and list functions")
```

**Expected**:
- Takes 2-4 iterations to complete
- UI updates each iteration
- May see some errors then recovery
- Final success

**Watch for**:
- Progress bar loops (iteration 1 → 2 → 3 → ...)
- Error appearance and recovery
- Actions changing between iterations
- Plan refinement each iteration

---

### Scenario 3: Error Handling (Advanced)

```python
# Terminal 2
from autonomous_agent import AutonomousAgent
agent = AutonomousAgent(max_iterations=3)
result = agent.run("Use a non-existent library called 'impossible_lib' to do X")
```

**Expected**:
- First iteration fails with error
- UI shows error in Errors panel
- Loop continues trying to fix
- May eventually timeout after max iterations
- Final status shows failure

**Watch for**:
- Error instantly appears in Errors panel
- Loop continues despite error
- Subsequent iterations try to fix
- Final status reflects failure

---

## Troubleshooting

### Issue: Transparency panel shows nothing

**Check**:
1. Backend running? `python web_app.py` in Terminal 1
   - Should see "Running on http://127.0.0.1:5000"

2. Frontend endpoint accessible?
   ```bash
   curl http://localhost:5000/api/transparency/state
   ```
   - Should return JSON with execution status

3. Agent running? Check Terminal 2 output
   - Should see "🔄 [Iteration 1/X]"

4. Browser console errors? Open DevTools (F12)
   - Check for network errors or JS errors

---

### Issue: Panel shows but doesn't update

**Check**:
1. Polling working? Watch Network tab (F12)
   - Should see repeated GET requests to `/api/transparency/state`
   - Every 500ms

2. Agent stuck? Check Terminal 2
   - Should see progress messages
   - If frozen, agent code might have blocking call

3. Tracker calls happening? Check Terminal 1
   - Should see POST requests: `/api/transparency/actions`
   - Should see POST requests: `/api/transparency/errors`

---

### Issue: Errors show in console but not panel

**Check**:
1. Agent traceback vs. deliberate error?
   - Use Scenario 3 to test deliberate error handling

2. Agent calling `tracker.add_error()`?
   - Check Terminal 1 for POST to `/api/transparency/error`

3. Panel subscribed to errors endpoint?
   - Check browser Network tab for polling errors endpoint

---

## Performance Validation

While running tests, monitor:

### Terminal 1 (Backend)
Count requests per second during execution:
```
GET /api/transparency/state - 200  # ~2 per second (polling)
POST /api/transparency/action - 201  # During execution
POST /api/transparency/error - 201  # On errors
```

Expected: 2 requests/sec = normal (500ms polling interval)

### Terminal 2 (Agent)
Should see progression every 5-20 seconds:
```
🔄 [Iteration 1/3]
...
🔄 [Iteration 2/3]
...
✅ Goal completed at iteration 2
```

Should NOT see:
- Excessive delays (>30s between iterations)
- Freeze/hang (no output for >1 minute)
- Tracker errors in output

### VS Code Panel
Should see smooth updates:
- Progress bar moving every 1-2 seconds
- No freezing or stalling
- Icons animating smoothly

If any stalls > 5 seconds, check Terminal 2 for blocking code.

---

## Validation Checklist

After running tests, verify:

- [ ] Backend started successfully
- [ ] Transparency tab opens without errors
- [ ] Agent runs from Python terminal
- [ ] Status shows "⬜ Initializing..."
- [ ] Status progresses to "🔄 Executing..."
- [ ] Progress bar advances from 0-100%
- [ ] Thinking panel shows plan steps
- [ ] Actions panel shows action list
- [ ] Icons animate (◯ → ⟳ → ✓)
- [ ] Final status shows ✅ or error
- [ ] No errors in browser console
- [ ] No errors in Terminal 1
- [ ] Agent completes and shows result

---

## Next Steps After Testing

If all checks pass:

1. ✅ Integration is working correctly
2. ✅ UI updates in real-time
3. ✅ No performance issues
4. ✅ Ready for production use

Then you can:
- Add more complex tasks
- Monitor multiple agent runs
- Extend tracking with custom metrics
- Export execution logs

---

## Quick Commands Reference

```bash
# Start backend
python web_app.py

# Test backend endpoint
curl http://localhost:5000/api/transparency/state

# Run simple agent test
python -c "from autonomous_agent import AutonomousAgent; agent = AutonomousAgent(max_iterations=2); result = agent.run('Create a greeting function')"

# Run multi-iteration test
python -c "from autonomous_agent import AutonomousAgent; agent = AutonomousAgent(max_iterations=5); result = agent.run('Build a todo app')"

# Check integration
python -c "import autonomous_agent; from transparency import create_new_session; print('✅ Integration verified')"
```

---

**Ready to test? Start with Step 1! 🚀**
