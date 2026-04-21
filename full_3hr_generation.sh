#!/bin/bash
# 3-Hour Traffic Generation with Pre-Flight Checks
# Ensures all 3 apps are healthy before starting

set -e

echo "=========================================="
echo "WAF 3-HOUR TRAFFIC GENERATION"
echo "=========================================="
echo ""

# Configuration
DURATION_PER_APP=3600  # 1 hour per app
USERS=50
SPAWN_RATE=10

# Create logs directory
mkdir -p /tmp/locust_logs

echo "[PRE-FLIGHT] Checking all applications are responding..."
echo ""

# Test DVWA
echo -n "Testing DVWA (localhost:8081)... "
if curl -sf -o /dev/null http://localhost:8081/login.php; then
    echo "✅ OK"
else
    echo "❌ FAILED - DVWA not responding!"
    echo "Fix: docker start dvwa"
    exit 1
fi

# Test Juice Shop
echo -n "Testing Juice Shop (localhost:8082)... "
if curl -sf -o /dev/null http://localhost:8082/; then
    echo "✅ OK"
else
    echo "❌ FAILED - Juice Shop not responding!"
    echo "Fix: docker start juice"
    exit 1
fi

# Test WebGoat
echo -n "Testing WebGoat (localhost:8083)... "
if curl -sf -o /dev/null http://localhost:8083/WebGoat/login; then
    echo "✅ OK"
else
    echo "❌ FAILED - WebGoat not responding!"
    echo "Fix: docker start webgoat"
    exit 1
fi

echo ""
echo "[PRE-FLIGHT] ✅ All applications healthy!"
echo ""
echo "Starting traffic generation..."
echo "Total duration: 3 hours"
echo "Expected requests: 60,000-80,000"
echo ""

# Clear old logs (optional)

echo ""
echo "=========================================="
echo "[1/3] DVWA Traffic Generation (1 hour)"
echo "=========================================="
echo "Started: $(date)"
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
echo "DVWA complete: $(date)"
echo "Checking logs..."
wc -l /opt/homebrew/var/log/nginx/dvwa_access.log
echo ""

echo "=========================================="
echo "[2/3] Juice Shop Traffic Generation (1 hour)"
echo "=========================================="
echo "Started: $(date)"
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
echo "Juice Shop complete: $(date)"
echo "Checking logs..."
wc -l /opt/homebrew/var/log/nginx/juice_access.log
echo ""

echo "=========================================="
echo "[3/3] WebGoat Traffic Generation (1 hour)"
echo "=========================================="
echo "Started: $(date)"
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
echo "WebGoat complete: $(date)"
echo "Checking logs..."
wc -l /opt/homebrew/var/log/nginx/webgoat_access.log
echo ""

echo "=========================================="
echo "✅ TRAFFIC GENERATION COMPLETE!"
echo "=========================================="
echo "Finished: $(date)"
echo ""

# Final stats
echo "Final log counts:"
wc -l /opt/homebrew/var/log/nginx/*.log
echo ""

echo "Next steps:"
echo "  1. python3 parser/parse_nginx_logs.py"
echo "  2. python3 tokenizer/tokenize_requests.py"
echo "  3. python3 model/vocab.py"
echo "  4. python3 validate_data.py"
echo "  5. Start training!"
echo ""
