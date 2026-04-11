import * as vscode from 'vscode';
import { spawn } from 'child_process';

export function activate(context: vscode.ExtensionContext) {
    const provider = new DCodeViewProvider(context.extensionUri);
    context.subscriptions.push(
        vscode.window.registerWebviewViewProvider('dcode-chat', provider)
    );
}

class DCodeViewProvider implements vscode.WebviewViewProvider {
    constructor(private readonly _extensionUri: vscode.Uri) {}
    public resolveWebviewView(webviewView: vscode.WebviewView) {
        webviewView.webview.options = { enableScripts: true, localResourceRoots: [this._extensionUri] };
        webviewView.webview.html = this._getHtml(webviewView.webview);
        webviewView.webview.onDidReceiveMessage(data => {
            if (data.type === 'sendPrompt') this._execute(data.value, webviewView);
        });
    }
    private _execute(prompt: string, webviewView: vscode.WebviewView) {
        const python = 'C:\\Users\\disha\\Documents\\CODES\\001\\agent\\.venv\\Scripts\\python.exe';
        const script = 'C:\\Users\\disha\\Documents\\CODES\\001\\agent\\main.py';
        
        webviewView.webview.postMessage({ type: 'log', value: `\n[DCode] Executing: ${prompt}\n` });
        
        const proc = spawn(python, [script, prompt]);
        proc.stdout.on('data', d => webviewView.webview.postMessage({ type: 'log', value: d.toString() }));
        proc.stderr.on('data', d => webviewView.webview.postMessage({ type: 'log', value: `ERR: ${d.toString()}` }));
        proc.on('close', code => webviewView.webview.postMessage({ type: 'log', value: `\n[Done] Code: ${code}\n---` }));
    }
    private _getHtml(webview: vscode.Webview) {
        return `<html><body style="padding:10px;background:var(--vscode-sideBar-background);color:var(--vscode-foreground);font-family:sans-serif;">
            <div style="font-size:11px;color:#007acc;font-weight:bold;margin-bottom:10px;letter-spacing:1px;">DCODE ASSISTANT</div>
            <input id="p" style="width:100%;padding:10px;background:var(--vscode-input-background);color:white;border:1px solid var(--vscode-input-border);border-radius:4px;" placeholder="What should we build?" />
            <button onclick="s()" style="width:100%;margin-top:8px;padding:8px;background:#007acc;color:white;border:none;cursor:pointer;font-weight:bold;border-radius:4px;">RUN AGENT</button>
            <div id="l" style="margin-top:15px;font-family:var(--vscode-editor-font-family);font-size:11px;background:#1e1e1e;padding:10px;height:450px;overflow:auto;white-space:pre-wrap;border:1px solid #333;border-radius:4px;">Ready for input...</div>
            <script>
                const vscode = acquireVsCodeApi();
                const l = document.getElementById('l');
                const p = document.getElementById('p');
                function s() { vscode.postMessage({type:'sendPrompt',value:p.value}); p.value=''; }
                p.addEventListener('keypress', (e) => { if(e.key==='Enter') s(); });
                window.addEventListener('message', e => { 
                    l.textContent += e.data.value;
                    l.scrollTop = l.scrollHeight;
                });
            </script>
        </body></html>`;
    }
}
