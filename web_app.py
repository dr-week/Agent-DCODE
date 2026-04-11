from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from ollama_client import ask_llm
from parser import extract_json
from executor import execute_actions
import os
import threading

app = Flask(__name__, static_folder="static", static_url_path="/static")
CORS(app)

# Store chat history
chat_history = []

def run_agent(user_input):
    """Run the agent with retry logic"""
    for attempt in range(3):
        try:
            response = ask_llm(user_input)
            data = extract_json(response)
            
            if data:
                actions = data.get("actions", [])
                execute_actions(actions)
                return {"success": True, "actions": actions, "raw": response}
            
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


if __name__ == "__main__":
    print("🚀 DCode Web UI starting on http://localhost:5000")
    print("📝 Local model: qwen2.5-coder:7b")
    app.run(debug=True, host="0.0.0.0", port=5000)
