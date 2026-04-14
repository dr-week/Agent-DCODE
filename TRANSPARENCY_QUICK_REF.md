# Agent Transparency - Quick Reference

## UI Layout

```
╔════════════════════════════════════════════════════════════════╗
║  ⬤ Agent Transparency          Progress: 45%    Time: 2m 15s  ║
╠═══════════════════════════════╦════════════════════════════════╣
║                               ║                                ║
║  □ THINKING                   ║  ▶ ACTIONS                   ║
║  ─────────────────────────────║  ─────────────────────────────║
║  1. Analyze request           ║  ✓ Parse code                ║
║  2. Design solution  (NOW)    ║  ⟳ Analyze patterns          ║
║  3. Generate code             ║  ✓ Generate solution         ║
║  4. Run tests                 ║  ○ Run tests                 ║
║                               ║                                ║
╠═══════════════════════════════╬════════════════════════════════╣
║                               ║                                ║
║  ● STATUS                     ║  ⚠ ERRORS                    ║
║  ─────────────────────────────║  ─────────────────────────────║
║  State:     Executing...      ║  (No errors detected)         ║
║  Step:      Design solution   ║                                ║
║  Progress:  45% ████░░░░░░░░  ║                                ║
║  Elapsed:   2m 15s            ║                                ║
║  Est Total: 5m 00s            ║                                ║
║                               ║                                ║
╚═══════════════════════════════╩════════════════════════════════╝
```

## Status Indicators

| Indicator | Meaning | Color |
|-----------|---------|-------|
| ◯ | Pending | Gray |
| ⟳ | Running (animated) | Yellow |
| ✓ | Completed | Green |
| ✕ | Error | Red |
| ⬤ | Running | Green (pulsing) |

## API Endpoints (Quick)

```bash
# Start session
curl -X POST http://localhost:5000/api/transparency/session \
  -H "Content-Type: application/json" \
  -d '{"task": "Build login", "plan_steps": ["Design", "Code"]}'

# Get state
curl http://localhost:5000/api/transparency/state

# Start step
curl -X POST http://localhost:5000/api/transparency/step/start \
  -H "Content-Type: application/json" \
  -d '{"step_index": 0, "step_name": "Design"}'

# Add action
curl -X POST http://localhost:5000/api/transparency/action \
  -H "Content-Type: application/json" \
  -d '{"action": {"type": "code_gen", "description": "Auth module"}}'

# Complete action (action_index=0)
curl -X POST http://localhost:5000/api/transparency/action/0/complete \
  -H "Content-Type: application/json" \
  -d '{"output": "Generated 250 LOC", "success": true}'

# Report error
curl -X POST http://localhost:5000/api/transparency/error \
  -H "Content-Type: application/json" \
  -d '{"error": "Module not found", "context": "During import"}'

# Complete execution
curl -X POST http://localhost:5000/api/transparency/complete \
  -H "Content-Type: application/json" \
  -d '{"success": true}'
```

## Python API (Quick)

```python
from transparency import get_tracker, create_new_session

# Create session
tracker = create_new_session()

# Start tracking
tracker.start_execution("Build feature", ["Design", "Code", "Test"])
tracker.add_plan(["Design", "Code", "Test"], estimated_time=300)

# Track step
tracker.start_step(0, "Design database schema")
tracker.complete_step("Schema designed", success=True)

# Track actions
tracker.add_action({"type": "db_design", "description": "Create schema"})
tracker.complete_action(0, "Schema created", success=True)

# Handle errors
tracker.add_error("Connection timeout", "During DB migration")

# Mark complete
tracker.complete_execution(success=True)

# Get state
state = tracker.get_state()
print(state["progress"])  # 100
print(state["status"])    # "completed"
```

## Common Status Values

```
"idle"                  # Not running
"planning"              # Generating plan
"planned"               # Plan ready
"executing_step_0"      # Executing step 0
"executing_step_1"      # Executing step 1
"error"                 # Error occurred
"completed"             # All done
"failed"                # Failed execution
```

## Colors (VS Code Theme)

```
Cyan:   Planning, step numbers
Yellow: Running, active actions
Green:  Completed, success
Red:    Errors, failures
Gray:   Pending, idle
White:  Neutral text
```

## Polling Behavior

```
Request:  GET /api/transparency/state
Interval: 500ms (configurable)
Timeout:  5000ms per request
Retries:  None (silently continues)
```

## File Locations

```
Backend:     transparency.py
Frontend:    vsc-agent/dcode/src/webview/transparency.ts
Extension:   vsc-agent/dcode/src/extension.ts
Config:      vsc-agent/dcode/package.json
API Routes:  web_app.py
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| No UI | Start backend: `python web_app.py` |
| Stuck at Idle | Did you call `create_new_session()`? |
| Data not updating | Check `/api/transparency/state` manually |
| Console errors | Check browser F12 dev tools |
| No actions showing | Call `add_action()` then `complete_action()` |
| Progress stuck | Verify `start_step()` and `complete_step()` calls |

## Limits

- **Max actions**: ~50 per session (configurable)
- **Max errors**: ~50 per session (configurable)  
- **Polling interval**: 200ms - 2000ms (recommended)
- **State size**: ~2-5KB per poll
- **Session lifetime**: Until reset or app restart

## Integration Checklist

- [ ] `transparency.py` imported in your agent code
- [ ] Backend routes added to `web_app.py` ✅
- [ ] Extension compiled successfully ✅
- [ ] New "Transparency" tab visible in VS Code
- [ ] Calls to `create_new_session()` in your loop
- [ ] Calls to `tracker.start_execution()` at start
- [ ] Calls to `tracker.start_step()` for each step
- [ ] Calls to `tracker.add_action()` for each action
- [ ] Calls to `tracker.complete_action()` when done
- [ ] Calls to `tracker.complete_execution()` at end
- [ ] Test with simple task first
- [ ] Verify UI updates in real-time

## Example Output

```json
{
  "state": {
    "session_id": "session_1713186755",
    "plan": ["Analyze", "Design", "Code", "Test"],
    "current_step": {
      "index": 2,
      "name": "Code Generation",
      "status": "running",
      "start_time": "2024-04-15T14:32:50.000Z",
      "output": "Generated auth.py..."
    },
    "actions": [
      {
        "timestamp": "2024-04-15T14:32:45.000Z",
        "type": "analysis",
        "description": "Analyze requirements",
        "status": "completed",
        "output": "Found 3 requirements",
        "success": true
      },
      {
        "timestamp": "2024-04-15T14:32:50.000Z",
        "type": "code_gen",
        "description": "Generate auth module",
        "status": "running",
        "output": "",
        "success": null
      }
    ],
    "status": "executing_step_2",
    "progress": 55,
    "estimated_time": 300,
    "elapsed_time": 15,
    "errors": [],
    "start_time": "2024-04-15T14:32:45.000Z",
    "end_time": null
  }
}
```

## Next Steps After Setup

1. Open VS Code with your project
2. Click **DCODE AI** → **Transparency** tab
3. Run your agent task
4. Watch execution unfold in real-time
5. Monitor step progress and errors
6. One-click debugging with transparency view

---

**Created**: 2024-04-15  
**Status**: ✅ Production Ready  
**Performance**: Optimized for sub-second updates
