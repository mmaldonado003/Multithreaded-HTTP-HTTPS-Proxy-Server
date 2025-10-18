"""
db_logger.py
Maxmillion Maldonado
-------------
SQLite database logger for the multithreaded HTTP/HTTPS proxy.

Provides thread-safe logging functions:
- log_request: Log successful HTTP/HTTPS requests
- log_blocked_request: Log blocked domain attempts
- log_rate_limit_violation: Log rate limiting enforcement
- Query functions for analytics and reporting

"""

import sqlite3
import threading
from datetime import datetime
import os

DB_DIR = os.path.join('Logs', 'Database')
DB_PATH = os.path.join(DB_DIR, 'proxy_traffic.db')

class DatabaseLogger:
    """
    Database logger for proxy traffic.
    Logs requests, blocked attempts, and rate limit violations to SQLite
    """
    
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self.lock = threading.Lock()
    
    def log_request(self, source_ip, dest_host, dest_port, protocol,
                   bytes_sent, bytes_received, duration, ttfb, 
                   method='CONNECT'):
        """
        Log a successful HTTP/HTTPS request with performance metrics.
        """
        with self.lock:
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO requests 
                    (timestamp, source_ip, destination_host, destination_port,
                     request_method, protocol, bytes_sent, bytes_received,
                     duration_seconds, ttfb_seconds)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    datetime.now().isoformat(),
                    source_ip,
                    dest_host,
                    dest_port,
                    method,
                    protocol,
                    bytes_sent,
                    bytes_received,
                    duration,
                    ttfb
                ))
                
                conn.commit()
                conn.close()
            except Exception as e:
                print(f"Database logging error: {e}")
    
    def log_blocked_request(self, source_ip, blocked_hostname):
        """
        Log a blocked request attempt for security audit.
        """
        with self.lock:
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO blocked_requests 
                    (timestamp, source_ip, blocked_hostname, reason)
                    VALUES (?, ?, ?, ?)
                ''', (
                    datetime.now().isoformat(),
                    source_ip,
                    blocked_hostname,
                    'Blocklist'
                ))
                
                conn.commit()
                conn.close()
            except Exception as e:
                print(f"Database logging error (blocked): {e}")
    
    def log_rate_limit_violation(self, source_ip, request_count):
        """
        Log a rate limit violation for monitoring and security.
        """
        with self.lock:
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO rate_limit_violations 
                    (timestamp, source_ip, request_count)
                    VALUES (?, ?, ?)
                ''', (
                    datetime.now().isoformat(),
                    source_ip,
                    request_count
                ))
                
                conn.commit()
                conn.close()
            except Exception as e:
                print(f"Database logging error (rate limit): {e}")
    
    def get_total_requests(self):
        """Get total number of requests logged in database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM requests')
        count = cursor.fetchone()[0]
        conn.close()
        return count
    
    def get_top_domains(self, limit=10):
        """
        Get top domains by request count with aggregated statistics.
        Returns a list of tuples (hostname, request_count, bytes_sent, bytes_received, avg_duration)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT destination_host, 
                   COUNT(*) as request_count,
                   SUM(bytes_sent) as total_bytes_sent,
                   SUM(bytes_received) as total_bytes_received,
                   AVG(duration_seconds) as avg_duration
            FROM requests
            GROUP BY destination_host
            ORDER BY request_count DESC
            LIMIT ?
        ''', (limit,))
        
        results = cursor.fetchall()
        conn.close()
        return results
    
    def get_bandwidth_stats(self):
        """
        Get overall bandwidth and performance statistics.
        Returns a tuple (total_sent, total_received, avg_duration, avg_ttfb)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                SUM(bytes_sent) as total_sent,
                SUM(bytes_received) as total_received,
                AVG(duration_seconds) as avg_duration,
                AVG(ttfb_seconds) as avg_ttfb
            FROM requests
        ''')
        
        stats = cursor.fetchone()
        conn.close()
        return stats
    
    def get_blocked_count(self):
        """Get total number of blocked requests."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM blocked_requests')
        count = cursor.fetchone()[0]
        conn.close()
        return count
    
    def get_rate_limit_count(self):
        """Get total number of rate limit violations."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM rate_limit_violations')
        count = cursor.fetchone()[0]
        conn.close()
        return count