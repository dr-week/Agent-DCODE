import * as vscode from "vscode";
import { sendCodeToAI, sendMessageToAI } from "./api/openai";
import { executeAgentTask, applyCodeChanges } from "./api/agent-api";
import { getWebviewContent } from "./webview/chat";
import { getAgentWebviewContent } from "./webview/agent";

let chatWebview: vscode.Webview | null = null;
let agentWebview: vscode.Webview | null = null;

export function activate(context: vscode.ExtensionContext) {
	// Chat Mode
	const chatProvider = new ChatWebviewProvider(context.extensionUri);
	const chatView = vscode.window.registerWebviewViewProvider("dcode.sidebar", chatProvider);

	// Agent Mode
	const agentCmd = vscode.commands.registerCommand("dcode.agent", async () => {
		const panel = vscode.window.createWebviewPanel("agentMode", "DCODE Agent", vscode.ViewColumn.Beside, {
			enableScripts: true,
			localResourceRoots: [context.extensionUri],
		});

		panel.webview.html = getAgentWebviewContent(panel.webview);
		agentWebview = panel.webview;

		panel.webview.onDidReceiveMessage((message) => handleAgentMessage(message, panel.webview));
	});

	context.subscriptions.push(agentCmd, chatView);
}

class ChatWebviewProvider implements vscode.WebviewViewProvider {
	constructor(private extensionUri: vscode.Uri) {}

	resolveWebviewView(
		webviewView: vscode.WebviewView,
		_context: vscode.WebviewViewResolveContext,
		_token: vscode.CancellationToken
	) {
		webviewView.webview.options = {
			enableScripts: true,
			localResourceRoots: [this.extensionUri],
		};

		webviewView.webview.html = getWebviewContent(webviewView.webview);
		chatWebview = webviewView.webview;

		webviewView.webview.onDidReceiveMessage((message) => {
			if (message.command === "sendMessage") {
				sendToAI(message.text, "message", webviewView.webview);
			}
		});
	}
}

async function handleAgentMessage(message: any, webview: vscode.Webview) {
	if (message.command === "getSelectedCode") {
		const editor = vscode.window.activeTextEditor;
		const code = editor ? editor.document.getText(editor.selection) || editor.document.getText() : undefined;
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
		vscode.window.showErrorMessage(msg);
		if (webview) {
			webview.postMessage({ type: "response", data: { error: msg } });
		}
		return;
	}

	try {
		const response =
			type === "code" ? await sendCodeToAI(userInput, apiKey) : await sendMessageToAI(userInput, apiKey);

		const targetWebview = webview || chatWebview;
		if (targetWebview) {
			targetWebview.postMessage({ type: "response", data: { response: response.substring(0, 5000) } });
		} else {
			vscode.window.showInformationMessage(response.substring(0, 500));
		}
	} catch (error: any) {
		const errorMsg = error.message || "AI request failed";
		const targetWebview = webview || chatWebview;
		if (targetWebview) {
			targetWebview.postMessage({ type: "response", data: { error: errorMsg } });
		} else {
			vscode.window.showErrorMessage(errorMsg);
		}
	}
}

export function deactivate() {}
