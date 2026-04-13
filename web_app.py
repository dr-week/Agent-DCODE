from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from ollama_client import ask_llm
from parser import extract_json
from executor import execute_actions
from agent import execute_task
from context_handler import prepare_agent_context, format_context_for_llm
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


if __name__ == "__main__":
    print("🚀 DCode Web UI starting on http://localhost:5000")
    print("📝 Local model: qwen2.5-coder:7b")
    app.run(debug=True, host="0.0.0.0", port=5000)
