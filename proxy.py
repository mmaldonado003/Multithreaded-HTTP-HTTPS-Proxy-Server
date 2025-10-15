"""
proxy.py
Maxmillion Maldonado
-------------
Core proxy logic for the multithreaded HTTP/HTTPS server.

Functions:
- parse_server_info: Extract hostname, port, and method from client request.
- is_blocked: Check a hostname against BLOCKLIST.
- check_rate_limit: Enforce per-IP request limits.
- send_error: Send an HTTP error response to client.
- proxy: Main handler for a client connection, routes to HTTP/HTTPS handlers.
"""

import socket
import time
import threading
import utils
from handlers import handle_http, handle_https
from logging_utils import log_blocked_request

# Blocked domains (wildcard supported)
BLOCKLIST = ["*.youtube.com", "*.ytimg.com", "*.googlevideo.com"]

# Track per-IP request timestamps
request_counter = {}
request_counter_lock = threading.Lock()

def parse_server_info(client_data_bytes):
    """
    Parse the request from the client to extract hostname, server port, and method.
    Returns (hostname, port, is_connect, valid) or (None, None, None, False) if invalid.
    """
    try:
        client_text = client_data_bytes.decode('utf-8', 'ignore')
        lines = client_text.splitlines()
        if not lines:
            return None, None, None, False

        first_line = lines[0].strip()
        parts = first_line.split(" ", 2)
        if len(parts) < 2:
            return None, None, None, False

        method = parts[0].upper()
        target = parts[1]
        is_connect = method == "CONNECT"

        if is_connect:
            if ":" not in target:
                return None, None, None, False
            hostname, port_str = target.split(":", 1)
            server_port = int(port_str)
        else:
            import re
            m = re.match(r"^(https?://)?([^/:]+)(?::(\d+))?(/.*)?$", target)
            if not m:
                return None, None, None, False
            hostname = m.group(2)
            server_port = int(m.group(3)) if m.group(3) else (443 if target.startswith("https://") else 80)

        return hostname.lower(), server_port, is_connect, True
    except Exception:
        return None, None, None, False

def is_blocked(hostname):
    """
    Check if a hostname matches any pattern in BLOCKLIST
    Returns True if blocked, False if not.
    """
    import fnmatch
    for pattern in BLOCKLIST:
        if fnmatch.fnmatch(hostname, pattern):
            return True
    return False

def check_rate_limit(client_ip):
    """
    Enforce a per-IP rate limit: max 100 requests per 10-second window.
    Returns True if allowed, False if rate limit exceeded.
    """
    now = time.time()
    window = 10
    limit = 100

    with request_counter_lock:
        if client_ip not in request_counter:
            request_counter[client_ip] = []

        # Remove timestamps outside the current window
        request_counter[client_ip] = [t for t in request_counter[client_ip] if now - t < window]
        if len(request_counter[client_ip]) >= limit:
            return False

        request_counter[client_ip].append(now)

    return True

def send_error(client_socket, code, message):
    """
    Send a simple HTTP error response to the client and close the socket.
    """
    try:
        client_socket.sendall(f"HTTP/1.1 {code} {message}\r\n\r\n".encode())
    except:
        pass
    client_socket.close()

def proxy(client_socket, client_ip):
    """
    Main entry point for handling a single client connection.
    - Applies rate limiting
    - Parses request info
    - Checks blocking rules
    - Routes to HTTP or HTTPS handlers
    """
    client_socket.settimeout(1.0)
    client_ip_str = client_ip[0] if isinstance(client_ip, (list, tuple)) else str(client_ip)

    if not check_rate_limit(client_ip_str):
        print(f"Rate limit exceeded for {client_ip_str}")
        send_error(client_socket, 429, "Too Many Requests")
        return

    try:
        raw = client_socket.recv(utils.BUFFER_SIZE)
        if not raw:
            send_error(client_socket, 502, "Bad Gateway")
            return
        hostname, server_port, is_connect, valid = parse_server_info(raw)
        if not valid or hostname is None:
            send_error(client_socket, 400, "Bad Request")
            return
        client_data = raw.decode('utf-8', 'backslashreplace')
        if is_blocked(hostname):
            print(f"Blocked request to {hostname} from {client_ip_str}")
            if utils.LOG_FLAG:
                try:
                    log_blocked_request(hostname, client_ip_str)
                except Exception as e:
                    print(f"Failed to log blocked request: {e}")
            send_error(client_socket, 403, "Forbidden")
            return


        try:
            server_ip = socket.gethostbyname(hostname)
        except socket.gaierror:
            send_error(client_socket, 502, "Bad Gateway")
            return
        start_time = time.perf_counter()
        if is_connect:
            handle_https(client_socket, server_ip, server_port, hostname, client_data, start_time)
        else:
            handle_http(client_socket, client_data, server_ip, server_port, hostname, start_time)
            
    except Exception:
        client_socket.close()
