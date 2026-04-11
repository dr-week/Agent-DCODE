import { OpenAI } from "openai";

export async function sendCodeToAI(code: string, apiKey: string): Promise<string> {
	const client = new OpenAI({ apiKey });

	const response = await client.chat.completions.create({
		model: "gpt-4o-mini",
		messages: [
			{
				role: "user",
				content: `Help me with this code:\n\n\`\`\`\n${code}\n\`\`\`\n\nProvide a concise response.`,
			},
		],
		max_tokens: 1024,
	});

	const message = response.choices[0].message;
	if (message.content) {
		return message.content;
	}

	throw new Error("Unexpected response from OpenAI");
}

export async function sendMessageToAI(userMessage: string, apiKey: string): Promise<string> {
	const client = new OpenAI({ apiKey });

	const response = await client.chat.completions.create({
		model: "gpt-4o-mini",
		messages: [
			{
				role: "user",
				content: userMessage,
			},
		],
		max_tokens: 1024,
	});

	const message = response.choices[0].message;
	if (message.content) {
		return message.content;
	}

	throw new Error("Unexpected response from OpenAI");
}
