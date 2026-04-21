#!/usr/bin/env python3
"""
Endpoint Discovery & Validation
Tests which routes actually exist before running traffic generation
"""

import requests
import json
from urllib.parse import urljoin

def test_endpoints(base_url, endpoints, app_name):
    """Test which endpoints return 200/302 (valid) vs 404 (missing)"""
    print(f"\n{'='*60}")
    print(f"Testing {app_name} endpoints: {base_url}")
    print(f"{'='*60}\n")
    
    valid = []
    invalid = []
    
    for endpoint in endpoints:
        url = urljoin(base_url, endpoint)
        try:
            resp = requests.get(url, timeout=5, allow_redirects=False)
            status = resp.status_code
            
            if status in [200, 302, 301]:
                valid.append((endpoint, status))
                print(f"✅ {endpoint:50s} [{status}]")
            elif status == 404:
                invalid.append((endpoint, status))
                print(f"❌ {endpoint:50s} [404 NOT FOUND]")
            else:
                print(f"⚠️  {endpoint:50s} [{status}]")
        except requests.exceptions.RequestException as e:
            invalid.append((endpoint, "ERROR"))
            print(f"❌ {endpoint:50s} [ERROR: {e}]")
    
    print(f"\n{'='*60}")
    print(f"Results for {app_name}:")
    print(f"  Valid endpoints: {len(valid)}/{len(endpoints)}")
    print(f"  Invalid endpoints: {len(invalid)}/{len(endpoints)}")
    print(f"  Success rate: {(len(valid)/len(endpoints)*100):.1f}%")
    print(f"{'='*60}\n")
    
    return valid, invalid


def test_dvwa():
    """Test DVWA endpoints"""
    endpoints = [
        "/",
        "/login.php",
        "/setup.php",
        "/instructions.php",
        "/about.php",
        "/security.php",
        "/vulnerabilities/brute/",
        "/vulnerabilities/exec/",
        "/vulnerabilities/csrf/",
        "/vulnerabilities/fi/",
        "/vulnerabilities/sqli/",
        "/vulnerabilities/upload/",
        "/vulnerabilities/xss_r/",
        "/dvwa/css/main.css",
        "/dvwa/images/login_logo.png",
        "/favicon.ico"
    ]
    return test_endpoints("http://localhost:8081", endpoints, "DVWA")


def test_juice_shop():
    """Test Juice Shop endpoints"""
    endpoints = [
        "/",
        "/rest/products/search?q=",
        "/api/Challenges/",
        "/api/Products/1",
        "/api/Quantitys/",
        "/rest/basket/1",
        "/rest/captcha/",
        "/api/SecurityQuestions/",
        "/api/Deliverys/",
        "/rest/user/whoami",
        "/socket.io/?EIO=4&transport=polling",
        "/assets/public/favicon_js.ico",
        "/assets/public/images/JuiceShop_Logo.png",
        "/assets/i18n/en.json"
    ]
    return test_endpoints("http://localhost:8082", endpoints, "Juice Shop")


def test_webgoat():
    """Test WebGoat endpoints"""
    endpoints = [
        "/WebGoat/login",
        "/WebGoat/start.mvc",
        "/WebGoat/service/user.mvc",
        "/WebGoat/service/lessonoverview.mvc",
        "/WebGoat/service/statistics.mvc",
        "/WebGoat/css/main.css",
        "/WebGoat/images/logos/webgoat.png",
        "/WebGoat/favicon.ico"
    ]
    return test_endpoints("http://localhost:8083", endpoints, "WebGoat")


def generate_safe_config(dvwa_valid, juice_valid, webgoat_valid):
    """Generate configuration file with only valid endpoints"""
    config = {
        "dvwa": {
            "valid_endpoints": [ep for ep, _ in dvwa_valid],
            "success_rate": len(dvwa_valid) / 16 * 100
        },
        "juice_shop": {
            "valid_endpoints": [ep for ep, _ in juice_valid],
            "success_rate": len(juice_valid) / 13 * 100
        },
        "webgoat": {
            "valid_endpoints": [ep for ep, _ in webgoat_valid],
            "success_rate": len(webgoat_valid) / 8 * 100
        }
    }
    
    with open("validated_endpoints.json", "w") as f:
        json.dump(config, f, indent=2)
    
    print("\n" + "="*60)
    print("✅ Configuration saved to: validated_endpoints.json")
    print("="*60)
    print("\nUse these validated endpoints in your Locust scripts!")
    print("This ensures no 404 pollution in your training data.\n")


if __name__ == "__main__":
    print("\n🔍 ENDPOINT VALIDATION - Checking what actually exists...")
    print("This prevents 404s polluting your benign dataset\n")
    
    dvwa_valid, dvwa_invalid = test_dvwa()
    juice_valid, juice_invalid = test_juice_shop()
    webgoat_valid, webgoat_invalid = test_webgoat()
    
    generate_safe_config(dvwa_valid, juice_valid, webgoat_valid)
    
    # Overall assessment
    total_tested = 16 + 13 + 8  # Total endpoints across all apps
    total_valid = len(dvwa_valid) + len(juice_valid) + len(webgoat_valid)
    
    print("\n" + "="*60)
    print("OVERALL ASSESSMENT")
    print("="*60)
    print(f"Total endpoints tested: {total_tested}")
    print(f"Valid endpoints: {total_valid}")
    print(f"Invalid endpoints: {total_tested - total_valid}")
    print(f"Overall success rate: {(total_valid/total_tested*100):.1f}%")
    
    if total_valid / total_tested < 0.7:
        print("\n⚠️  WARNING: Less than 70% of endpoints are valid!")
        print("   Check if applications are running correctly.")
        print("   Consider adjusting Locust scripts to match your deployment.")
    else:
        print("\n✅ GOOD: Most endpoints are valid!")
        print("   Safe to proceed with traffic generation.")
    
    print("="*60 + "\n")