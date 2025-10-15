"""
utils.py
Maxmillion Maldonado
-------------
Utility functions and global constants for the HTTP/HTTPS proxy.

Contains:
- BUFFER_SIZE, MAX_HEADER_SIZE, LOG_FLAG
- Thread-safe domain_stats tracking
- Header modification for proxying
"""

import threading
import re

# GLOBAL CONSTANTS
BUFFER_SIZE = 65536
MAX_HEADER_SIZE = 8192
LOG_FLAG = False  # Enable logging

# DOMAIN STATISTICS
domain_stats = {}
domain_stats_lock = threading.Lock()

def update_domain_stats(hostname, bytes_sent, bytes_received, duration, ttfb=None):
    """
    Update the domain statistics.
    Tracks request count, bytes sent/received, total duration, and optional ttfb
    """
    with domain_stats_lock:
        if hostname not in domain_stats:
            domain_stats[hostname] = {
                'requests': 0,
                'bytes_sent': 0,
                'bytes_received': 0,
                'total_duration': 0,
                'total_ttfb': 0
            }
        stats = domain_stats[hostname]
        stats['requests'] += 1
        stats['bytes_sent'] += bytes_sent
        stats['bytes_received'] += bytes_received
        stats['total_duration'] += duration
        if ttfb is not None:
            stats['total_ttfb'] += ttfb

def modify_headers(request_str, hostname=None):
    """
    Modify HTTP headers for proxying:
    - Ensures 'Connection: close' is set
    - Strips scheme and host from absolute URLs in request line
    """
    lines = request_str.split("\r\n")
    if not lines:
        return request_str
    
    # Modify request line if URL
    request_line = lines[0]
    parts = request_line.split(" ", 2)
    if len(parts) >= 2:
        method, target = parts[0], parts[1]
        m = re.match(r"^https?://[^/]+(/.*)$", target)
        if m:
            target = m.group(1)
            parts[1] = target
            lines[0] = " ".join(parts)
    
    # Ensure Connection closes
    new_lines = []
    found_connection = False
    for line in lines[1:]:
        if line.lower().startswith("connection:"):
            new_lines.append("Connection: close")
            found_connection = True
        else:
            new_lines.append(line)
    if not found_connection:
        try:
            blank_idx = new_lines.index('')
        except ValueError:
            blank_idx = len(new_lines)
        new_lines.insert(blank_idx, "Connection: close")

    return "\r\n".join([lines[0]] + new_lines)
