# DCODE System Orchestrator

**One-Click Service Management for Local AI Agent**

Automatically manages startup, shutdown, and health of all required services (Backend + Model Server) with zero admin privileges needed.

---

## Overview

The orchestrator handles:
- **Backend Service** (Flask web app on port 5000)
- **Model Server** (Ollama on port 11434)

Features:
- ✅ Automatic service startup
- ✅ Duplicate process detection & cleanup
- ✅ Health monitoring & auto-restart
- ✅ Cross-platform support (Windows/Mac/Linux)
- ✅ No admin privileges required
- ✅ Command-line & VS Code integration

---

## Installation

### Prerequisites
```
- Python 3.10+
- Ollama installed and in PATH
- project_root/orchestrator.py (created automatically)
```

### Quick Setup
```bash
# Already included in project
# Just run:
python orchestrator.py start
```

---

## Usage

### Command Line

#### Start All Services
```bash
python dcode_orchestrator.py start
```

**Output:**
```
============================================================
  DCODE SYSTEM ORCHESTRATOR - START
============================================================

[INFO] Starting backend service...
[INFO] Backend started (PID 12345)
[INFO] Starting Ollama service...
[INFO] Ollama started (PID 12346)
============================================================
All services started successfully!
Backend: http://localhost:5000
Ollama: http://localhost:11434
```

#### Stop All Services
```bash
python dcode_orchestrator.py stop
```

#### Check Status
```bash
python dcode_orchestrator.py status
```

**Output:**
```
============================================================
DCODE System Status
============================================================

✓ BACKEND
  Port: 5000
  Status: running
  PID: 12345
  Message: Backend healthy
  Uptime: 245s

✓ OLLAMA
  Port: 11434
  Status: running
  PID: 12346
  Message: Ollama healthy
  Uptime: 189s

============================================================
```

#### Restart Services
```bash
# Restart all
python dcode_orchestrator.py restart

# Restart specific service
python dcode_orchestrator.py restart --service backend
python dcode_orchestrator.py restart --service ollama
```

#### With Health Monitoring
```bash
python dcode_orchestrator.py start --health-check
```

This runs continuous health checks and auto-restarts services if they become unresponsive.

---

### VS Code Integration

#### Commands Available

**Cmd + Shift + P** on macOS or **Ctrl + Shift + P** on Windows/Linux:

1. **Start DCODE System**
   - Starts backend + Ollama
   - Displays progress in output panel
   - Enables continuous health monitoring

2. **Stop DCODE System**
   - Gracefully stops all services
   - Confirms completion

3. **Check DCODE System Status**
   - Shows real-time status of all services
   - Display in output panel

#### Quick Access

Add keyboard shortcuts in `keybindings.json`:

```json
{
  "key": "ctrl+alt+shift+s",
  "command": "dcode.startSystem"
},
{
  "key": "ctrl+alt+shift+x",
  "command": "dcode.stopSystem"
},
{
  "key": "ctrl+alt+shift+c",
  "command": "dcode.statusSystem"
}
```

---

## API Reference

### Python Module

```python
from orchestrator import Orchestrator, start_all, stop_all, get_status

# Convenience functions
start_all()          # Start all services
stop_all()           # Stop all services
status = get_status() # Get current status

# Class usage
orch = Orchestrator(verbose=True)
orch.start_all()
orch.print_status()
orch.stop_all()
```

### Orchestrator Class Methods

#### Startup
```python
orch.start_backend() -> bool
orch.start_ollama() -> bool
orch.start_all() -> bool
```

#### Shutdown
```python
orch.stop_service(service_name: str) -> bool
orch.stop_all() -> bool
```

#### Health & Status
```python
orch.check_service_health(service_name: str) -> Tuple[bool, str]
orch.get_status() -> Dict[str, Dict]
orch.print_status() -> None
```

#### Management
```python
orch.restart_service(service_name: str) -> bool
orch.is_port_open(port: int) -> bool
orch.get_process_by_port(port: int) -> Optional[Process]
orch.get_duplicate_processes(service_name: str) -> List[Process]
orch.kill_duplicate_processes(service_name: str) -> int
orch.health_check_loop(interval: int = 5) -> None
orch.run_health_check_background() -> Thread
```

#### Examples

```python
# Simple startup
from orchestrator import start_all, get_status
if start_all():
    print(get_status())

# Advanced usage with monitoring
orch = Orchestrator()
orch.start_all()
orch.run_health_check_background()
# Services will auto-restart if they fail
```

---

## Architecture

### Startup Flow

```
User initiates start
    ↓
Check backend port 5000
  ├─ Running? → Continue
  └─ Not running? → Start process
    ↓
Check Ollama port 11434
  ├─ Running? → Continue
  └─ Not running? → Start process
    ↓
Wait for readiness
  ├─ Ping /health (backend)
  ├─ Ping /api/tags (ollama)
  └─ Confirm both responding
    ↓
Return success/failure
```

### Duplicate Handling

```
Process check
    ↓
Find all instances
    ↓
Keep newest one
    ↓
Kill others gracefully
  ├─ Send SIGTERM (15)
  ├─ Wait 3 seconds
  └─ Send SIGKILL (9) if needed
    ↓
Start fresh if needed
```

### Health Monitoring

```
Every 5 seconds (configurable):
    ↓
Check each service
  ├─ Backend: GET http://localhost:5000/health
  ├─ Ollama: GET http://localhost:11434/api/tags
  └─ Response code == 200?
    ↓
If unhealthy:
  ├─ Log warning
  ├─ Mark as unresponsive
  └─ Attempt restart
    ↓
If restart succeeds:
  └─ Resume normal operation
```

---

## Configuration

### Port Configuration

Edit port in code:

```python
# In orchestrator.py
services["backend"].port = 5000    # Change backend port
services["ollama"].port = 11434    # Change Ollama port
```

### Backend Script Location

Default: `./web_app.py` (auto-detected from project root)

Change in code:
```python
self.backend_script = Path("<project-root>/web_app.py")
```

### Health Check Interval

```python
orch = Orchestrator()
orch.health_check_interval = 10  # Check every 10 seconds
orch.run_health_check_background()
```

---

## Endpoints Added

### Backend Health Check

```
GET /health

Response (200 OK):
{
  "status": "healthy",
  "service": "backend"
}
```

Used by orchestrator to verify backend is responsive.

---

## Cross-Platform Support

### Windows
- ✅ Subprocess process group handling
- ✅ Python executable detection
- ✅ Process termination via SIGTERM/SIGKILL

### macOS/Linux
- ✅ Standard subprocess handling
- ✅ Uses `python3` executable
- ✅ Full POSIX signal support

### Verified On
- Windows 10/11 (Python 3.10+)
- macOS 12+ (Python 3.10+)
- Linux (Ubuntu 20.04+, Python 3.10+)

---

## Troubleshooting

### "Ollama not installed or not in PATH"
```bash
# Solution 1: Install ollama
# Download from https://ollama.ai

# Solution 2: Add ollama to PATH
# Windows: Set environment variable
# macOS/Linux: ln -s /Applications/Ollama.app/bin/ollama /usr/local/bin/ollama
```

### "Port already in use"
```bash
# Solution 1: Kill existing process
lsof -i :5000           # macOS/Linux
netstat -ano | findstr :5000  # Windows

# Solution 2: Change port in configuration
```

### "Backend failed to start"
```bash
# Check Flask backend directly
python web_app.py

# Check for errors in terminal
# Verify Python dependencies: pip install -r requirements.txt
```

### "Health check stuck"
```bash
# If continuous monitoring hangs:
# Press Ctrl+C to stop
# Check port availability manually: netstat -ano
```

### "Admin privileges required"
```bash
# Orchestrator requires NO admin privileges
# If you see this error:
# 1. Check file permissions on orchestrator.py
# 2. Try running as regular user (not sudo)
```

---

## Performance

| Operation | Time | Notes |
|-----------|------|-------|
| Start backend | 1-3s | Depends on system |
| Start Ollama | 5-15s | Slower on first run |
| Health check | <1s | Fast port check |
| Auto-restart | 10-20s | Stop + start + verify |
| Total system startup | 10-20s | Both services + verification |

---

## Security

### What It Does
- ✅ Manages local processes only
- ✅ Checks ports before starting
- ✅ Graceful process termination
- ✅ No network exposure (localhost only)

### What It Doesn't Do
- ❌ No authentication/authorization
- ❌ No encrypted transport
- ❌ No user isolation
- ⚠️ Only for local development

### Best Practices
- Use only on development machines
- Don't expose services publicly
- Keep Ollama updated
- No sensitive data in projects/

---

## Advanced Usage

### Integration with CI/CD

```bash
# Start services for testing
python dcode_orchestrator.py start

# Run tests
pytest tests/

# Stop services
python dcode_orchestrator.py stop
```

### Programmatic Control

```python
from orchestrator import Orchestrator
import time

orch = Orchestrator()

# Start and monitor
orch.start_all()
orch.run_health_check_background()

# Do work...
time.sleep(30)

# Stop cleanly
orch.stop_all()
```

### Custom Service Management

```python
# Custom startup with retries
max_attempts = 3
for attempt in range(max_attempts):
    if orch.start_backend():
        break
    time.sleep(2)
else:
    print("Failed to start backend after 3 attempts")
```

---

## Future Enhancements

- [ ] Process restart on crash detection
- [ ] Service dependency management
- [ ] Custom startup/shutdown hooks
- [ ] Service logging to file
- [ ] Metrics collection (CPU, memory)
- [ ] Web dashboard for monitoring
- [ ] Docker container support
- [ ] Systemd service generation

---

## File Structure

```
agent/
├── orchestrator.py           # Main orchestrator module
├── dcode_orchestrator.py     # CLI wrapper
├── web_app.py               # Flask backend (with /health endpoint)
│
└── vsc-agent/dcode/
    ├── package.json         # Commands: start/stop/status
    └── src/extension.ts     # VS Code command handlers
```

---

## Examples

### Example 1: One-Click Startup

```bash
$ python dcode_orchestrator.py start
============================================================
  DCODE SYSTEM ORCHESTRATOR - START
============================================================

[INFO] Starting backend service...
[INFO] Backend already running
[INFO] Starting Ollama service...
[INFO] Ollama started (PID 12346)
============================================================
All services started successfully!
Backend: http://localhost:5000
Ollama: http://localhost:11434
```

### Example 2: VS Code Quick Start

1. Open command palette: `Ctrl+Shift+P`
2. Type "DCODE" and select "Start DCODE System"
3. Watch progress in output panel
4. Services ready to use

### Example 3: Health Monitoring

```bash
$ python dcode_orchestrator.py start --health-check
[Starting services with continuous monitoring...]
[Health check: Backend ✓, Ollama ✓]
[Health check: Backend ✓, Ollama ✓]
[Health check: Backend ✓, Ollama ✗]
[Attempting to restart: Ollama...]
[Health check: Backend ✓, Ollama ✓]
```

### Example 4: Python Integration

```python
#!/usr/bin/env python3
"""Start DCODE before running tests"""

from orchestrator import start_all, stop_all, get_status
import sys

# Start system
if not start_all():
    print("Failed to start services")
    sys.exit(1)

# Check status
status = get_status()
print(f"Backend: {status['backend']['status']}")
print(f"Ollama: {status['ollama']['status']}")

# ... run tests ...

# Cleanup
stop_all()
```

---

## License

MIT License - See LICENSE file

---

**Created**: April 15, 2026  
**Status**: Production Ready  
**Version**: 1.0  
**Platform Support**: Windows, macOS, Linux (basic)
