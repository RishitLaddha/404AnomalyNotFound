import csv
import json
import re

INPUT_CSV = "data/parsed/benign_requests.csv"
OUTPUT_JSONL = "data/tokenized/benign_sequences.jsonl"

def ua_bucket(ua):
    ua = ua.lower()
    if "chrome" in ua or "safari" in ua or "firefox" in ua:
        return "UA_BROWSER"
    if "curl" in ua or "python" in ua:
        return "UA_SCRIPT"
    return "UA_OTHER"

def rt_bucket(rt):
    if rt < 0.1:
        return "RT_FAST"
    if rt < 1.0:
        return "RT_MEDIUM"
    return "RT_SLOW"

def normalize_path_token(path):
    path = re.sub(r'[^a-zA-Z0-9/_\-<>]', '', path)
    return f"PATH_{path}"

def build_sequence(row):
    tokens = []

    tokens.append(f"APP_{row['app'].upper()}")
    tokens.append(f"METHOD_{row['method']}")
    tokens.append(normalize_path_token(row['path']))
    tokens.append(f"STATUS_{row['status']}")
    tokens.append(ua_bucket(row['user_agent']))
    tokens.append(rt_bucket(float(row['response_time'])))

    if row["query_params"]:
        for qp in row["query_params"].split(","):
            tokens.append(f"QP_{qp}")

    return tokens

def tokenize():
    with open(INPUT_CSV) as f, open(OUTPUT_JSONL, "w") as out:
        reader = csv.DictReader(f)

        for row in reader:
            sequence = build_sequence(row)
            out.write(json.dumps({
                "tokens": sequence
            }) + "\n")

if __name__ == "__main__":
    tokenize()
    print("[+] Tokenization complete")

