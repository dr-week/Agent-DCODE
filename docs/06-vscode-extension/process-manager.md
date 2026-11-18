# Local Model Process Manager

Automatic management of local AI models (Ollama) directly from the VS Code extension.

## Overview

The process manager automatically ensures a local AI model is running before executing tasks. It handles:

- ✅ Server availability checks
- ✅ Automatic process startup on first use
- ✅ User prompts for confirmation
- ✅ Duplicate process detection and cleanup
- ✅ Automatic restart on connection failures
- ✅ Cross-platform support (Windows, Mac, Linux)

## How It Works

### 1. User Selects Local Model

```
Model: [Local (Ollama) ▼]
```

### 2. Before First Request

```
Extension checks: Is localhost:11434 running?
  ✅ If YES → Use existing instance
  ❌ If NO  → Prompt user
```

### 3. User Prompt

```
⚠️ Local model (ollama) is not running. Start it now?
[Yes] [No] [Always Start]
```

### 4. Auto Start Process

If user clicks "Yes" or has "Always Start" enabled:

```
[Process Manager] Starting ollama...
[Process Manager] ollama started successfully on port 11434
```

The extension will:
1. Kill any duplicate processes
2. Start fresh instance
3. Wait up to 3 seconds for server readiness
4. Return to user if failed

### 5. Reuse or Restart

- If process is already running → reuse it
- If process becomes unresponsive → automatically restart

## Configuration

### `dcode.autoStartModel`

**Type:** `boolean`  
**Default:** `false`

If `true`, the extension will automatically start the model without prompting.

```json
{
  "dcode.autoStartModel": true
}
```

### Where to Find

VS Code → Settings → Search "dcode" → Toggle "Auto Start Model"

## Behavior

### Normal Flow

1. User sends code
2. Extension checks: Is Ollama running?
3. If not:
   - Prompt user (only once if "Always Start" enabled)
   - Start Ollama in background
4. Call backend API
5. Display result

### Error Recovery

If backend call fails with "Connection":

```
User: "Send to DCODE AI"
  ↓
[Extension] Attempting to restart model after connection failure
  ↓
Restart current model
  ↓
Retry request (manually user would resend)
```

### Duplicate Process Handling

If multiple Ollama processes are detected:
- Kill all except one
- Log: `[Process Manager] Killed duplicate process`
- Continue with single instance

## Logs

View in VS Code Debug Console:

```
[Process Manager] Starting ollama...
[Process Manager] ollama is already running
[Process Manager] Killed duplicate process
[Process Manager] Restarting model...
[Process Manager] Model started successfully on port 11434
```

## Requirements

- **Ollama installed** (on PATH)
  - Windows: `ollama.exe` must be in PATH
  - Mac/Linux: `ollama` must be in PATH

- **Port 11434 available** (default Ollama port)

## Supported Models

- `local` → Uses default Ollama (localhost:11434)
- `ollama` → Same as local

Remote models don't need process management:
- `gemini` → No local process
- `openai` → No local process

## Troubleshooting

### "Local model not running" but Ollama IS running

**Solution:**
1. Check if Ollama is on correct port: `http://localhost:11434`
2. If on different port, update `dcode.backendURL`
3. Check firewall isn't blocking localhost

### "Failed to start process"

**Possible Causes:**
- Ollama not installed
- Ollama not in PATH
- Port 11434 already in use by other process

**Solution:**
```bash
# Test if ollama works
ollama --version
ollama serve
```

### Process keeps restarting

**Solution:**
1. Manually start Ollama: `ollama serve`
2. Check system logs for errors
3. Disable auto-start: `dcode.autoStartModel = false`

## Technical Details

### File

`src/utils/process-manager.ts`

### Public Functions

#### `isServerRunning(port?: number): Promise<boolean>`

Check if server is running on port.

```typescript
const running = await isServerRunning(11434);
```

#### `startModelProcess(config?: ProcessConfig): Promise<boolean>`

Start the model process.

```typescript
const started = await startModelProcess();
if (started) {
  console.log("✅ Model started");
}
```

#### `killModelProcess(): void`

Kill the managed process.

#### `killDuplicateProcesses(processName?: string): Promise<void>`

Find and terminate duplicate processes.

```typescript
await killDuplicateProcesses("ollama");
```

#### `ensureLocalModelRunning(modelName?: string, forceStart?: boolean): Promise<boolean>`

Main function - ensure model is running with user prompts.

```typescript
const ready = await ensureLocalModelRunning("local", false);
```

#### `restartModel(): Promise<boolean>`

Kill and restart the model (for recovery).

```typescript
await restartModel();
```

#### `getModelStatus(): Promise<{running: boolean, port: number, name: string}>`

Get current process status.

```typescript
const status = await getModelStatus();
console.log(`Running: ${status.running}`);
```

## Integration

Called in `src/extension.ts` before `callAgent()`:

```typescript
async function processWithAgent(...) {
  if (selectedModel === "local" || selectedModel === "ollama") {
    const modelReady = await ensureLocalModelRunning(selectedModel, autoStartModel);
    if (!modelReady) {
      // Show error
      return;
    }
  }
  // Call API
  const response = await callAgent({...});
}
```

## Safety

### What It Does NOT Do

❌ Kill unrelated processes  
❌ Modify system PATH  
❌ Install software  
❌ Access other user files  

### What It Does

✅ Spawn child process for `ollama serve` only  
✅ Kill processes by exact name matching  
✅ Check port availability  
✅ Log all operations  

## Cross-Platform Support

### Windows
- Uses `cmd.exe /c "ollama serve"`
- Uses `tasklist` and `taskkill` for process management
- Binary: `ollama.exe`

### Mac/Linux
- Uses `/bin/bash -c "ollama serve"`
- Uses `pgrep` and `kill` for process management
- Binary: `ollama`

## Performance

- Initial check: ~1-2 seconds (port check timeout)
- Startup: ~3 seconds (waiting for readiness)
- Restart: ~5 seconds total
- Duplicate check: <1 second
- No polling overhead (event-based)

## Future Enhancements

- [ ] Support for other local models (LiteLLM, vLLM, etc.)
- [ ] Model selection from installed models
- [ ] Custom startup commands per model
- [ ] GPU/resource monitoring
- [ ] Log streaming to output panel
