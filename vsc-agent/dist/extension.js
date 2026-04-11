var __create = Object.create;
var __defProp = Object.defineProperty;
var __getOwnPropDesc = Object.getOwnPropertyDescriptor;
var __getOwnPropNames = Object.getOwnPropertyNames;
var __getProtoOf = Object.getPrototypeOf;
var __hasOwnProp = Object.prototype.hasOwnProperty;
var __export = (target, all) => {
  for (var name in all)
    __defProp(target, name, { get: all[name], enumerable: true });
};
var __copyProps = (to, from, except, desc) => {
  if (from && typeof from === "object" || typeof from === "function") {
    for (let key of __getOwnPropNames(from))
      if (!__hasOwnProp.call(to, key) && key !== except)
        __defProp(to, key, { get: () => from[key], enumerable: !(desc = __getOwnPropDesc(from, key)) || desc.enumerable });
  }
  return to;
};
var __toESM = (mod, isNodeMode, target) => (target = mod != null ? __create(__getProtoOf(mod)) : {}, __copyProps(
  // If the importer is in node compatibility mode or this is not an ESM
  // file that has been converted to a CommonJS file using a Babel-
  // compatible transform (i.e. "__esModule" has not been set), then set
  // "default" to the CommonJS "module.exports" for node compatibility.
  isNodeMode || !mod || !mod.__esModule ? __defProp(target, "default", { value: mod, enumerable: true }) : target,
  mod
));
var __toCommonJS = (mod) => __copyProps(__defProp({}, "__esModule", { value: true }), mod);

// src/extension.ts
var extension_exports = {};
__export(extension_exports, {
  activate: () => activate
});
module.exports = __toCommonJS(extension_exports);
var vscode = __toESM(require("vscode"));
var import_child_process = require("child_process");
function activate(context) {
  const provider = new DCodeViewProvider(context.extensionUri);
  context.subscriptions.push(
    vscode.window.registerWebviewViewProvider("dcode-chat", provider)
  );
}
var DCodeViewProvider = class {
  constructor(_extensionUri) {
    this._extensionUri = _extensionUri;
  }
  resolveWebviewView(webviewView) {
    webviewView.webview.options = { enableScripts: true, localResourceRoots: [this._extensionUri] };
    webviewView.webview.html = this._getHtml(webviewView.webview);
    webviewView.webview.onDidReceiveMessage((data) => {
      if (data.type === "sendPrompt") this._execute(data.value, webviewView);
    });
  }
  _execute(prompt, webviewView) {
    const python = "C:\\Users\\disha\\Documents\\CODES\\001\\agent\\.venv\\Scripts\\python.exe";
    const script = "C:\\Users\\disha\\Documents\\CODES\\001\\agent\\main.py";
    webviewView.webview.postMessage({ type: "log", value: `
[DCode] Executing: ${prompt}
` });
    const proc = (0, import_child_process.spawn)(python, [script, prompt]);
    proc.stdout.on("data", (d) => webviewView.webview.postMessage({ type: "log", value: d.toString() }));
    proc.stderr.on("data", (d) => webviewView.webview.postMessage({ type: "log", value: `ERR: ${d.toString()}` }));
    proc.on("close", (code) => webviewView.webview.postMessage({ type: "log", value: `
[Done] Code: ${code}
---` }));
  }
  _getHtml(webview) {
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
};
// Annotate the CommonJS export names for ESM import in node:
0 && (module.exports = {
  activate
});
