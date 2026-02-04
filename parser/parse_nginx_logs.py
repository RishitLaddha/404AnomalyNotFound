import re
import csv
import os
from urllib.parse import urlparse, parse_qs

LOG_PATTERN = re.compile(
    r'(?P<ip>\S+) \[(?P<time>[^\]]+)\] '
    r'"(?P<request>[^"]+)" (?P<status>\d+) '
    r'"(?P<ua>[^"]*)" rt=(?P<rt>[0-9.]+)'
)

INPUT_LOGS = {
    "dvwa": "/opt/homebrew/var/log/nginx/dvwa_access.log",
    "juice_shop": "/opt/homebrew/var/log/nginx/juice_access.log",
    "webgoat": "/opt/homebrew/var/log/nginx/webgoat_access.log",
}

OUTPUT_FILE = "data/parsed/benign_requests.csv"

def normalize_path(path):
    # replace numbers, UUIDs, hex tokens
    path = re.sub(r'/\d+', '/<num>', path)
    path = re.sub(r'[a-f0-9]{8,}', '<hex>', path)
    return path

def parse_request(req):
    parts = req.split()
    if len(parts) != 3:
        return None, None, None

    method, full_path, protocol = parts
    parsed = urlparse(full_path)

    path = normalize_path(parsed.path)
    params = list(parse_qs(parsed.query).keys())

    return method, path, ",".join(params)

def parse_logs():
    rows = []

    for app, logfile in INPUT_LOGS.items():
        if not os.path.exists(logfile):
            print(f"[!] Missing log file: {logfile}")
            continue

        with open(logfile) as f:
            for line in f:
                match = LOG_PATTERN.search(line)
                if not match:
                    continue

                method, path, params = parse_request(match["request"])
                if not method:
                    continue

                rows.append({
                    "app": app,
                    "method": method,
                    "path": path,
                    "query_params": params,
                    "status": match["status"],
                    "user_agent": match["ua"][:120],
                    "response_time": float(match["rt"])
                })

    return rows

def save_csv(rows):
    with open(OUTPUT_FILE, "w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=rows[0].keys()
        )
        writer.writeheader()
        writer.writerows(rows)

if __name__ == "__main__":
    data = parse_logs()
    print(f"[+] Parsed {len(data)} requests")
    save_csv(data)
    print(f"[+] Saved to {OUTPUT_FILE}")

