# DCODE Extension Refactor

## Overview

The VS Code extension has been refactored to **remove OpenAI dependency** and use a **unified backend API** instead. The extension now supports multiple AI models through a single backend interface.

## Changes

### What Was Removed

- ❌ Direct OpenAI API calls
- ❌ `apiKey` setting requirement
- ❌ `openai.ts` dependency (can be deprecated)
- ❌ `sendCodeToAI()` and `sendMessageToAI()` functions

### What Was Added

✅ `backend-api.ts` — Unified backend client
✅ Model selection UI (dropdown)
✅ `dcode.switchModel` command
✅ `dcode.model` setting
✅ `dcode.backendURL` setting
✅ Multi-model support: `local | ollama | gemini | openai`

## Architecture

### Old Flow
```
VS Code Extension
    ↓
[OpenAI API Key] → sendCodeToAI()
    ↓
OpenAI API (gpt-4o-mini)
```

### New Flow
```
VS Code Extension
    ↓
[Backend URL] + [Model Selection] → callAgent()
    ↓
Local Backend API (/agent endpoint)
    ↓
Selected Model (Local/Ollama/Gemini/OpenAI)
```

## Files Modified

### New Files
- `src/api/backend-api.ts` — Unified API client

### Modified Files
- `src/extension.ts` — Removed OpenAI logic, added model selection
- `src/webview/chat.ts` — Added model dropdown UI
- `package.json` — Removed OpenAI dependency, updated settings

### Deprecated Files
- `src/api/openai.ts` — No longer used (can be deleted)

## Settings

### Configuration (VS Code Settings)

```json
{
  "dcode.model": "local",
  "dcode.backendURL": "http://localhost:5000"
}
```

#### `dcode.model`
- Type: `string`
- Values: `"local" | "ollama" | "gemini" | "openai"`
- Default: `"local"`

#### `dcode.backendURL`
- Type: `string`
- Default: `"http://localhost:5000"`

## Commands

### `dcode.sendToAI`
Send selected code to the backend for analysis.

### `dcode.switchModel` (NEW)
Open a quick picker to switch between available models.

## UI Changes

### Chat Sidebar
Added a model selection dropdown at the top of the chat panel:

```
Model: [Local (Ollama) ▼]
[Chat messages...]
[Input box] [Send button]
```

Users can switch models without reloading the extension.

## API Integration

### Backend Endpoint

The extension calls `POST /agent` on the backend:

```http
POST /agent HTTP/1.1
Content-Type: application/json

{
  "task": "Analyze this code",
  "code": "function add(a, b) { return a + b; }",
  "model": "local"
}
```

### Response Format

```json
{
  "success": true,
  "task": "Analyze this code",
  "model": "local",
  "plan": ["step 1", "step 2"],
  "actions": [...],
  "result": "Function looks good"
}
```

## Usage

### 1. Start Backend
```bash
cd c:\Users\disha\Documents\CODES\001\agent
python web_app.py
```

### 2. Open VS Code Extension
The extension is pre-configured to connect to `http://localhost:5000`.

### 3. Select Model
Use the dropdown in the Chat sidebar or run `dcode.switchModel` command.

### 4. Send Code
- Right-click → "Send to DCODE AI"
- Or type in the Chat sidebar

## Error Handling

If backend is unreachable:
```
Error: Failed to call backend: fetch failed
```

**Solution**: Ensure backend is running on the configured URL.

## Migration Guide

If you were using the old OpenAI extension:

1. ❌ **Remove** OpenAI API key from settings
2. ✅ **Ensure** backend is running (`python web_app.py`)
3. ✅ **Update** extension to this version
4. ✅ **Select** your preferred model from the dropdown

## Dependencies

### Old Dependencies
- `openai@^4.26.0` ❌ Removed

### New Dependencies
- None! Pure fetch API

## Benefits

✅ No API key exposure in extension
✅ Support for multiple AI models
✅ Easy model switching
✅ Extensible backend architecture
✅ Reduced extension complexity
✅ Unified error handling

## Future Enhancements

- [ ] Custom model parameters per model
- [ ] Model-specific settings in UI
- [ ] History persistence per model
- [ ] Backend health checks
- [ ] Model info display (tokens, cost estimate)
