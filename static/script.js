// ===== AGENT MODE VARIABLES & STATE =====
let currentMode = "agent"; // "agent" or "chat"
let isExecuting = false;

// DOM Elements - General
const statusText = document.getElementById("status-text");
const statusDot = document.querySelector(".status-dot");

// DOM Elements - Mode Selector
const modeButtons = document.querySelectorAll(".mode-btn");
const modeContents = document.querySelectorAll(".mode-content");

// DOM Elements - Agent Mode
const agentTask = document.getElementById("agentTask");
const executeBtn = document.getElementById("executeBtn");
const clearAgentBtn = document.getElementById("clearAgentBtn");
const agentWorkflow = document.getElementById("agentWorkflow");
const loadingSpinner = document.getElementById("loadingSpinner");
const planSteps = document.getElementById("planSteps");
const actionsList = document.getElementById("actionsList");
const resultsList = document.getElementById("resultsList");
const executionInfo = document.getElementById("executionInfo");

// DOM Elements - Chat Mode
const chatMessages = document.getElementById("chatMessages");
const userInput = document.getElementById("userInput");
const sendBtn = document.getElementById("sendBtn");
const clearBtn = document.getElementById("clearBtn");
const refreshBtn = document.getElementById("refreshBtn");

// ===== EVENT LISTENERS =====

// Mode switching
modeButtons.forEach(btn => {
    btn.addEventListener("click", () => switchMode(btn.dataset.mode));
});

// Agent Mode
executeBtn.addEventListener("click", executeAgentTask);
clearAgentBtn.addEventListener("click", clearAgentMode);
agentTask.addEventListener("keydown", (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
        executeAgentTask();
    }
});

// Chat Mode
sendBtn.addEventListener("click", sendMessage);
userInput.addEventListener("keypress", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});
clearBtn.addEventListener("click", clearChat);
refreshBtn.addEventListener("click", refreshStatus);

// ===== INITIALIZATION =====
loadChatHistory();
refreshStatus();

// ===== MODE SWITCHING =====
function switchMode(mode) {
    currentMode = mode;
    
    // Update buttons
    modeButtons.forEach(btn => {
        btn.classList.toggle("active", btn.dataset.mode === mode);
    });
    
    // Update content visibility
    modeContents.forEach(content => {
        content.style.display = content.id === `${mode}Mode` ? "flex" : "none";
    });
    
    if (mode === "agent") {
        agentTask.focus();
    } else if (mode === "chat") {
        userInput.focus();
    }
}

// ===== AGENT MODE FUNCTIONS =====

async function executeAgentTask() {
    const task = agentTask.value.trim();
    if (!task || isExecuting) return;

    isExecuting = true;
    executeBtn.disabled = true;
    agentWorkflow.style.display = "none";
    loadingSpinner.style.display = "flex";

    try {
        const response = await fetch("/api/agent/execute", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ task })
        });

        const data = await response.json();
        loadingSpinner.style.display = "none";

        if (data.success) {
            // Display results
            displayAgentWorkflow(data);
            agentWorkflow.style.display = "flex";
        } else {
            addAgentError(data.error || "Unknown error");
        }
    } catch (error) {
        console.error(error);
        loadingSpinner.style.display = "none";
        addAgentError(`Network error: ${error.message}`);
    } finally {
        isExecuting = false;
        executeBtn.disabled = false;
    }
}

function displayAgentWorkflow(data) {
    // Clear previous content
    planSteps.innerHTML = "";
    actionsList.innerHTML = "";
    resultsList.innerHTML = "";
    executionInfo.innerHTML = "";

    // Display plan
    if (data.plan && data.plan.length > 0) {
        data.plan.forEach(step => {
            const stepDiv = document.createElement("div");
            stepDiv.className = "plan-step";
            stepDiv.innerHTML = `<span class="plan-step-number">${step.step}.</span> ${escapeHtml(step.description)}`;
            planSteps.appendChild(stepDiv);
        });
    }

    // Display actions
    if (data.actions && data.actions.length > 0) {
        data.actions.forEach(action => {
            const actionDiv = document.createElement("div");
            actionDiv.className = "action-item";
            actionDiv.innerHTML = `<span class="action-type">${action.type}</span><br>${escapeHtml(JSON.stringify(action).substring(0, 100))}`
            actionsList.appendChild(actionDiv);
        });
    }

    // Display results
    if (data.results && data.results.length > 0) {
        data.results.forEach(result => {
            const resultDiv = document.createElement("div");
            resultDiv.className = result.error ? "result-item error" : "result-item";
            const output = result.output ? result.output.substring(0, 150) : "No output";
            resultDiv.innerHTML = `<strong>${result.type}</strong>: ${escapeHtml(output)}...`;
            resultsList.appendChild(resultDiv);
        });
    }

    // Display execution info
    const infoHtml = `
        <div class="exec-stat">
            <span>⏱️ Time:</span>
            <span class="exec-stat-value">${data.execution_time}s</span>
        </div>
        <div class="exec-stat">
            <span>▶️ Actions:</span>
            <span class="exec-stat-value">${data.actions_count}</span>
        </div>
        <div class="exec-stat">
            <span>✅ Status:</span>
            <span class="exec-stat-value">${data.success ? "Success" : "Failed"}</span>
        </div>
    `;
    executionInfo.innerHTML = infoHtml;
}

function addAgentError(message) {
    agentWorkflow.style.display = "flex";
    planSteps.innerHTML = `<div class="plan-step" style="border-left-color: #ef4444; background: #fef2f2; color: #dc2626;">❌ ${escapeHtml(message)}</div>`;
}

function clearAgentMode() {
    if (confirm("Clear task and results?")) {
        agentTask.value = "";
        planSteps.innerHTML = "";
        actionsList.innerHTML = "";
        resultsList.innerHTML = "";
        executionInfo.innerHTML = "";
        agentWorkflow.style.display = "none";
        agentTask.focus();
    }
}

// ===== CHAT MODE FUNCTIONS =====

async function sendMessage() {
    const message = userInput.value.trim();
    if (!message || isExecuting) return;

    isExecuting = true;
    userInput.disabled = true;
    sendBtn.disabled = true;

    addMessage(message, "user");
    userInput.value = "";

    const loadingId = addMessage("Thinking...", "loading");

    try {
        const response = await fetch("/api/ask", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message })
        });

        const data = await response.json();

        const loadingMsg = document.querySelector(`[data-id="${loadingId}"]`);
        if (loadingMsg) loadingMsg.remove();

        if (data.success) {
            addMessage(data.message, "assistant");
         if (data.details.actions && data.details.actions.length > 0) {
                for (const action of data.details.actions) {
                    renderActionOutput(action);
                }
            }
        } else {
            addMessage(`Error: ${data.message || "Unknown error"}`, "error");
        }
    } catch (error) {
        const loadingMsg = document.querySelector(`[data-id="${loadingId}"]`);
        if (loadingMsg) loadingMsg.remove();
        addMessage(`Network error: ${error.message}`, "error");
        console.error(error);
    } finally {
        isExecuting = false;
        userInput.disabled = false;
        sendBtn.disabled = false;
        userInput.focus();
    }
}

function addMessage(content, type = "assistant") {
    const messageId = Date.now().toString();
    const messageDiv = document.createElement("div");
    messageDiv.className = `message ${type}`;
    messageDiv.setAttribute("data-id", messageId);

    const p = document.createElement("p");
    
    if (type === "loading") {
        p.innerHTML = `<span class="loading-dot">.</span><span class="loading-dot">.</span><span class="loading-dot">.</span>`;
    } else {
        p.textContent = content;
    }

    messageDiv.appendChild(p);
    chatMessages.appendChild(messageDiv);

    setTimeout(() => {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }, 0);

    return messageId;
}

async function clearChat() {
    if (confirm("Clear chat history?")) {
        try {
            await fetch("/api/clear", { method: "POST" });
            chatMessages.innerHTML = `
                <div class="message system">
                    <p>👋 Welcome! I'm DCode, your offline AI coding assistant.</p>
                    <p>Ask me to write code, refactor files, run commands, and more!</p>
                    <p><small>Using: qwen2.5-coder:7b</small></p>
                </div>
            `;
        } catch (error) {
            console.error("Error clearing chat:", error);
        }
    }
}

async function refreshStatus() {
    try {
        const response = await fetch("/api/status");
        const data = await response.json();

        if (data.status === "online") {
            statusDot.className = "status-dot online";
            statusText.textContent = `Online • ${data.messages} messages`;
        } else {
            statusDot.className = "status-dot offline";
            statusText.textContent = "Offline";
        }
    } catch (error) {
        statusDot.className = "status-dot offline";
        statusText.textContent = "Offline";
    }
}

async function loadChatHistory() {
    try {
        const response = await fetch("/api/history");
        const data = await response.json();

        data.history.forEach(msg => {
            if (msg.role === "user") {
                addMessage(msg.content, "user");
            } else if (msg.role === "assistant") {
                addMessage(msg.content, "assistant");
            }
        });
    } catch (error) {
        console.error("Error loading history:", error);
    }
}

function renderActionOutput(action) {
    const type = action.type;
    const messageId = Date.now().toString();
    const messageDiv = document.createElement("div");
    messageDiv.className = `message action-output action-${type}`;
    messageDiv.setAttribute("data-id", messageId);

    const container = document.createElement("div");
    container.className = "action-container";

    const header = document.createElement("div");
    header.className = "action-header";
    header.innerHTML = `<strong>📋 ${type.toUpperCase()}</strong>`;
    container.appendChild(header);

    const content = document.createElement("div");
    content.className = "action-content";

    switch (type) {
        case "write_file":
        case "append_file":
            content.innerHTML = `<code>${action.path || ""}</code>`;
            break;

        case "read_file":
            content.innerHTML = `<pre>${escapeHtml(action.output || "")}</pre>`;
            break;

        case "run_command":
        case "run_bash":
            content.innerHTML = `<div class="command-box"><code>$ ${escapeHtml(action.command || "")}</code></div>
                                <pre class="output">${escapeHtml(action.output || "")}</pre>`;
            break;

        case "run_python":
        case "run_js":
            content.innerHTML = `<pre class="code-block">${escapeHtml(action.output || "")}</pre>`;
            break;

        case "list_files":
            content.innerHTML = `<pre class="file-tree">${escapeHtml(action.output || "")}</pre>`;
            break;

        case "get_processes":
            if (action.output) {
                const lines = action.output.split("\n").filter(l => l.trim());
                let html = "<table class='process-table'>";
                lines.forEach((line, i) => {
                    if (i === 0) {
                        html += `<thead><tr><th>${line.replace(/\t/g, "</th><th>")}</th></tr></thead>`;
                    } else {
                        html += `<tr><td>${line.replace(/\t/g, "</td><td>")}</td></tr>`;
                    }
                });
                html += "</table>";
                content.innerHTML = html;
            }
            break;

        default:
            content.textContent = JSON.stringify(action).substring(0, 200);
    }

    container.appendChild(content);
    messageDiv.appendChild(container);
    chatMessages.appendChild(messageDiv);

    setTimeout(() => {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }, 0);
}

function escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
}

// Status refresh
setInterval(refreshStatus, 5000);
