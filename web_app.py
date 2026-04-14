from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from ollama_client import ask_llm
from parser import extract_json
from executor import execute_actions
from agent import execute_task
from context_handler import prepare_agent_context, format_context_for_llm
from logger import write_log, read_logs, format_log_summary
from transparency import get_tracker, create_new_session, reset_tracker
import os
import threading

app = Flask(__name__, static_folder="static", static_url_path="/static")
CORS(app)

# Store chat history
chat_history = []
agent_log = []

def run_agent(user_input):
    """Run the agent with retry logic"""
    for attempt in range(3):
        try:
            response = ask_llm(user_input)
            data = extract_json(response)
            
            if data:
                actions = data.get("actions", [])
                results = execute_actions(actions)  # Now returns results with output
                return {"success": True, "actions": results, "raw": response}
            
        except Exception as e:
            print(f"[ATTEMPT {attempt+1} ERROR]", str(e))
    
    return {"success": False, "error": "Could not get valid JSON after 3 attempts"}


@app.route("/")
def index():
    """Serve the main chat page"""
    return send_from_directory("static", "index.html")


@app.route("/api/ask", methods=["POST"])
def api_ask():
    """API endpoint to send a prompt to the agent"""
    data = request.json
    user_input = data.get("message", "").strip()
    
    if not user_input:
        return jsonify({"error": "Empty message"}), 400
    
    # Add to chat history
    chat_history.append({"role": "user", "content": user_input})
    
    # Run agent (non-blocking with threading)
    result = run_agent(user_input)
    
    # Add response to chat history
    response_msg = f"Executed {len(result.get('actions', []))} actions" if result["success"] else result.get("error", "Unknown error")
    chat_history.append({"role": "assistant", "content": response_msg})
    
    return jsonify({
        "success": result["success"],
        "message": response_msg,
        "details": result,
        "history": chat_history
    })


@app.route("/api/history", methods=["GET"])
def api_history():
    """Get chat history"""
    return jsonify({"history": chat_history})


@app.route("/api/clear", methods=["POST"])
def api_clear():
    """Clear chat history"""
    global chat_history
    chat_history = []
    return jsonify({"message": "Chat history cleared"})


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint (for orchestrator)"""
    return jsonify({"status": "healthy", "service": "backend"}), 200


@app.route("/api/status", methods=["GET"])
def api_status():
    """Get agent status"""
    return jsonify({
        "status": "online",
        "model": "qwen2.5-coder:7b",
        "messages": len(chat_history)
    })


@app.route("/api/agent/execute", methods=["POST"])
def agent_execute():
    """
    Codex-like agent endpoint.
    
    Request:
    {
        "task": "Build a login system",
        "selected_code": "optional selected code",
        "active_file": "optional current file",
        "mode": "plan" | "execute" (default: execute)
    }
    
    Response:
    {
        "success": true,
        "task": "...",
        "plan": [...],
        "actions": [...],
        "results": [...],
        "execution_time": 1.23
    }
    """
    import time
    
    data = request.json
    task = data.get("task", "").strip()
    
    if not task:
        return jsonify({"error": "Task is required"}), 400
    
    selected_code = data.get("selected_code")
    active_file = data.get("active_file")
    
    try:
        start_time = time.time()
        
        # Prepare context for efficient prompt
        context = prepare_agent_context(
            task=task,
            selected_code=selected_code,
            active_file=active_file
        )
        
        # Execute agent task (single-cycle: plan → action → result)
        result = execute_task(task, context)
        
        execution_time = time.time() - start_time
        
        # Log execution to web API project
        status = "success" if result.get("success") else "fail"
        details = result.get("error") or f"{len(result.get('actions', []))} actions executed"
        write_log("web_api", task, "agent_execute", status, details)
        
        # Log execution
        agent_log.append({
            "task": task,
            "success": result.get("success"),
            "time": execution_time,
            "actions_count": len(result.get("actions", []))
        })
        
        return jsonify({
            "success": result.get("success"),
            "task": task,
            "plan": result.get("plan", []),
            "actions_count": len(result.get("actions", [])),
            "actions": result.get("actions", []),
            "results": result.get("results", []),
            "error": result.get("error"),
            "execution_time": round(execution_time, 2)
        })
        
    except Exception as e:
        return jsonify({
            "error": str(e),
            "success": False
        }), 500


@app.route("/api/agent/log", methods=["GET"])
def agent_log_endpoint():
    """Get agent execution log"""
    return jsonify({"log": agent_log})


@app.route("/api/agent/clear", methods=["POST"])
def agent_clear():
    """Clear agent log"""
    global agent_log
    agent_log = []
    return jsonify({"message": "Agent log cleared"})


@app.route("/api/logs/<project>", methods=["GET"])
def get_project_logs(project):
    """Get structured logs for a project"""
    logs = read_logs(project)
    return jsonify({"project": project, "logs": logs, "count": len(logs)})


@app.route("/api/logs/<project>/summary", methods=["GET"])
def get_project_summary(project):
    """Get formatted summary of project logs"""
    summary = format_log_summary(project)
    return jsonify({"project": project, "summary": summary})


@app.route("/api/logs", methods=["GET"])
def list_all_logs():
    """List available log files"""
    import glob
    log_files = glob.glob(".logs/*.json")
    projects = [os.path.basename(f)[:-5] for f in log_files]
    return jsonify({"projects": projects, "count": len(projects)})


# ============================================================================
# TRANSPARENCY ENDPOINTS - Real-time agent execution tracking
# ============================================================================

@app.route("/api/transparency/session", methods=["POST"])
def transparency_start_session():
    """Start a new transparency session"""
    data = request.json or {}
    session_id = data.get("session_id")
    task = data.get("task", "")
    plan_steps = data.get("plan_steps", [])
    
    tracker = create_new_session()
    tracker.start_execution(task, plan_steps)
    
    return jsonify({
        "session_id": tracker.session_id,
        "status": "started",
        "state": tracker.get_state()
    })


@app.route("/api/transparency/state", methods=["GET"])
def transparency_get_state():
    """Get current transparency state"""
    tracker = get_tracker()
    return jsonify({
        "state": tracker.get_state()
    })


@app.route("/api/transparency/plan", methods=["POST"])
def transparency_add_plan():
    """Add plan steps"""
    data = request.json or {}
    steps = data.get("steps", [])
    estimated_time = data.get("estimated_time", 0)
    
    tracker = get_tracker()
    tracker.add_plan(steps, estimated_time)
    
    return jsonify({
        "status": "plan_added",
        "state": tracker.get_state()
    })


@app.route("/api/transparency/step/start", methods=["POST"])
def transparency_start_step():
    """Mark step as running"""
    data = request.json or {}
    step_index = data.get("step_index", 0)
    step_name = data.get("step_name", "")
    
    tracker = get_tracker()
    tracker.start_step(step_index, step_name)
    
    return jsonify({
        "status": "step_started",
        "state": tracker.get_state()
    })


@app.route("/api/transparency/step/complete", methods=["POST"])
def transparency_complete_step():
    """Mark step as complete"""
    data = request.json or {}
    output = data.get("output", "")
    success = data.get("success", True)
    
    tracker = get_tracker()
    tracker.complete_step(output, success)
    
    return jsonify({
        "status": "step_completed",
        "state": tracker.get_state()
    })


@app.route("/api/transparency/action", methods=["POST"])
def transparency_add_action():
    """Record action execution"""
    data = request.json or {}
    action = data.get("action", {})
    
    tracker = get_tracker()
    tracker.add_action(action)
    
    return jsonify({
        "status": "action_added",
        "action_index": len(tracker.actions) - 1,
        "state": tracker.get_state()
    })


@app.route("/api/transparency/action/<int:action_index>/complete", methods=["POST"])
def transparency_complete_action(action_index):
    """Mark action as complete"""
    data = request.json or {}
    output = data.get("output", "")
    success = data.get("success", True)
    
    tracker = get_tracker()
    tracker.complete_action(action_index, output, success)
    
    return jsonify({
        "status": "action_completed",
        "state": tracker.get_state()
    })


@app.route("/api/transparency/error", methods=["POST"])
def transparency_report_error():
    """Report an error"""
    data = request.json or {}
    error = data.get("error", "")
    context = data.get("context", "")
    
    tracker = get_tracker()
    tracker.add_error(error, context)
    
    return jsonify({
        "status": "error_recorded",
        "state": tracker.get_state()
    })


@app.route("/api/transparency/complete", methods=["POST"])
def transparency_complete_execution():
    """Mark execution as complete"""
    data = request.json or {}
    success = data.get("success", True)
    
    tracker = get_tracker()
    tracker.complete_execution(success)
    
    return jsonify({
        "status": "execution_completed",
        "state": tracker.get_state()
    })


if __name__ == "__main__":
    print("🚀 DCode Web UI starting on http://localhost:5000")
    print("📝 Local model: qwen2.5-coder:7b")
    app.run(debug=True, host="0.0.0.0", port=5000)
