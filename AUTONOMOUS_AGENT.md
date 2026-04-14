# Autonomous Agent Loop

Continuous planning, execution, and error recovery system.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  Autonomous Loop                        │
└─────────────────────────────────────────────────────────┘
                          ↓
            ┌─────────────────────────────┐
            │  1. Generate Plan           │
            │  (LLM: What to do?)         │
            └─────────────┬───────────────┘
                          ↓
            ┌─────────────────────────────┐
            │  2. Generate Actions        │
            │  (LLM: How to do it?)       │
            └─────────────┬───────────────┘
                          ↓
            ┌─────────────────────────────┐
            │  3. Execute Actions         │
            │  (Run code, write files)    │
            └─────────────┬───────────────┘
                          ↓
            ┌─────────────────────────────┐
            │  4. Check Results           │
            │  (Did it work?)             │
            └─────────────┬───────────────┘
                   YES ↓  ↓ NO
          ✅ SUCCESS   CONTINUE LOOP
                       (iterate context)
```

## Key Features

### 1. Continuous Planning
- Takes high-level goal and current context
- Generates 3-5 step plan
- Refines plan based on execution errors

### 2. Intelligent Execution
- Converts plan to concrete actions
- Supports: write_file, read_file, run_python, run_bash, etc.
- Limits actions to projects/ directory (safety)

### 3. Error Detection & Recovery
- Detects failures in execution output
- Adds error context to next iteration
- Retries with improved understanding

### 4. Iteration Limits
- Max iteration setting prevents infinite loops
- Defaults to 10 iterations (configurable)
- Each iteration adds to execution history

### 5. State Tracking
- Logs to .logs/{project_name}/ 
- Tracks completion percentage over iterations
- Enables resumption from checkpoints

## Usage

### Basic

```python
from autonomous_agent import run_autonomous_agent

result = run_autonomous_agent(
    goal="Create a Python script that calculates fibonacci",
    project_name="fib_task",
    max_iterations=5
)

print(f"Success: {result['success']}")
print(f"Iterations: {result['iterations']}")
```

### Advanced

```python
from autonomous_agent import AutonomousAgent

agent = AutonomousAgent(
    project_name="complex_project",
    max_iterations=10
)

result = agent.run(
    goal="Build a REST API with database",
    initial_context="Use Flask framework, SQLite database in projects/",
    success_criteria="API starts without errors on port 5000"
)

# Access history
for i, execution in enumerate(agent.execution_history):
    print(f"Iteration {i+1}: {execution['actions_count']} actions")
    if execution['error']:
        print(f"  Error: {execution['error']}")
```

### With Error Recovery

```python
result = run_autonomous_agent(
    goal="Create email validator with regex",
    context="Handle edge cases: special chars, subdomains, etc",
    max_iterations=8  # More iterations for error recovery
)

if not result['success']:
    print(f"Errors encountered:")
    for error in result['errors'][:3]:  # First 3 errors
        print(f"  - {error}")
```

## Action Types

The agent can generate these actions:

```python
# File Operations
{"type": "write_file", "path": "projects/file.py", "content": "code"}
{"type": "append_file", "path": "projects/file.py", "content": "more code"}
{"type": "read_file", "path": "projects/file.py"}

# Execution
{"type": "run_python", "code": "import sys; print(sys.version)"}
{"type": "run_bash", "command": "ls -la projects/"}

# Discovery
{"type": "list_files", "path": "projects"}
```

## Loop Iteration

Each iteration follows:

```
Iteration N:
  1. Call LLM for PLAN (3-5 steps)
  2. Check if goal can be completed with these steps
  3. Call LLM for ACTIONS based on plan
  4. Execute all actions
  5. Check for errors in output
  6. If success → exit loop
  7. If error → add to context, continue
  8. If max_iterations reached → stop
```

## Configuration

### Environment Setup

```bash
# Ensure ollama_client can reach local LLM
export OLLAMA_HOST=http://localhost:11434

# Or configure in extension settings:
# dcode.backendURL = "http://localhost:5000"
```

### Max Iterations

- Default: 10 (reasonable for most tasks)
- Increase for complex tasks: 15-20
- Decrease for simple tasks: 3-5

### Success Criteria

Set explicit success criteria for better termination:

```python
result = run_autonomous_agent(
    goal="Create Flask app",
    success_criteria="App starts on port 5000 and responds to /health with 200"
)
```

## Output

### Result Dictionary

```python
{
    "goal": "Original goal",
    "success": True,           # Goal completed?
    "iterations": 3,           # How many loops?
    "final_state": {...},      # Last execution result
    "errors": [],              # Errors encountered
    "plan": [...],             # Generated plan steps
    "actions_executed": 7      # Total actions run
}
```

### Logging

All runs logged to `.logs/{project_name}/`:

```json
{
    "timestamp": "2026-04-15T10:30:45Z",
    "event_type": "autonomous_start",
    "status": "success",
    "details": "Max iterations: 10"
}
```

## Testing

Run test suite:

```bash
# Test 1: Basic creation
python test_autonomous.py 1

# Test 2: Complex task
python test_autonomous.py 2

# Test 3: Error recovery
python test_autonomous.py 3

# Custom goal
python test_autonomous.py manual
```

## Performance

### Token Usage

- Plan prompt: ~150 tokens
- Actions prompt: ~250 tokens
- Per iteration: ~400 tokens
- Typical 5-iteration task: ~2000 tokens

### Time Per Iteration

- LLM calls: 2-5 seconds (local) or 5-10 seconds (Gemini)
- Action execution: 0.5-2 seconds
- Total per iteration: ~5-15 seconds

### Optimization Tips

1. **Fewer iterations**: Set specific success_criteria
2. **Smaller context**: Only include relevant history
3. **Local models**: Use ollama for faster planning
4. **Parallel execution**: Future: parallelize action execution

## Integration

### With Flask Backend

```python
# In agent.py or web_app.py
from autonomous_agent import run_autonomous_agent

@app.route('/autonomous', methods=['POST'])
def autonomous_endpoint():
    data = request.json
    result = run_autonomous_agent(
        goal=data['goal'],
        project_name=data['project'],
        max_iterations=data.get('max_iterations', 10),
        context=data.get('context', '')
    )
    return result
```

### With VS Code Extension

```typescript
// In extension.ts
const result = await callAgent({
    task: userGoal,
    model: 'local',
    useAutonomousLoop: true,
    maxIterations: 10
});
```

## Limitations

1. **Bounded execution**: Max iterations prevents infinite loops
2. **Action scope**: Limited to projects/ directory for safety
3. **Error detection**: Heuristic-based (looks for "error" in output)
4. **State loss**: Restarting agent loses execution history

## Future Enhancements

- [ ] Parallel action execution (vectorize I/O)
- [ ] Multi-agent collaboration (different agents for different tasks)
- [ ] Checkpoint/resume (save state mid-loop)
- [ ] Cost tracking (monitor token usage)
- [ ] Model routing (auto-select best model per step)
- [ ] Confidence scoring (how certain of success?)

## Examples

### Example 1: Interactive Setup

```bash
$ python test_autonomous.py manual
Enter your goal: Create a scraper for weather data
Enter context: Use requests and BeautifulSoup, save to CSV
Max iterations: 8

🔄 [Iteration 1/8]
📋 Plan: 3 steps
  1. Set up project structure
  2. Write web scraper
  3. Test and validate data

⚙️  Actions: 3 to execute
✅ File created: projects/scraper.py
```

### Example 2: Complex Task

```python
result = run_autonomous_agent(
    goal="Implement merge sort algorithm with unit tests",
    context="Use pytest, put in projects/sorting.py, test file in projects/test_sorting.py",
    max_iterations=7
)

# After 3 iterations:
# - Iteration 1: Created sorting.py with basic structure
# - Iteration 2: Fixed syntax errors, added algorithm
# - Iteration 3: Added tests, all passing
# Success: True
```

---

**Status**: Ready for use
**Version**: 1.0
**Last Updated**: April 15, 2026
