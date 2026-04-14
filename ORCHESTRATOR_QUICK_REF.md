# Orchestrator Quick Reference

**Fast commands for managing DCODE services**

---

## CLI Commands

```bash
# Start all services
python dcode_orchestrator.py start

# Stop all services
python dcode_orchestrator.py stop

# Check status
python dcode_orchestrator.py status

# Restart all or specific service
python dcode_orchestrator.py restart
python dcode_orchestrator.py restart --service backend
python dcode_orchestrator.py restart --service ollama

# Start with health monitoring
python dcode_orchestrator.py start --health-check

# Quiet mode (less output)
python dcode_orchestrator.py stop --quiet
```

---

## VS Code Commands

**Cmd+Shift+P** (macOS) or **Ctrl+Shift+P** (Windows/Linux)

```
> DCODE: Start DCODE System
> DCODE: Stop DCODE System
> DCODE: Check DCODE System Status
```

---

## Python API

### Quick Start
```python
from orchestrator import start_all, stop_all, get_status

# Start everything
start_all()

# Check status
status = get_status()
print(status['backend']['status'])  # running/stopped
print(status['ollama']['healthy'])   # true/false

# Stop everything
stop_all()
```

### Advanced
```python
from orchestrator import Orchestrator

orch = Orchestrator()

# Start services
orch.start_backend()
orch.start_ollama()

# Get detailed health info
health, msg = orch.check_service_health('backend')
print(f"Backend healthy: {health} ({msg})")

# Restart with monitoring
orch.restart_service('backend')
orch.run_health_check_background()

# Stop gracefully
orch.stop_all()
```

---

## Status Format

```json
{
  "backend": {
    "port": 5000,
    "status": "running",
    "healthy": true,
    "pid": 12345,
    "message": "Backend healthy",
    "uptime_seconds": 245.5
  },
  "ollama": {
    "port": 11434,
    "status": "running",
    "healthy": true,
    "pid": 12346,
    "message": "Ollama healthy",
    "uptime_seconds": 189.2
  }
}
```

---

## Service Ports

| Service | Port | Endpoint |
|---------|------|----------|
| Backend | 5000 | http://localhost:5000 |
| Ollama | 11434 | http://localhost:11434 |
| Health | 5000 | GET /health |

---

## Common Tasks

### Start Development Environment
```bash
python dcode_orchestrator.py start
# Services ready in 10-20 seconds
```

### Check if Services Running
```bash
python dcode_orchestrator.py status
```

### Stop Before Closing IDE
```bash
python dcode_orchestrator.py stop
```

### Fix Stuck Service
```bash
python dcode_orchestrator.py restart --service backend
```

### Continuous Monitoring
```bash
python dcode_orchestrator.py start --health-check
# Services auto-restart if they fail
# Press Ctrl+C to stop
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Port already in use | `restart --service backend` |
| Ollama not found | Install from https://ollama.ai |
| Backend won't start | Check Python dependencies: `pip install -r requirements.txt` |
| Health check frozen | Press Ctrl+C, then `status` |
| Process stuck | System restart or `taskkill /PID <pid> /F` |

---

## Integration Examples

### Before Running Tests
```python
from orchestrator import start_all, stop_all

# Setup
if not start_all():
    raise RuntimeError("Failed to start services")

try:
    # Run your tests
    pytest.main()
finally:
    # Cleanup
    stop_all()
```

### In VS Code Dev Task
```bash
#!/bin/bash
cd /path/to/agent
python dcode_orchestrator.py start --health-check
```

### Scheduled Startup
```bash
# Windows Task Scheduler
python dcode_orchestrator.py start

# Or cron (macOS/Linux)
@reboot /usr/bin/python3 /path/to/dcode_orchestrator.py start
```

---

## Performance Notes

- **First start**: 15-20 seconds (Ollama slower first time)
- **Subsequent starts**: 10-15 seconds  
- **Status check**: <1 second
- **Health monitoring**: ~1 second per check (5s interval)
- **Auto-restart**: 10-15 seconds

---

**See ORCHESTRATOR.md for complete documentation**
