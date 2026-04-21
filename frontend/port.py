import os
import re

pinnacle_dir = '/Users/rishitladdha/Downloads/pinnacle 2/pages'
dest_dir = '/Users/rishitladdha/Downloads/waf-project 2/frontend/src/pages'

# Port About.jsx and Dashboard.jsx
for page in ['About.jsx', 'Dashboard.jsx']:
    with open(os.path.join(pinnacle_dir, page)) as f:
        content = f.read()
    
    # Prepend import
    content = "import React, { useState, useEffect } from 'react';\nimport TypewriterWord from '../components/TypewriterWord';\n" + content
    # Remove `/* global React */`
    content = content.replace("/* global React */", "")
    content = content.replace("const { useState, useEffect } = React;", "")
    content = content.replace("const { useState: _twUseState, useEffect: _twUseEffect } = React;", "")
    
    # Replace window... = ... with export default function
    content = re.sub(r'window\.([A-Za-z0-9_]+)\s*=\s*\1;', r'export default \1;', content)
    
    with open(os.path.join(dest_dir, page), 'w') as f:
        f.write(content)

# For Assistant.jsx, it requires manual wiring for the backend. Let's do it specifically.
with open(os.path.join(pinnacle_dir, 'Assistant.jsx')) as f:
    ast_content = f.read()

# Replace imports
ast_content = "import React, { useState, useEffect, useRef } from 'react';\nimport ReactMarkdown from 'react-markdown';\nimport TypewriterWord from '../components/TypewriterWord';\nconst API = import.meta.env.VITE_API_URL || 'http://localhost:8001';\n\n" + ast_content
ast_content = ast_content.replace("const { useState, useRef, useEffect } = React;", "")
ast_content = ast_content.replace("/* global React */", "")

# We need to swap the `async function send(text)` implementation!
original_send = r"""  async function send\(text\) \{
    const t = \(text \?\? input\)\.trim\(\);
    if \(!t \|\| busy\) return;
    setInput\(''\);
    setMessages\(m => \[\.\.\.m, \{ who: 'you', text: t, meta: now\(\) \}\]\);
    setBusy\(true\);

    // Simulated reply via window\.claude \(if present\), else canned
    let reply;
    try \{
      if \(window\.claude\?.complete\) \{
        reply = await window\.claude\.complete\(\{
          messages: \[\{ role: 'user', content:
            `You are the 404AnomalyNotFound WAF security assistant\. Be terse, technical, brutalist in tone\. Keep under 90 words\. User: \$\{t\}` \}\]
        \}\);
      \} else \{
        reply = CANNED\(t\);
      \}
    \} catch \{ reply = CANNED\(t\); \}

    setBusy\(false\);
    setMessages\(m => \[\.\.\.m, \{ who: 'bot', text: reply, meta: 'tool · gemini · ' \+ now\(\) \}\]\);
  \}"""

new_send = r"""  async function send(text) {
    const t = (text ?? input).trim();
    if (!t || busy) return;
    setInput('');
    setMessages(m => [...m, { who: 'you', text: t, meta: now() }]);
    setBusy(true);

    try {
      const resp = await fetch(`${API}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: t, api_key: apiKey || undefined }),
      });
      if (!resp.ok) throw new Error((await resp.json()).detail || 'API error');
      const data = await resp.json();
      
      // Assume the backend now returns `data.summary` and `data.detail` or just `data.response`
      // We will render `data.response` or `data.detail` with ReactMarkdown in the Msg component.
      setMessages(m => [...m, { 
        who: 'bot', 
        text: data.response || data.detail || (data.summary + '\n\n' + data.detail), 
        meta: `tool · ${data.tool_used || 'gemini'} · ` + now() 
      }]);
    } catch (err) {
      setMessages(m => [...m, { 
        who: 'bot', 
        text: `**Error:** ${err.message}\n\nEnsure backend is running.`, 
        meta: 'system · error · ' + now() 
      }]);
    } finally {
      setBusy(false);
    }
  }"""

ast_content = re.sub(original_send, new_send, ast_content)

# We must also change the output rendering to ReactMarkdown for the bot's messages
# Find the Msg component
original_msg_render = r"""      <div style=\{\{
        fontFamily: isYou \? 'var\(--f-mono\)' : 'var\(--f-body\)',
        fontSize: isYou \? 13 : 15,
        lineHeight: 1\.6,
        padding: isYou \? '10px 14px' : '2px 0 2px 14px',
        borderLeft: '2px solid ' \+ \(isYou \? 'var\(--red\)' : 'var\(--teal\)'\),
        background: isYou \? 'var\(--paper-2\)' : 'transparent',
        whiteSpace: 'pre-wrap',
      \}\}>\{m\.text\}</div>"""

new_msg_render = r"""      <div style={{
        fontFamily: isYou ? 'var(--f-mono)' : 'var(--f-body)',
        fontSize: isYou ? 13 : 15,
        lineHeight: 1.6,
        padding: isYou ? '10px 14px' : '2px 0 2px 14px',
        borderLeft: '2px solid ' + (isYou ? 'var(--red)' : 'var(--teal)'),
        background: isYou ? 'var(--paper-2)' : 'transparent',
        whiteSpace: 'pre-wrap',
      }}>
        {isYou ? m.text : (
          <div className="md-body">
            <ReactMarkdown>{m.text}</ReactMarkdown>
          </div>
        )}
      </div>"""

ast_content = re.sub(original_msg_render, new_msg_render, ast_content)

# Add md-body styles roughly matching the ReactMarkdown styles inside Assistant
# (Note: we could inject these styles into the page directly)
md_styles = r"""
      <style>{`
        .md-body h2, .md-body h3 { font-family: var(--f-display); font-style: italic; font-size: 18px; margin: 12px 0 6px; color: var(--ink); }
        .md-body h4 { font-family: var(--f-mono); font-size: 11px; letter-spacing: 0.18em; text-transform: uppercase; color: var(--ink-3); margin: 10px 0 4px; }
        .md-body p  { margin: 6px 0; font-size: 14px; }
        .md-body ul, .md-body ol { padding-left: 1.4rem; margin: 6px 0; }
        .md-body li { margin: 3px 0; font-size: 14px; }
        .md-body strong { color: var(--ink); }
        .md-body em { font-style: italic; color: var(--red); }
        .md-body code { background: var(--paper-3); padding: 1px 5px; font-family: var(--f-mono); font-size: 12px; border: 1px solid var(--ink); }
        .md-body pre  { background: var(--ink); color: var(--paper); padding: 14px 16px; margin: 8px 0; overflow-x: auto; border: 1px solid var(--ink); }
        .md-body pre code { background: none; border: none; color: var(--paper); font-size: 12px; }
      `}</style>
    </div>
  );
}"""

ast_content = ast_content.replace("    </div>\n  );\n}", md_styles)

# Update Health Check for Kali
kali_check = r"""  const [status, setStatus] = useState('online'); // 'online' | 'offline' | 'checking'"""
new_kali_check = r"""  const [status, setStatus] = useState('checking'); // 'online' | 'offline' | 'checking'
  useEffect(() => {
    fetch(`${API}/health`)
      .then(r => r.json())
      .then(d => setStatus(d.kali?.status === 'healthy' ? 'online' : 'offline'))
      .catch(() => setStatus('offline'));
  }, []);"""
ast_content = ast_content.replace(kali_check, new_kali_check)


ast_content = re.sub(r'window\.Assistant\s*=\s*Assistant;', r'export default Assistant;', ast_content)

with open(os.path.join(dest_dir, 'Assistant.jsx'), 'w') as f:
    f.write(ast_content)
