import * as vscode from "vscode";
import { callAgent, setBackendUrl, getBackendUrl } from "./api/backend-api";
import { ensureLocalModelRunning, restartModel } from "./utils/process-manager";
import { getWebviewContent } from "./webview/chat";

let sidebarWebview: vscode.Webview | null = null;
let selectedModel = "local";
let autoStartModel = false;

export function activate(context: vscode.ExtensionContext) {
	// Initialize settings
	selectedModel = vscode.workspace.getConfiguration("dcode").get("model") as string || "local";
	autoStartModel = vscode.workspace.getConfiguration("dcode").get("autoStartModel") as boolean || false;
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

	// Command: Start DCODE System (Orchestrator)
	const startSystemCmd = vscode.commands.registerCommand("dcode.startSystem", async () => {
		const output = vscode.window.createOutputChannel("DCODE Orchestrator");
		output.show();
		output.appendLine("🚀 Starting DCODE System Services...");
		output.appendLine("=====================================");

		try {
			const spawn = require("child_process").spawn;
			const python = process.platform === "win32" ? "python" : "python3";

			// Get workspace root
			const workspaceFolders = vscode.workspace.workspaceFolders;
			if (!workspaceFolders) {
				output.appendLine("[ERROR] No workspace folder found");
				vscode.window.showErrorMessage("No workspace folder found");
				return;
			}

			const workspaceRoot = workspaceFolders[0].uri.fsPath;
			const orchestratorScript = `${workspaceRoot}/dcode_orchestrator.py`;

			const proc = spawn(python, [orchestratorScript, "start", "--health-check"], {
				cwd: workspaceRoot,
			});

			let isRunning = true;

			proc.stdout.on("data", (data: Buffer) => {
				const message = data.toString().trim();
				if (message) {
					output.appendLine(message);
				}
			});

			proc.stderr.on("data", (data: Buffer) => {
				const message = data.toString().trim();
				if (message) {
					output.appendLine(`[WARN] ${message}`);
				}
			});

			proc.on("close", (code: number) => {
				if (isRunning) {
					isRunning = false;
					output.appendLine(`=====================================`);
					output.appendLine(`Services stopped (exit code: ${code})`);
				}
			});

			vscode.window.showInformationMessage("✅ DCODE Services starting... Check output panel for details");
		} catch (error: any) {
			output.appendLine(`[ERROR] Failed to start orchestrator: ${error.message}`);
			vscode.window.showErrorMessage(`Failed to start orchestrator: ${error.message}`);
		}
	});

	// Command: Stop DCODE System
	const stopSystemCmd = vscode.commands.registerCommand("dcode.stopSystem", async () => {
		const output = vscode.window.createOutputChannel("DCODE Orchestrator");
		output.show();
		output.appendLine("🛑 Stopping DCODE System Services...");

		try {
			const spawn = require("child_process").spawn;
			const python = process.platform === "win32" ? "python" : "python3";

			const workspaceFolders = vscode.workspace.workspaceFolders;
			if (!workspaceFolders) {
				output.appendLine("[ERROR] No workspace folder found");
				return;
			}

			const workspaceRoot = workspaceFolders[0].uri.fsPath;
			const orchestratorScript = `${workspaceRoot}/dcode_orchestrator.py`;

			const proc = spawn(python, [orchestratorScript, "stop"], {
				cwd: workspaceRoot,
			});

			proc.stdout.on("data", (data: Buffer) => {
				const message = data.toString().trim();
				if (message) {
					output.appendLine(message);
				}
			});

			proc.on("close", (code: number) => {
				output.appendLine(`Services stopped (exit code: ${code})`);
				vscode.window.showInformationMessage("✅ DCODE Services stopped");
			});
		} catch (error: any) {
			vscode.window.showErrorMessage(`Failed to stop services: ${error.message}`);
		}
	});

	// Command: Check System Status
	const statusSystemCmd = vscode.commands.registerCommand("dcode.statusSystem", async () => {
		const output = vscode.window.createOutputChannel("DCODE Orchestrator");
		output.show();
		output.appendLine("📊 Checking DCODE System Status...");
		output.appendLine("=====================================");

		try {
			const spawn = require("child_process").spawn;
			const python = process.platform === "win32" ? "python" : "python3";

			const workspaceFolders = vscode.workspace.workspaceFolders;
			if (!workspaceFolders) {
				output.appendLine("[ERROR] No workspace folder found");
				return;
			}

			const workspaceRoot = workspaceFolders[0].uri.fsPath;
			const orchestratorScript = `${workspaceRoot}/dcode_orchestrator.py`;

			const proc = spawn(python, [orchestratorScript, "status"], {
				cwd: workspaceRoot,
			});

			proc.stdout.on("data", (data: Buffer) => {
				output.appendLine(data.toString());
			});

			proc.on("close", (code: number) => {
				output.appendLine("=====================================");
			});
		} catch (error: any) {
			vscode.window.showErrorMessage(`Failed to check status: ${error.message}`);
		}
	});

	// Sidebar Webview
	const provider = new ChatWebviewProvider(context.extensionUri);
	const sidebarView = vscode.window.registerWebviewViewProvider("dcode.sidebar", provider);

	context.subscriptions.push(
		sendToAICmd,
		switchModelCmd,
		startSystemCmd,
		stopSystemCmd,
		statusSystemCmd,
		sidebarView
	);
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
		// Ensure local model is running if needed
		if (selectedModel === "local" || selectedModel === "ollama") {
			const modelReady = await ensureLocalModelRunning(selectedModel, autoStartModel);
			if (!modelReady) {
				const errorMsg = "Local model is not running";
				const targetWebview = webview || sidebarWebview;
				if (targetWebview) {
					targetWebview.postMessage({ type: "response", data: { error: errorMsg } });
				} else {
					vscode.window.showErrorMessage(errorMsg);
				}
				return;
			}
		}

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
		// Attempt to restart model if connection failed
		if ((selectedModel === "local" || selectedModel === "ollama") && errorMsg.includes("Connection")) {
			console.log("[Extension] Attempting to restart model after connection failure");
			await restartModel();
		}
		if (targetWebview) {
			targetWebview.postMessage({ type: "response", data: { error: errorMsg } });
		} else {
			vscode.window.showErrorMessage(errorMsg);
		}
	}
}

export function deactivate() {}
