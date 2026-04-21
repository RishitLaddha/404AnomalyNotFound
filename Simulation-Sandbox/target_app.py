from flask import Flask, request, jsonify

app = Flask(__name__)

# --- TRAFFIC COUNTER ---
normal_traffic_count = 0

# --- THE TRIPWIRE ---
def check_for_compromise(payload):
    if not payload:
        return False
    payload = payload.lower()
    signatures = ['<script>', 'or 1=1', "or '1'='1'", 'drop table', '../', 'etc/passwd', 'alert(']
    for sig in signatures:
        if sig in payload:
            return True
    return False

# --- THE COMPROMISED SCREEN ---
def show_compromised_screen():
    return """
    <div style="background-color: #2b0000; padding: 40px; border: 4px solid #ff4444; text-align: center; font-family: monospace; color: white; height: 100vh;">
        <h1 style="color: #ff4444; font-size: 3rem;">⚠️ CRITICAL BREACH DETECTED ⚠️</h1>
        <h2 style="color: white;">WEBSITE COMPROMISED</h2>
        <p style="font-size: 1.2rem; color: #ff9999;">A malicious payload successfully bypassed the perimeter and executed on the backend!</p>
        <p>If you are seeing this, the Firewall failed, or you attacked the backend directly.</p>
    </div>
    """, 400

# --- API FOR LIVE UPDATES ---
@app.route('/api/traffic_count')
def get_traffic_count():
    return jsonify({"count": normal_traffic_count})

# --- LIVE UPDATE JAVASCRIPT ---
# This script polls the API every 1 second and updates the HTML span element
LIVE_SCRIPT = """
<script>
    setInterval(() => {
        fetch('/api/traffic_count')
            .then(response => response.json())
            .then(data => {
                const counterElement = document.getElementById('live-counter');
                if (counterElement) {
                    counterElement.innerText = data.count;
                }
            })
            .catch(err => console.error("Error fetching live count: ", err));
    }, 1000);
</script>
"""

# --- HELPER FOR COUNTER UI ---
def get_counter_ui():
    return f"""
    <div style="background-color: #d4edda; color: #155724; padding: 10px; border: 1px solid #c3e6cb; border-radius: 5px; display: inline-block; margin-bottom: 15px;">
        <strong>✅ Safe Requests Handled: <span id="live-counter">{normal_traffic_count}</span></strong>
    </div>
    """


@app.route('/')
def home():
    global normal_traffic_count
    normal_traffic_count += 1
    return f"""
    <div style="font-family: sans-serif; padding: 20px;">
        <h1>Welcome to the Vulnerable Corp Internal Network</h1>
        {get_counter_ui()}
        <p>This backend server is running on port 8080.</p>
        <ul>
            <li><a href="/login">Login Portal</a></li>
            <li><a href="/search">Employee Search</a></li>
        </ul>
    </div>
    {LIVE_SCRIPT}
    """

@app.route('/login')
def login():
    global normal_traffic_count
    user = request.args.get('user', '')
    if user:
        if check_for_compromise(user):
            return show_compromised_screen()
        
        normal_traffic_count += 1
        return f"<h3>Attempting database lookup for user: {user}</h3> {get_counter_ui()} {LIVE_SCRIPT}"
    
    normal_traffic_count += 1
    return f"<h3>Login Page - Please provide a ?user= parameter</h3> {get_counter_ui()} {LIVE_SCRIPT}"

@app.route('/search')
def search():
    global normal_traffic_count
    query = request.args.get('q', '')
    if query:
        if check_for_compromise(query):
            return show_compromised_screen()
            
        normal_traffic_count += 1
        return f"<h3>Search results for: {query}</h3> {get_counter_ui()} {LIVE_SCRIPT}"
        
    normal_traffic_count += 1
    return f"<h3>Search Page - Please provide a ?q= parameter</h3> {get_counter_ui()} {LIVE_SCRIPT}"


if __name__ == '__main__':
    print("🎯 TARGET BACKEND ONLINE on http://0.0.0.0:8080")
    print("Shield this with SentinelShield!")
    app.run(host='0.0.0.0', port=8080)