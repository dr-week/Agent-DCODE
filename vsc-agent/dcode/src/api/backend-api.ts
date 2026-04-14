/**
 * Unified backend API client
 * Calls POST /agent endpoint on local backend
 */

export interface AgentRequest {
	task: string;
	code?: string;
	model?: string;
}

export interface AgentResponse {
	success: boolean;
	task: string;
	model: string;
	plan: any[];
	actions: any[];
	result: string;
	error?: string;
}

const DEFAULT_BACKEND = "http://localhost:5000";

let backendUrl = DEFAULT_BACKEND;

export function setBackendUrl(url: string): void {
	backendUrl = url || DEFAULT_BACKEND;
}

export function getBackendUrl(): string {
	return backendUrl;
}

export async function callAgent(request: AgentRequest): Promise<AgentResponse> {
	const url = `${backendUrl}/agent`;

	try {
		const response = await fetch(url, {
			method: "POST",
			headers: {
				"Content-Type": "application/json",
			},
			body: JSON.stringify({
				task: request.task,
				code: request.code,
				model: request.model,
			}),
		});

		if (!response.ok) {
			throw new Error(`Backend error: ${response.statusText}`);
		}

		const data = await response.json();
		return data as AgentResponse;
	} catch (error: any) {
		throw new Error(`Failed to call backend: ${error.message}`);
	}
}
