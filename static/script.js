// DOM Elements
const chatMessages = document.getElementById("chatMessages");
const userInput = document.getElementById("userInput");
const sendBtn = document.getElementById("sendBtn");
const clearBtn = document.getElementById("clearBtn");
const refreshBtn = document.getElementById("refreshBtn");
const statusText = document.getElementById("status-text");
const statusDot = document.querySelector(".status-dot");

// State
let isLoading = false;

// Event Listeners
sendBtn.addEventListener("click", sendMessage);
userInput.addEventListener("keypress", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});
clearBtn.addEventListener("click", clearChat);
refreshBtn.addEventListener("click", refreshStatus);

// Initialize
loadChatHistory();
refreshStatus();

async function sendMessage() {
    const message = userInput.value.trim();
    if (!message || isLoading) return;

    // Disable input
    isLoading = true;
    userInput.disabled = true;
    sendBtn.disabled = true;

    // Add user message to UI
    addMessage(message, "user");
    userInput.value = "";

    // Add loading indicator
    const loadingId = addMessage("Thinking...", "loading");

    try {
        const response = await fetch("/api/ask", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message })
        });

        const data = await response.json();

        // Remove loading indicator
        const loadingMsg = document.querySelector(`[data-id="${loadingId}"]`);
        if (loadingMsg) loadingMsg.remove();

        if (data.success) {
            addMessage(data.message, "assistant");
            
            // Show execution details if available with rich formatting
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
        // Enable input
        isLoading = false;
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
    } else if (type === "system") {
        p.textContent = content;
    } else {
        p.textContent = content;
    }

    messageDiv.appendChild(p);
    chatMessages.appendChild(messageDiv);
    
    // Scroll to bottom
    setTimeout(() => {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }, 0);

    return messageId;
}

async function clearChat() {
    if (confirm("Clear chat history? This cannot be undone.")) {
        try {
            const response = await fetch("/api/clear", { method: "POST" });
            const data = await response.json();
            
            // Clear messages except system welcome
            const messages = chatMessages.querySelectorAll(".message");
            messages.forEach(m => m.remove());
            
            addMessage("💬 Chat cleared! Ready for new conversations.", "system");
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
        console.error("Error fetching status:", error);
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

// Rich action output renderer
function renderActionOutput(action) {
    const type = action.type;
    const messageId = Date.now().toString();
    const messageDiv = document.createElement("div");
    messageDiv.className = `message action-output action-${type}`;
    messageDiv.setAttribute("data-id", messageId);

    const container = document.createElement("div");
    container.className = "action-container";

    // Action header
    const header = document.createElement("div");
    header.className = "action-header";
    header.innerHTML = `<strong>📋 ${type.toUpperCase()}</strong>`;
    container.appendChild(header);

    // Action-specific rendering
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
            content.innerHTML = `<pre class="code-block">${escapeHtml(action.output || "")}</pre>`;
            break;

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

        case "show_progress":
            content.innerHTML = `<div class="progress-display">${escapeHtml(action.output || "")}</div>`;
            break;

        default:
            content.textContent = JSON.stringify(action);
    }

    container.appendChild(content);
    messageDiv.appendChild(container);
    chatMessages.appendChild(messageDiv);

    // Scroll to bottom
    setTimeout(() => {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }, 0);
}

function escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
}

// Refresh status every 5 seconds
setInterval(refreshStatus, 5000);
