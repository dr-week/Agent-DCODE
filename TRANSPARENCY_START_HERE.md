# 🚀 Agent Transparency - START HERE

**Welcome!** You now have a real-time agent transparency system. This page gets you started in 5 minutes.

---

## What Is This?

A **live dashboard in VS Code** that shows what your AI agent is doing in real-time:

```
See Agent Thinking    →  See Actions Being Done  →  Track Progress
     (Planning)              (Execution)             (Status/Errors)
```

**No terminals**, **no logs**, **just visual feedback**.

---

## ⚡ 5-Minute Quick Start

### Step 1: Open Your Agent File
Any file where you run your agent (e.g., `agent.py`, `autonomous_agent.py`)

### Step 2: Add 3 Lines at Top
```python
from transparency import create_new_session, get_tracker
```

That's it! No other imports needed.

### Step 3: Wrap Your Execution
```python
# BEFORE your main loop
tracker = create_new_session()
tracker.start_execution("Your Task Name")

# INSIDE your loop (when each step starts)
tracker.start_step(step_id, "Step Name Here")

# INSIDE your loop (when each step ends)
tracker.complete_step("any output")

# AFTER your loop completes
tracker.complete_execution(success=True)
```

### Step 4: Open VS Code Dashboard  
- Click **DCODE AI** in left sidebar
- Click **Transparency** tab
- You'll see 4 empty panels

### Step 5: Run Your Agent
Run your agent as normal — the dashboard will start updating in real-time!

**That's it! You're done.**

---

## 🎨 What You'll See

```
┌────────────── THINKING ────────────┐
│ 1. Parse requirements              │
│ 2. Design solution                 │
│ 3. Generate code                   │
│ 4. Run tests                       │
└────────────────────────────────────┘

┌────────────── ACTIONS ─────────────┐
│ ✓ Parse requirements               │
│ ⟳ Generating code... (spinning)    │
│ ○ Run tests (pending)              │
└────────────────────────────────────┘

┌────────────── STATUS ──────────────┐
│ Progress: 50% ████░░░░░            │
│ Time: 2m 15s elapsed               │
│ Est: 5m total                      │
└────────────────────────────────────┘

┌────────────── ERRORS ──────────────┐
│ (none so far)                      │
└────────────────────────────────────┘
```

---

## 📝 Complete Minimal Example

```python
# my_agent.py

from transparency import create_new_session

def main():
    # Start tracking
    tracker = create_new_session()
    tracker.start_execution("Build Login System")
    
    # Add plan
    tracker.add_plan(
        steps=["Design", "Code", "Test"],
        estimated_time=300
    )
    
    # Step 1: Design
    tracker.start_step(0, "Design Database Schema")
    schema = design_database()
    tracker.complete_step(f"Designed schema: {schema}", success=True)
    
    # Step 2: Code
    tracker.start_step(1, "Generate Code")
    code = generate_code(schema)
    tracker.complete_step(f"Generated {len(code)} lines", success=True)
    
    # Step 3: Test
    tracker.start_step(2, "Run Tests")
    results = run_tests(code)
    tracker.complete_step(f"Tests: {results}", success=True)
    
    # Done
    tracker.complete_execution(success=True)
    print("✅ Complete!")

if __name__ == "__main__":
    main()
```

---

## 🎯 Common Patterns

### Pattern 1: Simple Steps
```python
tracker = create_new_session()
tracker.start_execution("My Task")

for i, step in enumerate(["Step 1", "Step 2", "Step 3"]):
    tracker.start_step(i, step)
    # do work
    tracker.complete_step("done")

tracker.complete_execution(success=True)
```

### Pattern 2: With Actions
```python
tracker.start_step(0, "Generate Code")

tracker.add_action({"type": "gen", "description": "Create auth.py"})
result = generate_auth()
tracker.complete_action(0, result, success=True)

tracker.complete_step("Generated", success=True)
```

### Pattern 3: Error Handling
```python
try:
    tracker.start_step(i, step)
    result = execute(step)
    tracker.complete_step(result, success=True)
except Exception as e:
    tracker.add_error(str(e), f"During {step}")
    tracker.complete_step("", success=False)
```

---

## 🖥️ Using the Dashboard

### Opening
```
1. Click "DCODE AI" in VS Code sidebar
2. Click "Transparency" tab
3. That's it!
```

### Reading
```
TOP-LEFT:    What agent PLANS to do (steps)
TOP-RIGHT:   What agent IS doing (live)
BOTTOM-LEFT: Progress bar and timing
BOTTOM-RIGHT: Any errors
```

### Watching
```
- ✓ Green check: Step completed
- ⟳ Spinning icon: Currently running
- ○ Hollow dot: Waiting/pending
- ✕ Red X: Error occurred
```

---

## 🐛 If It's Not Working

### Dashboard shows nothing?
```
1. Check backend is running:
   $ python web_app.py
   
2. Check you called create_new_session():
   tracker = create_new_session()
   
3. Check you called start_execution():
   tracker.start_execution("Task Name")
```

### Dashboard stuck at "Idle"?
```
Did you add the tracking calls?
- tracker.start_step(i, name)
- tracker.complete_step(output)

If missing, steps won't show.
```

### Actions not showing?
```
Must do both:
1. tracker.add_action({...})
2. tracker.complete_action(index, output)

Only add_action() won't show progress.
```

### Errors not displaying?
```
Make sure to call:
tracker.add_error("Error message", "Context")

Before the complete_step/execution calls.
```

---

## 📚 For More Info

| Want to... | Read |
|-----------|------|
| Quick lookup | TRANSPARENCY_QUICK_REF.md |
| Code examples | TRANSPARENCY_INTEGRATION.md |
| How it works | ARCHITECTURE_TRANSPARENCY.md |
| All details | TRANSPARENCY_UI.md |
| What was built | BUILD_TRANSPARENCY_COMPLETE.md |

---

## API Methods (All You Need)

```python
from transparency import create_new_session, get_tracker

# Session
tracker = create_new_session()          # Start new session
tracker = get_tracker()                 # Get existing session

# Main flow
tracker.start_execution(task, [steps])  # Begin tracking
tracker.add_plan([steps], time=300)     # Set plan
tracker.start_step(0, "Step Name")      # Mark step start
tracker.complete_step("output")         # Mark step end
tracker.complete_execution(True)        # Mark done

# Optional actions
tracker.add_action({"type": "gen", "description": "..."})
tracker.complete_action(0, "output")

# Error handling
tracker.add_error("Error message", "context")
```

That's literally all the methods you need!

---

## 🌟 Pro Tips

### Tip 1: Use Descriptive Names
```python
# Good
tracker.start_step(0, "Connect to Database")

# Bad
tracker.start_step(0, "Step 1")
```

### Tip 2: Give Time Estimates
```python
tracker.add_plan(steps, estimated_time=300)  # minutes
# Shows realistic progress to user
```

### Tip 3: Track Actions Too
```python
tracker.add_action({"type": "file_write", "description": "Save config"})
# Users see what's happening inside steps
```

### Tip 4: Report All Errors
```python
tracker.add_error(str(exception), "During initialization")
# Errors visible in dashboard, not hidden in terminal
```

### Tip 5: Complete Everything
```python
tracker.complete_step(output)          # Always call
tracker.complete_execution(success)    # Always call
# Even if failing - user needs to know
```

---

## 🎯 Example: Before & After

### Before (What You Have)
```python
def my_agent(task):
    print("Starting...")
    
    schema = design()
    print("Designed")
    
    code = generate(schema)
    print("Generated")
    
    test(code)
    print("Done!")
```

### After (With Transparency)
```python
def my_agent(task):
    tracker = create_new_session()
    tracker.start_execution(task)
    
    tracker.start_step(0, "Design")
    schema = design()
    tracker.complete_step("Done")
    
    tracker.start_step(1, "Generate")
    code = generate(schema)
    tracker.complete_step("Done")
    
    tracker.start_step(2, "Test")
    test(code)
    tracker.complete_step("Done")
    
    tracker.complete_execution(success=True)
```

**Difference**: Dashboard automatically shows progress!

---

## ⚙️ Configuration

### Change Update Speed
```python
# In transparency.ts, line 62:
updateInterval = setInterval(..., 300);  # 300ms instead of 500ms
```

### Change Backend URL
```python
# In transparency.ts, line 66:
fetch('http://your-server:8000/api/transparency/state')
```

### Change Colors
(Uses VS Code theme - no changes needed)

---

## 🚀 Next Steps

### Now
- [ ] Read this file ✓ (just did)
- [ ] Add 3 lines to your agent
- [ ] Run and test
- [ ] **Done!** (10 minutes total)

### Optional Later
- [ ] Read TRANSPARENCY_QUICK_REF.md for reference
- [ ] Customize polling speed
- [ ] Add more detailed action tracking
- [ ] Export logs

---

## 🎓 Learning Path

```
1. START HERE (this file)
   ↓
2. TRANSPARENCY_QUICK_REF.md (quick lookup)
   ↓
3. TRANSPARENCY_INTEGRATION.md (examples)
   ↓
4. TRANSPARENCY_UI.md (full details)
```

**Time to proficiency**: ~30 minutes

---

## 📊 What Gets Tracked

```
✅ Your Plan      → Which steps you'll do
✅ Your Actions   → What you're actually doing
✅ Your Progress  → How far along (%)
✅ Your Status    → What state you're in
✅ Your Errors    → What went wrong
✅ Your Timing    → How long it took
```

All visible in one dashboard!

---

## 🎁 What You Get

```
✅ Real-time monitoring (500ms updates)
✅ Visual 4-panel layout
✅ No terminal needed
✅ Live progress tracking
✅ Error alerts
✅ Minimal code changes (3-10 lines)
✅ Production ready
✅ Zero external dependencies
✅ VS Code integrated
✅ Fully documented
```

---

## 🔑 Key Takeways

1. **3-line setup** - Import, create session, start execution
2. **10 methods** - That's all you need
3. **Real-time dashboard** - Automatic updates every 500ms
4. **No terminal**- VS Code sidebar shows everything
5. **Easy to debug** - Errors show immediately

---

## 🎊 You're Ready!

```
1. Add 3 lines to your code
2. Open VS Code Transparency tab
3. Run your agent
4. Watch it execute in real-time!
```

**Questions?** Check TRANSPARENCY_QUICK_REF.md or docs folder.

**Let's go! 🚀**

---

## Quick Reference Card

```
from transparency import create_new_session

tracker = create_new_session()
tracker.start_execution("Task Name")
tracker.add_plan(["s1", "s2", "s3"], estimated_time=300)

for i, step in enumerate(["s1", "s2", "s3"]):
    tracker.start_step(i, step)
    result = do_step(step)
    tracker.complete_step(result)

tracker.complete_execution(success=True)
```

Copy-paste, change step names, done!

---

*Welcome to real-time transparency! Open VS Code and get started. 🎯*
