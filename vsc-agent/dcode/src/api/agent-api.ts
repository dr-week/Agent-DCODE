import * as vscode from "vscode";

const AGENT_API = "http://localhost:5000/api/agent/execute";

export interface AgentResponse {
	success: boolean;
	task: string;
	plan: Array<{ step: number; description: string }>;
	actions: Array<any>;
	results: Array<any>;
	execution_time: number;
	error?: string;
}

export async function executeAgentTask(task: string, code?: string): Promise<AgentResponse> {
	try {
		const response = await fetch(AGENT_API, {
			method: "POST",
			headers: { "Content-Type": "application/json" },
			body: JSON.stringify({
				task,
				selected_code: code || undefined,
			}),
		});

		if (!response.ok) {
			throw new Error(`API error: ${response.statusText}`);
		}

		return await response.json();
	} catch (error) {
		throw new Error(`Failed to execute task: ${error instanceof Error ? error.message : String(error)}`);
	}
}

export async function applyCodeChanges(results: Array<any>) {
	const edit = new vscode.WorkspaceEdit();

	for (const result of results) {
		if (result.type === "write_file" || result.type === "append_file") {
			const filePath = result.path;
			if (!filePath) continue;

			try {
				// Convert to VS Code URI
				const uri = vscode.Uri.file("/projects/" + filePath);
				const content = result.content || result.output || "";

				if (result.type === "write_file") {
					edit.createFile(uri, { overwrite: true, ignoreIfExists: false });
					edit.insert(uri, new vscode.Position(0, 0), content);
				} else if (result.type === "append_file") {
					// Try to append to existing file
					try {
						const doc = await vscode.workspace.openTextDocument(uri);
						const lastLine = doc.lineCount - 1;
						const lastChar = doc.lineAt(lastLine).text.length;
						edit.insert(uri, new vscode.Position(lastLine, lastChar), "\n" + content);
					} catch {
						// File doesn't exist, create it
						edit.createFile(uri, { overwrite: true });
						edit.insert(uri, new vscode.Position(0, 0), content);
					}
				}
			} catch (error) {
				console.error(`Failed to apply changes to ${filePath}:`, error);
			}
		}
	}

	// Apply all edits
	if (edit.size > 0) {
		await vscode.workspace.applyEdit(edit);
	}
}
