import * as vscode from "vscode";
import { callAgent, setBackendUrl, getBackendUrl } from "./api/backend-api";
import { getWebviewContent } from "./webview/chat";

let sidebarWebview: vscode.Webview | null = null;
let selectedModel = "local";

export function activate(context: vscode.ExtensionContext) {
	// Initialize settings
	selectedModel = vscode.workspace.getConfiguration("dcode").get("model") as string || "local";
	const backendUrl = vscode.workspace.getConfiguration("dcode").get("backendURL") as string;
	if (backendUrl) {
		setBackendUrl(backendUrl);
	}
	vscode.window.showInformationMessage(
		`✅ DCODE initialized - Backend: ${getBackendUrl()}, Model: ${selectedModel}`
	);

	// Command: Send selected code to AI
	const sendToAICmd = vscode.commands.registerCommand("dcode.sendToAI", async () => {
		const editor = vscode.window.activeTextEditor;
		if (!editor) {
			vscode.window.showWarningMessage("No active editor");
			return;
		}

		const selectedText = editor.document.getText(editor.selection);
		const code = selectedText || editor.document.getText();

		if (!code.trim()) {
			vscode.window.showWarningMessage("No code selected or found");
			return;
		}

		await processWithAgent(code, "Analyze this code");
	});

	// Command: Switch model
	const switchModelCmd = vscode.commands.registerCommand("dcode.switchModel", async () => {
		const models = ["local", "ollama", "gemini", "openai"];
		const choice = await vscode.window.showQuickPick(models, {
			placeHolder: `Current model: ${selectedModel}`,
		});

		if (choice) {
			selectedModel = choice;
			await vscode.workspace.getConfiguration("dcode").update("model", choice, vscode.ConfigurationTarget.Global);
			vscode.window.showInformationMessage(`✅ Model switched to: ${choice}`);
			sidebarWebview?.postMessage({ command: "modelChanged", model: choice });
		}
	});

	// Sidebar Webview
	const provider = new ChatWebviewProvider(context.extensionUri);
	const sidebarView = vscode.window.registerWebviewViewProvider("dcode.sidebar", provider);

	context.subscriptions.push(sendToAICmd, switchModelCmd, sidebarView);
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
		sidebarWebview = webviewView.webview;

		webviewView.webview.onDidReceiveMessage((message) => {
			if (message.command === "sendMessage") {
				processWithAgent(message.text, message.text, webviewView.webview);
			} else if (message.command === "modelChange") {
				selectedModel = message.model;
				vscode.workspace.getConfiguration("dcode").update("model", message.model, vscode.ConfigurationTarget.Global);
			}
		});
	}
}

async function processWithAgent(
	userInput: string,
	taskDescription: string,
	webview?: vscode.Webview
) {
	try {
		const response = await callAgent({
			task: taskDescription,
			code: userInput,
			model: selectedModel,
		});

		const targetWebview = webview || sidebarWebview;
		if (targetWebview) {
			if (response.success) {
				const summary = response.result || `Executed ${response.actions.length} actions`;
				targetWebview.postMessage({ type: "response", data: { response: summary, plan: response.plan } });
			} else {
				targetWebview.postMessage({ type: "response", data: { error: response.error || "Unknown error" } });
			}
		} else {
			vscode.window.showInformationMessage((response.result || "Task completed").substring(0, 500));
		}
	} catch (error: any) {
		const errorMsg = error.message || "Connection to backend failed";
		const targetWebview = webview || sidebarWebview;
		if (targetWebview) {
			targetWebview.postMessage({ type: "response", data: { error: errorMsg } });
		} else {
			vscode.window.showErrorMessage(errorMsg);
		}
	}
}

export function deactivate() {}
