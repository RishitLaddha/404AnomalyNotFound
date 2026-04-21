# 404AnomalyNotFound

**Transformer-based Unsupervised Web Application Firewall**  
SIH Problem ID 25172 · ATLAS SkillTech University · uGDX School of Technology

> Trained exclusively on benign HTTP traffic. Detects zero-shot attacks through reconstruction error — no rules, no labeled attack data required.

---

## Live Links

| | |
|---|---|
| 🌐 Dashboard | [404-anomaly-not-found.vercel.app](https://404-anomaly-not-found.vercel.app) |
| 📓 Training Notebook | [waf-training-pinnacle (Kaggle)](https://www.kaggle.com/code/wsijdicudhincjfc/waf-training-pinnacle) |
| 📖 Full Wiki | [GitHub Wiki](https://github.com/RishitLaddha/404AnomalyNotFound/wiki) |

---

## What It Does

Most WAFs work from a list of known bad patterns — if an attacker uses a new variant, they slip through. This WAF flips the approach: train only on what *normal* looks like, then flag anything that doesn't fit.

An HTTP request is tokenized into an 87-token vocabulary, fed through a Transformer autoencoder, and reconstructed. If the reconstruction error is high, the request is structurally anomalous — blocked. If it's low, it passes. No signatures. No labels. No manual rules.

---

## Key Results

| Metric | Value |
|--------|-------|
| Block rate (demo attack set) | 89% |
| False positive rate | 0% |
| Score separation (benign vs attack) | ~10,000× |
| Training corpus | 77,000 benign requests |
| Model parameters | 1.41M |
| Training time | ~10 min (Kaggle T4 GPU) |
| Training epochs | 26 (early stop, 99.99% loss reduction) |

---

## Architecture

```
Client / Attacker
      │  HTTP Request
      ▼
waf_proxy.py  (:8000)
      │
      ├─ Tokenizer (87-token vocab)
      │
      ├─ Transformer Autoencoder (best.pt)
      │       encoder → latent z → decoder
      │
      ├─ Reconstruction Error = Anomaly Score
      │
      ├─ score > threshold ──► BLOCK (403) + MITRE tag + waf.log
      │
      └─ score ≤ threshold ──► ALLOW → target_app.py (:8080)

React Dashboard (Vercel) ◄── REST API ◄── WAF proxy (Render)
AI Assistant (Gemini) ◄── ngrok tunnel ◄── kali-server (:5001)
```

---

## Repository Structure

```
404AnomalyNotFound/
│
├── waf_proxy.py                  # WAF reverse proxy — FastAPI, scores every request
│
├── checkpoints/
│   ├── best.pt                   # Trained Transformer autoencoder weights
│   └── thresholds.json           # Calibrated anomaly threshold (mean + 3σ)
│
├── model/                        # Transformer architecture definitions
│   ├── config.py
│   ├── dataset.py
│   └── vocab.py
│
├── data/tokenized/
│   ├── benign_sequences.jsonl    # 77K tokenized benign HTTP requests
│   └── vocab.json                # 87-token vocabulary
│
├── tokenizer/                    # Tokenization pipeline
├── parser/                       # Nginx log parsing utilities
├── traffic/                      # Locust traffic generation scripts
│
├── Simulation-Sandbox/
│   └── target_app.py             # Intentionally vulnerable Flask app (:8080)
│
├── kali-server/                  # Kali Linux Docker + Flask API for attack tools
│   ├── server.py
│   └── Dockerfile
│
├── backend/                      # FastAPI backend (Render deployment)
├── frontend/                     # React + Vite dashboard (Vercel deployment)
│
├── waf-training-pinnacle-2.ipynb # Kaggle training notebook
├── render.yaml                   # Render deployment blueprint
├── flowchart.png                 # System flowchart
└── training_curves.png           # Model training loss curves
```

---

## Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- Docker Desktop
- ngrok (with reserved domain)

### 1. Clone

```bash
git clone https://github.com/RishitLaddha/404AnomalyNotFound.git
cd 404AnomalyNotFound
```

### 2. Install dependencies

```bash
pip install fastapi uvicorn aiohttp torch flask python-dotenv
cd frontend && npm install
```

### 3. Set up Kali Docker

```bash
docker pull kalilinux/kali-rolling
docker run -it kalilinux/kali-rolling /bin/bash
# inside Kali:
apt update && apt install -y sqlmap nmap nikto dirb gobuster
```

### 4. Run all three components simultaneously

```bash
# Terminal 1 — Vulnerable backend
python3 Simulation-Sandbox/target_app.py       # :8080

# Terminal 2 — WAF proxy
python3 waf_proxy.py                           # :8000

# Terminal 3 — AI Assistant tunnel
ngrok http --domain=tranquil-perm-swung.ngrok-free.dev 5001
```

### 5. Test it

```bash
# Benign — ALLOWED
curl http://localhost:8000/

# Attack — BLOCKED (403)
curl "http://localhost:8000/etc/passwd"
curl "http://localhost:8000/login?id=1 OR 1=1"
curl -H "User-Agent: <script>alert(1)</script>" http://localhost:8000/
```

---

## How the Model Works

**Tokenization**

HTTP requests are converted to a compact integer sequence using a path-segment-aware vocabulary:

```
GET /rest/products/5/reviews
→ [METHOD_GET, SEG_rest, SEG_products, SEG_NUM, SEG_reviews, STATUS_200]
```

**Training**

The Transformer autoencoder is trained only on benign traffic. It learns to reconstruct normal requests with near-zero MSE. Attack patterns — SQL keywords, path traversal sequences, script tags — produce structurally foreign token sequences that reconstruct poorly.

**Inference**

```
anomaly_score = MSE(original_tokens, reconstructed_tokens)

benign:  score ≈ 0.000001 – 0.000005
attack:  score ≈ 0.88 – 2.01
```

Threshold set at `mean + 3σ` of validation benign scores. Stored in `checkpoints/thresholds.json`.

---

## MITRE ATT&CK Coverage

| Technique | Description | Trigger |
|-----------|-------------|---------|
| T1190 | Exploit Public-Facing Application (SQLi) | `OR 1=1`, `UNION SELECT` |
| T1059 | Command & Scripting Interpreter (XSS) | `<script>`, `javascript:` |
| T1083 | File & Directory Discovery | `../`, `/etc/passwd` |
| T1078 | Valid Accounts (Auth bypass) | `/admin`, `/config` |

---

## WAF Effectiveness (Tool-by-Tool)

| Tool | Against :8080 (no WAF) | Against :8000 (WAF) |
|------|----------------------|---------------------|
| sqlmap | SQLi confirmed, DB extracted | No vulnerabilities — all payloads blocked |
| nikto | 9 vulnerabilities, server fingerprinted | Timed out, server obfuscated |
| dirb | `/admin`, `/config`, `/backup` found | Path traversal patterns blocked |
| gobuster | Sensitive endpoints enumerated | Burst flagged as anomalous, blocked |
| nmap | Ports and services fingerprinted | Fingerprinted (port scan is network-level, not HTTP) |

---

## Deployment

**Frontend (Vercel)**
```bash
cd frontend
npm run build
# Connect GitHub repo to Vercel — auto-deploys on push
```

**Backend + Kali (Render)**

Uses `render.yaml`. Connect GitHub repo to Render, set `GEMINI_API_KEY` as an environment variable.

---

## Team

| Name | App ID | GitHub |
|------|--------|--------|
| Rishit Laddha | 2309575 | [@RishitLaddha](https://github.com/RishitLaddha) |

**Faculty Guide:** Yogesh Haridas Jadhav  
**Institution:** ATLAS SkillTech University — uGDX School of Technology  
**SIH Problem ID:** 25172

---

## Evaluation

### Mid-Semester Demonstration

As part of the mid-semester evaluation, the project was demonstrated through real-world offensive security exercises to validate the AI assistant and WAF pipeline in live attack scenarios.

| Exercise | Link |
|----------|------|
| 🚩 Solving a web CTF challenge from RamadanCTF | [Watch Demo](https://drive.google.com/file/d/1LhToW1X4DoJMRezhrJa-c-8nH_E6W-g/view?usp=share_link) |
| 💻 Trying to solve machine "code" from HackTheBox | [Watch Demo](https://drive.google.com/file/d/1pJ0JHCokHbTdfUpVGRwUVV6panFhQ7MO/view?usp=share_link) |

The current submission is the **end-semester version** — a complete, deployed system with the full WAF pipeline, live dashboard, AI security assistant, and documented attack testing across sqlmap, nmap, nikto, dirb, and gobuster.

---

## References

- Vaswani et al., "Attention Is All You Need" — NeurIPS 2017
- Chandola et al., "Anomaly Detection: A Survey" — ACM Computing Surveys 2009
- Saxe & Berlin, "eXpose: Character-Level CNN for Malicious URLs" — 2017
- Strom et al., "MITRE ATT&CK: Design and Philosophy" — 2018
- OWASP Top 10 · MITRE ATT&CK Framework · OWASP ModSecurity CRS
