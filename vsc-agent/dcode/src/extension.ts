import * as vscode from "vscode";
import { sendCodeToAI, sendMessageToAI } from "./api/openai";
import { executeAgentTask, applyCodeChanges } from "./api/agent-api";
import { getWebviewContent } from "./webview/chat";
import { getAgentWebviewContent } from "./webview/agent";

let chatWebview: vscode.Webview | null = null;
let agentWebview: vscode.Webview | null = null;

// Fallback HTML if webview content generation fails
const FALLBACK_HTML = `<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta http-equiv="Content-Security-Policy" content="default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline';">
  <style>
    body { font-family: sans-serif; padding: 20px; background: #1e1e1e; color: #e0e0e0; }
    .warning { background: #ff6b6b; padding: 10px; border-radius: 4px; margin-bottom: 10px; }
    input { padding: 8px; width: 100%; margin-bottom: 10px; background: #2d2d2d; color: #e0e0e0; border: 1px solid #3e3e3e; }
    button { padding: 8px 16px; background: #007acc; color: white; border: none; cursor: pointer; border-radius: 4px; }
    button:hover { background: #005a9e; }
  </style>
</head>
<body>
  <h2>DCODE AI Chat</h2>
  <div class="warning">✅ Fallback UI active - main HTML generator may have an issue</div>
  <div id="messages" style="height: 300px; overflow-y: auto; border: 1px solid #3e3e3e; padding: 10px; margin-bottom: 10px;"></div>
  <input type="text" id="userInput" placeholder="Ask me anything..." />
  <button onclick="sendMsg()">Send</button>
  <script>
    const msgs = document.getElementById('messages');
    const inp = document.getElementById('userInput');
    function sendMsg() {
      const text = inp.value;
      if (!text) return;
      const div = document.createElement('div');
      div.style.marginBottom = '10px';
      div.textContent = '👤 ' + text;
      msgs.appendChild(div);
      inp.value = '';
      msgs.scrollTop = msgs.scrollHeight;
    }
    inp.addEventListener('keypress', (e) => e.key === 'Enter' && sendMsg());
  </script>
</body>
</html>`;

export function activate(context: vscode.ExtensionContext) {
	console.log("🚀 DCODE extension activated");

	// Chat Mode
	const chatProvider = new ChatWebviewProvider(context.extensionUri);
	const chatView = vscode.window.registerWebviewViewProvider("dcode.sidebar", chatProvider);

	// Agent Mode
	const agentCmd = vscode.commands.registerCommand("dcode.agent", async () => {
		const panel = vscode.window.createWebviewPanel("agentMode", "DCODE Agent", vscode.ViewColumn.Beside, {
			enableScripts: true,
			localResourceRoots: [context.extensionUri],
		});

		try {
			const agentHtml = getAgentWebviewContent(panel.webview);
			if (!agentHtml || agentHtml.length === 0) {
				console.error("❌ Agent HTML is empty, using fallback");
				panel.webview.html = FALLBACK_HTML;
			} else {
				panel.webview.html = agentHtml;
				console.log("✅ Agent webview HTML set");
			}
		} catch (error: any) {
			console.error("❌ Error generating agent HTML:", error.message);
			panel.webview.html = FALLBACK_HTML;
		}

		agentWebview = panel.webview;
		panel.webview.onDidReceiveMessage((message) => handleAgentMessage(message, panel.webview));
	});

	context.subscriptions.push(agentCmd, chatView);
	console.log("✅ DCODE commands registered");
}

class ChatWebviewProvider implements vscode.WebviewViewProvider {
	constructor(private extensionUri: vscode.Uri) {}

	resolveWebviewView(
		webviewView: vscode.WebviewView,
		_context: vscode.WebviewViewResolveContext,
		_token: vscode.CancellationToken
	) {
		console.log("📍 Resolving Chat webview...");

		webviewView.webview.options = {
			enableScripts: true,
			localResourceRoots: [this.extensionUri],
		};

		try {
			const html = getWebviewContent(webviewView.webview);
			if (!html || html.length === 0) {
				console.error("❌ HTML content is empty, using fallback!");
				webviewView.webview.html = FALLBACK_HTML;
			} else {
				webviewView.webview.html = html;
				console.log("✅ Chat webview HTML set successfully");
			}
		} catch (error: any) {
			console.error("❌ Error generating HTML, using fallback:", error.message);
			webviewView.webview.html = FALLBACK_HTML;
		}
		chatWebview = webviewView.webview;

		webviewView.webview.onDidReceiveMessage((message) => {
			console.log("📨 Message from webview:", message.command);
			if (message.command === "sendMessage") {
				sendToAI(message.text, "message", webviewView.webview);
			}
		});
	}
}

async function handleAgentMessage(message: any, webview: vscode.Webview) {
	console.log("👁️ Agent message:", message.command);

	if (message.command === "getSelectedCode") {
		const editor = vscode.window.activeTextEditor;
		const code = editor ? editor.document.getText(editor.selection) || editor.document.getText() : undefined;
		console.log("📦 Sending selected code:", code ? `${code.length} chars` : "none");
		webview.postMessage({ command: "selectedCode", code });
	} else if (message.command === "agentResponse") {
		const response = message.data;
		if (response.success && response.results) {
			try {
				await applyCodeChanges(response.results);
				vscode.window.showInformationMessage("✅ Task completed. Files updated.");
			} catch (error: any) {
				console.error("Failed to apply changes:", error);
			}
		}
	}
}

async function sendToAI(userInput: string, type: "code" | "message", webview?: vscode.Webview) {
	const apiKey = vscode.workspace.getConfiguration("dcode").get("apiKey") as string;

	if (!apiKey) {
		const msg = "OpenAI API key not configured. Set it in settings (dcode.apiKey)";
		console.error("❌", msg);
		vscode.window.showErrorMessage(msg);
		if (webview) {
			webview.postMessage({ type: "response", data: { error: msg } });
		}
		return;
	}

	try {
		console.log(`🔄 Sending ${type} to AI...`);
		const response =
			type === "code" ? await sendCodeToAI(userInput, apiKey) : await sendMessageToAI(userInput, apiKey);

		const targetWebview = webview || chatWebview;
		if (targetWebview) {
			console.log("✅ Response received, sending to webview");
			targetWebview.postMessage({ type: "response", data: { response: response.substring(0, 5000) } });
		} else {
			console.warn("⚠️ No webview available, showing message");
			vscode.window.showInformationMessage(response.substring(0, 500));
		}
	} catch (error: any) {
		const errorMsg = error.message || "AI request failed";
		console.error("❌ AI error:", errorMsg);
		const targetWebview = webview || chatWebview;
		if (targetWebview) {
			targetWebview.postMessage({ type: "response", data: { error: errorMsg } });
		} else {
			vscode.window.showErrorMessage(errorMsg);
		}
	}
}

export function deactivate() {}
