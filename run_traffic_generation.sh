#!/bin/bash
# Master Traffic Generation Script for WAF Training Data
# Run time: 3 hours total (1 hour per app)

set -e

echo "=========================================="
echo "WAF Traffic Generation - 24H Sprint Mode"
echo "=========================================="
echo ""

# Configuration
DURATION_PER_APP=3600  # 1 hour per app = 3600 seconds
USERS=50               # Concurrent users per app
SPAWN_RATE=10          # Users spawned per second

# Create logs directory
mkdir -p /tmp/locust_logs

echo "[1/4] Starting DVWA traffic generation..."
echo "  - Duration: 1 hour"
echo "  - Users: $USERS"
echo "  - Target: ~15,000-20,000 requests"
echo ""

locust -f traffic/dvwa_locust.py \
    --headless \
    --users $USERS \
    --spawn-rate $SPAWN_RATE \
    --run-time ${DURATION_PER_APP}s \
    --host http://localhost:8081 \
    --logfile /tmp/locust_logs/dvwa.log \
    --only-summary

echo ""
echo "[2/4] Starting Juice Shop traffic generation..."
echo "  - Duration: 1 hour"
echo "  - Users: $USERS"
echo "  - Target: ~20,000-30,000 requests"
echo ""

locust -f traffic/juice_locust.py \
    --headless \
    --users $USERS \
    --spawn-rate $SPAWN_RATE \
    --run-time ${DURATION_PER_APP}s \
    --host http://localhost:8082 \
    --logfile /tmp/locust_logs/juice.log \
    --only-summary

echo ""
echo "[3/4] Starting WebGoat traffic generation..."
echo "  - Duration: 1 hour"
echo "  - Users: $USERS"
echo "  - Target: ~15,000-20,000 requests"
echo ""

locust -f traffic/webgoat_locust.py \
    --headless \
    --users $USERS \
    --spawn-rate $SPAWN_RATE \
    --run-time ${DURATION_PER_APP}s \
    --host http://localhost:8083 \
    --logfile /tmp/locust_logs/webgoat.log \
    --only-summary

echo ""
echo "=========================================="
echo "Traffic Generation Complete!"
echo "=========================================="
echo ""
echo "Next Steps:"
echo "  1. Check nginx logs in /opt/homebrew/var/log/nginx/"
echo "  2. Run: python parse_nginx_logs.py"
echo "  3. Run: python tokenize_requests.py"
echo "  4. Run: python validate_data.py"
echo ""
echo "Expected Results:"
echo "  - Total requests: 50,000-70,000"
echo "  - Unique patterns: 2,000-5,000+"
echo "  - Ready for training in ~10 minutes after processing"
echo ""