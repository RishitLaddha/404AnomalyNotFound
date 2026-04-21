"""
Improved Tokenizer for WAF Training
Preserves path structure instead of collapsing everything into one PATH_ token
This dramatically improves sequence diversity
"""

import csv
import json
import re

INPUT_CSV    = "data/parsed/benign_requests.csv"
OUTPUT_JSONL = "data/tokenized/benign_sequences.jsonl"

# ── Helpers ───────────────────────────────────────────────────

def ua_bucket(ua):
    ua = ua.lower()
    if "chrome" in ua or "safari" in ua or "firefox" in ua or "mozilla" in ua:
        return "UA_BROWSER"
    if "curl" in ua or "python" in ua or "locust" in ua or "requests" in ua:
        return "UA_SCRIPT"
    return "UA_OTHER"


def rt_bucket(rt):
    rt = float(rt)
    if rt < 0.05:  return "RT_VFAST"
    if rt < 0.1:   return "RT_FAST"
    if rt < 0.5:   return "RT_MEDIUM"
    if rt < 1.0:   return "RT_SLOW"
    return "RT_VSLOW"


def tokenize_path(path):
    """
    Split path into meaningful segment tokens instead of one big PATH_ blob.

    Examples:
      /login.php                    → [SEG_login]
      /rest/products/search         → [SEG_rest, SEG_products, SEG_search]
      /rest/products/<num>/reviews  → [SEG_rest, SEG_products, SEG_num, SEG_reviews]
      /api/Products/<num>           → [SEG_api, SEG_Products, SEG_num]
      /assets/i18n/en.json          → [SEG_assets, SEG_i18n, SEG_en_json]
    """
    # Strip leading slash, split on /
    parts = [p for p in path.strip("/").split("/") if p]

    tokens = []
    for part in parts:
        # Already-normalized placeholders
        if part in ("<num>", "<hex>"):
            tokens.append(f"SEG_{part[1:-1].upper()}")   # SEG_NUM, SEG_HEX
            continue

        # Strip extension (.php, .js, .css, .json, .png, .jpg, etc.)
        part_clean = re.sub(r'\.[a-zA-Z0-9]+$', '', part)

        # Sanitize: keep alphanumeric, underscore, hyphen
        part_clean = re.sub(r'[^a-zA-Z0-9_\-]', '_', part_clean)
        part_clean = part_clean.strip("_")

        if part_clean:
            tokens.append(f"SEG_{part_clean[:30]}")   # cap length

    # Fallback for root path
    if not tokens:
        tokens = ["SEG_ROOT"]

    return tokens


def build_sequence(row):
    tokens = []

    # App
    tokens.append(f"APP_{row['app'].upper()}")

    # Method
    tokens.append(f"METHOD_{row['method']}")

    # Path segments (richer than single PATH_ token)
    tokens.extend(tokenize_path(row["path"]))

    # Status
    tokens.append(f"STATUS_{row['status']}")

    # User-agent bucket
    tokens.append(ua_bucket(row["user_agent"]))

    # Response time bucket
    tokens.append(rt_bucket(row["response_time"]))

    # Query parameters (key names only, not values)
    if row["query_params"]:
        for qp in row["query_params"].split(","):
            qp = qp.strip()
            if qp:
                tokens.append(f"QP_{qp[:20]}")

    return tokens


def tokenize():
    sequences = []
    with open(INPUT_CSV) as f:
        reader = csv.DictReader(f)
        for row in reader:
            seq = build_sequence(row)
            sequences.append(seq)

    # Write output
    with open(OUTPUT_JSONL, "w") as out:
        for seq in sequences:
            out.write(json.dumps({"tokens": seq}) + "\n")

    # Report diversity
    unique = len(set(tuple(s) for s in sequences))
    total  = len(sequences)
    lengths = [len(s) for s in sequences]

    print(f"[+] Tokenization complete")
    print(f"    Total sequences:  {total:,}")
    print(f"    Unique sequences: {unique:,}")
    print(f"    Diversity:        {unique/total*100:.2f}%")
    print(f"    Seq length:       min={min(lengths)}, max={max(lengths)}, avg={sum(lengths)/len(lengths):.1f}")
    print(f"    Output:           {OUTPUT_JSONL}")


if __name__ == "__main__":
    tokenize()
