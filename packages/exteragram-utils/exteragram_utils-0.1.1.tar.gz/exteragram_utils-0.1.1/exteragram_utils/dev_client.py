import argparse
import ast
import json
import logging
import os
import socket
import subprocess
import sys
import threading
import time
from dataclasses import dataclass
from threading import Lock, Event
from typing import Dict, Any, Optional, List, Tuple


@dataclass
class PluginMetadata:
    id: str
    name: str
    description: str
    author: str
    version: str
    icon: str
    min_version: str


@dataclass
class PendingRequest:
    request_id: int
    action: str
    event: Event
    response: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class AdbManager:
    def __init__(self):
        self.logger: logging.Logger = logging.getLogger("AdbManager")

    def run_command(self, command: List[str]) -> Optional[str]:
        try:
            result = subprocess.run(
                ["adb"] + command, check=True, capture_output=True, text=True
            )
            self.logger.debug(f"ADB command successful: {' '.join(command)}")
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            self.logger.error(f"ADB command failed: {e}")
            self.logger.error(f"Error output: {e.stderr}")
            return None

    def start_server(self):
        self.logger.info("Starting ADB server...")
        self.run_command(["start-server"])

    def wait_for_device(self):
        self.logger.info("Waiting for device to connect...")
        self.run_command(["wait-for-device"])
        self.logger.info("Device connected")

    def forward_port(self, local_port: int, remote_port: int) -> bool:
        self.logger.info(f"Forwarding port {local_port} to {remote_port}...")
        result = self.run_command(
            ["forward", f"tcp:{local_port}", f"tcp:{remote_port}"]
        )
        return result is not None

    def reverse_port(self, local_port: int, remote_port: int) -> bool:
        self.logger.info(f"Reverse forwarding port {remote_port}...")
        result = self.run_command(
            ["reverse", f"tcp:{local_port}", f"tcp:{remote_port}"]
        )
        return result is not None

    def setup_device(self, debug_mode: bool = False) -> bool:
        self.start_server()
        self.wait_for_device()

        main_success = self.forward_port(42690, 42690)

        if debug_mode:
            debug_success = self.forward_port(5678, 5678)
            return main_success and debug_success

        return main_success


class DeviceConnection:
    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 42690,
        debug_enabled: bool = False,
        debug_host: str = "127.0.0.1",
        debug_port: int = 5678,
        retry_delay: int = 2,
        response_timeout: int = 30,
    ):
        self.host: str = host
        self.port: int = port
        self.debug_enabled: bool = debug_enabled
        self.debug_host: str = debug_host
        self.debug_port: int = debug_port
        self.retry_delay: int = retry_delay
        self.response_timeout: int = response_timeout
        self.socket: Optional[socket.socket] = None
        self.connected: bool = False
        self.logger: logging.Logger = logging.getLogger("DeviceConnection")
        self.ping_thread: Optional[threading.Thread] = None
        self.response_thread: Optional[threading.Thread] = None
        self.running: bool = True
        self.request_id: int = 1

        self.pending_requests: Dict[int, PendingRequest] = {}
        self.requests_lock: Lock = Lock()

        self.response_buffer: bytes = b""
        self.buffer_lock: Lock = Lock()

    def connect(self) -> bool:
        if self.connected and self.socket:
            return True

        attempt: int = 1
        while self.running:
            try:
                self.logger.info(f"Connecting to device (attempt {attempt})...")
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.settimeout(1.0)  # Set timeout for non-blocking reads
                self.socket.connect((self.host, self.port))
                self.connected = True
                self.logger.info("Connected to device")

                if not self.response_thread or not self.response_thread.is_alive():
                    self.start_response_thread()

                if self.debug_enabled:
                    self.stop_debugger()
                    self.logger.info("Sent stop_debugger message")
                    time.sleep(0.5)
                    self.setup_debugger()

                if not self.ping_thread or not self.ping_thread.is_alive():
                    self.start_ping_thread()

                return True
            except Exception as e:
                self.logger.error(f"Connection attempt {attempt} failed: {e}")
                if self.socket:
                    self.socket.close()
                    self.socket = None
                self.connected = False

                self.logger.info(f"Retrying in {self.retry_delay} seconds...")
                time.sleep(self.retry_delay)
                attempt += 1

        return False

    def disconnect(self):
        self.running = False

        with self.requests_lock:
            for request in self.pending_requests.values():
                request.error = "Connection closed"
                request.event.set()
            self.pending_requests.clear()

        if self.socket:
            try:
                self.socket.close()
            except Exception as e:
                self.logger.error(f"Error closing connection: {e}")
            finally:
                self.socket = None
                self.connected = False
                self.logger.info("Disconnected from device")

    def start_response_thread(self):
        def response_reader():
            while self.running and self.connected:
                try:
                    data = self.socket.recv(4096)
                    if not data:
                        self.logger.error("Connection closed by server")
                        self.connected = False
                        break

                    with self.buffer_lock:
                        self.response_buffer += data
                        self._process_response_buffer()

                except socket.timeout:
                    continue
                except Exception as e:
                    if self.running:
                        self.logger.error(f"Error reading response: {e}")
                        self.connected = False
                    break

        self.response_thread = threading.Thread(target=response_reader, daemon=True)
        self.response_thread.start()
        self.logger.debug("Response reader thread started")

    def _process_response_buffer(self):
        buffer_str = self.response_buffer.decode("utf-8", errors="replace")
        pos = 0

        while pos < len(buffer_str):
            while pos < len(buffer_str) and buffer_str[pos].isspace():
                pos += 1

            if pos >= len(buffer_str):
                break

            try:
                json_obj, end_pos = json.JSONDecoder().raw_decode(buffer_str[pos:])
                self._handle_response(json_obj)
                pos += end_pos
            except json.JSONDecodeError:
                break

        self.response_buffer = buffer_str[pos:].encode("utf-8")

    def _handle_response(self, response: Dict[str, Any]):
        request_id = response.get("#")
        if request_id is None:
            self.logger.warning(f"Received response without request ID: {response}")
            return

        with self.requests_lock:
            pending_request = self.pending_requests.get(request_id)
            if pending_request:
                pending_request.response = response
                pending_request.event.set()
                del self.pending_requests[request_id]
                self.logger.debug(f"Matched response for request {request_id}")
            else:
                self.logger.warning(
                    f"Received response for unknown request ID: {request_id}"
                )

    def ping(self) -> bool:
        response = self.send_message("ping")
        return response is not None

    def start_ping_thread(self):
        def ping_worker():
            while self.running and self.connected:
                try:
                    if not self.ping():
                        self.logger.error("Ping failed, connection may be lost")
                        break
                    time.sleep(10)
                except Exception as e:
                    self.logger.error(f"Error in ping thread: {e}")
                    break

        self.ping_thread = threading.Thread(target=ping_worker, daemon=True)
        self.ping_thread.start()
        self.logger.debug("Ping thread started")

    def send_message(
        self, action: str, arguments: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        if not self.connected and not self.connect():
            return None

        with self.requests_lock:
            request_id = self.request_id
            self.request_id += 1

            pending_request = PendingRequest(
                request_id=request_id, action=action, event=Event()
            )
            self.pending_requests[request_id] = pending_request

        message = {
            "@": action,
            "#": request_id,
        }

        if arguments:
            message.update(arguments)

        try:
            data = json.dumps(message).encode("utf-8")
            self.socket.sendall(data)
            self.logger.debug(f"Sent message: {action} (ID: {request_id})")

            if pending_request.event.wait(timeout=self.response_timeout):
                if pending_request.error:
                    self.logger.error(
                        f"Request {request_id} failed: {pending_request.error}"
                    )
                    return None
                return pending_request.response
            else:
                with self.requests_lock:
                    if request_id in self.pending_requests:
                        del self.pending_requests[request_id]
                self.logger.error(
                    f"Request {request_id} timed out after {self.response_timeout}s"
                )
                return None

        except Exception as e:
            self.logger.error(f"Failed to send message: {e}")
            with self.requests_lock:
                if request_id in self.pending_requests:
                    del self.pending_requests[request_id]
            self.disconnect()
            if self.connect():
                return self.send_message(action, arguments)
            return None

    def get_plugins(self) -> Optional[Dict[str, Any]]:
        response = self.send_message("get_plugins")
        if response:
            response.pop("#", None)
            return response
        return None

    def write_plugin(self, plugin_id: str, content: str) -> bool:
        response = self.send_message(
            "write_plugin", {"plugin_id": plugin_id, "content": content}
        )
        return response is not None

    def reload_plugin(self, plugin_id: str) -> bool:
        response = self.send_message("reload_plugin", {"plugin_id": plugin_id})
        return response is not None

    def stop_debugger(self) -> bool:
        response = self.send_message("stop_debugger", {"platform": "vscode"})
        return response is not None

    def setup_debugger(self) -> bool:
        response = self.send_message(
            "start_debugger",
            {
                "host": self.debug_host,
                "port": self.debug_port,
                "platform": "vscode",
            },
        )
        return response is not None


# copied from plugins manager
def parse_metadata(content: str) -> Optional[PluginMetadata]:
    logger = logging.getLogger("metadata")
    metadata_dict = {}
    try:
        tree = ast.parse(content)
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if (
                        isinstance(target, ast.Name)
                        and target.id.startswith("__")
                        and target.id.endswith("__")
                    ):
                        if isinstance(node.value, ast.Constant):
                            metadata_dict[target.id[2:-2]] = node.value.value

        plugin_id = metadata_dict.get("id")
        plugin_name = metadata_dict.get("name")

        if not isinstance(plugin_id, str) or not plugin_id:
            raise ValueError(
                "Plugin metadata missing or invalid '__id__'. Must be a non-empty string."
            )
        if not isinstance(plugin_name, str) or not plugin_name:
            raise ValueError(
                "Plugin metadata missing or invalid '__name__'. Must be a non-empty string."
            )

        return PluginMetadata(
            id=plugin_id,
            name=plugin_name,
            description=metadata_dict.get("description"),
            author=metadata_dict.get("author"),
            version=metadata_dict.get("version"),
            icon=metadata_dict.get("icon"),
            min_version=metadata_dict.get("min_version"),
        )
    except Exception as e:
        logger.error(f"Error parsing plugin metadata from file: {e}")
        return None


class FileMonitor:
    def __init__(self, connection: DeviceConnection):
        self.connection: DeviceConnection = connection
        self.logger: logging.Logger = logging.getLogger("FileMonitor")
        self.file_metadata: Dict[str, Tuple[float, Optional[PluginMetadata]]] = {}
        self.running: bool = True

    def add_files(self, filenames: List[str]):
        for filename in filenames:
            if not os.path.isfile(filename):
                self.logger.error(f"File '{filename}' not found - skipping")
                continue

            content, metadata = self._read_file_and_metadata(filename)
            if metadata is None or not metadata.id:
                self.logger.error(
                    f"File '{filename}' has no valid plugin ID - skipping"
                )
                continue

            self.file_metadata[filename] = (os.path.getmtime(filename), metadata)

            self._upload_file(filename, content, metadata.id)
            self.logger.info(
                f"Added file '{filename}' with plugin ID '{metadata.id}' for monitoring"
            )

    def _read_file_and_metadata(
        self, filename: str
    ) -> Tuple[str, Optional[PluginMetadata]]:
        try:
            with open(filename, "r", encoding="utf-8") as f:
                content = f.read()

            metadata = parse_metadata(content)
            return content, metadata
        except Exception as e:
            self.logger.error(f"Error reading file '{filename}': {e}")
            return "", None

    def _upload_file(self, filename: str, content: str, plugin_id: str) -> bool:
        try:
            if self.connection.write_plugin(plugin_id, content):
                self.logger.info(f"Uploaded '{filename}' with plugin ID '{plugin_id}'")
                time.sleep(0.3)
                success = self.connection.reload_plugin(plugin_id)
                if success:
                    self.logger.info(f"Reloaded plugin '{plugin_id}'")
                else:
                    self.logger.warning(f"Failed to reload plugin '{plugin_id}'")
                return success
            self.logger.warning(f"Failed to upload '{filename}'")
            return False
        except Exception as e:
            self.logger.error(f"Error uploading file '{filename}': {e}")
            return False

    def start_monitoring(self):
        if not self.file_metadata:
            self.logger.warning("No valid files to monitor")
            return

        self.logger.info(f"Starting to monitor {len(self.file_metadata)} files")

        plugins = self.connection.get_plugins()
        if plugins:
            self.logger.info(f"Connected device has {len(plugins)} plugins loaded")

        try:
            while self.running:
                time.sleep(1)
                self._check_for_changes()
        except KeyboardInterrupt:
            self.logger.info("Monitoring stopped by user")
        finally:
            self.connection.stop_debugger()
            self.connection.disconnect()

    def _check_for_changes(self):
        for filename, (last_modified, metadata) in list(self.file_metadata.items()):
            try:
                if not os.path.isfile(filename):
                    self.logger.warning(
                        f"File '{filename}' no longer exists - skipping check"
                    )
                    continue

                current_modified = os.path.getmtime(filename)
                if current_modified != last_modified:
                    self.logger.info(f"File '{filename}' changed")

                    content, new_metadata = self._read_file_and_metadata(filename)

                    if new_metadata is None or not new_metadata.id:
                        self.logger.warning(
                            f"Modified file '{filename}' has no valid plugin ID - skipping update"
                        )
                        self.file_metadata[filename] = (current_modified, metadata)
                        continue

                    self._upload_file(filename, content, new_metadata.id)

                    self.file_metadata[filename] = (current_modified, new_metadata)

            except FileNotFoundError:
                self.logger.error(f"File '{filename}' not found during check")
            except PermissionError:
                self.logger.error(f"Permission denied when accessing '{filename}'")
            except Exception as e:
                self.logger.error(f"Error checking file '{filename}': {e}")


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Monitor plugins' changes and sync them to Android device."
    )
    parser.add_argument(
        "files", nargs="+", help="One or more files to monitor for changes"
    )
    parser.add_argument("--debug", action="store_true", help="Enable PyCharm debugger")
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Set the logging level",
    )
    return parser.parse_args()


def setup_logging(level: str):
    numeric_level: int = getattr(logging, level.upper(), None)
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(level=numeric_level, format=log_format)


def main():
    args = parse_arguments()
    setup_logging(args.log_level)
    logger = logging.getLogger("main")

    valid_files = [f for f in args.files if os.path.isfile(f)]
    if not valid_files:
        logger.error("None of the specified files exist. Exiting.")
        sys.exit(1)

    adb_manager = AdbManager()
    if not adb_manager.setup_device(args.debug):
        logger.error("Failed to set up ADB connection. Exiting.")
        sys.exit(1)

    connection = DeviceConnection(debug_enabled=args.debug)
    if not connection.connect():
        logger.error("Failed to establish connection to device. Exiting.")
        sys.exit(1)

    monitor = FileMonitor(connection)
    monitor.add_files(args.files)

    logger.info(
        f"Monitoring {len(args.files)} files for changes. Press Ctrl+C to stop."
    )
    monitor.start_monitoring()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
