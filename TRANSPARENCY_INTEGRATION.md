# Agent Transparency - Quick Integration Guide

## 5-Minute Setup

### Step 1: Update Your Agent to Use Transparency

In your agent execution function (e.g., `autonomous_agent.py`):

```python
from transparency import get_tracker, create_new_session

def run_autonomous_agent(goal: str):
    # Create new session
    tracker = create_new_session()
    
    # Start execution with initial plan
    plan_steps = ["Analyze task", "Generate solution", "Test results", "Refine"]
    tracker.start_execution(goal, plan_steps)
    
    # Add refined plan with time estimate
    tracker.add_plan(plan_steps, estimated_time=300)
    
    # Loop through steps
    for i, step_name in enumerate(plan_steps):
        tracker.start_step(i, step_name)
        
        try:
            # Your step logic here
            result = execute_step(step_name)
            tracker.complete_step(result, success=True)
        except Exception as e:
            tracker.add_error(str(e), f"Step: {step_name}")
            tracker.complete_step("", success=False)
    
    # Mark complete
    tracker.complete_execution(success=True)
```

### Step 2: Track Actions Within Steps

```python
def execute_step(step_name):
    tracker = get_tracker()
    
    # Add action
    tracker.add_action({
        "type": "code_generation",
        "description": f"Generating code for {step_name}"
    })
    
    # Execute
    action_index = len(tracker.actions) - 1
    try:
        output = generate_code(step_name)
        tracker.complete_action(action_index, output, success=True)
        return output
    except Exception as e:
        tracker.complete_action(action_index, str(e), success=False)
        raise
```

### Step 3: Open VS Code and Watch

1. Press `Ctrl+Shift+P` → Type "Show Agent Transparency"
2. Or click **Transparency** tab in DCODE sidebar
3. Run your agent and watch in real-time:

```
Thinking ──── Actions ─────
  ✓ Step 1     ⟳ Running Task
  ✓ Step 2     ✓ Completed
  ⟳ Step 3     ☆ Queued

Status ────── Errors
  45% ████     (No errors)
```

## Complete Example

### Full Integration with autonomous_agent.py

```python
from transparency import get_tracker, create_new_session

class AutonomousAgent:
    def run(self, goal: str, initial_context: str = "", success_criteria: Optional[str] = None):
        """Run with transparency tracking"""
        # Create tracking session
        tracker = create_new_session()
        plan_steps = ["Plan", "Code Gen", "Test", "Refine"]
        tracker.start_execution(goal, plan_steps)
        
        result = {
            "goal": goal,
            "success": False,
            "iterations": 0,
            "plan": [],
            "actions_executed": 0,
        }
        
        while self.iteration < self.max_iterations:
            self.iteration += 1
            
            # STEP 1: Planning
            tracker.start_step(0, "Generate Plan")
            plan = self._get_plan(goal, initial_context)
            tracker.complete_step(f"Generated {len(plan['steps'])} steps", success=True)
            result["plan"] = plan.get("steps", [])
            
            # STEP 2: Actions
            tracker.start_step(1, "Generate Actions")
            
            # Track each action separately
            actions = self._get_actions(goal, result["plan"], initial_context)
            for j, action in enumerate(actions.get("actions", [])):
                tracker.add_action({
                    "type": action.get("type"),
                    "description": action.get("description")
                })
                
                # Execute and track result
                try:
                    action_result = execute_action(action)
                    tracker.complete_action(j, action_result["output"], success=True)
                except Exception as e:
                    tracker.add_error(str(e), f"Action: {action['type']}")
                    tracker.complete_action(j, str(e), success=False)
            
            tracker.complete_step("All actions complete", success=True)
            
            # STEP 3: Verification
            tracker.start_step(2, "Verify Results")
            if self._check_success(goal, self.execution_history):
                tracker.complete_step("Success criteria met!", success=True)
                tracker.complete_execution(success=True)
                return {"success": True, "result": "..."}
            
            tracker.complete_step("Continue to next iteration", success=True)
        
        tracker.complete_execution(success=False)
        return {"success": False, "error": "Max iterations reached"}
```

### In web_app.py

```python
from transparency import get_tracker, create_new_session

@app.route("/api/agent/execute", methods=["POST"])
def agent_execute():
    """Agent endpoint with transparency"""
    data = request.json
    task = data.get("task", "")
    
    # Create tracking session
    tracker = create_new_session()
    tracker.start_execution(task)
    
    try:
        # Get plan from agent
        plan = llm_get_plan(task)
        tracker.add_plan(plan["steps"], plan.get("estimated_time", 300))
        
        # Execute plan
        for i, step in enumerate(plan["steps"]):
            tracker.start_step(i, step)
            
            # Execute action
            action = {"type": "execute", "description": step}
            tracker.add_action(action)
            
            result = execute_step(step)
            tracker.complete_action(0, result, success=True)
            tracker.complete_step(result, success=True)
        
        tracker.complete_execution(success=True)
        
        return jsonify({
            "success": True,
            "state": tracker.get_state()
        })
    
    except Exception as e:
        tracker.add_error(str(e), "Execution failed")
        tracker.complete_execution(success=False)
        
        return jsonify({
            "success": False,
            "error": str(e),
            "state": tracker.get_state()
        }), 500
```

## Real-Time Workflow

### Terminal Output (Old Way - Limited Info)

```
🔄 [Iteration 1/10]
📋 Plan: 4 steps
⚙️  Actions: 3 to execute
Executing...
✓ Complete
```

### VS Code Transparency Panel (New Way - Full Transparency)

```
┌──────────────────────┬──────────────────────┐
│     THINKING         │      ACTIONS         │
├──────────────────────┼──────────────────────┤
│ 1. Analyze task      │ ✓ Parse request      │
│ 2. Design solution   │ ⟳ Generate code      │
│ 3. Implement code    │ ○ Run tests          │
│ 4. Run tests         │                      │
├──────────────────────┼──────────────────────┤
│     STATUS (45%)     │     ERRORS           │
├──────────────────────┼──────────────────────┤
│ State: Executing     │ (No errors)          │
│ Step: Design sol...  │                      │
│ Progress: 45% ████░  │                      │
│ Time: 1m 23s         │                      │
└──────────────────────┴──────────────────────┘
```

## Data Flow

### How Data Gets to Panel

```
Your Agent
    ↓ (calls tracker.add_action, etc.)
TransparencyTracker (in-memory state)
    ↓ (HTTP request)
        Flask Backend
    ↓ (/api/transparency/state)
    VS Code Webview
    ↓ (JavaScript rendering)
    User sees live updates
```

### Polling Loop (500ms intervals)

```
Time 0s:    Panel opens → start polling
Time 0.5s:  GET /api/transparency/state → {"progress": 0, ...}
Time 1.0s:  GET /api/transparency/state → {"progress": 15, ...}
Time 1.5s:  GET /api/transparency/state → {"progress": 30, ...}
Time 2.0s:  GET /api/transparency/state → {"progress": 50, ...}
            (UI updates smoothly with progress bar)
```

## Common Patterns

### Pattern 1: Simple Execution

```python
tracker = create_new_session()
tracker.start_execution(task)
tracker.add_plan(["Step 1", "Step 2"], estimated_time=60)

for i, step in enumerate(steps):
    tracker.start_step(i, step)
    result = do_step(step)
    tracker.complete_step(result)

tracker.complete_execution(success=True)
```

### Pattern 2: With Actions

```python
tracker.start_step(0, "Code Generation")

tracker.add_action({"type": "gen", "description": "Generate auth"})
result = generate_auth()
tracker.complete_action(0, result)

tracker.add_action({"type": "gen", "description": "Generate routes"})
result = generate_routes()
tracker.complete_action(1, result)

tracker.complete_step("All code generated")
```

### Pattern 3: Error Handling

```python
try:
    result = risky_operation()
    tracker.complete_action(idx, result, success=True)
except Exception as e:
    tracker.add_error(str(e), "During risky operation")
    tracker.complete_action(idx, str(e), success=False)
```

### Pattern 4: Multi-Step Tracking

```python
tracker.start_execution("Build API")
tracker.add_plan(["Design", "Implement", "Test"])

for step_idx, step_name in enumerate(plan):
    tracker.start_step(step_idx, step_name)
    
    for action_idx, action in enumerate(get_actions(step_name)):
        tracker.add_action(action)
        result = execute(action)
        tracker.complete_action(action_idx, result)
    
    tracker.complete_step("Done")

tracker.complete_execution(True)
```

## Debugging Tips

### No Data Showing?

1. Check backend is running: `python web_app.py`
2. Backend must be at `http://localhost:5000`
3. Check browser console for errors (F12 in VS Code)

### Stuck at "Idle"?

1. Did you call `create_new_session()`?
2. Did you call `start_execution()`?
3. Check for exceptions in your code

### Progress Not Moving?

1. Make sure you're calling `start_step()` before ending
2. Verify `complete_step()` is called
3. Check `estimated_time` is reasonable

### Actions Not Showing?

1. Call `tracker.add_action(action_dict)` before execution
2. Call `tracker.complete_action(index, output, success)` after
3. Verify action has `type` and `description` fields

## Best Practices

1. **Always add plan first** - Gives users context
2. **Use estimated_time** - Shows realistic progress
3. **Complete each action** - Even if it fails
4. **Report all errors** - Important for debugging  
5. **Keep descriptions short** - UI has limited space (60px)
6. **Use consistent action types** - Makes UI easier to scan
7. **Close sessions** - Call `reset_tracker()` when done (optional)

## Performance Notes

- **500ms polling** is usually perfect for ~2-5 min operations
- **Reduce to 200ms** for fast operations (<1 min)
- **Increase to 1000ms** for very slow operations (>10 min)
- **Max 50 actions** in memory (configurable in transparency.py)

## What's Next?

1. ✅ Transparency tracking system built
2. ✅ VS Code panel integrated
3. ⏭️ **TODO**: Integrate with autonomous_agent.py
4. ⏭️ **TODO**: Stream actions from your specific agent
5. ⏭️ **TODO**: Customize colors/layout to your taste

**Start** with the simple pattern above and expand as needed!
