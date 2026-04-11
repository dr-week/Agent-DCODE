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
            
            // Show execution details if available
            if (data.details.actions && data.details.actions.length > 0) {
                const actionList = data.details.actions
                    .map((a, i) => `${i + 1}. ${a.type}: ${a.path || a.command || ""}`)
                    .join("\n");
                addMessage(`Actions executed:\n${actionList}`, "system");
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

// Refresh status every 5 seconds
setInterval(refreshStatus, 5000);
