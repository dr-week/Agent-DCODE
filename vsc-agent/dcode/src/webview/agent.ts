import * as vscode from "vscode";

export function getAgentWebviewContent(webview: vscode.Webview): string {
	return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="Content-Security-Policy" content="default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline';">
    <title>Agent Mode</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: monospace;
            background: var(--vscode-editor-background);
            color: var(--vscode-editor-foreground);
            display: flex;
            flex-direction: column;
            height: 100vh;
        }
        
        #content {
            flex: 1;
            overflow-y: auto;
            padding: 12px;
            font-size: 12px;
            line-height: 1.6;
        }
        
        .section {
            margin-bottom: 16px;
        }
        
        .section-title {
            color: var(--vscode-terminal-ansiCyan);
            font-weight: bold;
            margin-bottom: 6px;
        }
        
        .item {
            padding: 4px 8px;
            margin: 2px 0;
            background: var(--vscode-input-background);
            border-left: 2px solid var(--vscode-terminal-ansiGreen);
        }
        
        .plan-item {
            border-left-color: var(--vscode-terminal-ansiCyan);
        }
        
        .action-item {
            border-left-color: var(--vscode-terminal-ansiYellow);
        }
        
        .result-item {
            border-left-color: var(--vscode-terminal-ansiGreen);
        }
        
        .result-item.error {
            border-left-color: var(--vscode-terminal-ansiRed);
            opacity: 0.8;
        }
        
        .loading {
            color: var(--vscode-terminal-ansiYellow);
            font-style: italic;
        }
        
        .error {
            color: var(--vscode-terminal-ansiRed);
            background: var(--vscode-inputValidation-errorBackground);
            padding: 8px;
            border-radius: 4px;
            margin: 8px 0;
        }
        
        .success {
            color: var(--vscode-terminal-ansiGreen);
        }
        
        .stats {
            color: var(--vscode-terminal-ansiWhite);
            opacity: 0.7;
            font-size: 11px;
            margin-top: 8px;
        }
        
        #inputContainer {
            padding: 12px;
            border-top: 1px solid var(--vscode-panel-border);
            display: flex;
            flex-direction: column;
            gap: 8px;
        }
        
        textarea {
            flex: 1;
            padding: 8px;
            background: var(--vscode-input-background);
            color: var(--vscode-input-foreground);
            border: 1px solid var(--vscode-input-border);
            border-radius: 4px;
            font-family: monospace;
            resize: vertical;
            min-height: 60px;
        }
        
        .button-group {
            display: flex;
            gap: 8px;
        }
        
        button {
            flex: 1;
            padding: 6px 12px;
            background: var(--vscode-button-background);
            color: var(--vscode-button-foreground);
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 12px;
        }
        
        button:hover {
            background: var(--vscode-button-hoverBackground);
        }
        
        button:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
    </style>
</head>
<body>
    <div id="content"></div>
    <div id="inputContainer">
        <textarea id="taskInput" placeholder="Enter your task here..."></textarea>
        <div class="button-group">
            <button id="executeBtn">Execute Task</button>
            <button id="clearBtn">Clear</button>
        </div>
    </div>

    <script>
        const vscode = acquireVsCodeApi();
        const content = document.getElementById("content");
        const taskInput = document.getElementById("taskInput");
        const executeBtn = document.getElementById("executeBtn");
        const clearBtn = document.getElementById("clearBtn");
        
        let isLoading = false;

        executeBtn.addEventListener("click", executeTask);
        clearBtn.addEventListener("click", clearUI);
        
        taskInput.addEventListener("keydown", (e) => {
            if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
                executeTask();
            }
        });

        async function executeTask() {
            const task = taskInput.value.trim();
            if (!task || isLoading) return;

            isLoading = true;
            executeBtn.disabled = true;
            content.innerHTML = '<div class="loading">⏳ Executing task...</div>';

            // Request selected code from extension
            vscode.postMessage({ command: "getSelectedCode" });
        }

        function clearUI() {
            content.innerHTML = "";
            taskInput.value = "";
            taskInput.focus();
        }

        // Handle messages from extension
        window.addEventListener("message", (event) => {
            const message = event.data;

            if (message.command === "executeResponse") {
                displayResponse(message.data);
                isLoading = false;
                executeBtn.disabled = false;
            } else if (message.command === "selectedCode") {
                executeWithCode(message.code);
            }
        });

        async function executeWithCode(code) {
            const task = taskInput.value.trim();
            
            try {
                const response = await fetch("http://localhost:5000/api/agent/execute", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        task,
                        selected_code: code || undefined,
                    }),
                });

                if (!response.ok) throw new Error(\`API error: \${response.statusText}\`);
                
                const data = await response.json();
                
                // Send response back to extension
                vscode.postMessage({
                    command: "agentResponse",
                    data: data,
                });
                
                displayResponse(data);
            } catch (error) {
                const errorMsg = error instanceof Error ? error.message : String(error);
                content.innerHTML = \`<div class="error">❌ \${errorMsg}</div>\`;
                console.error(error);
            } finally {
                isLoading = false;
                executeBtn.disabled = false;
            }
        }

        function displayResponse(data) {
            let html = "";

            // Plan
            if (data.plan && data.plan.length > 0) {
                html += '<div class="section">';
                html += '<div class="section-title">📋 PLAN</div>';
                data.plan.forEach((step) => {
                    html += \`<div class="item plan-item">\${step.step}. \${step.description}</div>\`;
                });
                html += "</div>";
            }

            // Actions
            if (data.actions && data.actions.length > 0) {
                html += '<div class="section">';
                html += '<div class="section-title">⚙️ ACTIONS</div>';
                data.actions.forEach((action) => {
                    const details = action.path || action.command || action.code || "";
                    html += \`<div class="item action-item">\${action.type} - \${details.substring(0, 50)}</div>\`;
                });
                html += "</div>";
            }

            // Results
            if (data.results && data.results.length > 0) {
                html += '<div class="section">';
                html += '<div class="section-title">✅ RESULTS</div>';
                data.results.forEach((result) => {
                    const success = !result.error;
                    const output = result.output ? result.output.substring(0, 100) : "OK";
                    html += \`<div class="item result-item \${success ? "" : "error"}">\${result.type}: \${success ? "✓" : "✗"} \${output}</div>\`;
                });
                html += "</div>";
            }

            // Stats
            if (data.success !== undefined) {
                html += \`<div class="stats">⏱️ \${data.execution_time}s | Actions: \${data.actions_count} | Status: \${data.success ? '<span class="success">✅ Success</span>' : '<span style="color: var(--vscode-terminal-ansiRed)">❌ Failed</span>'}</div>\`;
            }

            // Error
            if (data.error) {
                html = \`<div class="error">❌ \${data.error}</div>\`;
            }

            content.innerHTML = html || "<div>No response</div>";
        }
    </script>
</body>
</html>`;
}
