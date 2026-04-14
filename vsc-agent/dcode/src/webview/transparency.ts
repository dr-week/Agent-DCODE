import * as vscode from "vscode";

export function getTransparencyWebviewContent(webview: vscode.Webview): string {
	return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="Content-Security-Policy" content="default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline';">
    <title>Agent Transparency</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, monospace;
            background: var(--vscode-editor-background);
            color: var(--vscode-editor-foreground);
            display: flex;
            flex-direction: column;
            height: 100vh;
            overflow: hidden;
        }
        
        /* Header */
        #header {
            padding: 12px 16px;
            border-bottom: 1px solid var(--vscode-panel-border);
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: var(--vscode-editor-background);
            flex-shrink: 0;
        }
        
        .header-title {
            font-size: 14px;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .status-indicator {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            display: inline-block;
        }
        
        .status-indicator.idle {
            background: var(--vscode-terminal-ansiGray);
        }
        
        .status-indicator.running {
            background: var(--vscode-terminal-ansiYellow);
            animation: pulse 1s infinite;
        }
        
        .status-indicator.completed {
            background: var(--vscode-terminal-ansiGreen);
        }
        
        .status-indicator.error {
            background: var(--vscode-terminal-ansiRed);
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        .header-stats {
            display: flex;
            gap: 16px;
            font-size: 12px;
            opacity: 0.7;
        }
        
        .stat-item {
            display: flex;
            align-items: center;
            gap: 4px;
        }
        
        /* Main Container */
        #container {
            flex: 1;
            display: grid;
            grid-template-columns: 1fr 1fr;
            grid-template-rows: 1fr 1fr;
            gap: 0;
            overflow: hidden;
        }
        
        .panel {
            border-right: 1px solid var(--vscode-panel-border);
            border-bottom: 1px solid var(--vscode-panel-border);
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }
        
        .panel:nth-child(2n) {
            border-right: none;
        }
        
        .panel:nth-last-child(-n+2) {
            border-bottom: none;
        }
        
        /* Panel Headers */
        .panel-header {
            padding: 8px 12px;
            border-bottom: 1px solid var(--vscode-panel-border);
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            background: var(--vscode-terminal-background);
            flex-shrink: 0;
        }
        
        #thinkingHeader { color: var(--vscode-terminal-ansiCyan); }
        #actionsHeader { color: var(--vscode-terminal-ansiYellow); }
        #statusHeader { color: var(--vscode-terminal-ansiGreen); }
        #errorsHeader { color: var(--vscode-terminal-ansiRed); }
        
        /* Panel Content */
        .panel-content {
            flex: 1;
            overflow-y: auto;
            padding: 0;
            font-size: 12px;
            line-height: 1.5;
        }
        
        .panel-item {
            padding: 8px 12px;
            border-bottom: 1px solid rgba(128, 128, 128, 0.2);
        }
        
        .panel-item:last-child {
            border-bottom: none;
        }
        
        .item-label {
            font-weight: 600;
            margin-bottom: 2px;
        }
        
        .item-value {
            opacity: 0.8;
            word-break: break-word;
        }
        
        /* Thinking Panel */
        .thinking-step {
            display: flex;
            gap: 8px;
            align-items: flex-start;
        }
        
        .step-number {
            font-weight: bold;
            color: var(--vscode-terminal-ansiCyan);
            min-width: 20px;
            margin-top: 2px;
        }
        
        .step-content {
            flex: 1;
        }
        
        /* Actions Panel */
        .action-item {
            display: flex;
            gap: 12px;
            align-items: flex-start;
        }
        
        .action-icon {
            min-width: 16px;
            text-align: center;
            margin-top: 2px;
            font-size: 10px;
        }
        
        .action-icon.pending::before {
            content: "◯";
            color: var(--vscode-terminal-ansiGray);
        }
        
        .action-icon.running::before {
            content: "⟳";
            color: var(--vscode-terminal-ansiYellow);
            animation: spin 1s linear infinite;
        }
        
        .action-icon.completed::before {
            content: "✓";
            color: var(--vscode-terminal-ansiGreen);
        }
        
        .action-icon.error::before {
            content: "✕";
            color: var(--vscode-terminal-ansiRed);
        }
        
        @keyframes spin {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
        }
        
        .action-content {
            flex: 1;
            min-width: 0;
        }
        
        .action-type {
            font-weight: 600;
            color: var(--vscode-terminal-ansiYellow);
        }
        
        .action-desc {
            opacity: 0.8;
            font-size: 11px;
            margin-top: 2px;
        }
        
        .action-output {
            background: var(--vscode-input-background);
            padding: 4px 8px;
            border-radius: 2px;
            font-size: 10px;
            margin-top: 4px;
            max-height: 60px;
            overflow: hidden;
            text-overflow: ellipsis;
            opacity: 0.7;
        }
        
        /* Status Panel */
        .status-row {
            display: flex;
            justify-content: space-between;
            gap: 12px;
        }
        
        .status-label {
            opacity: 0.6;
            flex: 0 0 auto;
        }
        
        .status-value {
            font-weight: 600;
            flex: 1 1 auto;
            text-align: right;
        }
        
        .progress-bar {
            width: 100%;
            height: 3px;
            background: var(--vscode-progressBar-background);
            border-radius: 1px;
            margin-top: 4px;
            overflow: hidden;
        }
        
        .progress-fill {
            height: 100%;
            background: var(--vscode-terminal-ansiGreen);
            width: 0%;
            transition: width 0.3s ease;
        }
        
        /* Errors Panel */
        .error-item {
            background: var(--vscode-inputValidation-errorBackground);
            padding: 8px 12px;
            border-left: 3px solid var(--vscode-terminal-ansiRed);
            border-radius: 2px;
        }
        
        .error-message {
            font-weight: 600;
            color: var(--vscode-terminal-ansiRed);
            margin-bottom: 2px;
        }
        
        .error-context {
            font-size: 11px;
            opacity: 0.7;
        }
        
        .error-time {
            font-size: 10px;
            opacity: 0.5;
            margin-top: 2px;
        }
        
        /* Empty State */
        .empty-state {
            display: flex;
            align-items: center;
            justify-content: center;
            height: 100%;
            opacity: 0.5;
            font-size: 11px;
            text-align: center;
            padding: 12px;
        }
        
        /* Scrollbar */
        .panel-content::-webkit-scrollbar {
            width: 8px;
        }
        
        .panel-content::-webkit-scrollbar-track {
            background: var(--vscode-editor-background);
        }
        
        .panel-content::-webkit-scrollbar-thumb {
            background: var(--vscode-scrollbarSlider-background);
            border-radius: 4px;
        }
        
        .panel-content::-webkit-scrollbar-thumb:hover {
            background: var(--vscode-scrollbarSlider-hoverBackground);
        }
    </style>
</head>
<body>
    <div id="header">
        <div class="header-title">
            <span class="status-indicator idle" id="statusIndicator"></span>
            <span>Agent Transparency</span>
        </div>
        <div class="header-stats">
            <div class="stat-item">
                <span>Progress:</span>
                <span id="progressStat">0%</span>
            </div>
            <div class="stat-item">
                <span>Time:</span>
                <span id="timeStat">0s</span>
            </div>
        </div>
    </div>
    
    <div id="container">
        <!-- THINKING Panel -->
        <div class="panel">
            <div class="panel-header" id="thinkingHeader">□ Thinking</div>
            <div class="panel-content" id="thinkingContent">
                <div class="empty-state">No plan yet...</div>
            </div>
        </div>
        
        <!-- ACTIONS Panel -->
        <div class="panel">
            <div class="panel-header" id="actionsHeader">▶ Actions</div>
            <div class="panel-content" id="actionsContent">
                <div class="empty-state">No actions executed</div>
            </div>
        </div>
        
        <!-- STATUS Panel -->
        <div class="panel">
            <div class="panel-header" id="statusHeader">● Status</div>
            <div class="panel-content" id="statusContent">
                <div class="panel-item">
                    <div class="status-row">
                        <span class="status-label">State:</span>
                        <span class="status-value" id="statusValue">idle</span>
                    </div>
                    <div class="status-row">
                        <span class="status-label">Current Step:</span>
                        <span class="status-value" id="stepValue">—</span>
                    </div>
                    <div class="status-row">
                        <span class="status-label">Progress:</span>
                        <span class="status-value" id="progressValue">0%</span>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill" id="progressFill"></div>
                    </div>
                    <div class="status-row" style="margin-top: 8px;">
                        <span class="status-label">Elapsed:</span>
                        <span class="status-value" id="elapsedValue">0s</span>
                    </div>
                    <div class="status-row">
                        <span class="status-label">Est. Total:</span>
                        <span class="status-value" id="estimateValue">—</span>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- ERRORS Panel -->
        <div class="panel">
            <div class="panel-header" id="errorsHeader">⚠ Errors</div>
            <div class="panel-content" id="errorsContent">
                <div class="empty-state">No errors</div>
            </div>
        </div>
    </div>

    <script>
        const vscode = acquireVsCodeApi();
        let currentState = null;
        let updateInterval = null;
        
        // Update interval: poll backend for state every 500ms
        function startPolling() {
            updateInterval = setInterval(updateFromBackend, 500);
        }
        
        function stopPolling() {
            if (updateInterval) clearInterval(updateInterval);
        }
        
        async function updateFromBackend() {
            try {
                const response = await fetch('http://localhost:5000/api/transparency/state');
                const data = await response.json();
                updateUI(data.state);
            } catch (e) {
                // Backend not available yet
            }
        }
        
        function updateUI(state) {
            if (!state) return;
            currentState = state;
            
            // Update header
            updateStatusIndicator(state.status);
            document.getElementById('progressStat').textContent = state.progress + '%';
            document.getElementById('timeStat').textContent = formatTime(state.elapsed_time);
            
            // Update panels
            updateThinkingPanel(state.plan);
            updateActionsPanel(state.actions);
            updateStatusPanel(state);
            updateErrorsPanel(state.errors);
        }
        
        function updateStatusIndicator(status) {
            const indicator = document.getElementById('statusIndicator');
            indicator.classList.remove('idle', 'running', 'completed', 'error');
            
            if (status.includes('error') || status === 'failed') {
                indicator.classList.add('error');
            } else if (status === 'completed') {
                indicator.classList.add('completed');
            } else if (status === 'idle') {
                indicator.classList.add('idle');
            } else {
                indicator.classList.add('running');
            }
        }
        
        function updateThinkingPanel(plan) {
            const content = document.getElementById('thinkingContent');
            
            if (!plan || plan.length === 0) {
                content.innerHTML = '<div class="empty-state">No plan yet...</div>';
                return;
            }
            
            let html = '';
            plan.forEach((step, idx) => {
                html += \`
                    <div class="panel-item">
                        <div class="thinking-step">
                            <span class="step-number">\${idx + 1}.</span>
                            <div class="step-content">
                                <div class="item-label">\${escapeHtml(step)}</div>
                            </div>
                        </div>
                    </div>
                \`;
            });
            
            content.innerHTML = html;
        }
        
        function updateActionsPanel(actions) {
            const content = document.getElementById('actionsContent');
            
            if (!actions || actions.length === 0) {
                content.innerHTML = '<div class="empty-state">No actions executed</div>';
                return;
            }
            
            let html = '';
            actions.forEach((action, idx) => {
                const statusClass = action.status || 'pending';
                const itemHtml = \`
                    <div class="panel-item">
                        <div class="action-item">
                            <div class="action-icon \${statusClass}"></div>
                            <div class="action-content">
                                <div class="action-type">\${escapeHtml(action.type)}</div>
                                <div class="action-desc">\${escapeHtml(action.description || action.type)}</div>
                                \${action.output ? \`<div class="action-output">\${escapeHtml(action.output)}</div>\` : ''}
                            </div>
                        </div>
                    </div>
                \`;
                html += itemHtml;
            });
            
            content.innerHTML = html;
        }
        
        function updateStatusPanel(state) {
            document.getElementById('statusValue').textContent = formatStatus(state.status);
            document.getElementById('stepValue').textContent = 
                state.current_step ? state.current_step.name : '—';
            document.getElementById('progressValue').textContent = state.progress + '%';
            document.getElementById('progressFill').style.width = state.progress + '%';
            document.getElementById('elapsedValue').textContent = formatTime(state.elapsed_time);
            
            if (state.estimated_time > 0) {
                document.getElementById('estimateValue').textContent = formatTime(state.estimated_time);
            }
        }
        
        function updateErrorsPanel(errors) {
            const content = document.getElementById('errorsContent');
            
            if (!errors || errors.length === 0) {
                content.innerHTML = '<div class="empty-state">No errors</div>';
                return;
            }
            
            let html = '';
            errors.forEach(error => {
                const time = new Date(error.timestamp).toLocaleTimeString();
                html += \`
                    <div class="panel-item">
                        <div class="error-item">
                            <div class="error-message">\${escapeHtml(error.message)}</div>
                            \${error.context ? \`<div class="error-context">Context: \${escapeHtml(error.context)}</div>\` : ''}
                            \${error.step ? \`<div class="error-context">Step: \${escapeHtml(error.step)}</div>\` : ''}
                            <div class="error-time">\${time}</div>
                        </div>
                    </div>
                \`;
            });
            
            content.innerHTML = html;
        }
        
        function formatTime(seconds) {
            if (!seconds) return '0s';
            if (seconds < 60) return Math.round(seconds) + 's';
            const mins = Math.floor(seconds / 60);
            const secs = Math.round(seconds % 60);
            return \`\${mins}m \${secs}s\`;
        }
        
        function formatStatus(status) {
            const map = {
                'idle': 'Idle',
                'planning': 'Planning...',
                'planned': 'Planned',
                'executing_step_0': 'Executing...',
                'error': 'Error',
                'failed': 'Failed',
                'completed': 'Completed'
            };
            
            for (let [key, val] of Object.entries(map)) {
                if (status.includes(key)) return val;
            }
            
            return status.replace(/_/g, ' ').split(' ').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
        }
        
        function escapeHtml(text) {
            if (!text) return '';
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
        
        // Start polling when panel loads
        startPolling();
        
        // Clean up on unload
        window.addEventListener('beforeunload', () => {
            stopPolling();
        });
    </script>
</body>
</html>
	`;
}
