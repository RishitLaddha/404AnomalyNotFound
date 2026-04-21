#!/bin/bash
# 3-Hour Traffic Generation - Fully Non-Interactive

DURATION=3600
USERS=50
SPAWN_RATE=10

echo "=========================================="
echo "Starting 3-hour generation at $(date)"
echo "=========================================="

# DVWA (1 hour)
echo "[1/3] DVWA - Started $(date)"
locust -f traffic/dvwa_locust.py \
    --headless \
    --users $USERS \
    --spawn-rate $SPAWN_RATE \
    --run-time ${DURATION}s \
    --host http://localhost:8081 \
    --only-summary \
    --logfile /tmp/dvwa_locust.log 2>&1

echo "[1/3] DVWA - Complete $(date)"
wc -l /opt/homebrew/var/log/nginx/dvwa_access.log

# Juice Shop (1 hour)
echo "[2/3] Juice Shop - Started $(date)"
locust -f traffic/juice_locust.py \
    --headless \
    --users $USERS \
    --spawn-rate $SPAWN_RATE \
    --run-time ${DURATION}s \
    --host http://localhost:8082 \
    --only-summary \
    --logfile /tmp/juice_locust.log 2>&1

echo "[2/3] Juice Shop - Complete $(date)"
wc -l /opt/homebrew/var/log/nginx/juice_access.log

# WebGoat (1 hour)
echo "[3/3] WebGoat - Started $(date)"
locust -f traffic/webgoat_locust.py \
    --headless \
    --users $USERS \
    --spawn-rate $SPAWN_RATE \
    --run-time ${DURATION}s \
    --host http://localhost:8083 \
    --only-summary \
    --logfile /tmp/webgoat_locust.log 2>&1

echo "[3/3] WebGoat - Complete $(date)"
wc -l /opt/homebrew/var/log/nginx/webgoat_access.log

echo "=========================================="
echo "COMPLETE at $(date)"
wc -l /opt/homebrew/var/log/nginx/*.log
echo "Run: python3 parser/parse_nginx_logs.py"
echo "=========================================="
