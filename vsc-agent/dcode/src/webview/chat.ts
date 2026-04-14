import * as vscode from "vscode";

export function getWebviewContent(webview: vscode.Webview): string {
	return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="Content-Security-Policy" content="default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline';">
    <title>DCODE AI Chat</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: var(--vscode-editor-background);
            color: var(--vscode-editor-foreground);
            display: flex;
            flex-direction: column;
            height: 100vh;
        }
        
        #messages {
            flex: 1;
            overflow-y: auto;
            padding: 16px;
            display: flex;
            flex-direction: column;
            gap: 12px;
        }
        
        .message {
            padding: 10px 12px;
            border-radius: 6px;
            word-wrap: break-word;
            font-size: 13px;
            line-height: 1.4;
        }
        
        .message.user {
            background: var(--vscode-inputValidation-infoBackground);
            color: var(--vscode-inputValidation-infoForeground);
            align-self: flex-end;
            max-width: 80%;
        }
        
        .message.assistant {
            background: var(--vscode-inputValidation-warningBackground);
            color: var(--vscode-inputValidation-warningForeground);
            align-self: flex-start;
            max-width: 80%;
        }
        
        .message.error {
            background: var(--vscode-inputValidation-errorBackground);
            color: var(--vscode-inputValidation-errorForeground);
        }
        
        .message.loading {
            font-style: italic;
            opacity: 0.7;
        }
        
        #inputContainer {
            padding: 12px;
            border-top: 1px solid var(--vscode-panel-border);
            display: flex;
            gap: 8px;
        }
        
        #userInput {
            flex: 1;
            padding: 8px 12px;
            background: var(--vscode-input-background);
            color: var(--vscode-input-foreground);
            border: 1px solid var(--vscode-input-border);
            border-radius: 4px;
            font-size: 13px;
            font-family: inherit;
        }
        
        #userInput:focus {
            outline: none;
            border-color: var(--vscode-focusBorder);
        }
        
        button {
            padding: 8px 16px;
            background: var(--vscode-button-background);
            color: var(--vscode-button-foreground);
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 13px;
            font-weight: 500;
        }
        
        button:hover {
            background: var(--vscode-button-hoverBackground);
        }
        
        button:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }

        #modelContainer {
            padding: 8px 12px;
            border-bottom: 1px solid var(--vscode-panel-border);
            display: flex;
            gap: 8px;
            align-items: center;
        }

        #modelSelect {
            padding: 4px 8px;
            background: var(--vscode-input-background);
            color: var(--vscode-input-foreground);
            border: 1px solid var(--vscode-input-border);
            border-radius: 4px;
            font-size: 12px;
            cursor: pointer;
        }

        .model-label {
            font-size: 12px;
            opacity: 0.8;
        }
    </style>
</head>
<body>
    <div id="modelContainer">
        <span class="model-label">Model:</span>
        <select id="modelSelect">
            <option value="local">Local (Ollama)</option>
            <option value="ollama">Ollama</option>
            <option value="gemini">Gemini</option>
            <option value="openai">OpenAI</option>
        </select>
    </div>
    <div id="messages"></div>
    <div id="inputContainer">
        <input type="text" id="userInput" placeholder="Ask me anything..." />
        <button id="sendBtn">Send</button>
    </div>

    <script>
        const vscode = acquireVsCodeApi();
        const messagesDiv = document.getElementById('messages');
        const userInput = document.getElementById('userInput');
        const sendBtn = document.getElementById('sendBtn');
        const modelSelect = document.getElementById('modelSelect');

        function addMessage(text, type = 'assistant') {
            const msg = document.createElement('div');
            msg.className = \`message \${type}\`;
            msg.textContent = text;
            messagesDiv.appendChild(msg);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }

        function sendMessage() {
            const text = userInput.value.trim();
            if (!text) return;

            addMessage(text, 'user');
            userInput.value = '';
            sendBtn.disabled = true;
            addMessage('Thinking...', 'loading');

            vscode.postMessage({ command: 'sendMessage', text });
        }

        modelSelect.addEventListener('change', (e) => {
            vscode.postMessage({ command: 'modelChange', model: e.target.value });
        });

        sendBtn.addEventListener('click', sendMessage);
        userInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') sendMessage();
        });

        window.addEventListener('message', (event) => {
            const { type, data } = event.data;

            if (type === 'response') {
                const loading = messagesDiv.querySelector('.message.loading');
                if (loading) loading.remove();

                sendBtn.disabled = false;
                if (data.error) {
                    addMessage(\`Error: \${data.error}\`, 'error');
                } else {
                    addMessage(data.response, 'assistant');
                }
            } else if (event.data.command === 'modelChanged') {
                modelSelect.value = event.data.model;
            }
        });
    </script>
</body>
</html>`;
}
