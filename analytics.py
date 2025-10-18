"""
analytics.py
Maxmillion Maldonado
-------------
Analytics for proxy database.

Provides functions to:
- Generate summary reports from database
- Query traffic statistics
- Export data to CSV for external analysis

Usage:
python analytics.py
"""

import sqlite3
from db_logger import DatabaseLogger
import os

DB_PATH = os.path.join('Logs', 'Database', 'proxy_traffic.db')

def generate_database_summary():
    """
    Generate summary report from database.
    Displays total requests, bandwidth, top domains, and security events
    """
    db = DatabaseLogger(DB_PATH)
    
    print("=" * 70)
    print("PROXY TRAFFIC DATABASE ANALYTICS")
    print("=" * 70)
    
    # Total requests
    total = db.get_total_requests()
    print(f"\nTotal Requests Logged: {total:,}")
    
    if total == 0:
        print("\nNo traffic data in database yet.")
        print("Run the proxy with logging enabled to collect data.")
        return
    
    # Bandwidth statistics
    stats = db.get_bandwidth_stats()
    if stats[0]:
        print(f"\nBandwidth Statistics:")
        print(f"  Total Bytes Sent:     {stats[0]:,} bytes ({stats[0]/1024/1024:.2f} MB)")
        print(f"  Total Bytes Received: {stats[1]:,} bytes ({stats[1]/1024/1024:.2f} MB)")
        print(f"  Average Duration:     {stats[2]:.3f} seconds")
        print(f"  Average TTFB:         {stats[3]:.3f} seconds")
    
    # Top domains
    print(f"\n{'Top 10 Domains by Request Count':-^70}")
    domains = db.get_top_domains(10)
    for i, (host, count, sent, received, duration) in enumerate(domains, 1):
        print(f"\n{i}. {host}")
        print(f"   Requests: {count:,} | Bytes Sent: {sent:,} | "
              f"Bytes Received: {received:,}")
        print(f"   Avg Duration: {duration:.3f}s")
    
    # Security statistics
    blocked = db.get_blocked_count()
    rate_limited = db.get_rate_limit_count()
    
    print(f"\n{'Security Statistics':-^70}")
    print(f"  Blocked Requests:        {blocked:,}")
    print(f"  Rate Limit Violations:   {rate_limited:,}")
    
    print("=" * 70)

def export_to_csv(output_file=None):
    """
    Export all requests from database to CSV file in Logs/Database/ folder.
    Overwrites existing CSV if present (like other logs).
    Useful for external analysis in Excel, pandas, etc.
    """
    # CSV location in Database folder
    if output_file is None:
        output_file = os.path.join('Logs', 'Database', 'traffic_export.csv')
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM requests')
    rows = cursor.fetchall()
    
    if not rows:
        print("No data to export.")
        conn.close()
        return
    
    # Ensure Database directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, 'w') as f:
        # Header
        f.write("id,timestamp,source_ip,dest_host,dest_port,method,protocol,"
                "bytes_sent,bytes_received,duration,ttfb\n")
        
        # Data rows
        for row in rows:
            f.write(','.join(str(x) if x is not None else '' for x in row) + '\n')
    
    conn.close()
    print(f"\nExported {len(rows):,} requests to {output_file}")

def query_specific_domain(domain):
    """
    Query all requests for a specific domain.
    For troubleshooting or an analyzing traffic patterns.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT timestamp, source_ip, bytes_sent, bytes_received, duration_seconds
        FROM requests
        WHERE destination_host = ?
        ORDER BY timestamp DESC
    ''', (domain,))
    
    results = cursor.fetchall()
    conn.close()
    
    if not results:
        print(f"No requests found for domain: {domain}")
        return
    
    print(f"\nRequests to {domain}:")
    print("-" * 70)
    for ts, ip, sent, recv, dur in results:
        print(f"{ts} | {ip} | Sent: {sent} | Recv: {recv} | Duration: {dur:.3f}s")

if __name__ == "__main__":
    generate_database_summary()
    
    # Export to CSV
    export_choice = input("\nExport data to CSV? (y/n): ").strip().lower()
    if export_choice == 'y':
        export_to_csv()
        print("Export complete! Check Database Folder in Logs!")