# Debug Agent-DCODE Extension

## Quick Start

1. **Open extension folder in VS Code:**
   ```powershell
   code c:\Users\disha\Documents\CODES\001\agent\vsc-agent\dcode
   ```

2. **Press `F5`** to launch extension in debug mode
   - VS Code will automatically:
     - Run `npm run compile`
     - Open a new extension host window
     - Attach debugger

3. **Test in extension window:**
   - Open any file with code
   - Cmd+Shift+P → "Send to DCODE AI"
   - Check debug console for logs

## Debug Features

- ✅ Full breakpoint support
- ✅ Step through code
- ✅ Watch variables
- ✅ Debug console
- ✅ Hot reload on save

## Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| Start Debug | `F5` |
| Stop Debug | `Shift+F5` |
| Step Over | `F10` |
| Step Into | `F11` |
| Continue | `F5` |
| Breakpoint | `Ctrl+B` or click line |

## Configuration Files

- `.vscode/launch.json` — Debug configuration
- `.vscode/tasks.json` — Build tasks
- `.vscode/settings.json` — Editor settings

All configured and ready to use!
