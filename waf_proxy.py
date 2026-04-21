"""
Transformer WAF - Real-Time Proxy Server
=========================================
Sits between attacker/browser and target_app.py
Scores every request with trained transformer model
Blocks attacks, forwards benign traffic

Architecture:
  waf-stressor / browser
        ↓
  THIS PROXY (port 5000)
        ↓ benign only
  target_app.py (port 8080)

Usage:
  python3 waf_proxy.py

Then point waf-stressor at http://localhost:5000
"""

import time
import json
import math
import re
import logging
from datetime import datetime
from urllib.parse import urlparse, parse_qs

import torch
import torch.nn as nn
import httpx
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
import uvicorn

# ── Config ────────────────────────────────────────────────────
TARGET_APP   = "http://127.0.0.1:8080"   # Simulation-Sandbox target
WAF_PORT     = 8000
MODEL_PATH   = "checkpoints/best.pt"      # Downloaded from Kaggle
VOCAB_PATH   = "data/tokenized/vocab.json"
THRESHOLD    = None   # Auto-loaded from thresholds.json or calibrated
MAX_SEQ_LEN  = 12

# ── Logging ───────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("waf.log")
    ]
)
log = logging.getLogger("WAF")

# ── MITRE ATT&CK Mapping ──────────────────────────────────────
MITRE_MAP = {
    "SEG_vulnerabilities": ("T1190", "Exploit Public-Facing Application"),
    "SEG_sqli":            ("T1190", "SQL Injection"),
    "SEG_exec":            ("T1059", "Command & Scripting Interpreter"),
    "SEG_etc":             ("T1083", "File & Directory Discovery"),
    "SEG_passwd":          ("T1552", "Unsecured Credentials"),
    "SEG_shadow":          ("T1552", "Unsecured Credentials"),
    "SEG_admin":           ("T1078", "Valid Accounts - Admin Access"),
    "SEG_config":          ("T1592", "Gather Victim Host Information"),
    "SEG_upload":          ("T1105", "Ingress Tool Transfer"),
    "SEG_shell":           ("T1505", "Server Software Component - Webshell"),
    "SEG_cmd":             ("T1059", "Command & Scripting Interpreter"),
    "SEG_eval":            ("T1059", "Command & Scripting Interpreter"),
    "QP_UNION":            ("T1190", "SQL Injection - UNION Attack"),
    "QP_SELECT":           ("T1190", "SQL Injection - SELECT Statement"),
    "QP_DROP":             ("T1485", "Data Destruction"),
    "QP_script":           ("T1059", "Cross-Site Scripting"),
    "QP_alert":            ("T1059", "Cross-Site Scripting"),
    "SEG_wp-admin":        ("T1078", "Valid Accounts - CMS Admin"),
    "SEG_phpmyadmin":      ("T1078", "Valid Accounts - DB Admin"),
    "SEG_xmlrpc":          ("T1190", "XML-RPC Exploitation"),
}

def map_mitre(tokens):
    for token in tokens:
        if token in MITRE_MAP:
            tid, name = MITRE_MAP[token]
            return tid, name
    return "T1190", "Unknown Web Anomaly"


# ── Model Architecture (must match Kaggle training) ────────────
class PositionalEncoding(nn.Module):
    def __init__(self, d_model, max_len=5000):
        super().__init__()
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(
            torch.arange(0, d_model, 2).float() * (-math.log(10000.0) / d_model)
        )
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        self.register_buffer("pe", pe.unsqueeze(0))

    def forward(self, x):
        return x + self.pe[:, : x.size(1)]


class TransformerWAF(nn.Module):
    def __init__(self, vocab_size, d_model, nhead, num_enc, num_dec,
                 dim_ff, dropout, max_len):
        super().__init__()
        self.d_model     = d_model
        self.embedding   = nn.Embedding(vocab_size, d_model)
        self.pos_encoder = PositionalEncoding(d_model, max_len)
        enc_layer = nn.TransformerEncoderLayer(
            d_model, nhead, dim_ff, dropout, batch_first=True)
        dec_layer = nn.TransformerDecoderLayer(
            d_model, nhead, dim_ff, dropout, batch_first=True)
        self.encoder     = nn.TransformerEncoder(enc_layer, num_layers=num_enc)
        self.decoder     = nn.TransformerDecoder(dec_layer, num_layers=num_dec)
        self.output_proj = nn.Linear(d_model, vocab_size)

    def forward(self, src, tgt=None):
        if tgt is None:
            tgt = src
        scale   = math.sqrt(self.d_model)
        src_emb = self.pos_encoder(self.embedding(src) * scale)
        tgt_emb = self.pos_encoder(self.embedding(tgt) * scale)
        memory  = self.encoder(src_emb)
        output  = self.decoder(tgt_emb, memory)
        return self.output_proj(output)


# ── Tokenizer (matches your improved tokenizer) ───────────────
def ua_bucket(ua: str) -> str:
    ua = ua.lower()
    if any(b in ua for b in ["chrome", "safari", "firefox", "mozilla"]):
        return "UA_BROWSER"
    if any(b in ua for b in ["curl", "python", "httpx", "requests", "go-http"]):
        return "UA_SCRIPT"
    return "UA_OTHER"


def rt_bucket(rt: float) -> str:
    if rt < 0.05:  return "RT_VFAST"
    if rt < 0.1:   return "RT_FAST"
    if rt < 0.5:   return "RT_MEDIUM"
    if rt < 1.0:   return "RT_SLOW"
    return "RT_VSLOW"


def tokenize_path(path: str) -> list:
    parts = [p for p in path.strip("/").split("/") if p]
    tokens = []
    for part in parts:
        if part in ("<num>", "<hex>"):
            tokens.append(f"SEG_{part[1:-1].upper()}")
            continue
        part_clean = re.sub(r"\.[a-zA-Z0-9]+$", "", part)
        part_clean = re.sub(r"[^a-zA-Z0-9_\-]", "_", part_clean).strip("_")
        if part_clean:
            tokens.append(f"SEG_{part_clean[:30]}")
    return tokens or ["SEG_ROOT"]


def normalize_path(path: str) -> str:
    path = re.sub(r"/\d+", "/<num>", path)
    path = re.sub(r"[a-f0-9]{8,}", "<hex>", path)
    return path


def build_tokens(method: str, path: str, query_params: dict,
                 status: int, ua: str, rt: float, app: str = "UNKNOWN") -> list:
    tokens = []
    tokens.append(f"APP_{app.upper()}")
    tokens.append(f"METHOD_{method.upper()}")
    tokens.extend(tokenize_path(normalize_path(path)))
    tokens.append(f"STATUS_{status}")
    tokens.append(ua_bucket(ua))
    tokens.append(rt_bucket(rt))
    for key in list(query_params.keys())[:3]:   # max 3 QP tokens
        tokens.append(f"QP_{key[:20]}")
    return tokens


# ── WAF Engine ────────────────────────────────────────────────
class WAFEngine:
    def __init__(self):
        self.device    = torch.device("cpu")   # CPU is fine for inference
        self.vocab     = {}
        self.model     = None
        self.threshold = 0.001   # Default, overridden by thresholds.json
        self.stats     = {"total": 0, "blocked": 0, "allowed": 0}

    def load(self):
        # Load vocab
        with open(VOCAB_PATH) as f:
            self.vocab = json.load(f)
        log.info(f"Vocab loaded: {len(self.vocab)} tokens")

        # Load threshold
        try:
            with open("checkpoints/thresholds.json") as f:
                td = json.load(f)
            self.threshold = td.get("recommended_threshold",
                                    td.get("threshold_95", 0.001))
            log.info(f"Threshold loaded: {self.threshold:.6f}")
        except FileNotFoundError:
            log.warning("thresholds.json not found, using default 0.001")

        # Load model
        ckpt   = torch.load(MODEL_PATH, map_location=self.device)
        cfg    = ckpt.get("config", {})

        self.model = TransformerWAF(
            vocab_size = ckpt.get("vocab_size", len(self.vocab)),
            d_model    = cfg.get("d_model", 128),
            nhead      = cfg.get("nhead", 4),
            num_enc    = cfg.get("num_enc", 3),
            num_dec    = cfg.get("num_dec", 3),
            dim_ff     = cfg.get("dim_ff", 512),
            dropout    = cfg.get("dropout", 0.3),
            max_len    = cfg.get("max_len", MAX_SEQ_LEN),
        ).to(self.device)

        self.model.load_state_dict(ckpt["model_state_dict"])
        self.model.eval()
        log.info(f"Model loaded from epoch {ckpt.get('epoch','?')} "
                 f"(val_loss={ckpt.get('val_loss', 0):.6f})")

    def score(self, tokens: list) -> float:
        pad_id = self.vocab.get("<PAD>", 0)
        unk_id = self.vocab.get("<UNK>", 1)
        ids    = [self.vocab.get(t, unk_id) for t in tokens]
        if len(ids) < MAX_SEQ_LEN:
            ids += [pad_id] * (MAX_SEQ_LEN - len(ids))
        ids = ids[:MAX_SEQ_LEN]
        x   = torch.tensor([ids], dtype=torch.long).to(self.device)

        with torch.no_grad():
            out  = self.model(x, x)
            loss = nn.CrossEntropyLoss(reduction="none", ignore_index=0)(
                out.reshape(-1, out.size(-1)), x.reshape(-1)
            ).reshape(x.shape)
            mask  = (x != 0).float()
            score = ((loss * mask).sum() / mask.sum().clamp(min=1)).item()
        return score

    def inspect(self, method, path, query_params, ua, rt, app="DVWA"):
        tokens  = build_tokens(method, path, query_params, 200, ua, rt, app)
        score   = self.score(tokens)
        blocked = score > self.threshold
        self.stats["total"]   += 1
        if blocked:
            self.stats["blocked"] += 1
        else:
            self.stats["allowed"] += 1
        return score, blocked, tokens


# ── FastAPI App ───────────────────────────────────────────────
app    = FastAPI(title="Transformer WAF Proxy")
engine = WAFEngine()


@app.on_event("startup")
async def startup():
    engine.load()
    log.info("=" * 60)
    log.info("TRANSFORMER WAF PROXY STARTED")
    log.info(f"  Listening on:  http://0.0.0.0:{WAF_PORT}")
    log.info(f"  Forwarding to: {TARGET_APP}")
    log.info(f"  Threshold:     {engine.threshold:.6f}")
    log.info("=" * 60)


@app.api_route("/{path:path}", methods=["GET", "POST", "PUT",
                                         "DELETE", "PATCH", "HEAD", "OPTIONS"])
async def proxy(request: Request, path: str):
    t0     = time.time()
    method = request.method
    ua     = request.headers.get("user-agent", "")
    parsed = urlparse(str(request.url))
    qp     = parse_qs(parsed.query)
    full_path = "/" + path

    # Determine which app this maps to (simple heuristic)
    if "WebGoat" in full_path:
        app_name = "WEBGOAT"
    elif any(x in full_path for x in ["/rest/", "/api/", "/socket"]):
        app_name = "JUICE_SHOP"
    else:
        app_name = "DVWA"

    # Score the request
    rt    = time.time() - t0   # pre-response time (tiny, that's fine)
    score, blocked, tokens = engine.inspect(method, full_path, qp, ua, rt, app_name)

    timestamp = datetime.now().strftime("%H:%M:%S")

    if blocked:
        tid, technique = map_mitre(tokens)
        log.warning(
            f"🚨 BLOCKED  | {method:6} {full_path:<45} | "
            f"score={score:.4f} | {tid} - {technique}"
        )
        return JSONResponse(
            status_code=403,
            content={
                "waf":       "BLOCKED",
                "score":     round(score, 6),
                "threshold": round(engine.threshold, 6),
                "tokens":    tokens,
                "mitre": {
                    "technique_id":   tid,
                    "technique_name": technique,
                    "url": f"https://attack.mitre.org/techniques/{tid}/"
                },
                "timestamp": timestamp,
            }
        )

    # Forward benign request to target
    try:
        target_url = f"{TARGET_APP}/{path}"
        if parsed.query:
            target_url += f"?{parsed.query}"

        body = await request.body()

        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.request(
                method  = method,
                url     = target_url,
                headers = {k: v for k, v in request.headers.items()
                           if k.lower() not in ("host", "content-length")},
                content = body,
            )

        rt_final = time.time() - t0
        log.info(
            f"✅ ALLOWED  | {method:6} {full_path:<45} | "
            f"score={score:.6f} | status={resp.status_code} | {rt_final*1000:.0f}ms"
        )

        return Response(
            content    = resp.content,
            status_code= resp.status_code,
            headers    = dict(resp.headers),
        )

    except httpx.ConnectError:
        log.error(f"Cannot reach target {TARGET_APP} - is target_app.py running?")
        return JSONResponse(
            status_code=502,
            content={"error": "Target app unreachable",
                     "hint": f"Start target_app.py on {TARGET_APP}"}
        )


@app.get("/__waf/stats")
async def stats():
    """Live WAF statistics endpoint"""
    total   = engine.stats["total"]
    blocked = engine.stats["blocked"]
    allowed = engine.stats["allowed"]
    return {
        "total_requests":  total,
        "blocked":         blocked,
        "allowed":         allowed,
        "block_rate":      f"{blocked/total*100:.1f}%" if total else "0%",
        "threshold":       engine.threshold,
        "model":           MODEL_PATH,
    }


@app.get("/__waf/health")
async def health():
    return {"status": "ok", "threshold": engine.threshold,
            "vocab_size": len(engine.vocab)}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=WAF_PORT, log_level="warning")
