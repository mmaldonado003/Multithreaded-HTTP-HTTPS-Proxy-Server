"""
logging_utils.py
Maxmillion Maldonado
-------------
Logging utilities for the multithreaded HTTP/HTTPS proxy.

Provides functions to:
- Log individual HTTP/HTTPS requests
- Log blocked requests
- Generate a text summary of traffic
- Generate a top domains chart 

Usage:
Logging optional with matplotlib, use command below to install. 
pip install matplotlib
"""

import os
import json
import time
import uuid
import utils

# Paths for logs in folder
LOG_ROOT = "Logs"
TRAFFIC_LOGS = os.path.join(LOG_ROOT, "Website Traffic")
BLOCKED_LOGS = os.path.join(LOG_ROOT, "Blocked Logs")
SUMMARY_LOGS = os.path.join(LOG_ROOT, "Summary Logs")

def log_request(hostname, incoming_header, modified_header=None,
                server_response=None, response_sent=None,
                bytes_sent=None, bytes_received=None, duration=None, ttfb=None):
    """
    Logs a single HTTP/HTTPS request in JSON format, including headers, 
    bytes sent/received, duration, and TTFB. Only logs if LOG_FLAG is True.
    """
    if not utils.LOG_FLAG:
        return

    pathname = os.path.join(TRAFFIC_LOGS, hostname)
    os.makedirs(pathname, exist_ok=True)

    json_dict = {
        'Timestamp': time.strftime("%Y-%m-%d %H:%M:%S"),
        'Incoming header': incoming_header,
        'Modified header': modified_header,
        'Server response received': server_response,
        'Proxy response sent': response_sent,
        'Bytes sent': bytes_sent,
        'Bytes received': bytes_received,
        'Request duration (s)': duration,
        'TTFB (s)': ttfb
    }

    # Remove any keys with None values
    json_dict = {k: v for k, v in json_dict.items() if v is not None}
    filename = os.path.join(pathname, f"{hostname}_{uuid.uuid1()}.json")
    with open(filename, "w+") as outfile:
        json.dump(json_dict, outfile, indent=4)

def log_blocked_request(hostname, client_ip):
    """
    Logs a blocked request with timestamp, hostname, and client IP.
    Only writes if requested.
    """
    os.makedirs(BLOCKED_LOGS, exist_ok=True)
    filename = os.path.join(BLOCKED_LOGS, f"blocked_{uuid.uuid1()}.json")
    data = {
        "Timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "Blocked hostname": hostname,
        "Client IP": client_ip
    }
    with open(filename, "w+") as f:
        json.dump(data, f, indent=4)

def generate_text_summary(domain_stats):
    """
    Generates a text summary of domain stats including total requests,
    bytes sent/received, and top 5 domains by request count.
    """
    report_lines = []
    total_requests = sum(d['requests'] for d in domain_stats.values())
    total_bytes_sent = sum(d['bytes_sent'] for d in domain_stats.values())
    total_bytes_received = sum(d['bytes_received'] for d in domain_stats.values())

    report_lines.append(f"Total requests handled: {total_requests}")
    report_lines.append(f"Total bytes sent: {total_bytes_sent}")
    report_lines.append(f"Total bytes received: {total_bytes_received}\n")

    sorted_domains = sorted(domain_stats.items(), key=lambda x: x[1]['requests'], reverse=True)
    report_lines.append("Top 5 domains by request count:")

    for i, (domain, stats) in enumerate(sorted_domains[:5], 1):
        report_lines.append(
            f"{i}. {domain} - Requests: {stats['requests']}, "
            f"Avg Duration: {stats.get('avg_duration', 0):.3f}s, "
            f"Bytes Sent: {stats['bytes_sent']}, Bytes Received: {stats['bytes_received']}"
        )

    os.makedirs(SUMMARY_LOGS, exist_ok=True)
    text_summary_path = os.path.join(SUMMARY_LOGS, "summary_report.txt")
    with open(text_summary_path, "w+") as f:
        f.write("\n".join(report_lines))

def generate_chart(domain_stats):
    """
    Generates a bar graph of the top 5 domains by request count.
    Requires matplotlib; optional, will skip if not installed.
    """
    try:
        import matplotlib
        matplotlib.use('Agg')  
        import matplotlib.pyplot as plt
    except ImportError:
        print("Matplotlib not installed — skipping chart generation.")
        return

    sorted_domains = sorted(domain_stats.items(), key=lambda x: x[1]['requests'], reverse=True)[:5]
    if not sorted_domains:
        print("No domain data available for chart generation.")
        return

    domains = [d[0] for d in sorted_domains]
    requests = [d[1]['requests'] for d in sorted_domains]

    plt.bar(domains, requests)
    plt.title("Top 5 Domains by Requests")
    plt.ylabel("Request Count")
    plt.xticks(rotation=45)
    plt.tight_layout()

    os.makedirs(SUMMARY_LOGS, exist_ok=True)
    chart_path = os.path.join(SUMMARY_LOGS, "top_domains.png")
    plt.savefig(chart_path)
    plt.close()
    print(f"Chart saved to {chart_path}")

