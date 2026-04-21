#!/bin/bash
# Quick Traffic Generation Test - 15 minutes total
# Use this to validate setup before running the full 3-hour generation

set -e

echo "=========================================="
echo "QUICK TEST - 15 minute traffic generation"
echo "=========================================="
echo ""

DURATION=300  # 5 minutes per app
USERS=30
SPAWN_RATE=5

mkdir -p /tmp/locust_logs

echo "[1/3] Testing DVWA traffic (5 min)..."
locust -f traffic/dvwa_locust.py \
    --headless \
    --users $USERS \
    --spawn-rate $SPAWN_RATE \
    --run-time ${DURATION}s \
    --host http://localhost:8081 \
    --logfile /tmp/locust_logs/dvwa_test.log \
    --only-summary

echo ""
echo "[2/3] Testing Juice Shop traffic (5 min)..."
locust -f traffic/juice_locust.py \
    --headless \
    --users $USERS \
    --spawn-rate $SPAWN_RATE \
    --run-time ${DURATION}s \
    --host http://localhost:8082 \
    --logfile /tmp/locust_logs/juice_test.log \
    --only-summary

echo ""
echo "[3/3] Testing WebGoat traffic (5 min)..."
locust -f traffic/webgoat_locust.py \
    --headless \
    --users $USERS \
    --spawn-rate $SPAWN_RATE \
    --run-time ${DURATION}s \
    --host http://localhost:8083 \
    --logfile /tmp/locust_logs/webgoat_test.log \
    --only-summary

echo ""
echo "Quick test complete! Check nginx logs and verify traffic variety."
echo "If data looks good, run: ./run_traffic_generation.sh"
echo ""