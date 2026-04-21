# 🛡️ Pinnacle WAF — Transformer-Based Anomaly Detection

**SIH Problem ID 25172** | Rishit Laddha

A production-ready Web Application Firewall using unsupervised deep learning. Trained exclusively on benign traffic, detects zero-shot attacks through reconstruction loss — no labeled attack data required.

## 🔗 Live Links
- **Website**: https://pinnacle-waf.vercel.app
- **API**: https://pinnacle-waf-api.onrender.com
- **Kali Server**: https://pinnacle-kali.onrender.com

---

## 📊 Key Results

| Metric | Value |
|--------|-------|
| Attacks blocked (live demo) | **5,555 / 8,180 (67.9%)** |
| Score separation (benign vs attack) | **10,000×** |
| Training sequences | 77,004 benign requests |
| Model parameters | 1.41M |
| Training epochs | 26 (99.99% loss reduction) |

---

## 🏗️ Architecture

```
Traffic Generation (Locust)
        ↓
Nginx Proxy Logging
        ↓
Safe Data Filtering (whitelist approach)
        ↓
Semantic Tokenization (path segments)
        ↓
Transformer Autoencoder Training (Kaggle T4 GPU)
        ↓
Real-Time WAF Proxy (FastAPI)
        ↓ score > 1.5 → BLOCK + MITRE map
        ↓ score ≤ 1.5 → ALLOW → target app
```

---

## 📁 Repository Structure

```
├── waf_proxy.py              # Real-time WAF proxy (FastAPI)
├── model/                    # Transformer architecture
│   ├── config.py
│   ├── dataset.py
│   └── vocab.py
├── parser/                   # Nginx log parsing
│   └── parse_nginx_logs.py
├── tokenizer/                # Request tokenization
│   └── tokenize_requests.py
├── traffic/                  # Locust traffic generation
│   ├── dvwa_locust.py
│   ├── juice_locust.py
│   └── webgoat_locust.py
├── MCP-Kali-Server/          # Kali Linux Docker + Gemini AI
│   ├── server.py             # Flask API wrapping Kali tools
│   ├── gemini_kali_client_v2.py
│   └── Dockerfile
├── Simulation-Sandbox/       # Target vulnerable app
│   └── target_app.py
├── data/
│   ├── parsed/               # Processed nginx logs
│   └── tokenized/            # Token sequences + vocab
├── checkpoints/
│   ├── best.pt               # Trained model weights
│   └── thresholds.json       # Calibrated anomaly thresholds
├── frontend/                 # React dashboard (Vercel)
├── backend/                  # FastAPI backend (Render)
└── kali-server/              # Kali Docker (Render)
```

---

## 🚀 Quick Start (Local)

### 1. Start Kali Docker
```bash
cd MCP-Kali-Server
docker build -t kali-waf-server .
docker run -d -p 5001:5000 --name kali kali-waf-server
```

### 2. Start WAF Proxy
```bash
pip install fastapi uvicorn httpx torch
python3 waf_proxy.py
# Runs on port 8000
```

### 3. Start Gemini Assistant
```bash
export GEMINI_API_KEY=your_key
export KALI_SERVER=http://localhost:5001
python3 MCP-Kali-Server/gemini_kali_client_v2.py
```

### 4. Test WAF
```bash
# Benign request → ALLOWED
curl http://localhost:8000/

# Attack → BLOCKED (403)
curl "http://localhost:8000/<script>alert(1)</script>"
curl "http://localhost:8000/etc/passwd"
```

---

## 🧠 Model Details

- **Architecture**: Transformer Autoencoder (Encoder-Decoder)
- **Training**: Benign-only (unsupervised anomaly detection)
- **Detection**: Reconstruction loss as anomaly score
- **Threshold**: 1.5 (calibrated at 10× max benign score)

### Tokenization
```
GET /rest/products/5/reviews → [APP_JUICE_SHOP, METHOD_GET,
                                 SEG_rest, SEG_products, SEG_NUM,
                                 SEG_reviews, STATUS_200, UA_SCRIPT, RT_VFAST]
```

---

## 🎯 MITRE ATT&CK Coverage

| Technique | Blocked |
|-----------|---------|
| T1190 - Exploit Public-Facing App | 3,821 |
| T1083 - File & Directory Discovery | 847 |
| T1078 - Valid Accounts (Admin) | 412 |
| T1592 - Gather Victim Host Info | 203 |
| T1552 - Unsecured Credentials | 134 |
| T1505 - Server Software Component | 89 |
| T1059 - Command & Scripting | 49 |

---

## 🔬 WAF Effectiveness Test

| | Port 8080 (No WAF) | Port 8000 (WAF) |
|--|--|--|
| Nikto scan | ✅ Completed (64s) | ❌ TIMED OUT |
| Vulnerabilities | 9 found | 0 useful |
| Server fingerprint | Werkzeug/3.1.3 leaked | Obfuscated |
| Python version | Leaked | Not leaked |

---

## 📦 Deployment

### Vercel (Frontend)
```bash
cd frontend
npm install
npm run build
# Deploy to Vercel via GitHub
```

### Render (Backend + Kali)
Uses `render.yaml` — connect GitHub repo to Render, set `GEMINI_API_KEY` environment variable.

---

## 🙏 References

- Vaswani et al., "Attention Is All You Need" (2017)
- OWASP Top 10 Web Application Security Risks
- MITRE ATT&CK Framework
- Chandola et al., "Anomaly Detection: A Survey" (2009)
