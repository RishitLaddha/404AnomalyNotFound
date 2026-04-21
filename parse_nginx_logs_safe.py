"""
Safe Nginx Log Parser for WAF Training
Filters out attack-surface endpoints so benign dataset stays clean
"""

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
    "dvwa":      "/opt/homebrew/var/log/nginx/dvwa_access.log",
    "juice_shop":"/opt/homebrew/var/log/nginx/juice_access.log",
    # WebGoat excluded entirely - 91% failures + attack-practice endpoints
}

OUTPUT_FILE = "data/parsed/benign_requests.csv"

# ──────────────────────────────────────────────────────────────
# DVWA: allow ONLY safe navigation pages
# Everything under /vulnerabilities/ is an attack surface -
# even browsing it with safe params teaches the model that
# hitting SQLi/XSS/RCE endpoints is normal.
# ──────────────────────────────────────────────────────────────
DVWA_ALLOWED_PATHS = {
    "/",
    "/login.php",
    "/logout.php",
    "/setup.php",
    "/about.php",
    "/instructions.php",
    "/security.php",
    "/phpinfo.php",
    "/dvwa/css/main.css",
    "/dvwa/css/login.css",
    "/dvwa/images/login_logo.png",
    "/dvwa/images/logo.png",
    "/favicon.ico",
}

# ──────────────────────────────────────────────────────────────
# Juice Shop: block only genuinely problematic endpoints
# Most Juice Shop traffic is legitimate e-commerce behavior
# ──────────────────────────────────────────────────────────────
JUICE_BLOCKED_PREFIXES = [
    "/api/Feedbacks",       # Can contain XSS payloads
    "/b2b/v2",              # XXE-vulnerable endpoint
    "/metrics",             # Internal metrics
]

# ──────────────────────────────────────────────────────────────
# Status codes that mean the request was attack-like or broken
# 400 = bad request, 405 = method not allowed, 5xx = server error
# We keep: 200, 201, 204, 301, 302, 304, 401, 403, 404
# 401/403/404 are normal app behavior (unauthenticated, not found)
# ──────────────────────────────────────────────────────────────
BLOCKED_STATUS = {"400", "405", "500", "502", "503", "504"}


def is_allowed(app, path, status):
    """Return True if this request should be kept in the benign dataset"""

    # Drop bad status codes universally
    if status in BLOCKED_STATUS:
        return False

    # DVWA: whitelist only safe pages
    if app == "dvwa":
        # Normalize numbered paths before checking
        clean = re.sub(r'/\d+', '/<num>', path)
        return clean in DVWA_ALLOWED_PATHS

    # Juice Shop: blacklist a few bad endpoints, allow rest
    if app == "juice_shop":
        for prefix in JUICE_BLOCKED_PREFIXES:
            if path.startswith(prefix):
                return False
        return True

    # Default: allow
    return True


def normalize_path(path):
    """Replace dynamic values with placeholders"""
    path = re.sub(r'/\d+', '/<num>', path)
    path = re.sub(r'[a-f0-9]{8,}', '<hex>', path)
    return path


def parse_request(req):
    parts = req.split()
    if len(parts) != 3:
        return None, None, None
    method, full_path, _ = parts
    parsed = urlparse(full_path)
    path   = normalize_path(parsed.path)
    params = list(parse_qs(parsed.query).keys())
    return method, path, ",".join(params)


def parse_logs():
    rows = []
    stats = {}

    for app, logfile in INPUT_LOGS.items():
        if not os.path.exists(logfile):
            print(f"[!] Missing log file: {logfile}")
            continue

        total = kept = dropped_status = dropped_path = 0

        with open(logfile) as f:
            for line in f:
                match = LOG_PATTERN.search(line)
                if not match:
                    continue

                total += 1
                status = match["status"]
                method, path, params = parse_request(match["request"])
                if not method:
                    continue

                raw_path = urlparse(match["request"].split()[1]).path

                if not is_allowed(app, raw_path, status):
                    if status in BLOCKED_STATUS:
                        dropped_status += 1
                    else:
                        dropped_path += 1
                    continue

                kept += 1
                rows.append({
                    "app":           app,
                    "method":        method,
                    "path":          path,
                    "query_params":  params,
                    "status":        status,
                    "user_agent":    match["ua"][:120],
                    "response_time": float(match["rt"])
                })

        stats[app] = {
            "total":          total,
            "kept":           kept,
            "dropped_status": dropped_status,
            "dropped_path":   dropped_path,
        }

    # Print filtering summary
    print()
    print("FILTERING SUMMARY")
    print("=" * 55)
    for app, s in stats.items():
        pct = (s["kept"] / s["total"] * 100) if s["total"] else 0
        print(f"{app}:")
        print(f"  Total:           {s['total']:>7,}")
        print(f"  Kept (clean):    {s['kept']:>7,}  ({pct:.1f}%)")
        print(f"  Dropped (status):{s['dropped_status']:>7,}")
        print(f"  Dropped (path):  {s['dropped_path']:>7,}")
    print("=" * 55)
    print(f"  TOTAL CLEAN:     {len(rows):>7,}")
    print()

    return rows


def save_csv(rows):
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    print("[*] Parsing nginx logs with attack-surface filtering...")
    print("[*] WebGoat excluded entirely (91% failures + attack endpoints)")
    print("[*] DVWA: whitelist-only (navigation pages)")
    print("[*] Juice Shop: blacklist a few bad endpoints")
    print()

    data = parse_logs()

    if not data:
        print("[!] No data after filtering! Check log paths.")
        exit(1)

    save_csv(data)
    print(f"[+] Saved {len(data):,} clean requests → {OUTPUT_FILE}")
