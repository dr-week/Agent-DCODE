# Agent-DCODE - VS Code Extension

Minimal VS Code extension to send code to OpenAI and get AI responses in a sidebar chat.

## Setup

1. **Get OpenAI API Key**
   - Go to https://platform.openai.com/api-keys
   - Create a new secret key

2. **Configure in VS Code**
   - Open VS Code Settings (Cmd+, or Ctrl+,)
   - Search for "dcode.apiKey"
   - Paste your OpenAI API key

3. **Activate Extension**
   - Open Command Palette (Cmd+Shift+P or Ctrl+Shift+P)
   - Type "Send to DCODE AI"
   - Or click the DCODE icon in the activity bar

## Usage

### Via Command
1. Select code in editor (optional)
2. Run command: **"Send to DCODE AI"**
3. AI response shows in notification

### Via Sidebar Chat
1. Click **DCODE AI** icon in activity bar
2. Type your question in the chat box
3. Get instant AI response

## How It Works

- **Extension** (`src/extension.ts`) - Registers command & webview
- **API** (`src/api/openai.ts`) - Sends requests to OpenAI
- **Webview** (`src/webview/chat.ts`) - Sidebar chat UI
- **Config** - API key stored in VS Code settings

## Files

```
src/
├── extension.ts          # Main extension logic
├── api/
│   └── openai.ts         # OpenAI API calls
└── webview/
    └── chat.ts           # Sidebar chat interface
```

## Build

```bash
npm install
npm run compile    # Build once
npm run watch      # Build on file changes
npm run package    # Production build
```

## Debug

Press `F5` in VS Code to launch extension in debug mode.

## Features

✅ Send code to OpenAI  
✅ Sidebar chat interface  
✅ Real-time responses  
✅ Configurable API key  
✅ Minimal & fast  

## Limitations

❌ No internet = no AI (requires OpenAI API)  
❌ Single function call (no conversation memory)  
❌ No syntax highlighting  
❌ Limited to 5000 char responses  

---

**Total Code:** ~300 lines (including UI)
