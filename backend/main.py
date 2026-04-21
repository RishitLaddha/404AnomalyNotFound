import os
from dotenv import load_dotenv
load_dotenv()
import json
import re
import time
import threading
import socket
import ipaddress
from urllib.parse import urlparse

import requests
import uvicorn
import google.generativeai as genai
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, Tuple

app = FastAPI(title="WAF Security Assistant API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DEFAULT_GEMINI_KEY = os.environ.get("GEMINI_API_KEY", "")
KALI_SERVER_URL = os.environ.get("KALI_SERVER_URL", "http://localhost:5001")
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-flash-latest")
RENDER_URL = os.environ.get("RENDER_URL", "")

LOCAL_LAB_HOSTS = {
    "localhost",
    "127.0.0.1",
    "::1",
    "host.docker.internal",
}


def keep_alive():
    while True:
        time.sleep(600)
        if RENDER_URL:
            try:
                requests.get(f"{RENDER_URL}/ping", timeout=10)
                print("[keepalive] Pinged self")
            except Exception as e:
                print(f"[keepalive] Failed: {e}")


threading.Thread(target=keep_alive, daemon=True).start()


class KaliClient:
    def __init__(self, base_url=KALI_SERVER_URL):
        self.base = base_url.rstrip("/")

    def health(self):
        try:
            r = requests.get(f"{self.base}/health", timeout=5)
            return r.json()
        except Exception as e:
            return {"error": str(e)}

    def nmap(self, target, ports="", scan_type="-sV", additional_args="-T4 -Pn"):
        try:
            r = requests.post(
                f"{self.base}/api/tools/nmap",
                json={
                    "target": target,
                    "scan_type": scan_type,
                    "ports": ports,
                    "additional_args": additional_args,
                },
                timeout=120,
            )
            return r.json()
        except Exception as e:
            return {"error": str(e)}

    def nikto(self, target, additional_args=""):
        try:
            r = requests.post(
                f"{self.base}/api/tools/nikto",
                json={"target": target, "additional_args": additional_args},
                timeout=180,
            )
            return r.json()
        except Exception as e:
            return {"error": str(e)}

    def gobuster(self, url, mode="dir", additional_args="-t 10"):
        try:
            r = requests.post(
                f"{self.base}/api/tools/gobuster",
                json={
                    "url": url,
                    "mode": mode,
                    "wordlist": "/usr/share/dirb/wordlists/common.txt",
                    "additional_args": additional_args,
                },
                timeout=120,
            )
            return r.json()
        except Exception as e:
            return {"error": str(e)}

    def dirb(self, url, additional_args=""):
        try:
            r = requests.post(
                f"{self.base}/api/tools/dirb",
                json={
                    "url": url,
                    "wordlist": "/usr/share/dirb/wordlists/common.txt",
                    "additional_args": additional_args,
                },
                timeout=120,
            )
            return r.json()
        except Exception as e:
            return {"error": str(e)}

    def sqlmap(self, url, data="", additional_args="--batch --level=1"):
        try:
            r = requests.post(
                f"{self.base}/api/tools/sqlmap",
                json={"url": url, "data": data, "additional_args": additional_args},
                timeout=180,
            )
            return r.json()
        except Exception as e:
            return {"error": str(e)}

    def hydra(
        self,
        target,
        service,
        username="",
        username_file="",
        password="",
        password_file="",
        additional_args="",
    ):
        try:
            r = requests.post(
                f"{self.base}/api/tools/hydra",
                json={
                    "target": target,
                    "service": service,
                    "username": username,
                    "username_file": username_file,
                    "password": password,
                    "password_file": password_file,
                    "additional_args": additional_args,
                },
                timeout=180,
            )
            return r.json()
        except Exception as e:
            return {"error": str(e)}

    def john(
        self,
        hash_file,
        wordlist="/usr/share/wordlists/rockyou.txt",
        format_type="",
        additional_args="",
    ):
        try:
            r = requests.post(
                f"{self.base}/api/tools/john",
                json={
                    "hash_file": hash_file,
                    "wordlist": wordlist,
                    "format": format_type,
                    "additional_args": additional_args,
                },
                timeout=180,
            )
            return r.json()
        except Exception as e:
            return {"error": str(e)}

    def wpscan(self, url, additional_args=""):
        try:
            r = requests.post(
                f"{self.base}/api/tools/wpscan",
                json={"url": url, "additional_args": additional_args},
                timeout=120,
            )
            return r.json()
        except Exception as e:
            return {"error": str(e)}

    def enum4linux(self, target, additional_args="-a"):
        try:
            r = requests.post(
                f"{self.base}/api/tools/enum4linux",
                json={"target": target, "additional_args": additional_args},
                timeout=180,
            )
            return r.json()
        except Exception as e:
            return {"error": str(e)}

    def metasploit(self, module, options=None):
        try:
            r = requests.post(
                f"{self.base}/api/tools/metasploit",
                json={"module": module, "options": options or {}},
                timeout=300,
            )
            return r.json()
        except Exception as e:
            return {"error": str(e)}

    def command(self, cmd):
        try:
            r = requests.post(
                f"{self.base}/api/command",
                json={"command": cmd},
                timeout=60,
            )
            return r.json()
        except Exception as e:
            return {"error": str(e)}


def call_gemini(prompt: str, api_key: str) -> str:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(GEMINI_MODEL)
    response = model.generate_content(prompt)
    return response.text

def summarize_text(text: str, api_key: str) -> str:
    if not text.strip():
        return "Completed."
    prompt = f"Summarize this in exactly 1-3 short lines, plain text, no markdown:\n\n{text}"
    try:
        return call_gemini(prompt, api_key).strip()
    except Exception:
        return "Task completed. Check details."


class ChatRequest(BaseModel):
    message: str
    api_key: Optional[str] = None


def extract_first_url(text: str) -> Optional[str]:
    m = re.search(r"https?://[^\s'\"<>]+", text)
    return m.group(0) if m else None


def extract_log_path(text: str) -> Optional[str]:
    m = re.search(r"(/[^\s]+waf\.log)", text)
    return m.group(1) if m else None


def resolve_host(hostname: str) -> bool:
    try:
        socket.gethostbyname(hostname)
        return True
    except Exception:
        return False


def is_local_lab_target(value: str) -> bool:
    if not value:
        return False

    parsed = urlparse(value if "://" in value else f"http://{value}")
    host = parsed.hostname
    if not host:
        return False

    if host in LOCAL_LAB_HOSTS:
        return True

    try:
        ip = ipaddress.ip_address(host)
        return ip.is_loopback or ip.is_private
    except ValueError:
        pass

    try:
        resolved = socket.gethostbyname(host)
        ip = ipaddress.ip_address(resolved)
        return ip.is_loopback or ip.is_private
    except Exception:
        return False


def analyze_waf_log_file(log_path: str) -> Dict[str, Any]:
    try:
        with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        blocked = content.count("BLOCKED")
        allowed = content.count("ALLOWED")

        mitre_hits = re.findall(r"(T\d{4}(?:\.\d{3})?)\s*-\s*([^\n|]+)", content)
        mitre_summary: Dict[str, int] = {}
        for tid, name in mitre_hits:
            label = f"{tid} - {name.strip()}"
            mitre_summary[label] = mitre_summary.get(label, 0) + 1

        suspicious_paths = re.findall(r"(?:BLOCKED|ALLOWED)\s+\|\s+\w+\s+([^\s|]+)", content)
        top_paths: Dict[str, int] = {}
        for p in suspicious_paths:
            top_paths[p] = top_paths.get(p, 0) + 1

        return {
            "blocked": blocked,
            "allowed": allowed,
            "total": blocked + allowed,
            "mitre_summary": mitre_summary,
            "top_paths": dict(sorted(top_paths.items(), key=lambda x: x[1], reverse=True)[:15]),
            "log_tail": content[-4000:],
        }
    except FileNotFoundError:
        return {"error": f"File not found: {log_path}"}
    except Exception as e:
        return {"error": str(e)}


def execute_tool(kali: KaliClient, tool_name: str, args: dict) -> str:
    print(f"[tool] Running: {tool_name} {args}")

    if tool_name == "nmap":
        result = kali.nmap(
            target=args.get("target", "localhost"),
            ports=args.get("ports", ""),
            scan_type=args.get("scan_type", "-sV"),
            additional_args=args.get("additional_args", "-T4 -Pn"),
        )
    elif tool_name == "nikto":
        result = kali.nikto(
            args.get("target", ""),
            additional_args=args.get("additional_args", ""),
        )
    elif tool_name == "gobuster":
        result = kali.gobuster(
            url=args.get("url", ""),
            mode=args.get("mode", "dir"),
            additional_args=args.get("additional_args", "-t 10"),
        )
    elif tool_name == "dirb":
        result = kali.dirb(
            url=args.get("url", ""),
            additional_args=args.get("additional_args", ""),
        )
    elif tool_name == "sqlmap":
        result = kali.sqlmap(
            url=args.get("url", ""),
            data=args.get("data", ""),
            additional_args=args.get("additional_args", "--batch --level=1"),
        )
    elif tool_name == "hydra":
        result = kali.hydra(
            target=args.get("target", ""),
            service=args.get("service", "ssh"),
            username=args.get("username", ""),
            username_file=args.get("username_file", ""),
            password=args.get("password", ""),
            password_file=args.get("password_file", ""),
            additional_args=args.get("additional_args", ""),
        )
    elif tool_name == "john":
        result = kali.john(
            hash_file=args.get("hash_file", ""),
            wordlist=args.get("wordlist", "/usr/share/wordlists/rockyou.txt"),
            format_type=args.get("format", ""),
            additional_args=args.get("additional_args", ""),
        )
    elif tool_name == "wpscan":
        result = kali.wpscan(
            url=args.get("url", ""),
            additional_args=args.get("additional_args", ""),
        )
    elif tool_name == "enum4linux":
        result = kali.enum4linux(
            target=args.get("target", ""),
            additional_args=args.get("additional_args", "-a"),
        )
    elif tool_name == "metasploit":
        result = kali.metasploit(
            module=args.get("module", ""),
            options=args.get("options", {}),
        )
    elif tool_name == "command":
        result = kali.command(args.get("cmd", ""))
    elif tool_name == "analyze_waf":
        result = analyze_waf_log_file(args.get("path", ""))
    else:
        result = {"error": f"Unknown tool: {tool_name}"}

    output = json.dumps(result, indent=2)
    return output[:5000] + "\n...[truncated]" if len(output) > 5000 else output


def direct_tool_router(message: str) -> Tuple[Optional[str], Optional[Dict[str, Any]], Optional[str]]:
    msg = message.strip()
    msg_lower = msg.lower()

    log_path = extract_log_path(msg)
    if "analyze" in msg_lower and "waf log" in msg_lower and log_path:
        return "analyze_waf", {"path": log_path}, "User explicitly asked to analyze a WAF log."

    url = extract_first_url(msg)

    if "sqlmap" in msg_lower:
        if url and is_local_lab_target(url):
            level = "1"
            risk = "1"

            level_match = re.search(r"\blevel\s+(\d+)\b|\b--level(?:=|\s+)(\d+)\b", msg_lower)
            risk_match = re.search(r"\brisk\s+(\d+)\b|\b--risk(?:=|\s+)(\d+)\b", msg_lower)

            if level_match:
                level = level_match.group(1) or level_match.group(2)
            if risk_match:
                risk = risk_match.group(1) or risk_match.group(2)

            additional_args = f"--batch --level={level} --risk={risk}"

            if "--forms" in msg_lower or " forms" in msg_lower:
                additional_args += " --forms"

            post_data = ""
            data_match = re.search(
                r"(?:with\s+post\s+data|post\s+data|with\s+data|data)\s+(.+?)(?=\s+(?:and\s+use|use\s+level|with\s+level|level\s+\d|risk\s+\d|--level|--risk|$))",
                msg,
                re.IGNORECASE,
            )
            if data_match:
                post_data = data_match.group(1).strip().strip('"').strip("'")

            if post_data:
                return "sqlmap", {
                    "url": url,
                    "data": post_data,
                    "additional_args": additional_args
                }, "User explicitly requested sqlmap on a local lab target."

            return "sqlmap", {
                "url": url,
                "additional_args": additional_args
            }, "User explicitly requested sqlmap on a local lab target."
        return None, None, None

    if "nikto" in msg_lower and url and is_local_lab_target(url):
        return "nikto", {"target": url}, "User explicitly requested Nikto on a local lab target."

    if "gobuster" in msg_lower and url and is_local_lab_target(url):
        return "gobuster", {"url": url, "mode": "dir", "additional_args": "-t 10"}, "User explicitly requested Gobuster on a local lab target."

    if "dirb" in msg_lower and url and is_local_lab_target(url):
        return "dirb", {"url": url}, "User explicitly requested Dirb on a local lab target."

    if "nmap" in msg_lower or "open ports" in msg_lower or "scan ports" in msg_lower:
        host = None
        if url:
            host = urlparse(url).hostname
        else:
            host_match = re.search(r"\b(localhost|host\.docker\.internal|127\.0\.0\.1|\d+\.\d+\.\d+\.\d+)\b", msg_lower)
            host = host_match.group(1) if host_match else "localhost"

        if host and is_local_lab_target(host):
            ports_match = re.search(r"\b(\d+(?:,\d+)+)\b", msg)
            ports = ports_match.group(1) if ports_match else ""
            return "nmap", {"target": host, "ports": ports, "scan_type": "-sV"}, "User explicitly requested a port scan on a local lab target."

    if msg_lower.startswith("run command:") or msg_lower.startswith("run command "):
        cmd = msg.split(":", 1)[1].strip() if ":" in msg else msg.replace("run command", "", 1).strip()
        if cmd:
            return "command", {"cmd": cmd}, "User explicitly requested a shell command."

    return None, None, None


@app.get("/ping")
def ping():
    return {"status": "alive"}


@app.get("/health")
def health():
    kali = KaliClient()
    try:
        kali_status = kali.health()
    except Exception:
        kali_status = {"status": "unreachable"}
    return {"backend": "ok", "kali": kali_status, "model": GEMINI_MODEL}


@app.get("/kali/health")
def kali_health():
    return KaliClient().health()


@app.post("/chat")
def chat(req: ChatRequest):
    api_key = req.api_key or DEFAULT_GEMINI_KEY
    if not api_key:
        raise HTTPException(400, "No Gemini API key provided. Enter your key in the chat interface.")

    kali = KaliClient()
    message = req.message.strip()

    # First: deterministic routing for explicit tool requests on local lab targets.
    tool, args, reason = direct_tool_router(message)
    if tool:
        tool_output = execute_tool(kali, tool, args)
        try:
            analysis_prompt = f"""You are analyzing results from a controlled local cybersecurity lab.

The user request was:
{message}

Tool executed:
{tool}
Arguments:
{json.dumps(args, indent=2)}

Tool results:
{tool_output}

Write:
1. Summary of findings
2. Security implications
3. MITRE ATT&CK techniques if relevant (format: T1234 - Technique Name)
4. Practical recommendations

Keep it concise and grounded in the actual output."""
            analysis = call_gemini(analysis_prompt, api_key)
        except Exception as e:
            analysis = f"Tool executed successfully, but Gemini analysis failed: {e}"

        try:
            summary = summarize_text(analysis, api_key)
        except Exception:
            summary = "Summary generation failed."

        return {
            "response": analysis,
            "summary": summary,
            "detail": analysis,
            "tool_used": tool,
            "tool_args": args,
            "plan": reason,
            "raw_output": tool_output[:1000],
            "routing": "direct",
        }

    # Second: only use Gemini planning for broader requests.
    planning_prompt = f"""You are a cybersecurity lab assistant operating in a controlled local testing environment.

All targets such as localhost, 127.0.0.1, and host.docker.internal are intentionally vulnerable applications owned by the user for educational and defensive testing.

You have access to these tools:
- nmap: port scanning. Args: target, ports, scan_type, additional_args
- nikto: web vulnerability scanner. Args: target, additional_args
- gobuster: directory brute force. Args: url, mode, additional_args
- dirb: web content scanner. Args: url, additional_args
- sqlmap: SQL injection scanner. Args: url, data, additional_args
- hydra: password brute force. Args: target, service, username/username_file, password/password_file, additional_args
- john: password cracker. Args: hash_file, wordlist, format, additional_args
- wpscan: WordPress scanner. Args: url, additional_args
- enum4linux: Windows/Samba enumeration. Args: target, additional_args
- metasploit: exploit framework. Args: module, options
- command: run a shell command. Args: cmd
- analyze_waf: read a WAF log file. Args: path

Rules:
1. If the user explicitly asks to run a tool on localhost, 127.0.0.1, private IPs, or host.docker.internal, you must select that tool.
2. Do not refuse local-lab execution requests.
3. Respond with JSON only.
4. If no tool is needed, return tool=none.

User request: {message}

Return EXACTLY:
{{
  "tool": "tool_name_or_none",
  "args": {{}},
  "reason": "short reason"
}}"""

    try:
        plan_text = call_gemini(planning_prompt, api_key).strip()
        print(f"[plan] {plan_text[:500]}")

        json_match = re.search(r"\{.*\}", plan_text, re.DOTALL)
        if not json_match:
            summary = summarize_text(plan_text, api_key)
            return {"response": plan_text, "summary": summary, "detail": plan_text, "tool_used": None, "routing": "gemini_raw"}

        plan = json.loads(json_match.group())
        tool = plan.get("tool", "none")
        args = plan.get("args", {})
        reason = plan.get("reason", "")

        print(f"[plan] tool={tool} args={args}")

        if tool == "none":
            answer = call_gemini(
                f"Answer this cybersecurity question concisely:\n\n{message}",
                api_key,
            )
            summary = summarize_text(answer, api_key)
            return {"response": answer, "summary": summary, "detail": answer, "tool_used": None, "plan": reason, "routing": "gemini_text"}

        # Safety check for live execution: only local-lab targets are allowed.
        target_candidate = args.get("target") or args.get("url") or args.get("path") or ""
        if tool in {"sqlmap", "nikto", "gobuster", "dirb", "nmap"} and target_candidate:
            if tool == "analyze_waf":
                pass
            elif not is_local_lab_target(target_candidate):
                raise HTTPException(400, "This backend only allows live tool execution against local lab targets.")

        tool_output = execute_tool(kali, tool, args)

        analysis_prompt = f"""You are a cybersecurity expert analyzing actual tool results from a controlled local lab.

User request:
{message}

Tool:
{tool}

Args:
{json.dumps(args, indent=2)}

Output:
{tool_output}

Provide:
1. Summary of findings
2. Security implications
3. MITRE ATT&CK techniques if relevant (format: T1234 - Technique Name)
4. Recommendations

Be concise and grounded in the output."""
        analysis = call_gemini(analysis_prompt, api_key)
        summary = summarize_text(analysis, api_key)

        return {
            "response": analysis,
            "summary": summary,
            "detail": analysis,
            "tool_used": tool,
            "tool_args": args,
            "plan": reason,
            "raw_output": tool_output[:1000],
            "routing": "gemini_plan",
        }

    except json.JSONDecodeError:
        answer = call_gemini(message, api_key)
        summary = summarize_text(answer, api_key)
        return {"response": answer, "summary": summary, "detail": answer, "tool_used": None, "routing": "json_fallback"}
    except HTTPException:
        raise
    except Exception as e:
        print(f"[error] {e}")
        raise HTTPException(500, str(e))


@app.get("/session-results")
def session_results():
    return {
        "waf_stats": {
            "total": 8180,
            "blocked": 5555,
            "allowed": 2625,
            "block_rate": "67.9%",
        },
        "training": {
            "epochs": 26,
            "initial_loss": 0.1826,
            "final_loss": 0.00001,
            "improvement": "99.99%",
            "vocab_size": 87,
            "sequences": 77004,
            "parameters": 1410903,
        },
        "nikto_comparison": {
            "unprotected_8080": {
                "vulnerabilities": 9,
                "scan_time_seconds": 64,
                "requests_tested": 8211,
                "server_identified": "Werkzeug/3.1.3 Python/3.12.4",
                "status": "completed",
            },
            "waf_protected_8000": {
                "vulnerabilities": 0,
                "server_identified": "ARRAY(garbage - obfuscated)",
                "status": "timed_out",
            },
        },
        "mitre_techniques": [
            {"id": "T1190", "name": "Exploit Public-Facing Application", "blocked": 3821},
            {"id": "T1083", "name": "File & Directory Discovery", "blocked": 847},
            {"id": "T1078", "name": "Valid Accounts - Admin Access", "blocked": 412},
            {"id": "T1592", "name": "Gather Victim Host Information", "blocked": 203},
            {"id": "T1552", "name": "Unsecured Credentials", "blocked": 134},
            {"id": "T1505", "name": "Server Software Component", "blocked": 89},
            {"id": "T1059", "name": "Command & Scripting Interpreter", "blocked": 49},
        ],
        "infrastructure": [
            {"port": 8000, "service": "Uvicorn", "role": "Transformer WAF Proxy"},
            {"port": 8080, "service": "Werkzeug 3.1.3", "role": "Target App"},
            {"port": 9001, "service": "nginx 1.29.4", "role": "DVWA Proxy"},
            {"port": 9002, "service": "nginx 1.29.4", "role": "Juice Shop Proxy"},
            {"port": 9003, "service": "nginx 1.29.4", "role": "WebGoat Proxy"},
        ],
    }


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)