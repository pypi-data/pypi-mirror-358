# ub

**"UnBind"** - Frees occupied ports by detecting and unbinding blocking processes.

Never struggle with "port already in use" errors again! `ub` automatically detects what's using your ports, shows you the processes with their PIDs, and gives you options to kill them or find alternative ports.

## 🚀 Installation

```bash
pip install ub
```

## ✨ Quick Start

### For FastAPI/Uvicorn servers:
```python
from fastapi import FastAPI
from ub import start_uvicorn_with_port_handling

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

# This will handle port conflicts automatically
start_uvicorn_with_port_handling(app, host="0.0.0.0", port=8000, reload=True)
```

### For Flask servers:
```python
from flask import Flask
from ub import start_flask_with_port_handling

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'

# This will handle port conflicts automatically  
start_flask_with_port_handling(app, host="0.0.0.0", port=5000, debug=True)
```

### For any server:
```python
from ub import start_server_with_port_handling
import uvicorn

def my_server_starter(host, port, **kwargs):
    # Your server startup logic here
    uvicorn.run(my_app, host=host, port=port, **kwargs)

start_server_with_port_handling(
    my_server_starter,
    host="0.0.0.0", 
    port=8000,
    service_name="My Custom Server"
)
```

## 🎭 Context Managers

`ub` now provides powerful context managers for automatic port management and server lifecycle control:

### Basic Port Management
```python
from ub import port_context

with port_context("0.0.0.0", 8000, "My API") as port:
    # Port conflict automatically resolved
    uvicorn.run(app, host="0.0.0.0", port=port)
    # Automatic cleanup on exit
```

### Managed Server Lifecycle
```python
from ub import managed_server

def my_server(host, port, app):
    uvicorn.run(app, host=host, port=port)

with managed_server(my_server, port=8000, app=my_app) as port:
    print(f"Server running on port {port}")
    # Do other work while server runs
    time.sleep(10)
# Server automatically shut down here
```

### Framework-Specific Context Managers
```python
# FastAPI
from ub import fastapi_context
with fastapi_context(app, port=8000, reload=True) as port:
    print(f"FastAPI running on port {port}")
    # Server runs in background, auto-cleanup on exit

# Flask  
from ub import flask_context
with flask_context(app, port=5000, debug=True) as port:
    print(f"Flask running on port {port}")
    # Server runs in background, auto-cleanup on exit
```

### Port Reservation
```python
from ub import reserve_port

# Reserve multiple consecutive ports
with reserve_port("0.0.0.0", 8000, count=3) as ports:
    print(f"Reserved ports: {ports}")  # e.g., [8000, 8001, 8002]
    start_service_1(port=ports[0])
    start_service_2(port=ports[1]) 
    start_service_3(port=ports[2])
# Ports automatically released
```

### Temporary Process Management
```python
from ub import temporary_kill

# Temporarily clear a port
with temporary_kill(8000) as killed_processes:
    print(f"Temporarily killed {len(killed_processes)} processes")
    # Port 8000 is now free for your use
    start_my_server(port=8000)
# Processes info available, optional restoration
```

## 🔧 What It Does

When you try to start a server and the port is already in use, `ub` will:

1. **Detect the conflict** - Immediately identifies when a port is occupied
2. **Show process details** - Lists all processes using the port with PIDs, names, and full command lines
3. **Offer clear options**:
   - Kill the conflicting processes
   - Find and use an alternative port
   - Exit gracefully

### Example interaction:
```
🚨 Port 8000 is already in use!

Processes using port 8000:
--------------------------------------------------------------------------------
1. PID: 1234 | Name: python
   Command: python my_old_server.py

2. PID: 5678 | Name: node  
   Command: node server.js

What would you like to do for FastAPI Server?
1. Kill the conflicting process(es)
2. Use a different port
3. Exit

Enter your choice (1-3): 
```

## 📚 API Reference

### Core Functions

#### `handle_port_conflict(host, port, service_name=None)`
Handles port conflicts interactively. Returns the port to use (either original after cleanup or a new one).

```python
from ub import handle_port_conflict

port = handle_port_conflict("0.0.0.0", 8000, "My API")
# Now use 'port' to start your server
```

#### `check_port_available(host, port)`
Check if a port is available.

```python
from ub import check_port_available

if check_port_available("localhost", 8000):
    print("Port 8000 is free!")
```

#### `get_processes_using_port(port)`
Get detailed information about processes using a port.

```python
from ub import get_processes_using_port

processes = get_processes_using_port(8000)
for proc in processes:
    print(f"PID: {proc['pid']}, Name: {proc['name']}, Command: {proc['command']}")
```

#### `find_available_port(start_port, host="0.0.0.0", max_attempts=100)`
Find the next available port starting from a given port.

```python
from ub import find_available_port

available_port = find_available_port(8000)
print(f"Next available port: {available_port}")
```

### Convenience Wrappers

#### `start_uvicorn_with_port_handling(app, host="0.0.0.0", port=8000, **kwargs)`
Start a Uvicorn/FastAPI server with automatic port conflict handling.

#### `start_flask_with_port_handling(app, host="0.0.0.0", port=5000, **kwargs)`  
Start a Flask server with automatic port conflict handling.

#### `start_server_with_port_handling(server_func, host="0.0.0.0", port=8000, service_name=None, **server_kwargs)`
Generic wrapper for any server startup function.

### Context Managers

#### `port_context(host="0.0.0.0", port=8000, service_name=None, auto_kill=False)`
Context manager for handling port conflicts. Yields the port to use.

```python
from ub import port_context

with port_context("0.0.0.0", 8000, "My API", auto_kill=True) as port:
    uvicorn.run(app, host="0.0.0.0", port=port)
```

#### `managed_server(server_func, host="0.0.0.0", port=8000, service_name=None, auto_kill=False, **server_kwargs)`
Context manager that starts a server and ensures cleanup. Yields the port number.

#### `fastapi_context(app, host="0.0.0.0", port=8000, auto_kill=False, **uvicorn_kwargs)`
Context manager specifically for FastAPI applications.

#### `flask_context(app, host="0.0.0.0", port=5000, auto_kill=False, **flask_kwargs)`
Context manager specifically for Flask applications.

#### `reserve_port(host="0.0.0.0", start_port=8000, count=1)`
Context manager to reserve consecutive ports. Yields list of reserved port numbers.

#### `temporary_kill(port, restore=False)`
Context manager to temporarily kill processes using a port. Yields list of killed process info.

## 🎯 Usage Patterns

### Pattern 1: Drop-in replacement (Recommended)
Replace your existing server startup with the `ub` equivalent:

```python
# Before
uvicorn.run(app, host="0.0.0.0", port=8000)

# After  
from ub import start_uvicorn_with_port_handling
start_uvicorn_with_port_handling(app, host="0.0.0.0", port=8000)
```

### Pattern 2: Manual conflict handling
Handle conflicts yourself with full control:

```python
from ub import handle_port_conflict
import uvicorn

desired_port = 8000
final_port = handle_port_conflict("0.0.0.0", desired_port, "My Custom API")

print(f"Starting server on port {final_port}")
uvicorn.run(app, host="0.0.0.0", port=final_port)
```

### Pattern 3: Port checking utilities
Use individual utility functions:

```python
from ub import check_port_available, get_processes_using_port, find_available_port

port = 8000

if not check_port_available("localhost", port):
    print(f"Port {port} is busy!")
    
    # See what's using it
    processes = get_processes_using_port(port)
    for proc in processes:
        print(f"Process: {proc['name']} (PID: {proc['pid']})")
    
    # Find alternative
    alt_port = find_available_port(port + 1)
    print(f"Try port {alt_port} instead")
```

### Pattern 4: Custom server integration
Integrate with any server framework:

```python
from ub import start_server_with_port_handling
import http.server
import socketserver

def start_simple_server(host="0.0.0.0", port=8080):
    Handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer((host, port), Handler) as httpd:
        print(f"Serving at http://{host}:{port}")
        httpd.serve_forever()

start_server_with_port_handling(
    start_simple_server,
    host="0.0.0.0", 
    port=8080,
    service_name="Simple HTTP Server"
)
```

### Pattern 5: Context manager for testing
Perfect for tests that need temporary servers:

```python
from ub import fastapi_context

def test_my_api():
    with fastapi_context(my_app, auto_kill=True) as port:
        # Server runs in background with auto-cleanup
        response = requests.get(f"http://localhost:{port}/health")
        assert response.status_code == 200
    # Server automatically cleaned up after test
```

### Pattern 6: Multi-service development  
Run multiple services with automatic port management:

```python
from ub import reserve_port, fastapi_context

with reserve_port(start_port=8000, count=3) as ports:
    with fastapi_context(auth_service, port=ports[0]) as auth_port:
        with fastapi_context(api_service, port=ports[1]) as api_port:
            with fastapi_context(ui_service, port=ports[2]) as ui_port:
                # All services running, do integration work
                run_integration_tests(auth_port, api_port, ui_port)
# All services automatically cleaned up
```

## 🌍 Cross-Platform Support

`ub` works seamlessly across platforms:

- **macOS/Linux**: Uses `lsof` and `ps` for detailed process information
- **Windows**: Uses `netstat` and `tasklist` for process detection  
- **Fallbacks**: Gracefully handles missing system tools

## 🔐 Process Management

When killing processes, `ub`:

1. **Tries graceful termination first** (`SIGTERM` on Unix, standard termination on Windows)
2. **Falls back to force kill if needed** (`SIGKILL` on Unix, `/F` flag on Windows)
3. **Waits and verifies** process termination
4. **Reports success/failure** clearly

## ⚡ Benefits

- **🚫 No more "address already in use" mysteries** - See exactly what's blocking your port
- **⚡ One-click process cleanup** - Kill conflicting processes safely with a single choice
- **🔄 Automatic port discovery** - Find alternative ports instantly
- **🔧 Framework agnostic** - Works with FastAPI, Flask, Django, custom servers, anything
- **🖥️ Cross-platform** - Same experience on macOS, Linux, and Windows
- **👥 User-friendly** - Clear messages, safe defaults, graceful error handling
- **📦 Zero dependencies** - Uses only Python standard library
- **🎭 Context manager support** - Automatic cleanup and resource management
- **🧪 Perfect for testing** - Temporary servers with guaranteed cleanup
- **🔄 Exception safe** - Resources properly released even when errors occur

## 🤝 Contributing

Issues and pull requests welcome! This tool aims to eliminate the frustration of port conflicts for all developers.

## 📄 License

MIT License - Use freely in your projects!

---

**Stop fighting port conflicts. Start using `ub`.** 🎯
“UnBind”: Frees occupied ports by detecting and unbinding blocking processes. 

To install:	```pip install ub```

