"""
Core proxy implementation for JellyProxy.

Handles the IPC proxy server, MPV process management, JMS process management,
and message filtering between jellyfin-mpv-shim and mpv using the new JSON
configuration and rule-based filtering system.
"""

import asyncio
import json
import os
import signal
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Dict, Any, Optional

from .config import ProxyConfig

# Import python_mpv_jsonipc (checked in main.py)
try:
    from python_mpv_jsonipc import MPV, MPVError
except ImportError:
    # This should be caught in main.py, but handle gracefully
    MPV = None
    MPVError = Exception


class JellyProxy:
    """
    Main proxy class that manages MPV, JMS, and IPC communication.

    This class handles:
    - MPV process lifecycle management
    - JMS process lifecycle management
    - IPC proxy server for JMS connections
    - Command filtering and modification using the new rule-based system
    - Event forwarding from MPV to JMS
    """

    def __init__(self, config: ProxyConfig):
        """Initialize the proxy with the given configuration."""
        self.config = config

        # MPV instance managed by python_mpv_jsonipc
        self.mpv: Optional[MPV] = None
        self.jms_process: Optional[subprocess.Popen] = None
        self.proxy_server: Optional[asyncio.Server] = None
        self.client_connections: List[Tuple[asyncio.StreamReader, asyncio.StreamWriter]] = []

        # Shutdown coordination
        self._shutdown_event = asyncio.Event()
        self._tasks: List[asyncio.Task] = []

    def log(self, message: str, level: str = "INFO"):
        """Log a message with timestamp and level."""
        if level == "DEBUG" and self.config.log_level != "DEBUG":
            return

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_line = f"[{timestamp}] {level}: {message}"

        if self.config.log_to_console:
            print(log_line)
            sys.stdout.flush()

        # TODO: Add file logging support in Phase 3
        if self.config.log_to_file and self.config.log_file_path:
            # Placeholder for file logging
            pass

    def log_ipc(self, direction: str, command_data: Dict[str, Any], request_id: Optional[int] = None):
        """Log IPC communication between JMS and MPV."""
        if not self.config.log_ipc_messages:
            return

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        try:
            if isinstance(command_data, dict):
                formatted = json.dumps(command_data, separators=(',', ':'))
            else:
                formatted = str(command_data)
        except Exception:
            formatted = str(command_data)

        id_suffix = f" (req_id={request_id})" if request_id else ""
        log_line = f"[{timestamp}] {direction}{id_suffix}: {formatted}"

        if self.config.log_to_console:
            print(log_line)
            sys.stdout.flush()

    def setup_socket_directory(self):
        """Create socket directory and clean up stale sockets."""
        self.log("Creating socket directory", "STARTUP")
        self.config.socket_dir.mkdir(mode=self.config.socket_dir_permissions, exist_ok=True)

        # Clean up any existing sockets
        if self.config.spoof_socket_path.exists():
            self.log(f"Removing stale socket: {self.config.spoof_socket_path}", "STARTUP")
            self.config.spoof_socket_path.unlink()

    def start_mpv(self):
        """Start MPV using python_mpv_jsonipc library."""
        if MPV is None:
            raise RuntimeError("python_mpv_jsonipc not available")

        self.log("Starting MPV using python_mpv_jsonipc", "STARTUP")

        try:
            self.mpv = MPV(
                start_mpv=True,
                ipc_socket=str(self.config.real_socket_path),
                **self.config.mpv_config
            )
            self.log(f"MPV started successfully with socket: {self.config.real_socket_path}", "STARTUP")

            # Set up MPV event logging
            @self.mpv.on_event("log-message")
            def log_handler(data):
                if self.config.log_level == "DEBUG":
                    level = data.get('level', 'info').upper()
                    prefix = data.get('prefix', 'mpv')
                    text = data.get('text', '').strip()
                    self.log(f"MPV {level}: [{prefix}] {text}", "MPV")

            # Enable log messages for debug mode
            if self.config.log_level == "DEBUG":
                try:
                    self.mpv.command("request_log_messages", "info")
                except MPVError:
                    pass  # Ignore if this fails

            # Set up event forwarding for JMS
            self._setup_mpv_event_forwarding()

        except Exception as e:
            self.log(f"ERROR starting MPV: {e}", "ERROR")
            raise

    def _setup_mpv_event_forwarding(self):
        """Set up event forwarding from MPV to JMS connections."""
        important_events = [
            "start-file", "end-file", "file-loaded", "playback-restart",
            "seek", "audio-reconfig", "video-reconfig", "idle",
            "client-message", "property-change"
        ]

        for event_name in important_events:
            @self.mpv.on_event(event_name)
            def forward_event(data, event=event_name):
                # Add event name to data if not present
                if 'event' not in data:
                    data = {'event': event, **data}
                self.forward_event_to_jms(data)

    def start_jms(self):
        """Start jellyfin-mpv-shim subprocess."""
        if not self.config.auto_start_jms:
            self.log("Auto-start JMS disabled, skipping JMS startup", "STARTUP")
            return

        self.log(f"Starting jellyfin-mpv-shim: {self.config.jms_binary} {' '.join(self.config.jms_args)}", "STARTUP")

        try:
            # Open log file for JMS
            jms_log = open("jms.log", "w")

            # Build command: binary + args
            jms_command = [self.config.jms_binary] + self.config.jms_args

            self.jms_process = subprocess.Popen(
                jms_command,
                stdout=jms_log,
                stderr=subprocess.STDOUT,
                preexec_fn=os.setsid
            )

            self.log(f"JMS started with PID {self.jms_process.pid}", "STARTUP")

            # Wait a moment and check if JMS is still running
            time.sleep(2)
            if self.jms_process.poll() is not None:
                jms_log.close()
                try:
                    with open("jms.log", "r") as f:
                        log_content = f.read()
                    raise Exception(f"JMS exited immediately. Log content: {log_content}")
                except FileNotFoundError:
                    raise Exception("JMS exited immediately and no log file was created")

            self.log("JMS started successfully", "STARTUP")

        except Exception as e:
            self.log(f"ERROR starting JMS: {e}", "ERROR")
            raise

    def forward_event_to_jms(self, event_data: Dict[str, Any]):
        """Forward MPV events to all active JMS connections."""
        if not self.client_connections:
            return

        # Log the event
        self.log_ipc("MPV->JMS", event_data)

        # Send to all active JMS connections
        event_json = json.dumps(event_data) + '\n'
        disconnected_connections = []

        for reader, writer in self.client_connections:
            try:
                writer.write(event_json.encode('utf-8'))
                # Note: We can't await drain() here since this might be called from sync context
                # The event loop will handle flushing
            except Exception as e:
                self.log(f"Error forwarding event to JMS connection: {e}", "ERROR")
                disconnected_connections.append((reader, writer))

        # Clean up disconnected connections
        for conn in disconnected_connections:
            try:
                self.client_connections.remove(conn)
            except ValueError:
                pass

    def filter_command(self, command_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Filter commands using the rule-based system.

        Returns None if command should be blocked, otherwise returns the command_data.
        """
        # Check the rule-based filtering system
        should_filter, reason = self.config.check_command_filter(command_data)

        if should_filter:
            if self.config.log_filtered_commands:
                command = command_data.get('command', [])
                self.log(f"FILTERED: {command} - {reason}", "FILTER")
            return None

        return command_data

    def execute_filtered_command(self, command_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a command through the filter."""
        request_id = command_data.get('request_id', 0)

        # Log incoming command
        self.log_ipc("JMS->MPV", command_data, request_id)

        # Apply filtering
        filtered_command_data = self.filter_command(command_data)

        if filtered_command_data is None:
            # Command was blocked, return fake success
            response = {"request_id": request_id, "error": "success"}
            self.log_ipc("MPV->JMS", response, request_id)
            return response

        try:
            # Execute command on real MPV
            command = filtered_command_data.get('command', [])
            if command:
                result = self.mpv.command(*command)
            else:
                result = None

            response = {
                "request_id": request_id,
                "error": "success"
            }

            if result is not None:
                response["data"] = result

            self.log_ipc("MPV->JMS", response, request_id)
            return response

        except MPVError as e:
            response = {"request_id": request_id, "error": str(e)}
            self.log_ipc("MPV->JMS", response, request_id)
            return response
        except Exception as e:
            self.log(f"Unexpected error executing command {command}: {e}", "ERROR")
            response = {"request_id": request_id, "error": "command failed"}
            self.log_ipc("MPV->JMS", response, request_id)
            return response

    async def handle_jms_connection(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """Handle a connection from JMS."""
        client_addr = writer.get_extra_info('peername', 'unknown')
        self.log(f"JMS client connected: {client_addr}")

        # Add to active connections for event forwarding
        self.client_connections.append((reader, writer))

        try:
            while not self._shutdown_event.is_set():
                # Read line from JMS
                try:
                    line = await asyncio.wait_for(reader.readline(), timeout=1.0)
                except asyncio.TimeoutError:
                    continue

                if not line:
                    break

                try:
                    # Parse JSON command
                    command_data = json.loads(line.decode('utf-8'))

                    # Execute filtered command
                    response = self.execute_filtered_command(command_data)

                    # Send response back to JMS
                    response_line = json.dumps(response) + '\n'
                    writer.write(response_line.encode('utf-8'))
                    await writer.drain()

                except json.JSONDecodeError as e:
                    self.log(f"JSON decode error: {e}", "ERROR")
                    continue
                except Exception as e:
                    self.log(f"Error processing command: {e}", "ERROR")
                    continue

        except asyncio.CancelledError:
            pass
        except Exception as e:
            self.log(f"Error in JMS connection handler: {e}", "ERROR")
        finally:
            try:
                writer.close()
                await writer.wait_closed()
            except Exception:
                pass

            # Remove from active connections
            try:
                self.client_connections.remove((reader, writer))
            except ValueError:
                pass

            self.log(f"JMS client disconnected: {client_addr}")

    async def start_proxy_server(self):
        """Start the proxy server that JMS connects to."""
        self.log(f"Starting proxy server on {self.config.spoof_socket_path}", "STARTUP")

        # Create Unix socket server
        self.proxy_server = await asyncio.start_unix_server(
            self.handle_jms_connection,
            str(self.config.spoof_socket_path)
        )

        # Set socket permissions
        os.chmod(self.config.spoof_socket_path, self.config.socket_permissions)
        self.log("Proxy server started successfully", "STARTUP")

    async def monitor_processes(self):
        """Monitor JMS process and exit if it dies."""
        if not self.config.auto_start_jms or not self.jms_process:
            # If we're not managing JMS, just wait for shutdown
            await self._shutdown_event.wait()
            return

        while not self._shutdown_event.is_set():
            if self.jms_process and self.jms_process.poll() is not None:
                self.log(f"JMS process exited with code {self.jms_process.returncode}", "ERROR")
                self._shutdown_event.set()
                break

            try:
                await asyncio.wait_for(self._shutdown_event.wait(), timeout=self.config.process_monitor_interval)
                break
            except asyncio.TimeoutError:
                continue

        self.log("Process monitor shutting down", "SHUTDOWN")

    def cleanup(self):
        """Clean up resources."""
        self.log("Cleaning up resources", "SHUTDOWN")

        # Cancel all tasks
        for task in self._tasks:
            if not task.done():
                task.cancel()

        # Close proxy server
        if self.proxy_server:
            self.proxy_server.close()

        # Terminate JMS process
        if self.jms_process:
            try:
                os.killpg(os.getpgid(self.jms_process.pid), signal.SIGTERM)
                try:
                    self.jms_process.wait(timeout=5)
                    self.log("JMS terminated gracefully", "SHUTDOWN")
                except subprocess.TimeoutExpired:
                    self.log("Force killing JMS", "SHUTDOWN")
                    os.killpg(os.getpgid(self.jms_process.pid), signal.SIGKILL)
                    self.jms_process.wait()
            except Exception as e:
                self.log(f"Error terminating JMS: {e}", "ERROR")

        # Terminate MPV
        if self.mpv:
            try:
                self.mpv.terminate()
                self.log("MPV terminated gracefully", "SHUTDOWN")
            except Exception as e:
                self.log(f"Error terminating MPV: {e}", "ERROR")

        # Clean up socket files
        try:
            if self.config.spoof_socket_path.exists():
                self.config.spoof_socket_path.unlink()
                self.log(f"Removed socket: {self.config.spoof_socket_path}", "SHUTDOWN")
        except Exception as e:
            self.log(f"Error removing socket: {e}", "ERROR")

    async def run(self):
        """Main entry point for running the proxy."""
        try:
            # Setup
            self.setup_socket_directory()
            self.start_mpv()

            # Start proxy server
            await self.start_proxy_server()

            # Wait for proxy server to be ready
            await asyncio.sleep(1)

            # Start JMS
            self.start_jms()

            # Start monitoring task
            monitor_task = asyncio.create_task(self.monitor_processes())
            self._tasks.append(monitor_task)

            # Serve forever (until shutdown event is set)
            self.log("Proxy running, waiting for connections...", "STARTUP")

            async with self.proxy_server:
                server_task = asyncio.create_task(self.proxy_server.serve_forever())
                self._tasks.append(server_task)

                # Wait for shutdown
                await self._shutdown_event.wait()

                # Cancel server task
                server_task.cancel()
                try:
                    await server_task
                except asyncio.CancelledError:
                    pass

        except KeyboardInterrupt:
            self.log("Received interrupt signal", "SHUTDOWN")
            self._shutdown_event.set()
        except Exception as e:
            self.log(f"Unexpected error: {e}", "ERROR")
            self._shutdown_event.set()
            raise
        finally:
            # Cleanup is handled by the caller
            pass
