"""
main.py
Maxmillion Maldonado
-------------
Entry point for the multithreaded HTTP/HTTPS proxy server.

Main script for Proxy that:
- Starts the proxy listener on a specified port
- Optionally enables logging when started with the 'Log' argument
- Handles shutdown and triggers summary generation if logging is enabled

Usage:
Starts the proxy without logging:
python main.py [PORT]
        
Starts the proxy with logging enabled. Logs are saved 
under the "Logs" directory (Must have matplotlib installed for graph):
python main.py [PORT] Log

Optional Dependency (for charts) in Log command:
pip install matplotlib
"""

import sys
import socket
import threading
import os
import shutil
import json
import utils

# Local module imports
from proxy import proxy
from logging_utils import generate_text_summary, generate_chart
from utils import domain_stats

def main():
    """
    Starts the HTTP/HTTPS proxy server and listens for incoming client connections.
    If 'Log' is passed as a command-line argument, request and summary logs are made.
    """

    if len(sys.argv) not in (2, 3):
        print("Usage: python main.py PORT [Log]")
        sys.exit()

    port = int(sys.argv[1])

    # Enable logging if specified in command
    if len(sys.argv) == 3 and sys.argv[2] == "Log":
        utils.LOG_FLAG = True
        if os.path.isdir("Logs"):
            try:
                shutil.rmtree("Logs")
            except Exception:
                pass
        os.makedirs("Logs", exist_ok=True)

    # Create the main listening socket
    proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    proxy_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    proxy_socket.settimeout(1.0)
    proxy_socket.bind(('', port))
    proxy_socket.listen(50)
    print(f"HTTP proxy listening on port {port}")

    try:
        # Main accept loop for handling clients
        while True:
            try:
                client_socket, client_IP = proxy_socket.accept()
                t = threading.Thread(target=proxy, args=(client_socket, client_IP), daemon=True)
                t.start()
                print(f"Connected client: {client_IP}")
            except socket.timeout:
                continue
    except KeyboardInterrupt:
        # Shutdown and summary log made (if enabled)
        print("\nKeyboard Interrupt: Closing proxy")

        if utils.LOG_FLAG:
            # Compute averages and clean up stats
            for stats in domain_stats.values():
                if stats['requests'] > 0:
                    stats['avg_duration'] = stats['total_duration'] / stats['requests']
                    stats['avg_ttfb'] = stats['total_ttfb'] / stats['requests']
                else:
                    stats['avg_duration'] = 0
                    stats['avg_ttfb'] = 0
                stats.pop('total_duration', None)
                stats.pop('total_ttfb', None)

            # Save JSON summary
            os.makedirs("Logs/Summary Logs", exist_ok=True)
            summary_path = os.path.join("Logs/Summary Logs", "summary.json")
            with open(summary_path, "w+") as summary_file:
                json.dump(domain_stats, summary_file, indent=4)

            # Generate text summary and chart
            generate_text_summary(domain_stats)
            generate_chart(domain_stats)
            print("All summaries, charts, and JSON generated in Logs/")
            
        proxy_socket.close()
        os._exit(1)

if __name__ == "__main__":
    main()
