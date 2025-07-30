"""Utilities for server management, particularly handling port conflicts.

This module provides tools to:
- Check port availability
- Identify processes using specific ports
- Handle port conflicts interactively
- Kill processes blocking ports
- Find alternative ports
- Context managers for temporary port management

Usage examples:
    # Basic port conflict handling
    from ub import handle_port_conflict
    port = handle_port_conflict("0.0.0.0", 8000)
    uvicorn.run(app, host="0.0.0.0", port=port)

    # Context manager for automatic port management
    from ub import port_context
    with port_context("0.0.0.0", 8000, "My API") as port:
        uvicorn.run(app, host="0.0.0.0", port=port)

    # Managed server with automatic cleanup
    from ub import fastapi_context
    with fastapi_context(app, port=8000) as port:
        print(f"Server running on port {port}")
        # Server automatically cleaned up on exit
"""

import socket
import subprocess
import sys
import time
from contextlib import contextmanager
from typing import Dict, List, Optional, Generator, Any


def check_port_available(host: str, port: int) -> bool:
    """Check if a port is available on the given host.

    Args:
        host: Host address to check (e.g., '0.0.0.0', 'localhost')
        port: Port number to check

    Returns:
        True if port is available, False if in use
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind((host, port))
            return True
        except OSError:
            return False


def get_processes_using_port(port: int) -> List[Dict[str, str]]:
    """Get information about processes using a specific port.

    Args:
        port: Port number to check

    Returns:
        List of dictionaries with process information (pid, name, command)
    """
    processes = []

    try:
        # Use lsof to find processes using the port (macOS/Linux)
        result = subprocess.run(
            ["lsof", "-i", f":{port}", "-P", "-n"],
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode == 0:
            lines = result.stdout.strip().split("\n")
            # Skip header line
            for line in lines[1:]:
                parts = line.split()
                if len(parts) >= 9:
                    pid = parts[1]
                    name = parts[0]
                    # Get full command line
                    try:
                        cmd_result = subprocess.run(
                            ["ps", "-p", pid, "-o", "command="],
                            capture_output=True,
                            text=True,
                            check=False,
                        )
                        command = (
                            cmd_result.stdout.strip()
                            if cmd_result.returncode == 0
                            else name
                        )
                    except:
                        command = name

                    processes.append(
                        {
                            "pid": pid,
                            "name": name,
                            "command": command,
                            "port": str(port),
                        }
                    )

    except FileNotFoundError:
        # lsof not available, try netstat as fallback
        try:
            result = subprocess.run(
                ["netstat", "-tulpn"], capture_output=True, text=True, check=False
            )

            if result.returncode == 0:
                for line in result.stdout.split("\n"):
                    if f":{port} " in line and "LISTEN" in line:
                        # This is a simplified parser - netstat output varies
                        parts = line.split()
                        if len(parts) >= 7 and "/" in parts[-1]:
                            pid_name = parts[-1]
                            if "/" in pid_name:
                                pid = pid_name.split("/")[0]
                                name = pid_name.split("/")[1]
                                processes.append(
                                    {
                                        "pid": pid,
                                        "name": name,
                                        "command": name,
                                        "port": str(port),
                                    }
                                )
        except FileNotFoundError:
            # Try Windows netstat
            try:
                result = subprocess.run(
                    ["netstat", "-ano"], capture_output=True, text=True, check=False
                )

                if result.returncode == 0:
                    for line in result.stdout.split("\n"):
                        if f":{port} " in line and "LISTENING" in line:
                            parts = line.split()
                            if len(parts) >= 5:
                                pid = parts[-1]
                                # Get process name on Windows
                                try:
                                    name_result = subprocess.run(
                                        [
                                            "tasklist",
                                            "/fi",
                                            f"pid eq {pid}",
                                            "/fo",
                                            "csv",
                                        ],
                                        capture_output=True,
                                        text=True,
                                        check=False,
                                    )
                                    if name_result.returncode == 0:
                                        lines = name_result.stdout.strip().split("\n")
                                        if len(lines) > 1:
                                            name = lines[1].split(",")[0].strip('"')
                                        else:
                                            name = f"PID-{pid}"
                                    else:
                                        name = f"PID-{pid}"
                                except:
                                    name = f"PID-{pid}"

                                processes.append(
                                    {
                                        "pid": pid,
                                        "name": name,
                                        "command": name,
                                        "port": str(port),
                                    }
                                )
            except FileNotFoundError:
                pass

    return processes


def kill_process(pid: str) -> bool:
    """Kill a process by PID.

    Args:
        pid: Process ID to kill

    Returns:
        True if successful, False otherwise
    """
    try:
        if sys.platform == "win32":
            # Windows
            subprocess.run(["taskkill", "/F", "/PID", pid], check=True)
        else:
            # Unix-like systems
            subprocess.run(["kill", pid], check=True)
            time.sleep(1)  # Give process time to die gracefully

            # Check if still running, force kill if needed
            try:
                subprocess.run(["kill", "-0", pid], check=True)
                # Still running, force kill
                subprocess.run(["kill", "-9", pid], check=True)
            except subprocess.CalledProcessError:
                # Process is dead (kill -0 failed)
                pass

        time.sleep(1)  # Give process time to fully terminate
        return True
    except subprocess.CalledProcessError:
        return False


def find_available_port(
    start_port: int, host: str = "0.0.0.0", max_attempts: int = 100
) -> int:
    """Find the next available port starting from start_port.

    Args:
        start_port: Port to start searching from
        host: Host to check availability on
        max_attempts: Maximum number of ports to try

    Returns:
        An available port number

    Raises:
        RuntimeError: If no available port is found within max_attempts
    """
    port = start_port
    attempts = 0
    while attempts < max_attempts and port < 65535:
        if check_port_available(host, port):
            return port
        port += 1
        attempts += 1
    raise RuntimeError(
        f"No available ports found after checking {max_attempts} ports starting from {start_port}"
    )


def handle_port_conflict(
    host: str, port: int, service_name: Optional[str] = None
) -> int:
    """Handle port conflicts by offering options to user.

    Args:
        host: Host address for the server
        port: Desired port number
        service_name: Optional name of the service for user-friendly messages

    Returns:
        The port to use (either original after cleanup or a new one)
    """
    if check_port_available(host, port):
        return port

    service_name = service_name or "Server"
    print(f"\n🚨 Port {port} is already in use!")

    # Get processes using the port
    processes = get_processes_using_port(port)

    if not processes:
        print(f"Could not identify processes using port {port}")
        print(
            "This might be due to insufficient permissions or unavailable system tools."
        )
    else:
        print(f"\nProcesses using port {port}:")
        print("-" * 80)
        for i, proc in enumerate(processes, 1):
            print(f"{i}. PID: {proc['pid']} | Name: {proc['name']}")
            print(f"   Command: {proc['command']}")
            print()

    while True:
        print(f"What would you like to do for {service_name}?")
        if processes:
            print("1. Kill the conflicting process(es)")
        print("2. Use a different port")
        print("3. Exit")

        try:
            choice = input("\nEnter your choice (1-3): ").strip()

            if choice == "1" and processes:
                success_count = 0
                for proc in processes:
                    print(
                        f"Attempting to kill process {proc['pid']} ({proc['name']})..."
                    )
                    if kill_process(proc["pid"]):
                        print(f"✅ Successfully killed process {proc['pid']}")
                        success_count += 1
                    else:
                        print(f"❌ Failed to kill process {proc['pid']}")

                if success_count > 0:
                    print(
                        f"\nKilled {success_count} process(es). Checking port availability..."
                    )
                    time.sleep(2)  # Give processes time to fully terminate

                    if check_port_available(host, port):
                        print(f"✅ Port {port} is now available!")
                        return port
                    else:
                        print(
                            f"❌ Port {port} is still in use. There might be other processes."
                        )
                        # Refresh process list
                        processes = get_processes_using_port(port)
                        if processes:
                            print("\nRemaining processes:")
                            for proc in processes:
                                print(f"  PID: {proc['pid']} | Name: {proc['name']}")
                        continue
                else:
                    print(
                        "❌ Could not kill any processes. Try running as administrator/sudo."
                    )
                    continue

            elif choice == "2":
                try:
                    new_port = find_available_port(port + 1, host)
                    print(f"✅ Found available port: {new_port}")
                    return new_port
                except RuntimeError as e:
                    print(f"❌ {e}")
                    continue

            elif choice == "3":
                print("👋 Exiting...")
                sys.exit(0)

            else:
                print("❌ Invalid choice. Please try again.")
                continue

        except KeyboardInterrupt:
            print("\n\n👋 Exiting...")
            sys.exit(0)
        except EOFError:
            print("\n\n👋 Exiting...")
            sys.exit(0)


def start_server_with_port_handling(
    server_func,
    host: str = "0.0.0.0",
    port: int = 8000,
    service_name: Optional[str] = None,
    **server_kwargs,
):
    """Start a server with automatic port conflict handling.

    Args:
        server_func: Function to start the server (e.g., uvicorn.run)
        host: Host address
        port: Desired port
        service_name: Name of the service for user messages
        **server_kwargs: Additional arguments to pass to server_func

    Example:
        from ub import start_server_with_port_handling
        import uvicorn

        start_server_with_port_handling(
            uvicorn.run,
            host="0.0.0.0",
            port=8000,
            service_name="My API",
            app=app,
            reload=True
        )
    """
    try:
        final_port = handle_port_conflict(host, port, service_name)
        service_name = service_name or "Server"
        print(f"🚀 Starting {service_name} on http://{host}:{final_port}")

        # Call the server function with the resolved port
        server_func(host=host, port=final_port, **server_kwargs)

    except Exception as e:
        service_name = service_name or "server"
        print(f"❌ Failed to start {service_name}: {e}")
        sys.exit(1)


# Convenience functions for common server types
def start_uvicorn_with_port_handling(
    app, host: str = "0.0.0.0", port: int = 8000, **kwargs
):
    """Start a Uvicorn/FastAPI server with port conflict handling."""
    import uvicorn

    start_server_with_port_handling(
        uvicorn.run,
        host=host,
        port=port,
        service_name="FastAPI Server",
        app=app,
        **kwargs,
    )


def start_flask_with_port_handling(
    app, host: str = "0.0.0.0", port: int = 5000, **kwargs
):
    """Start a Flask server with port conflict handling."""

    def flask_run(**run_kwargs):
        app.run(**run_kwargs)

    start_server_with_port_handling(
        flask_run, host=host, port=port, service_name="Flask Server", **kwargs
    )


def usage_test():
    # Example usage and testing
    print("Testing port conflict handler...")

    # Test port availability check
    print(f"Port 80 available: {check_port_available('localhost', 80)}")
    print(f"Port 65000 available: {check_port_available('localhost', 65000)}")

    # Test finding available port
    try:
        available_port = find_available_port(8000)
        print(f"Next available port from 8000: {available_port}")
    except RuntimeError as e:
        print(f"Error finding port: {e}")


# Context Managers for Port Management


@contextmanager
def port_context(
    host: str = "0.0.0.0",
    port: int = 8000,
    service_name: Optional[str] = None,
    auto_kill: bool = False,
) -> Generator[int, None, None]:
    """Context manager for handling port conflicts.

    Args:
        host: Host address to check
        port: Desired port number
        service_name: Optional service name for user messages
        auto_kill: If True, automatically kill conflicting processes without asking

    Yields:
        int: The port number to use (either original or alternative)

    Example:
        with port_context("0.0.0.0", 8000, "My API") as port:
            # Use 'port' for your server
            uvicorn.run(app, host="0.0.0.0", port=port)
    """
    if check_port_available(host, port):
        yield port
        return

    service_name = service_name or "Server"

    if auto_kill:
        # Automatically kill processes without asking
        processes = get_processes_using_port(port)
        if processes:
            print(f"🔧 Auto-killing {len(processes)} process(es) using port {port}...")
            for proc in processes:
                if kill_process(proc["pid"]):
                    print(f"✅ Killed process {proc['pid']} ({proc['name']})")
                else:
                    print(f"❌ Failed to kill process {proc['pid']}")

            time.sleep(2)  # Give processes time to terminate

            if check_port_available(host, port):
                print(f"✅ Port {port} is now available!")
                yield port
                return

        # If auto-kill failed, fall back to finding alternative port
        try:
            alt_port = find_available_port(port + 1, host)
            print(f"🔄 Using alternative port {alt_port}")
            yield alt_port
        except RuntimeError:
            raise RuntimeError(f"Could not resolve port conflict for {service_name}")
    else:
        # Interactive handling
        final_port = handle_port_conflict(host, port, service_name)
        yield final_port


@contextmanager
def managed_server(
    server_func,
    host: str = "0.0.0.0",
    port: int = 8000,
    service_name: Optional[str] = None,
    auto_kill: bool = False,
    **server_kwargs,
) -> Generator[int, None, None]:
    """Context manager that starts a server and ensures cleanup.

    Args:
        server_func: Function to start the server
        host: Host address
        port: Desired port
        service_name: Service name for messages
        auto_kill: Whether to auto-kill conflicting processes
        **server_kwargs: Additional arguments for server_func

    Yields:
        int: The port the server is running on

    Example:
        def my_server_starter(host, port, app):
            uvicorn.run(app, host=host, port=port)

        with managed_server(my_server_starter, port=8000, app=my_app) as port:
            print(f"Server running on port {port}")
            # Do other work while server runs
            time.sleep(10)
        # Server automatically cleaned up here
    """
    import threading
    import signal

    server_thread = None
    server_port = None

    try:
        with port_context(host, port, service_name, auto_kill) as resolved_port:
            server_port = resolved_port

            # Start server in a separate thread
            def run_server():
                try:
                    server_func(host=host, port=resolved_port, **server_kwargs)
                except Exception as e:
                    print(f"❌ Server error: {e}")

            server_thread = threading.Thread(target=run_server, daemon=True)
            server_thread.start()

            # Give server time to start
            time.sleep(1)

            print(
                f"🚀 {service_name or 'Server'} started on http://{host}:{resolved_port}"
            )
            yield resolved_port

    finally:
        # Cleanup: try to gracefully shutdown
        if server_port:
            print(f"🛑 Shutting down server on port {server_port}...")

            # Try to find and kill the server process
            processes = get_processes_using_port(server_port)
            for proc in processes:
                # Only kill processes that look like our server
                if any(
                    keyword in proc["command"].lower()
                    for keyword in ["uvicorn", "flask", "django", "python"]
                ):
                    if kill_process(proc["pid"]):
                        print(f"✅ Stopped server process {proc['pid']}")


@contextmanager
def temporary_kill(
    port: int, restore: bool = False
) -> Generator[List[Dict[str, str]], None, None]:
    """Context manager to temporarily kill processes using a port.

    Args:
        port: Port number to clear
        restore: If True, attempt to restore killed processes (experimental)

    Yields:
        List of process info dictionaries that were killed

    Example:
        with temporary_kill(8000) as killed_processes:
            print(f"Killed {len(killed_processes)} processes")
            # Port 8000 is now free for your use
            start_my_server(port=8000)
        # Processes optionally restored here (if restore=True)
    """
    original_processes = get_processes_using_port(port)
    killed_processes = []

    try:
        # Kill processes using the port
        for proc in original_processes:
            print(
                f"🔪 Killing process {proc['pid']} ({proc['name']}) using port {port}"
            )
            if kill_process(proc["pid"]):
                killed_processes.append(proc)
                print(f"✅ Successfully killed {proc['pid']}")
            else:
                print(f"❌ Failed to kill {proc['pid']}")

        if killed_processes:
            time.sleep(2)  # Give processes time to die
            print(f"🆓 Port {port} is now available")

        yield killed_processes

    finally:
        if restore and killed_processes:
            print(f"🔄 Attempting to restore {len(killed_processes)} processes...")
            # This is experimental - trying to restart killed processes
            for proc in killed_processes:
                try:
                    # This is quite tricky and may not work for all processes
                    # We'd need to store more context about how to restart them
                    print(
                        f"⚠️  Cannot automatically restore {proc['name']} - manual restart required"
                    )
                except Exception as e:
                    print(f"❌ Failed to restore {proc['name']}: {e}")


@contextmanager
def reserve_port(
    host: str = "0.0.0.0", start_port: int = 8000, count: int = 1
) -> Generator[List[int], None, None]:
    """Context manager to reserve one or more consecutive ports.

    Args:
        host: Host to reserve ports on
        start_port: Starting port number
        count: Number of consecutive ports to reserve

    Yields:
        List of reserved port numbers

    Example:
        with reserve_port("0.0.0.0", 8000, 3) as ports:
            print(f"Reserved ports: {ports}")
            # Use ports[0], ports[1], ports[2] for your services
            start_service_1(port=ports[0])
            start_service_2(port=ports[1])
            start_service_3(port=ports[2])
        # Ports automatically released
    """
    reserved_sockets = []
    reserved_ports = []

    try:
        # Find and reserve consecutive ports
        current_port = start_port
        while len(reserved_ports) < count:
            if check_port_available(host, current_port):
                # Reserve the port by binding to it
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                try:
                    sock.bind((host, current_port))
                    reserved_sockets.append(sock)
                    reserved_ports.append(current_port)
                except OSError:
                    sock.close()
                    # Port became unavailable, reset and try again
                    for s in reserved_sockets:
                        s.close()
                    reserved_sockets.clear()
                    reserved_ports.clear()
                    current_port += 1
                    continue
            else:
                # Port not available, reset and try from next port
                for s in reserved_sockets:
                    s.close()
                reserved_sockets.clear()
                reserved_ports.clear()
                current_port += 1

            if len(reserved_ports) < count:
                current_port += 1

            # Safety check to avoid infinite loop
            if current_port > 65535:
                raise RuntimeError(
                    f"Could not find {count} consecutive available ports starting from {start_port}"
                )

        print(f"🔒 Reserved ports: {reserved_ports}")
        yield reserved_ports

    finally:
        # Release all reserved ports
        for sock in reserved_sockets:
            sock.close()
        if reserved_ports:
            print(f"🔓 Released ports: {reserved_ports}")


# Convenience context managers for specific frameworks


@contextmanager
def fastapi_context(
    app,
    host: str = "0.0.0.0",
    port: int = 8000,
    auto_kill: bool = False,
    **uvicorn_kwargs,
) -> Generator[int, None, None]:
    """Context manager for FastAPI applications.

    Example:
        from fastapi import FastAPI
        app = FastAPI()

        with fastapi_context(app, port=8000, reload=True) as port:
            print(f"FastAPI running on port {port}")
            # Do work while server runs
    """
    import uvicorn

    def server_func(host, port, **kwargs):
        uvicorn.run(app, host=host, port=port, **kwargs)

    with managed_server(
        server_func, host, port, "FastAPI Server", auto_kill, **uvicorn_kwargs
    ) as server_port:
        yield server_port


@contextmanager
def flask_context(
    app,
    host: str = "0.0.0.0",
    port: int = 5000,
    auto_kill: bool = False,
    **flask_kwargs,
) -> Generator[int, None, None]:
    """Context manager for Flask applications.

    Example:
        from flask import Flask
        app = Flask(__name__)

        with flask_context(app, port=5000, debug=True) as port:
            print(f"Flask running on port {port}")
            # Do work while server runs
    """

    def server_func(host, port, **kwargs):
        app.run(host=host, port=port, **kwargs)

    with managed_server(
        server_func, host, port, "Flask Server", auto_kill, **flask_kwargs
    ) as server_port:
        yield server_port
