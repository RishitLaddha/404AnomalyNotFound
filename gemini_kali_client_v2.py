"""
Gemini Kali Client - Fixed Version
Uses simple prompt-based approach instead of function calling
which is more reliable across Gemini API versions
"""

import os
import json
import requests
import re

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

KALI_SERVER  = os.environ.get("KALI_SERVER", "http://localhost:5001")
GEMINI_KEY   = os.environ.get("GEMINI_API_KEY", "")
GEMINI_MODEL = "gemini-1.5-flash"


# ── Kali API Client ───────────────────────────────────────────
class KaliClient:
    def __init__(self, base_url=KALI_SERVER):
        self.base = base_url.rstrip("/")

    def health(self):
        try:
            r = requests.get(f"{self.base}/health", timeout=5)
            return r.json()
        except Exception as e:
            return {"error": str(e)}

    def nmap(self, target, ports="", scan_type="-sV", additional_args="-T4 -Pn"):
        try:
            r = requests.post(f"{self.base}/api/tools/nmap", json={
                "target": target, "scan_type": scan_type,
                "ports": ports, "additional_args": additional_args
            }, timeout=120)
            return r.json()
        except Exception as e:
            return {"error": str(e)}

    def nikto(self, target):
        try:
            r = requests.post(f"{self.base}/api/tools/nikto", json={
                "target": target, "additional_args": ""
            }, timeout=180)
            return r.json()
        except Exception as e:
            return {"error": str(e)}

    def gobuster(self, url, mode="dir"):
        try:
            r = requests.post(f"{self.base}/api/tools/gobuster", json={
                "url": url, "mode": mode,
                "wordlist": "/usr/share/wordlists/dirb/common.txt",
                "additional_args": "-t 10"
            }, timeout=120)
            return r.json()
        except Exception as e:
            return {"error": str(e)}

    def sqlmap(self, url, additional_args="--batch --level=1"):
        try:
            r = requests.post(f"{self.base}/api/tools/sqlmap", json={
                "url": url, "data": "",
                "additional_args": additional_args
            }, timeout=180)
            return r.json()
        except Exception as e:
            return {"error": str(e)}

    def dirb(self, url):
        try:
            r = requests.post(f"{self.base}/api/tools/dirb", json={
                "url": url,
                "wordlist": "/usr/share/wordlists/dirb/common.txt",
                "additional_args": ""
            }, timeout=120)
            return r.json()
        except Exception as e:
            return {"error": str(e)}

    def command(self, cmd):
        try:
            r = requests.post(f"{self.base}/api/command", json={
                "command": cmd
            }, timeout=60)
            return r.json()
        except Exception as e:
            return {"error": str(e)}


# ── Tool Executor ─────────────────────────────────────────────
def execute_tool(kali, tool_name, args):
    """Execute a Kali tool and return results."""
    print(f"\n🔧 Running: {tool_name} {args}")

    if tool_name == "nmap":
        result = kali.nmap(
            target=args.get("target", "localhost"),
            ports=args.get("ports", ""),
            scan_type=args.get("scan_type", "-sV")
        )
    elif tool_name == "nikto":
        result = kali.nikto(args.get("target", ""))
    elif tool_name == "gobuster":
        result = kali.gobuster(args.get("url", ""))
    elif tool_name == "sqlmap":
        result = kali.sqlmap(args.get("url", ""))
    elif tool_name == "dirb":
        result = kali.dirb(args.get("url", ""))
    elif tool_name == "command":
        result = kali.command(args.get("cmd", ""))
    elif tool_name == "analyze_waf":
        log_path = args.get("path", "")
        try:
            with open(log_path) as f:
                content = f.read()
            blocked = content.count("BLOCKED")
            allowed = content.count("ALLOWED")
            result = {
                "log": content[-4000:],
                "blocked": blocked,
                "allowed": allowed,
                "total": blocked + allowed
            }
        except FileNotFoundError:
            result = {"error": f"File not found: {log_path}"}
    else:
        result = {"error": f"Unknown tool: {tool_name}"}

    output = json.dumps(result, indent=2)
    if len(output) > 3000:
        output = output[:3000] + "\n...[truncated]"
    print(f"✅ Done!\n")
    return output


# ── Main Agent ────────────────────────────────────────────────
def parse_and_execute(user_input, kali, model):
    """
    Ask Gemini what to do, parse its response,
    execute tools, then ask Gemini to explain results.
    """

    # Step 1: Ask Gemini what tool to run
    planning_prompt = f"""You are a cybersecurity AI with access to these Kali Linux tools:
- nmap: port scanning. Args: target, ports (optional), scan_type
- nikto: web vulnerability scanner. Args: target (URL)
- gobuster: directory brute force. Args: url
- sqlmap: SQL injection scanner. Args: url
- dirb: web content scanner. Args: url
- command: run any shell command. Args: cmd
- analyze_waf: read WAF log file. Args: path (absolute file path)

User request: {user_input}

Respond with EXACTLY this JSON format (nothing else):
{{
  "tool": "tool_name_here",
  "args": {{"arg1": "value1", "arg2": "value2"}},
  "reason": "why you chose this tool"
}}

If no tool needed, respond:
{{"tool": "none", "args": {{}}, "reason": "explanation"}}"""

    try:
        plan_response = model.generate_content(planning_prompt)
        plan_text = plan_response.text.strip()

        # Extract JSON from response
        json_match = re.search(r'\{.*\}', plan_text, re.DOTALL)
        if not json_match:
            print(f"\n🤖 Gemini: {plan_text}")
            return

        plan = json.loads(json_match.group())
        tool = plan.get("tool", "none")
        args = plan.get("args", {})
        reason = plan.get("reason", "")

        print(f"\n💭 Gemini's plan: {reason}")

        if tool == "none":
            # No tool needed - just answer directly
            answer = model.generate_content(f"Answer this cybersecurity question: {user_input}")
            print(f"\n🤖 Gemini: {answer.text}")
            return

        # Step 2: Execute the tool
        tool_output = execute_tool(kali, tool, args)

        # Step 3: Ask Gemini to analyze results
        analysis_prompt = f"""You are a cybersecurity expert. 
The user asked: "{user_input}"

You ran {tool} with args {args} and got these results:
{tool_output}

Please provide:
1. A clear summary of findings
2. Security implications
3. MITRE ATT&CK techniques if relevant (format: T1234 - Technique Name)
4. Recommendations

Be concise and professional."""

        analysis = model.generate_content(analysis_prompt)
        print(f"\n🤖 Gemini Analysis:\n{analysis.text}")

    except json.JSONDecodeError as e:
        print(f"\n⚠️  Could not parse Gemini response: {e}")
        print(f"Raw response: {plan_text}")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


def main():
    print("=" * 60)
    print("KALI + GEMINI SECURITY ASSISTANT")
    print("=" * 60)

    kali = KaliClient(KALI_SERVER)

    # Check Kali
    health = kali.health()
    if "error" in health:
        print(f"⚠️  Kali server not reachable at {KALI_SERVER}")
        print(f"   Error: {health['error']}")
        print(f"   Make sure Docker container is running!")
        return
    else:
        tools = health.get("tools_status", {})
        available = [t for t, v in tools.items() if v]
        print(f"✅ Kali connected | Tools: {', '.join(available)}")

    # Check Gemini
    api_key = GEMINI_KEY
    if not api_key:
        print("❌ No GEMINI_API_KEY set!")
        print("   Run: export GEMINI_API_KEY=your_key")
        return

    if not GEMINI_AVAILABLE:
        print("❌ google-generativeai not installed")
        print("   Run: pip3 install google-generativeai")
        return

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(GEMINI_MODEL)
    print(f"✅ Gemini ready | Model: {GEMINI_MODEL}")

    print("\n" + "=" * 60)
    print("Ready! Ask security questions or request scans.")
    print("Examples:")
    print("  Run nmap on localhost and show open ports")
    print("  Run nikto against http://localhost:8080")
    print("  Analyze WAF log at /Users/rishitladdha/Desktop/Sem 6/Pinnacle/waf.log")
    print("  Scan http://localhost:8080 for directories with gobuster")
    print("Type 'quit' to exit")
    print("=" * 60)

    while True:
        try:
            user_input = input("\nYou: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break

        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit", "q"):
            print("Goodbye!")
            break

        parse_and_execute(user_input, kali, model)


if __name__ == "__main__":
    main()
