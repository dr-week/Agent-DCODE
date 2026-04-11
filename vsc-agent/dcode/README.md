# Agent-DCODE - VS Code Extension

Minimal VS Code extension to send code to OpenAI API and get AI-powered responses instantly.

## Features

- **Send Code to AI** — Right-click or use command palette to submit code for analysis
- **Sidebar Chat** — Interactive chat interface for asking questions
- **Real-time Responses** — Get instant AI feedback without leaving VS Code
- **Simple Setup** — Just add your OpenAI API key and you're ready

## Requirements

- VS Code 1.110+
- OpenAI API key ([get one here](https://platform.openai.com/api-keys))

## Installation

1. Download `agent-dcode-0.1.0.vsix`
2. Open VS Code
3. Go to Extensions (Ctrl+Shift+X)
4. Click "..." menu → "Install from VSIX"
5. Select the downloaded file

## Setup

1. Open VS Code Settings (Ctrl+,)
2. Search for "dcode.apiKey"
3. Paste your OpenAI API key

## Usage

### Via Command
- Select code in editor
- Press Ctrl+Shift+P → "Send to DCODE AI"
- See response in notification

### Via Sidebar Chat
- Click DCODE AI icon in activity bar
- Type your question
- Get instant response

## Extension Settings

- `dcode.apiKey` — Your OpenAI API key (required)

## Known Issues

- Requires active internet (connects to OpenAI)
- Limited to 5000 characters per response
- No conversation history between sessions

Calling out known issues can help limit users opening duplicate issues against your extension.

## Release Notes

Users appreciate release notes as you update your extension.

### 1.0.0

Initial release of ...

### 1.0.1

Fixed issue #.

### 1.1.0

Added features X, Y, and Z.

---

## Following extension guidelines

Ensure that you've read through the extensions guidelines and follow the best practices for creating your extension.

* [Extension Guidelines](https://code.visualstudio.com/api/references/extension-guidelines)

## Working with Markdown

You can author your README using Visual Studio Code. Here are some useful editor keyboard shortcuts:

* Split the editor (`Cmd+\` on macOS or `Ctrl+\` on Windows and Linux).
* Toggle preview (`Shift+Cmd+V` on macOS or `Shift+Ctrl+V` on Windows and Linux).
* Press `Ctrl+Space` (Windows, Linux, macOS) to see a list of Markdown snippets.

## For more information

* [Visual Studio Code's Markdown Support](http://code.visualstudio.com/docs/languages/markdown)
* [Markdown Syntax Reference](https://help.github.com/articles/markdown-basics/)

**Enjoy!**
