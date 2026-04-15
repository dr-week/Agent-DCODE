// ===== AGENT MODE VARIABLES & STATE =====
let currentMode = "agent"; // "agent" or "chat"
let isExecuting = false;

// ===== FILE SIDEBAR STATE =====
let fileTreeData = [];
let currentFileState = {
    path: null,
    status: "pending"
};
let fileStatusUpdateInterval = null;

// ===== CODEX CONTROL BAR STATE =====
let codexState = {
    files: [],
    code: "",
    model: "local",
    environment: "local",
    approvalsMode: "auto",
    settings: {
        autoExecute: false,
        showThinking: false,
        safeMode: true
    }
};

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

// DOM Elements - Codex Control Bar
const addFileBtn = document.getElementById("addFileBtn");
const codeContextBtn = document.getElementById("codeContextBtn");
const modelSelect = document.getElementById("modelSelect");
const settingsBtn = document.getElementById("settingsBtn");
const sendTaskBtn = document.getElementById("sendTaskBtn");
const environmentSelect = document.getElementById("environmentSelect");
const approvalsSelect = document.getElementById("approvalsSelect");
const settingsPopup = document.getElementById("settingsPopup");
const closeSettingsBtn = document.getElementById("closeSettingsBtn");
const autoExecuteCheckbox = document.getElementById("autoExecute");
const showThinkingCheckbox = document.getElementById("showThinking");
const safeModeCheckbox = document.getElementById("safeMode");
const fileInput = document.getElementById("fileInput");
const filesIndicator = document.getElementById("filesIndicator");
const filesCount = document.getElementById("filesCount");

// DOM Elements - File Sidebar
const fileSidebar = document.getElementById("fileSidebar");
const sidebarToggle = document.getElementById("sidebarToggle");
const fileTreeContainer = document.getElementById("fileTreeContainer");

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

// Codex Control Bar Events
addFileBtn.addEventListener("click", handleAddFile);
codeContextBtn.addEventListener("click", handleCodeContext);
modelSelect.addEventListener("change", (e) => {
    codexState.model = e.target.value;
});
settingsBtn.addEventListener("click", toggleSettingsPopup);
closeSettingsBtn.addEventListener("click", hideSettingsPopup);
sendTaskBtn.addEventListener("click", sendCodexTask);
environmentSelect.addEventListener("change", (e) => {
    codexState.environment = e.target.value;
});
approvalsSelect.addEventListener("change", (e) => {
    codexState.approvalsMode = e.target.value;
});

// Settings Checkboxes
autoExecuteCheckbox.addEventListener("change", (e) => {
    codexState.settings.autoExecute = e.target.checked;
});
showThinkingCheckbox.addEventListener("change", (e) => {
    codexState.settings.showThinking = e.target.checked;
});
safeModeCheckbox.addEventListener("change", (e) => {
    codexState.settings.safeMode = e.target.checked;
});

// File Input
fileInput.addEventListener("change", handleFileSelection);

// File Sidebar
sidebarToggle.addEventListener("click", toggleSidebar);

// Close settings popup when clicking outside
document.addEventListener("click", (e) => {
    if (settingsPopup.style.display !== "none" && 
        !settingsPopup.contains(e.target) && 
        e.target !== settingsBtn) {
        hideSettingsPopup();
    }
});

// ===== INITIALIZATION =====
loadChatHistory();
refreshStatus();
initCodexBar();
initFilePanel();

// ===== CODEX CONTROL BAR FUNCTIONS =====

function initCodexBar() {
    // Initialize state from selects if they have values
    modelSelect.value = codexState.model;
    environmentSelect.value = codexState.environment;
    approvalsSelect.value = codexState.approvalsMode;
}

function handleAddFile() {
    fileInput.click();
}

function handleFileSelection(e) {
    const files = Array.from(e.target.files);
    
    files.forEach(file => {
        const reader = new FileReader();
        reader.onload = (event) => {
            const fileData = {
                name: file.name,
                content: event.target.result,
                type: file.type,
                size: file.size
            };
            codexState.files.push(fileData);
            updateFilesIndicator();
        };
        reader.readAsText(file, "UTF-8");
    });
    
    // Reset file input
    fileInput.value = "";
}

function updateFilesIndicator() {
    if (codexState.files.length > 0) {
        filesCount.textContent = codexState.files.length;
        filesIndicator.style.display = "block";
    } else {
        filesIndicator.style.display = "none";
    }
}

function handleCodeContext() {
    // Try to get code from clipboard or active file
    navigator.clipboard.read().then(items => {
        for (let item of items) {
            if (item.types.includes("text/plain")) {
                item.getType("text/plain").then(blob => {
                    blob.text().then(text => {
                        codexState.code = text;
                        agentTask.value = `Analyze and work with the following code:\n\n${text.substring(0, 100)}...`;
                    });
                });
            }
        }
    }).catch(err => {
        // Fallback: show prompt for code input
        const code = prompt("Paste your code context:");
        if (code) {
            codexState.code = code;
            agentTask.value = `Analyze and work with the following code context...`;
        }
    });
}

function toggleSettingsPopup() {
    if (settingsPopup.style.display === "none") {
        showSettingsPopup();
    } else {
        hideSettingsPopup();
    }
}

function showSettingsPopup() {
    settingsPopup.style.display = "block";
    // Update checkbox states
    autoExecuteCheckbox.checked = codexState.settings.autoExecute;
    showThinkingCheckbox.checked = codexState.settings.showThinking;
    safeModeCheckbox.checked = codexState.settings.safeMode;
}

function hideSettingsPopup() {
    settingsPopup.style.display = "none";
}

function buildCodexRequest() {
    return {
        task: agentTask.value.trim(),
        code: codexState.code,
        model: codexState.model,
        environment: codexState.environment,
        approval_mode: codexState.approvalsMode,
        files: codexState.files,
        settings: codexState.settings
    };
}

async function sendCodexTask() {
    const request = buildCodexRequest();
    
    if (!request.task) {
        alert("Please enter a task");
        return;
    }

    // Auto-execute if enabled
    if (codexState.settings.autoExecute) {
        executeAgentTask();
    } else {
        // Show the built request in the task area
        agentTask.value = `🎯 Task: ${request.task}\n📦 Model: ${request.model}\n🌍 Env: ${request.environment}\n✓ Approvals: ${request.approval_mode}\n📁 Files: ${request.files.length}`;
    }
}

// ===== FILE PANEL FUNCTIONS =====

async function initFilePanel() {
    // Initialize file panel on page load
    await loadFileTree();
    startFileStatusUpdate();
    
    // Handle window resize for responsive sidebar
    window.addEventListener("resize", handleWindowResize);
}

async function loadFileTree() {
    // Fetch and render project file tree
    try {
        const response = await fetch("/api/files");
        const data = await response.json();
        
        if (data.success) {
            fileTreeData = data.files;
            renderFileTree();
        }
    } catch (error) {
        console.error("Error loading file tree:", error);
        fileTreeContainer.innerHTML = `<div class="loading">Error loading files</div>`;
    }
}

function renderFileTree() {
    // Render file tree structure to HTML
    fileTreeContainer.innerHTML = "";
    
    if (fileTreeData.length === 0) {
        fileTreeContainer.innerHTML = `<div class="loading">No files found</div>`;
        return;
    }
    
    const tree = document.createElement("ul");
    tree.className = "file-tree";
    
    fileTreeData.forEach(item => {
        const li = renderFileItem(item);
        tree.appendChild(li);
    });
    
    fileTreeContainer.appendChild(tree);
}

function renderFileItem(item, level = 0) {
    // Render a single file/directory item
    const li = document.createElement("li");
    li.className = `file-item ${item.type}`;
    li.setAttribute("data-path", item.path);
    
    const content = document.createElement("div");
    content.className = "file-item-content";
    
    // Icon
    const icon = document.createElement("span");
    icon.className = "file-item-icon";
    icon.textContent = item.type === "directory" ? "📁" : getFileIcon(item.name);
    content.appendChild(icon);
    
    // Name
    const name = document.createElement("span");
    name.textContent = item.name;
    name.style.flex = 1;
    content.appendChild(name);
    
    // Status indicator
    const status = document.createElement("span");
    status.className = "file-item-status pending";
    status.textContent = "○";
    content.appendChild(status);
    
    li.appendChild(content);
    
    // Directory children
    if (item.type === "directory" && item.children && item.children.length > 0) {
        const nested = document.createElement("ul");
        nested.className = "file-tree-nested";
        
        item.children.forEach(child => {
            nested.appendChild(renderFileItem(child, level + 1));
        });
        
        li.appendChild(nested);
        
        // Toggle expand/collapse
        content.addEventListener("click", (e) => {
            e.stopPropagation();
            li.classList.toggle("expanded");
        });
    }
    
    return li;
}

function getFileIcon(filename) {
    // Get file type icon based on extension
    const ext = filename.split(".").pop().toLowerCase();
    const icons = {
        'py': '🐍',
        'js': '📜',
        'ts': '📘',
        'jsx': '⚛️',
        'tsx': '⚛️',
        'json': '{}',
        'html': '🌐',
        'css': '🎨',
        'md': '📝',
        'txt': '📄',
        'yml': '⚙️',
        'yaml': '⚙️',
        'sh': '💻',
        'bash': '💻',
        'sql': '💾',
        'git': '🔧'
    };
    return icons[ext] || '📄';
}

function startFileStatusUpdate() {
    // Start polling for current file status every 1s
    if (fileStatusUpdateInterval) {
        clearInterval(fileStatusUpdateInterval);
    }
    
    fileStatusUpdateInterval = setInterval(updateFileStatus, 1000);
}

async function updateFileStatus() {
    // Fetch and update current file status
    try {
        const response = await fetch("/api/current-file");
        const data = await response.json();
        
        if (data.current_file) {
            // Update current file highlight
            if (currentFileState.path !== data.current_file) {
                clearCurrentFileHighlight();
                currentFileState.path = data.current_file;
                highlightCurrentFile();
            }
            
            // Update status indicator
            updateFileStatusIndicator(data.current_file, data.status);
            currentFileState.status = data.status;
        }
    } catch (error) {
        console.error("Error updating file status:", error);
    }
}

function highlightCurrentFile() {
    // Highlight current file and scroll to it
    const fileElement = document.querySelector(`[data-path="${currentFileState.path}"]`);
    
    if (fileElement) {
        fileElement.querySelector(".file-item-content").classList.add("current");
        
        // Expand parent directories
        let parent = fileElement.parentElement.parentElement;
        while (parent && parent.classList.contains("file-item")) {
            parent.classList.add("expanded");
            parent = parent.parentElement.parentElement;
        }
        
        // Scroll into view
        fileElement.scrollIntoView({ behavior: "smooth", block: "nearest" });
    }
}

function clearCurrentFileHighlight() {
    // Remove highlight from current file
    if (currentFileState.path) {
        const fileElement = document.querySelector(`[data-path="${currentFileState.path}"]`);
        if (fileElement) {
            fileElement.querySelector(".file-item-content").classList.remove("current");
        }
    }
}

function updateFileStatusIndicator(filePath, status) {
    // Update status indicator for a file
    const fileElement = document.querySelector(`[data-path="${filePath}"]`);
    
    if (fileElement) {
        const statusEl = fileElement.querySelector(".file-item-status");
        
        // Remove old status classes
        statusEl.classList.remove("pending", "working", "done", "error");
        
        // Add new status class
        statusEl.classList.add(status);
        
        // Update icon
        const icons = {
            "pending": "○",
            "working": "⏳",
            "done": "✔",
            "error": "✕"
        };
        
        statusEl.textContent = icons[status] || "○";
    }
}

function toggleSidebar() {
    // Toggle sidebar visibility
    fileSidebar.classList.toggle("collapsed");
}

function handleWindowResize() {
    // Handle responsive sidebar behavior
    const width = window.innerWidth;
    
    // Auto-collapse on very small screens
    if (width < 600 && !fileSidebar.classList.contains("collapsed")) {
        fileSidebar.classList.add("collapsed");
    }
}

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
    sendTaskBtn.disabled = true;
    agentWorkflow.style.display = "none";
    loadingSpinner.style.display = "flex";

    try {
        // Build the request with Codex state
        const request = buildCodexRequest();
        
        const response = await fetch("/api/agent/execute", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(request)
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
        sendTaskBtn.disabled = false;
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
    if (confirm("Clear task, results, and Codex state?")) {
        agentTask.value = "";
        planSteps.innerHTML = "";
        actionsList.innerHTML = "";
        resultsList.innerHTML = "";
        executionInfo.innerHTML = "";
        agentWorkflow.style.display = "none";
        
        // Clear Codex state
        codexState.files = [];
        codexState.code = "";
        updateFilesIndicator();
        hideSettingsPopup();
        
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
