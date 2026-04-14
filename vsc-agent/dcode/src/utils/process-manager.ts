/**
 * Local model process manager
 * Handles starting, stopping, and monitoring local AI models (Ollama, etc.)
 */

import { exec, spawn, ChildProcess } from "child_process";
import { platform } from "os";
import * as vscode from "vscode";

interface ProcessConfig {
	name: string;
	port: number;
	startCommand: string;
	pidFile?: string;
}

let runningProcess: ChildProcess | null = null;
const DEFAULT_CONFIG: ProcessConfig = {
	name: "ollama",
	port: 11434,
	startCommand: platform() === "win32" ? "ollama serve" : "ollama serve",
};

/**
 * Check if a server is running on the specified port
 */
export async function isServerRunning(port: number = 11434): Promise<boolean> {
	return new Promise((resolve) => {
		const timeout = setTimeout(() => {
			resolve(false);
		}, 2000);

		const client = require("http").request(
			{
				hostname: "localhost",
				port: port,
				path: "/",
				method: "GET",
				timeout: 1000,
			},
			(res: any) => {
				clearTimeout(timeout);
				resolve(true);
			}
		);

		client.on("error", () => {
			clearTimeout(timeout);
			resolve(false);
		});

		client.on("timeout", () => {
			clearTimeout(timeout);
			client.destroy();
			resolve(false);
		});

		client.end();
	});
}

/**
 * Start the local model process
 */
export async function startModelProcess(config: ProcessConfig = DEFAULT_CONFIG): Promise<boolean> {
	return new Promise((resolve) => {
		try {
			const isWin = platform() === "win32";
			const shell = isWin ? "cmd.exe" : "/bin/bash";
			const shellArgs = isWin ? ["/c"] : ["-c"];

			// Kill any existing process first
			if (runningProcess) {
				runningProcess.kill();
				runningProcess = null;
			}

			console.log(`[Process Manager] Starting ${config.name}...`);

			runningProcess = spawn(shell, [...shellArgs, config.startCommand], {
				detached: isWin ? false : true,
				stdio: "ignore",
			});

			runningProcess.on("error", (err) => {
				console.error(`[Process Manager] Failed to start process: ${err}`);
				runningProcess = null;
				resolve(false);
			});

			// Wait for server to be ready
			setTimeout(async () => {
				const ready = await isServerRunning(config.port);
				if (ready) {
					console.log(`[Process Manager] ${config.name} started successfully on port ${config.port}`);
					resolve(true);
				} else {
					console.warn(`[Process Manager] Server may not have started properly`);
					resolve(false);
				}
			}, 3000);
		} catch (error: any) {
			console.error(`[Process Manager] Error starting process: ${error.message}`);
			resolve(false);
		}
	});
}

/**
 * Kill the managed process
 */
export function killModelProcess(): void {
	if (runningProcess) {
		try {
			const isWin = platform() === "win32";
			if (isWin) {
				exec(`taskkill /PID ${runningProcess.pid} /F`, (error) => {
					if (error) console.error(`[Process Manager] Error killing process: ${error}`);
				});
			} else {
				process.kill(-runningProcess.pid!);
			}
			runningProcess = null;
		} catch (error: any) {
			console.warn(`[Process Manager] Failed to kill process: ${error.message}`);
		}
	}
}

/**
 * Find and kill duplicate processes
 */
export async function killDuplicateProcesses(
	processName: string = "ollama"
): Promise<void> {
	return new Promise((resolve) => {
		try {
			const isWin = platform() === "win32";
			const command = isWin
				? `tasklist /FI "IMAGENAME eq ${processName}.exe" /FO CSV /NH`
				: `pgrep -a ${processName}`;

			exec(command, (error, stdout) => {
				if (error || !stdout.trim()) {
					resolve();
					return;
				}

				const lines = stdout.trim().split("\n");
				if (lines.length <= 1) {
					resolve();
					return;
				}

				// Keep first, kill others
				lines.slice(1).forEach((line) => {
					if (isWin) {
						const match = line.match(/"([^"]+)"/);
						if (match) {
							exec(`taskkill /IM ${processName}.exe /F`, () => {
								console.log(`[Process Manager] Killed duplicate process`);
							});
						}
					} else {
						const pid = line.split(" ")[0];
						if (pid && !isNaN(parseInt(pid)) && parseInt(pid) !== process.pid) {
							exec(`kill -9 ${pid}`, () => {
								console.log(`[Process Manager] Killed duplicate process ${pid}`);
							});
						}
					}
				});

				resolve();
			});
		} catch (error: any) {
			console.warn(`[Process Manager] Error checking duplicates: ${error.message}`);
			resolve();
		}
	});
}

/**
 * Ensure local model is running, with user prompt if needed
 */
export async function ensureLocalModelRunning(
	modelName: string = "local",
	forceStart: boolean = false
): Promise<boolean> {
	if (modelName !== "local" && modelName !== "ollama") {
		// Not a local model, no need to manage
		return true;
	}

	try {
		const isRunning = await isServerRunning(DEFAULT_CONFIG.port);

		if (isRunning) {
			console.log(`[Process Manager] ${DEFAULT_CONFIG.name} is already running`);
			return true;
		}

		if (!forceStart) {
			const choice = await vscode.window.showWarningMessage(
				`Local model (${DEFAULT_CONFIG.name}) is not running. Start it now?`,
				"Yes",
				"No",
				"Always Start"
			);

			if (!choice || choice === "No") {
				return false;
			}

			if (choice === "Always Start") {
				await vscode.workspace.getConfiguration("dcode").update(
					"autoStartModel",
					true,
					vscode.ConfigurationTarget.Global
				);
			}
		}

		// Kill any duplicate processes
		await killDuplicateProcesses(DEFAULT_CONFIG.name);

		// Start the model
		const started = await startModelProcess(DEFAULT_CONFIG);
		return started;
	} catch (error: any) {
		console.error(`[Process Manager] Error ensuring model: ${error.message}`);
		vscode.window.showErrorMessage(`Failed to ensure local model: ${error.message}`);
		return false;
	}
}

/**
 * Restart the model if it becomes unresponsive
 */
export async function restartModel(): Promise<boolean> {
	console.log(`[Process Manager] Restarting model...`);
	killModelProcess();
	await killDuplicateProcesses(DEFAULT_CONFIG.name);
	return startModelProcess(DEFAULT_CONFIG);
}

/**
 * Get current process status
 */
export async function getModelStatus(): Promise<{
	running: boolean;
	port: number;
	name: string;
}> {
	const running = await isServerRunning(DEFAULT_CONFIG.port);
	return {
		running,
		port: DEFAULT_CONFIG.port,
		name: DEFAULT_CONFIG.name,
	};
}
