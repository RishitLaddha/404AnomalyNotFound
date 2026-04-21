import React, { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import TypewriterWord from '../components/TypewriterWord';
const API = import.meta.env.VITE_API_URL || 'http://localhost:8001';




const SUGGESTIONS = [
  { label: 'Run nmap on 8000,8080,9001–9003', tool: 'nmap',     text: 'Run nmap on host.docker.internal ports 8000,8080,9001,9002,9003' },
  { label: 'Explain T1190',                   tool: 'mitre',    text: 'Explain T1190 — Exploit Public-Facing Application' },
  { label: 'Summarise WAF effectiveness',     tool: 'analyze_waf', text: 'Analyze WAF log at ./waf.log' },
  { label: 'Run nikto vs :8080',              tool: 'nikto',    text: 'Run nikto against http://host.docker.internal:8080' },
  { label: 'What is a Transformer WAF?',      tool: 'explain',  text: 'What is a Transformer autoencoder WAF?' },
  { label: 'Run gobuster on :8080',           tool: 'gobuster', text: 'Run gobuster on http://host.docker.internal:8080' },
];

const SESSION = {
  when: '2026 · IV · 21  15:00 IST',
  intro: "Cached transcript — live results from Rishit's demonstration session. 8,180 requests routed through the WAF proxy; 5,555 blocked.",
  blocks: [
    {
      kind: 'table',
      title: 'Session overview',
      rows: [
        ['Total requests processed',  '8,180'],
        ['Attacks blocked',           '5,555 (67.9%)'],
        ['Benign requests allowed',   '2,625 (32.1%)'],
        ['Score separation',          '10,000×'],
        ['Session duration',          '≈ 42 min'],
      ],
    },
    {
      kind: 'table',
      title: 'Nikto comparison',
      rows: [
        ['Port 8080 · unprotected', '9 vulnerabilities, 64 s'],
        ['Port 8000 · WAF',         'TIMED OUT — 0 findings'],
        ['Server banner',           'Obfuscated as ARRAY(garbage)'],
      ],
    },
    {
      kind: 'mitre',
      title: 'MITRE techniques detected',
      rows: [
        ['T1190', 'Exploit Public-Facing App', 3821],
        ['T1083', 'File & Directory Discovery', 847],
        ['T1078', 'Valid Accounts — Admin',     412],
        ['T1592', 'Gather Victim Host Info',    203],
        ['T1552', 'Unsecured Credentials',      134],
      ],
    },
    {
      kind: 'code',
      title: 'nmap discovery',
      lines: [
        '8000/tcp   open   Uvicorn         ← Transformer WAF',
        '8080/tcp   open   Werkzeug 3.1.3  ← Target App (unprotected)',
        '9001/tcp   open   nginx 1.29.4    ← DVWA',
        '9002/tcp   open   nginx 1.29.4    ← Juice Shop',
        '9003/tcp   open   nginx 1.29.4    ← WebGoat',
      ],
    },
  ],
};

function Assistant() {
  const [tab, setTab] = useState('chat');
  const [messages, setMessages] = useState([
    { who: 'sys',
      text: '404AnomalyNotFound AI ASSISTANT · Gemini 2.5 · Kali Linux Docker bridge',
      meta: 'bridge established · session ephemeral' },
    { who: 'bot',
      text: 'Good afternoon. I can run reconnaissance tools against the demo sandbox, explain MITRE techniques, or walk you through the WAF\'s architecture. Type a command below, or pick from the list on the right.',
      meta: 'ready' },
  ]);
  const [input, setInput] = useState('');
  const [apiKey, setApiKey] = useState('');
  const [status, setStatus] = useState('checking'); // 'online' | 'offline' | 'checking'
  useEffect(() => {
    fetch(`${API}/health`)
      .then(r => r.json())
      .then(d => setStatus(d.kali?.status === 'healthy' ? 'online' : 'offline'))
      .catch(() => setStatus('offline'));
  }, []);
  const [busy, setBusy] = useState(false);
  const viewRef = useRef();

  useEffect(() => {
    viewRef.current?.scrollTo({ top: 9e6, behavior: 'smooth' });
  }, [messages, busy]);

  async function send(text) {
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
        text: data.summary || data.response || 'Task completed.',
        detail: data.detail || data.response,
        raw_output: data.raw_output || '',
        meta: `tool · ${data.tool_used || 'gemini'} · ` + now() 
      }]);
    } catch (err) {
      setMessages(m => [...m, { 
        who: 'bot', 
        text: `**Error:** ${err.message}

Ensure backend is running.`, 
        meta: 'system · error · ' + now() 
      }]);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="page" style={{ paddingBottom: 60 }}>

      {/* HEAD */}
      <section className="banner" style={{ padding: '22px 0 24px' }}>
        <div className="banner-top">
          <span>Console · Live bridge</span>
          <span>Kali Docker · Gemini 2.5 · FastAPI</span>
        </div>
        <h1 className="banner-title" style={{ fontSize: 'clamp(60px, 9vw, 120px)' }}>
          The&nbsp;<TypewriterWord words={['Assistant.', 'Security Copilot.', 'OffSec AI.']} />
        </h1>
        <div className="banner-sub" style={{ gridTemplateColumns: '2fr 1fr 1fr' }}>
          <div className="cell">
            <span className="label">Purpose</span>
            A pair of long-form tools wrapped around Gemini: it can invoke <em>nmap, nikto, gobuster</em> and friends on the
            sandbox, and it answers questions about the WAF's training, architecture, and MITRE coverage.
          </div>
          <div className="cell">
            <span className="label">Status</span>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, fontFamily: 'var(--f-mono)', fontSize: 12 }}>
              <span className="blink" style={{ width: 9, height: 9, background: 'var(--teal)', display: 'inline-block', border: '1px solid var(--ink)' }}/>
              Bridge: <strong>ONLINE</strong>
            </div>
            <div style={{ fontFamily: 'var(--f-mono)', fontSize: 11, color: 'var(--ink-3)', marginTop: 6 }}>
              kali.404anf.internal · 5001
            </div>
          </div>
          <div className="cell">
            <span className="label">Caveat</span>
            <span style={{ fontFamily: 'var(--f-mono)', fontSize: 12 }}>
              Tools target only the demo sandbox. Supply your own Gemini key below for unrestricted sessions.
            </span>
          </div>
        </div>
      </section>

      {/* TAB STRIP */}
      <div style={{ display: 'flex', border: '1px solid var(--ink)', marginTop: 32 }}>
        {['chat','transcript'].map(t => (
          <button key={t} onClick={() => setTab(t)} style={{
            flex: 1, padding: '14px 18px', cursor: 'pointer',
            borderRight: t==='chat' ? '1px solid var(--ink)' : 'none',
            background: tab===t ? 'var(--ink)' : 'var(--paper)',
            color:      tab===t ? 'var(--paper)' : 'var(--ink)',
            fontFamily: 'var(--f-mono)', fontSize: 11,
            letterSpacing: '0.22em', textTransform: 'uppercase',
            textAlign: 'left',
          }}>
            <span style={{ color: tab===t ? 'var(--gold)' : 'var(--ink-3)', marginRight: 14 }}>
              {t==='chat' ? 'A.' : 'B.'}
            </span>
            {t==='chat' ? 'Live console' : "Rishit's cached transcript"}
          </button>
        ))}
      </div>

      {tab === 'chat' ? (
        <div style={{
          display: 'grid',
          gridTemplateColumns: '3fr 1fr',
          border: '1px solid var(--ink)', borderTop: 'none',
          background: 'var(--paper)',
          height: 600, overflow: 'hidden'
        }}>
          {/* Left Column (75%) — Output Pane */}
          <div style={{ borderRight: '1px solid var(--ink)', display: 'flex', flexDirection: 'column', height: '100%', overflow: 'hidden' }}>
            <div style={{
              padding: '10px 16px', borderBottom: '1px solid var(--ink)',
              fontFamily: 'var(--f-mono)', fontSize: 10, letterSpacing: '0.2em', textTransform: 'uppercase',
              color: 'var(--ink-3)', background: 'var(--paper-2)',
              display: 'flex', justifyContent: 'space-between',
            }}>
              <span>~/404anf/assistant — OUTPUT  {now()}</span>
              <span>▢ ▢ ▢</span>
            </div>
            
            <div style={{ flex: 1, overflowY: 'auto', padding: 32 }}>
              {messages.filter(m => m.who === 'bot' && (m.detail || m.raw_output)).map((m, i) => (
                <div key={i} style={{ marginBottom: 40, paddingBottom: 40, borderBottom: '3px solid var(--ink)' }}>
                  <div style={{ fontFamily: 'var(--f-mono)', fontSize: 10, letterSpacing: '0.18em', textTransform: 'uppercase', color: 'var(--teal)', marginBottom: 8 }}>
                    ◼ Assistant · {m.meta}
                  </div>
                  {m.raw_output && (
                    <div style={{ marginBottom: 20 }}>
                      <div style={{ fontFamily: 'var(--f-mono)', fontSize: 10, letterSpacing: '0.1em', textTransform: 'uppercase', color: 'var(--ink-3)', marginBottom: 4 }}>Raw output snippet</div>
                      <pre style={{
                        background: 'var(--ink)', color: 'var(--paper)', padding: '14px 16px',
                        fontFamily: 'var(--f-mono)', fontSize: 11, overflowX: 'auto', border: '1px solid var(--ink)', margin: 0
                      }}>
                        {m.raw_output}
                      </pre>
                    </div>
                  )}
                  {m.detail && (
                    <div className="md-body">
                      <ReactMarkdown>{m.detail}</ReactMarkdown>
                    </div>
                  )}
                </div>
              ))}
              {messages.filter(m => m.who === 'bot' && (m.detail || m.raw_output)).length === 0 && (
                <p style={{ fontFamily: 'var(--f-display)', fontStyle: 'italic', fontSize: 24, color: 'var(--ink-3)', textAlign: 'center', marginTop: 100 }}>
                  Tool outputs and detailed analysis will appear here.
                </p>
              )}
            </div>
          </div>

          {/* Right Column (25%) — Chat Pane */}
          <aside style={{ display: 'flex', flexDirection: 'column', background: 'var(--paper-2)', height: '100%', overflow: 'hidden' }}>
            <div style={{
              padding: '10px 16px', borderBottom: '1px solid var(--ink)',
              fontFamily: 'var(--f-mono)', fontSize: 10, letterSpacing: '0.2em', textTransform: 'uppercase',
              color: 'var(--ink-3)', background: 'var(--paper-2)',
              display: 'flex', justifyContent: 'space-between',
            }}>
              <span>chat</span><span>{now()}</span>
            </div>
            {/* Chat History */}
            <div ref={viewRef} style={{ flex: 1, overflowY: 'auto', padding: '18px 20px', borderBottom: '1px solid var(--ink)' }}>
              {messages.map((m,i) => <Msg key={i} m={m} />)}
              {busy && (
                <div style={{ fontFamily: 'var(--f-mono)', fontSize: 12, color: 'var(--ink-3)' }}>
                  <span style={{ color: 'var(--red)' }}>◼</span> thinking
                  <span className="blink">_</span>
                </div>
              )}
            </div>

            {/* Input Bar */}
            <div style={{ background: 'var(--paper)' }}>
              <div style={{ display: 'flex', alignItems: 'stretch' }}>
                <span style={{ fontFamily: 'var(--f-mono)', fontSize: 14, color: 'var(--red)', padding: '14px 0 14px 14px' }}>&gt;</span>
                <input
                  value={input}
                  onChange={e => setInput(e.target.value)}
                  onKeyDown={e => e.key==='Enter' && send()}
                  placeholder="type command..."
                  style={{
                    flex: 1, background: 'var(--paper)',
                    border: 'none', padding: '14px 12px',
                    fontFamily: 'var(--f-mono)', fontSize: 13, color: 'var(--ink)',
                    outline: 'none',
                    minWidth: 0,
                  }}
                />
                <button onClick={() => send()} disabled={busy || !input.trim()} style={{
                  padding: '0 20px', background: 'var(--ink)', color: 'var(--paper)',
                  fontFamily: 'var(--f-mono)', fontSize: 11, letterSpacing: '0.22em', textTransform: 'uppercase',
                  border: 'none',
                  borderLeft: '1px solid var(--ink)',
                  cursor: busy ? 'not-allowed' : 'pointer',
                  opacity: busy || !input.trim() ? 0.4 : 1,
                  display: 'flex', alignItems: 'center', justifyContent: 'center'
                }}>→</button>
              </div>

              <div style={{ display: 'flex', gap: 10, padding: '10px 14px', alignItems: 'center',
                fontFamily: 'var(--f-mono)', fontSize: 10, letterSpacing: '0.18em',
                textTransform: 'uppercase', color: 'var(--ink-3)', borderTop: '1px solid var(--ink)' }}>
                <span>KEY:</span>
                <input
                  type="password" value={apiKey} onChange={e=>setApiKey(e.target.value)}
                  placeholder="sk-... (optional)"
                  style={{
                    flex: 1, background: 'var(--paper-2)', border: '1px solid var(--ink)',
                    padding: '3px 6px', fontFamily: 'var(--f-mono)', fontSize: 10, outline: 'none', width: '100%'
                  }}
                />
              </div>
            </div>
          </aside>
        </div>
      ) : (
        <TranscriptView />
      )}

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
}

function now() {
  const d = new Date();
  return d.toTimeString().slice(0,8);
}

function CANNED(q) {
  const l = q.toLowerCase();
  if (l.includes('nmap')) return 'Starting nmap scan on host.docker.internal.\nPorts 8000, 8080, 9001–9003 open. Services: Uvicorn, Werkzeug 3.1.3, nginx 1.29.4 ×3. See Dashboard § 06 for the printed copy.';
  if (l.includes('nikto')) return 'Running nikto on :8080 (no WAF) … 9 findings in 64 s. Running the same scan on :8000 (behind WAF) … connection timed out. WAF dropped probes faster than nikto could pivot.';
  if (l.includes('t1190')) return 'T1190 · Exploit Public-Facing Application — adversary abuses a flaw in an externally-reachable service to gain code execution. In this session the WAF intercepted 3,821 such attempts, scoring them above the 1.5 anomaly threshold.';
  if (l.includes('transformer')) return 'A Transformer autoencoder trained only on benign traffic. It learns to reconstruct normal tokenised request sequences; attack traffic reconstructs poorly, producing high loss. The loss itself is the anomaly score.';
  return 'Understood. I would dispatch that to the Kali bridge, then summarise. Switch to the cached transcript for a fully-rendered example.';
}

function Msg({ m }) {
  if (m.who === 'sys') {
    return (
      <div style={{
        fontFamily: 'var(--f-mono)', fontSize: 10,
        letterSpacing: '0.18em', textTransform: 'uppercase',
        color: 'var(--ink-3)', padding: '8px 0 12px',
        borderBottom: '1px dashed var(--ink-3)', marginBottom: 14,
      }}>
        ◆ {m.text}<br/>
        <span style={{ color: 'var(--ink-3)' }}>{m.meta}</span>
      </div>
    );
  }
  const isYou = m.who === 'you';
  return (
    <div style={{ marginBottom: 16 }}>
      <div style={{
        fontFamily: 'var(--f-mono)', fontSize: 10,
        letterSpacing: '0.18em', textTransform: 'uppercase',
        color: isYou ? 'var(--red)' : 'var(--teal)',
        marginBottom: 4,
      }}>
        {isYou ? '▲ You' : '◼ Assistant'} · <span style={{ color: 'var(--ink-3)' }}>{m.meta}</span>
      </div>
      <div style={{
        fontFamily: isYou ? 'var(--f-mono)' : 'var(--f-body)',
        fontSize: isYou ? 13 : 15,
        lineHeight: 1.6,
        padding: isYou ? '10px 14px' : '2px 0 2px 14px',
        borderLeft: '2px solid ' + (isYou ? 'var(--red)' : 'var(--teal)'),
        background: isYou ? 'var(--paper-2)' : 'transparent',
        whiteSpace: 'pre-wrap',
      }}>
        {isYou ? m.text : m.text}
      </div>

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
}

function TranscriptView() {
  return (
    <div style={{
      border: '1px solid var(--ink)', borderTop: 'none', padding: '28px 32px',
      background: 'var(--paper)',
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between',
        fontFamily: 'var(--f-mono)', fontSize: 10, letterSpacing: '0.22em',
        textTransform: 'uppercase', color: 'var(--ink-3)',
        padding: '0 0 10px', borderBottom: '1px solid var(--ink)', marginBottom: 18 }}>
        <span>Filed · {SESSION.when}</span>
        <span>Author · Rishit · Session K-04</span>
      </div>

      <h2 style={{ fontFamily: 'var(--f-display)', fontSize: 48,
        lineHeight: 1, marginBottom: 10 }}>
        A conversation, <em>verbatim.</em>
      </h2>
      <p style={{ maxWidth: 680, fontSize: 16, lineHeight: 1.6, color: 'var(--ink-2)' }}>
        {SESSION.intro}
      </p>

      <div style={{ marginTop: 24, padding: '24px', background: 'var(--paper-2)', border: '1px solid var(--ink)' }}>
        <h3 style={{ fontFamily: 'var(--f-display)', fontStyle: 'italic', fontSize: 24, marginBottom: 16 }}>
          Try asking in the console:
        </h3>
        <ol style={{ listStyle: 'none', padding: 0 }}>
          {SUGGESTIONS.map((s, i) => (
            <li key={i} style={{ padding: '8px 0', borderBottom: i < SUGGESTIONS.length-1 ? '1px dashed var(--ink-3)' : 'none', display: 'flex', gap: 12, alignItems: 'center' }}>
              <span style={{ fontFamily: 'var(--f-mono)', fontSize: 10, color: 'var(--ink-3)' }}>{String(i+1).padStart(2,'0')}.</span>
              <span style={{ fontFamily: 'var(--f-mono)', fontSize: 13, color: 'var(--red)' }}>&gt;</span>
              <span style={{ fontFamily: 'var(--f-mono)', fontSize: 13, flex: 1 }}>{s.text.toLowerCase()}</span>
              <span style={{ fontFamily: 'var(--f-mono)', fontSize: 9, letterSpacing: '0.2em', textTransform: 'uppercase', padding: '3px 6px', border: '1px solid var(--ink)', background: 'var(--paper)' }}>{s.tool}</span>
            </li>
          ))}
        </ol>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr',
        gap: 24, marginTop: 28 }}>
        {SESSION.blocks.map((b, i) => (
          <div className="fig" key={i}>
            <div className="fig-head">
              <div className="fig-num">Ex. {String(i+1).padStart(2,'0')}</div>
              <div className="fig-title"><em>{b.title}</em></div>
            </div>

            {b.kind === 'table' && (
              <div className="kv">
                {b.rows.map(([k,v]) => (
                  <div className="kv-row" key={k}><span className="k">{k}</span><span className="v">{v}</span></div>
                ))}
              </div>
            )}

            {b.kind === 'mitre' && (
              <div>
                {b.rows.map(([id,name,n]) => (
                  <div key={id} style={{
                    display: 'grid', gridTemplateColumns: '80px 1fr auto',
                    padding: '7px 0', borderBottom: '1px dotted var(--ink-3)',
                    fontFamily: 'var(--f-body)', fontSize: 14,
                  }}>
                    <span style={{ fontFamily: 'var(--f-mono)', color: 'var(--red)' }}>{id}</span>
                    <span>{name}</span>
                    <span style={{ fontFamily: 'var(--f-mono)', fontSize: 12 }}>{n.toLocaleString()}</span>
                  </div>
                ))}
              </div>
            )}

            {b.kind === 'code' && (
              <pre style={{
                fontFamily: 'var(--f-mono)', fontSize: 12, lineHeight: 1.8,
                background: 'var(--paper-3)',
                border: '1px solid var(--ink)', padding: 14,
                overflowX: 'auto', margin: 0,
              }}>{b.lines.join('\n')}</pre>
            )}
          </div>
        ))}
      </div>

      <div style={{ marginTop: 24, padding: '14px 18px',
        border: '1px solid var(--ink)', background: 'var(--ink)', color: 'var(--paper)',
        fontFamily: 'var(--f-mono)', fontSize: 11, letterSpacing: '0.2em', textTransform: 'uppercase',
        display: 'flex', justifyContent: 'space-between' }}>
        <span>Σ · End of transcript</span>
        <span style={{ color: 'var(--gold)' }}>5,555 blocked · 67.9% rate</span>
      </div>

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
}

export default Assistant;
