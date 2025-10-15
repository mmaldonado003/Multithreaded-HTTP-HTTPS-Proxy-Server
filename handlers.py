"""
handlers.py
Maxmillion Maldonado
-------------
HTTP and HTTPS request handlers for the multithreaded proxy server.

Handlers provide:
- handle_http: handles standard HTTP requests
- handle_https: handles HTTPS CONNECT tunneling
- tunnel: utility function to relay data between sockets
- Updates statistics and optionally logs requests
"""

import socket
import threading
import time
import utils
from logging_utils import log_request
from utils import modify_headers, BUFFER_SIZE, update_domain_stats

def tunnel(from_socket, to_socket):
    """
    Relay data between two sockets until one closes.
    Returns the total number of bytes transferred.
    """
    total_bytes = 0
    try:
        while True:
            data = from_socket.recv(BUFFER_SIZE)
            if not data:
                break
            to_socket.sendall(data)
            total_bytes += len(data)
    except (socket.error, ConnectionResetError, BrokenPipeError):
        #Connection closed or reset 
        pass
    return total_bytes

def handle_http(client_socket, client_data, server_ip, server_port, hostname, start_time):
    """
    Handle a standard HTTP request:
    - Modify headers to ensure 'Connection: close'
    - Forward request to server
    - Relay server response to client
    - Track ttfb, bytes sent/received, and duration
    - Log if requested
    """
    total_bytes_sent = 0
    server_response = bytearray()
    ttfb_recorded = False
    ttfb = None
    try:
        modified_data = modify_headers(client_data, hostname)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.settimeout(5.0)
            server_socket.connect((server_ip, server_port))
            server_socket.sendall(modified_data.encode('utf-8'))
            while True:
                try:
                    chunk = server_socket.recv(BUFFER_SIZE)
                    if not chunk:
                        break
                    client_socket.sendall(chunk)
                    total_bytes_sent += len(chunk)

                    # Record TTFB (first byte sent)
                    if not ttfb_recorded:
                        ttfb = time.perf_counter() - start_time
                        ttfb_recorded = True

                    # Keep partial server response for logging
                    if len(server_response) < 65536:
                        need = 65536 - len(server_response)
                        server_response.extend(chunk[:need])
                except socket.timeout:
                    continue

        duration = time.perf_counter() - start_time

        # Log request if logging enabled
        log_request(hostname, client_data,
                    modified_header=modified_data,
                    server_response=server_response.decode(errors="ignore") if server_response else "",
                    response_sent="HTTP/1.1 200 OK",
                    bytes_sent=total_bytes_sent,
                    bytes_received=len(client_data.encode('utf-8')),
                    duration=duration,
                    ttfb=ttfb)

        # Update statistics
        update_domain_stats(hostname, total_bytes_sent, len(client_data.encode('utf-8')), duration, ttfb)

    except Exception as e:
        print(f"HTTP error {e} for {hostname}")
        client_socket.close()

def handle_https(client_socket, server_ip, server_port, hostname, client_data, start_time):
    """
    Handle HTTPS CONNECT tunneling:
    - Establish connection to target server
    - Send 200 Connection Established to client
    - Tunnel data bidirectionally
    - Track bytes, duration, and optionally log
    """
    t1_bytes, t2_bytes = [], []
    ttfb = None
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.settimeout(2.0)
            server_socket.connect((server_ip, server_port))
            client_socket.sendall(b"HTTP/1.1 200 Connection Established\r\n\r\n")

            ttfb = time.perf_counter() - start_time # first byte sent
            
            thread1 = threading.Thread(target=lambda q, a, b: q.append(tunnel(a, b)), args=(t1_bytes, client_socket, server_socket))
            thread2 = threading.Thread(target=lambda q, a, b: q.append(tunnel(a, b)), args=(t2_bytes, server_socket, client_socket))

            thread1.start()
            thread2.start()
            thread1.join()
            thread2.join()

            total_bytes_sent = sum(t2_bytes)
            total_bytes_received = sum(t1_bytes)
            duration = time.perf_counter() - start_time

            # Log request if logging enabled
            log_request(hostname, client_data,
                        response_sent="HTTP/1.1 200 Connection Established",
                        bytes_sent=total_bytes_sent,
                        bytes_received=total_bytes_received,
                        duration=duration,
                        ttfb=ttfb)

            # Update stats
            update_domain_stats(hostname, total_bytes_sent, total_bytes_received, duration, ttfb)
            
        client_socket.close()

    except Exception as e:
        print(f"HTTPS error {e} for {hostname}")
        client_socket.close()
