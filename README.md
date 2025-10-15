# Multithreaded HTTP/HTTPS Proxy Server

**ALL FILES PERTAINING TO THE PROJECT CAN BE VIEWED ABOVE.**

## Objective

The proxy handles multiple simultaneous connections, enforces rate limits, blocks specific domains, and records detailed statistics such as request count, bytes sent/received, TTFB (time to first byte), and overall request durations. In addition, the objective is to design and code the proxy from scratch, including multithreaded request handling, HTTPS tunneling, rate limiting, blocking, and logging. The goal overall was to create a fully functional proxy server with detailed performance insights.

## Setup

### Dependencies:
- Python 3.x
- **Optional (for charts)** — matplotlib:
```bash
  pip install matplotlib
```

### Start the Proxy:
- **Without logging:**
```bash
  python3 main.py [PORT]
```

- **With logging** (creates detailed logs and charts in `Logs/`):
```bash
  python3 main.py [PORT] Log
```

### Folder Structure:
- `main.py` — entry point
- `proxy.py` — handles client connections
- `handlers.py` — HTTP/HTTPS request handling
- `logging_utils.py` — logs requests, blocked requests, summaries, and charts
- `utils.py` — shared constants and helper functions

## Features & Capabilities

| Feature | Description | Verified |
|---------|-------------|----------|
| HTTP request routing | Standard GET/POST handling | ✓ |
| HTTPS CONNECT tunneling | Secure site connections handled via tunneling | ✓ |
| Blocklist enforcement | YouTube and related domains blocked | ✓ |
| Rate limiting | Rapid requests trigger 429 error responses (prevents overload) | ✓ |
| Logging | Logs created under `Logs/Website Traffic`, `Logs/Blocked Logs`, and `Logs/Summary Logs` | ✓ |
| Graceful shutdown | Ctrl + C generates summary JSON, text report, and chart | ✓ |

## Tested With / Usage

- **Browsers:** Microsoft Edge, Chrome, Firefox
- **Local machine configuration (Windows):** added proxy in network settings using the port specified at launch
- Works for both HTTP and HTTPS traffic
- Supports multiple simultaneous clients

## Example Logs

### Traffic Log (`Logs/Website Traffic/example.com/`):
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
```json
{
    "Timestamp": "2025-10-14 18:42:15",
    "Blocked hostname": "www.youtube.com",
    "Client IP": "127.0.0.1"
}
```

### Summary Report (`Logs/Summary Logs/summary_report.txt`):
```
Total requests handled: 1202
Total bytes sent: 73139325
Total bytes received: 9988055

Top 5 domains by request count:
1. fly.live.cnn.us.prd.media.max.com - Requests: 55, Avg Duration: 2.322s, Bytes Sent: 5492150, Bytes Received: 263549
2. s.amazon-adsystem.com - Requests: 28, Avg Duration: 2.420s, Bytes Sent: 187808, Bytes Received: 100542
3. m.media-amazon.com - Requests: 27, Avg Duration: 2.567s, Bytes Sent: 19834935, Bytes Received: 155551
4. unagi.amazon.com - Requests: 27, Avg Duration: 2.450s, Bytes Sent: 109544, Bytes Received: 2197401
5. unagi-na.amazon.com - Requests: 25, Avg Duration: 2.285s, Bytes Sent: 104939, Bytes Received: 121837
```

## Example Chart

### Top Domains Bar Chart:
- Shows the 5 most requested domains by number of requests.
![Top Domains Chart](Logs/Summary%20Logs/top_domains.png)
- Generated only if `Log` option is enabled and matplotlib is installed.

## Analysis

- **Performance:** Measures request duration and TTFB per domain.
- **Load:** Identifies which domains consume the most bandwidth or requests.
- **Blocking Efficacy:** Confirms blocked domains are logged and prevented from connecting.
- **Rate Limiting:** Observes how rapid requests from a single IP are handled with 429 responses.

## Technical Skills Developed

- Multithreaded socket programming in Python
- HTTP/HTTPS request parsing and header modification
- Rate limiting and domain blocking techniques
- JSON logging and automated summary generation
- Data visualization using Python (matplotlib)
- Practical proxy configuration on local machines

## Technical Details
Python 3.x | socket, threading, time | HTTP/HTTPS protocol handling | Local machine proxy configuration

