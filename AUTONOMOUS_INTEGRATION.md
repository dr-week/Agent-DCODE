"""
Integration example: Autonomous Agent with Flask backend
Shows how to integrate autonomous_agent.py with web_app.py
"""

# Option 1: Add route to web_app.py
# ====================================

INTEGRATION_CODE = """
# Add this to web_app.py

from autonomous_agent import run_autonomous_agent, AutonomousAgent
from flask import request, jsonify

@app.route('/autonomous', methods=['POST'])
def autonomous_agent_endpoint():
    '''
    Autonomous agent endpoint - continuous planning and execution
    
    Request body:
    {
        "goal": "Create a Python calculator",
        "project": "calc_task",
        "max_iterations": 10,
        "context": "Optional context or existing code"
    }
    
    Response:
    {
        "success": true/false,
        "iterations": 3,
        "actions_executed": 7,
        "plan": [...],
        "errors": [...]
    }
    '''
    try:
        data = request.json
        goal = data.get('goal')
        
        if not goal:
            return jsonify({'error': 'goal is required'}), 400
        
        project_name = data.get('project', 'autonomous_task')
        max_iterations = data.get('max_iterations', 10)
        context = data.get('context', '')
        
        # Run autonomous agent
        result = run_autonomous_agent(
            goal=goal,
            project_name=project_name,
            max_iterations=max_iterations,
            context=context
        )
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/autonomous/stream', methods=['POST'])
def autonomous_agent_stream():
    '''
    Streaming version - returns iterations as they complete
    Use for real-time progress in UI
    '''
    data = request.json
    goal = data.get('goal')
    project_name = data.get('project', 'autonomous_stream')
    max_iterations = data.get('max_iterations', 10)
    context = data.get('context', '')
    
    agent = AutonomousAgent(project_name, max_iterations)
    
    def generate():
        for iteration in range(1, max_iterations + 1):
            # Run one iteration
            plan = agent._get_plan(goal, context)
            if plan:
                yield f'data: {{\\"iteration\\": {iteration}, \\"status\\": \\"planning\\", \\"steps\\": {len(plan.get(\\"steps\\", []))}}}\\n\\n'
                
                actions = agent._get_actions(goal, plan.get('steps', []), context)
                if actions:
                    yield f'data: {{\\"iteration\\": {iteration}, \\"status\\": \\"executing\\", \\"actions\\": {len(actions.get(\\"actions\\", []))}}}\\n\\n'
                    
                    exec_result = agent._execute_and_check(actions.get('actions', []))
                    yield f'data: {{\\"iteration\\": {iteration}, \\"status\\": \\"checking\\", \\"success\\": {exec_result.get(\\"success\\", False)}}}\\n\\n'
                    
                    if agent._check_goal_complete(exec_result):
                        yield f'data: {{\\"status\\": \\"complete\\", \\"iterations\\": {iteration}}}\\n\\n'
                        break
                    
                    context += f"\\n\\nIteration {iteration} result: {exec_result}"
            else:
                break
    
    return Response(generate(), mimetype='text/event-stream')
"""

# Option 2: VS Code Extension Integration
# ========================================

EXTENSION_INTEGRATION = """
// In vsc-agent/dcode/src/extension.ts

import { callAgent } from './api/backend-api';

// Add autonomous mode command
context.subscriptions.push(
    vscode.commands.registerCommand('dcode.startAutonomousAgent', async () => {
        const goal = await vscode.window.showInputBox({
            prompt: 'Enter your goal for the autonomous agent',
            placeHolder: 'e.g., Create a web scraper using BeautifulSoup'
        });
        
        if (!goal) return;
        
        const maxIterations = await vscode.window.showInputBox({
            prompt: 'Max iterations (default: 10)',
            value: '10'
        });
        
        const iterations = parseInt(maxIterations || '10');
        
        const output = vscode.window.createOutputChannel('Autonomous Agent');
        output.show();
        
        try {
            output.appendLine(`Starting autonomous agent: ${goal}`);
            output.appendLine(`Max iterations: ${iterations}`);
            output.appendLine('---');
            
            const result = await fetch('http://localhost:5000/autonomous', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    goal,
                    project: 'vscode_autonomous',
                    max_iterations: iterations
                })
            }).then(r => r.json());
            
            output.appendLine(`Success: ${result.success}`);
            output.appendLine(`Iterations: ${result.iterations}`);
            output.appendLine(`Actions: ${result.actions_executed}`);
            
            if (result.errors.length > 0) {
                output.appendLine('Errors:');
                result.errors.forEach(e => output.appendLine(`  - ${e}`));
            }
            
            if (result.success) {
                vscode.window.showInformationMessage(
                    `Agent completed in ${result.iterations} iterations`
                );
            }
        } catch (error) {
            output.appendLine(`Error: ${error}`);
        }
    })
);
"""

# Option 3: Python client usage
# =============================

CLIENT_USAGE = """
# client_autonomous_agent.py - Python client to call autonomous agent

import requests
import json

class AutonomousAgentClient:
    def __init__(self, backend_url="http://localhost:5000"):
        self.backend_url = backend_url
    
    def run_goal(self, goal, project="auto_task", max_iterations=10, context=""):
        '''Run autonomous agent on backend'''
        response = requests.post(
            f'{self.backend_url}/autonomous',
            json={
                'goal': goal,
                'project': project,
                'max_iterations': max_iterations,
                'context': context
            },
            timeout=120  # 2 minutes for full execution
        )
        return response.json()
    
    def stream_goal(self, goal, project="auto_task", max_iterations=10):
        '''Stream agent progress (Server-Sent Events)'''
        response = requests.post(
            f'{self.backend_url}/autonomous/stream',
            json={
                'goal': goal,
                'project': project,
                'max_iterations': max_iterations
            },
            stream=True
        )
        
        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8')
                if line.startswith('data: '):
                    data = json.loads(line[6:])
                    yield data

# Usage
client = AutonomousAgentClient()

# Direct call
result = client.run_goal(
    goal="Create a Python function that validates email",
    project="email_validator"
)
print(f"Success: {result['success']}")
print(f"Iterations: {result['iterations']}")

# Streaming
for progress in client.stream_goal("Build a Flask REST API"):
    print(f"[{progress['iteration']}] {progress['status']}")
"""

# Option 4: Batch/Scheduler Usage
# ================================

BATCH_USAGE = """
# batch_autonomous_tasks.py - Run multiple autonomous tasks

from autonomous_agent import run_autonomous_agent

TASKS = [
    {
        "goal": "Create a Python calculator with add, subtract, multiply, divide",
        "project": "calc",
        "max_iterations": 5,
        "context": "Put in projects/calculator.py"
    },
    {
        "goal": "Create a web scraper for news headlines",
        "project": "scraper",
        "max_iterations": 7,
        "context": "Use requests and BeautifulSoup, save to CSV"
    },
    {
        "goal": "Implement quicksort algorithm with tests",
        "project": "sorting",
        "max_iterations": 6,
        "context": "Use pytest, put in projects/quicksort.py"
    }
]

results = {}
for task in TASKS:
    print(f"\\nRunning: {task['goal']}")
    result = run_autonomous_agent(
        goal=task['goal'],
        project_name=task['project'],
        max_iterations=task['max_iterations'],
        context=task['context']
    )
    results[task['project']] = result
    print(f"  Result: {'SUCCESS' if result['success'] else 'FAILED'} ({result['iterations']} iterations)")

# Summary
print("\\n=== BATCH SUMMARY ===")
success_count = sum(1 for r in results.values() if r['success'])
total_iterations = sum(r['iterations'] for r in results.values())
print(f"Success: {success_count}/{len(results)}")
print(f"Total iterations: {total_iterations}")
"""

if __name__ == '__main__':
    print("=== AUTONOMOUS AGENT INTEGRATION OPTIONS ===\n")
    
    print("1. FLASK BACKEND ROUTES")
    print("-" * 50)
    print("Add /autonomous endpoint to web_app.py")
    print("\n" + INTEGRATION_CODE)
    
    print("\n2. VS CODE EXTENSION")
    print("-" * 50)
    print("Add autonomous command to extension.ts")
    print("\n" + EXTENSION_INTEGRATION)
    
    print("\n3. PYTHON CLIENT")
    print("-" * 50)
    print("Use remote autonomous agent")
    print("\n" + CLIENT_USAGE)
    
    print("\n4. BATCH PROCESSING")
    print("-" * 50)
    print("Run multiple goals in sequence")
    print("\n" + BATCH_USAGE)
