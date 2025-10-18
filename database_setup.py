"""
database_setup.py
Maxmillion Maldonado
-------------
Database schema setup for the multithreaded HTTP/HTTPS proxy.
NOT currently utilized in Proxy, built for early iterations. 

Creates SQLite database with tables for:
- requests: All successful HTTP/HTTPS requests with performance metrics
- blocked_requests: Security audit log of blocked domains
- rate_limit_violations: Rate limiting enforcement log

Usage:
Run once to initialize database:
python database_setup.py
"""

import sqlite3
import os

DB_DIR = os.path.join('Logs', 'Database')
DB_PATH = os.path.join(DB_DIR, 'proxy_traffic.db')

def create_database():
    """
    Create the SQLite database and tables if they don't exist.
    Tables track requests, blocked requests, and rate limit violations.
    """
    # Create Database directory inside Logs
    os.makedirs(DB_DIR, exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Requests table - stores each individual request with metrics
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            source_ip TEXT NOT NULL,
            destination_host TEXT NOT NULL,
            destination_port INTEGER,
            request_method TEXT,
            protocol TEXT,
            bytes_sent INTEGER DEFAULT 0,
            bytes_received INTEGER DEFAULT 0,
            duration_seconds REAL,
            ttfb_seconds REAL
        )
    ''')
    
    # Blocked requests table - security audit log
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS blocked_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            source_ip TEXT NOT NULL,
            blocked_hostname TEXT NOT NULL,
            reason TEXT DEFAULT 'Blocklist'
        )
    ''')
    
    # Rate limit violations table - tracks rate limiting enforcement
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS rate_limit_violations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            source_ip TEXT NOT NULL,
            request_count INTEGER
        )
    ''')
    
    conn.commit()
    conn.close()
    print(f"Database '{DB_PATH}' created with 3 tables.")
    print("Tables: requests, blocked_requests, rate_limit_violations")

if __name__ == "__main__":
    create_database()