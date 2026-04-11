import * as vscode from "vscode";
import { sendCodeToAI, sendMessageToAI } from "./api/openai";
import { getWebviewContent } from "./webview/chat";

let sidebarWebview: vscode.Webview | null = null;

export function activate(context: vscode.ExtensionContext) {
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

		await sendToAI(code, "code");
	});

	// Sidebar Webview
	const provider = new ChatWebviewProvider(context.extensionUri);
	const sidebarView = vscode.window.registerWebviewViewProvider("dcode.sidebar", provider);

	context.subscriptions.push(sendToAICmd, sidebarView);
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
				sendToAI(message.text, "message", webviewView.webview);
			}
		});
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

		const targetWebview = webview || sidebarWebview;
		if (targetWebview) {
			targetWebview.postMessage({ type: "response", data: { response: response.substring(0, 5000) } });
		} else {
			vscode.window.showInformationMessage(response.substring(0, 500));
		}
	} catch (error: any) {
		const errorMsg = error.message || "AI request failed";
		const targetWebview = webview || sidebarWebview;
		if (targetWebview) {
			targetWebview.postMessage({ type: "response", data: { error: errorMsg } });
		} else {
			vscode.window.showErrorMessage(errorMsg);
		}
	}
}

export function deactivate() {}
