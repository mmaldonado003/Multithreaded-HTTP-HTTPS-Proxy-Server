# Multithreaded HTTP/HTTPS Proxy Server

**ALL FILES PERTAINING TO THE PROJECT CAN BE VIEWED ABOVE.**

## Objective
Network monitoring and security tool that handles concurrent 
connections, enforces security policies (domain blocking, rate limiting), 
and generates detailed analytics for IT operations and capacity planning.

Demonstrates practical application of network programming, security policy 
enforcement, and analytics.

## Key Features
| Feature                  | Description                                        | Business Impact                                         |
|---------------------------|---------------------------------------------------|--------------------------------------------------------|
| HTTP Request Routing      | Standard GET/POST handling                        | Enables reliable access to web resources and supports enterprise application traffic |
| HTTPS CONNECT Tunneling   | Secure site connections handled via tunneling    | Ensures encrypted traffic can pass securely, supporting privacy and regulatory compliance |
| Traffic Monitoring        | Logs all HTTP and HTTPS requests with metrics (TTFB, bandwidth, duration) | Provides audit trails for compliance, troubleshooting, and capacity planning |
| Domain Blocking           | Wildcard pattern matching for content filtering  | Enforces organizational policies, blocks websites, and ensures regulatory compliance |
| Rate Limiting             | Per-IP throttling (e.g., 100 req/10s) prevents abuse | Mitigates DDoS attacks, ensures fair resource allocation, and protects service quality |
| Performance Analytics     | Automated reports with charts and summaries      | Supports stakeholder reporting, operational insights, and infrastructure optimization |
| SQLite Database Backend   | Persistent storage of all traffic data for historical analysis | Enables trend analysis, complex queries, and data export for business intelligence tools |

## Example Logs

### Traffic Log (`Logs/Website Traffic/`):
Per-domain request logs (JSON)
```json
{
    "Timestamp": "2025-10-14 18:41:21",
    "Incoming header": "CONNECT aax.amazon-adsystem.com:443 HTTP/1.1\r\nUser-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:143.0) Gecko/20100101 Firefox/143.0\r\nProxy-Connection: keep-alive\r\nConnection: keep-alive\r\nHost: aax.amazon-adsystem.com:443\r\n\r\n",
    "Proxy response sent": "HTTP/1.1 200 Connection Established",
    "Bytes sent": 7404,
    "Bytes received": 5821,
    "Request duration (s)": 2.6146761999989394,
    "TTFB (s)": 0.04020260000106646
}
```

### Blocked Requests Log (`Logs/Blocked Logs/`):
Security audit logs
```json
{
    "Timestamp": "2025-10-14 18:42:15",
    "Blocked hostname": "www.youtube.com",
    "Client IP": "127.0.0.1"
}
```

### Summary Report (`Logs/Summary Logs/summary_report.txt`):
Analytics reports and charts
```
Total requests handled: 2118
Total bytes sent: 154905684
Total bytes received: 16713880

Top 5 domains by request count:
1. www.google.com - Requests: 52, Avg Duration: 2.480s, Bytes Sent: 2927190, Bytes Received: 275002
2. unagi.amazon.com - Requests: 47, Avg Duration: 2.408s, Bytes Sent: 196490, Bytes Received: 3231271
3. download.windowsupdate.com - Requests: 41, Avg Duration: 0.041s, Bytes Sent: 318790, Bytes Received: 11808
4. unagi-na.amazon.com - Requests: 38, Avg Duration: 2.308s, Bytes Sent: 221678, Bytes Received: 218702
5. s.amazon-adsystem.com - Requests: 32, Avg Duration: 2.425s, Bytes Sent: 241316, Bytes Received: 123745
```

### Database Analytics (`Logs/Database/`):
SQLite database with exportable CSV data
![CSV Export Example](Logs/Database/Traffic%20Export%20Database.png)

## Top Domains Bar Chart:
Shows the 5 most requested domains by number of requests.
![Top Domains Chart](Logs/Summary%20Logs/top_domains.png)

Generated only if `Log` option is enabled and matplotlib is installed.

## Tested With / Usage

- **Browsers:** Microsoft Edge, Chrome, Firefox
- **Local machine configuration (Windows):** added proxy in network settings using the port specified at launch
- Works for both HTTP and HTTPS traffic
- Supports multiple simultaneous clients

## Setup

### Clone the Repository:
```bash
git clone https://github.com/mmaldonado003/Multithreaded-HTTP-HTTPS-Proxy-Server.git
cd Multithreaded-HTTP-HTTPS-Proxy-Server
```

### Dependencies:
- Python 3.x
- **Optional (for charts)** — matplotlib:
```bash
pip install matplotlib
```

### Start the Proxy:

**Without logging:**
```bash
python3 main.py [PORT]
```

**With logging** (creates detailed logs, database, and charts in `Logs/`):
```bash
python3 main.py [PORT] Log
```

**Example:**
```bash
python3 main.py 8080 Log
```

### Folder Structure:
- `main.py` — entry point
- `proxy.py` — handles client connections
- `handlers.py` — HTTP/HTTPS request handling
- `logging_utils.py` — logs requests, blocked requests, summaries, and charts
- `utils.py` — shared constants and helper functions
- `db_logger.py` — SQLite database logging functions
- `database_setup.py` — database schema initialization
- `analytics.py` — query and export database analytics

### Database Analytics:

**View traffic statistics:**
```bash
python3 analytics.py
```

**Export data to CSV:**
```bash
python3 analytics.py
# Choose 'y' when prompted to export
```

**Output locations:**
- Database: `Logs/Database/proxy_traffic.db`
- CSV Export: `Logs/Database/traffic_export.csv`

## Technical Analysis

- **Performance:** Measures request duration and TTFB per domain
- **Load:** Identifies which domains consume the most bandwidth or requests
- **Blocking Efficacy:** Confirms blocked domains are logged and prevented from connecting
- **Rate Limiting:** Observes how rapid requests from a single IP are handled with 429 responses
- **Database Queries:** Supports complex analytics queries for historical trend analysis 

## Technical Details
Python 3.x | socket, threading, time, sqlite3 | HTTP/HTTPS protocol handling | SQLite database backend | Local machine proxy configuration
