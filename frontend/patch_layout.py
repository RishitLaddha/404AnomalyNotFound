import os
import codecs

path = '/Users/rishitladdha/Downloads/waf-project 2/frontend/src/pages/Assistant.jsx'

with codecs.open(path, 'r', 'utf-8') as f:
    text = f.read()

# 1. Update setMessages 
old_set_messages = """        text: data.response || data.detail || (data.summary + '\\n\\n' + data.detail), 
        meta: `tool · ${data.tool_used || 'gemini'} · ` + now() """
new_set_messages = """        text: data.summary || data.response || 'Task completed.',
        detail: data.detail || data.response,
        raw_output: data.raw_output || '',
        meta: `tool · ${data.tool_used || 'gemini'} · ` + now() """
text = text.replace(old_set_messages, new_set_messages)

# 2. Update grid template columns
text = text.replace("gridTemplateColumns: '1.75fr 1fr',", "gridTemplateColumns: '3fr 1fr',")

# 3. Replace Console Column
old_console = """          {/* Console column */}
          <div style={{ borderRight: '1px solid var(--ink)', display: 'flex', flexDirection: 'column', minHeight: 560 }}>
            <div style={{
              padding: '10px 16px', borderBottom: '1px solid var(--ink)',
              fontFamily: 'var(--f-mono)', fontSize: 10, letterSpacing: '0.2em', textTransform: 'uppercase',
              color: 'var(--ink-3)', background: 'var(--paper-2)',
              display: 'flex', justifyContent: 'space-between',
            }}>
              <span>~/404anf/assistant — session  {now()}</span>
              <span>▢ ▢ ▢</span>
            </div>

            <div ref={viewRef} style={{ flex: 1, overflowY: 'auto', padding: 20, maxHeight: 560 }}>
              {messages.map((m,i) => <Msg key={i} m={m} />)}
              {busy && (
                <div style={{ fontFamily: 'var(--f-mono)', fontSize: 12, color: 'var(--ink-3)' }}>
                  <span style={{ color: 'var(--red)' }}>◼</span> thinking
                  <span className="blink">_</span>
                </div>
              )}
            </div>

            <div style={{ borderTop: '1px solid var(--ink)', padding: 14, background: 'var(--paper-2)' }}>
              <div style={{ display: 'flex', gap: 10, alignItems: 'stretch' }}>
                <span style={{ fontFamily: 'var(--f-mono)', fontSize: 14, color: 'var(--red)', paddingTop: 10 }}>&gt;</span>
                <input
                  value={input}
                  onChange={e => setInput(e.target.value)}
                  onKeyDown={e => e.key==='Enter' && send()}
                  placeholder="type a command or question — ENTER to send"
                  style={{
                    flex: 1, background: 'var(--paper)',
                    border: '1px solid var(--ink)', padding: '10px 12px',
                    fontFamily: 'var(--f-mono)', fontSize: 13, color: 'var(--ink)',
                    outline: 'none',
                  }}
                />
                <button onClick={() => send()} disabled={busy || !input.trim()} style={{
                  padding: '10px 18px', background: 'var(--ink)', color: 'var(--paper)',
                  fontFamily: 'var(--f-mono)', fontSize: 11, letterSpacing: '0.22em', textTransform: 'uppercase',
                  border: '1px solid var(--ink)',
                  cursor: busy ? 'not-allowed' : 'pointer',
                  opacity: busy || !input.trim() ? 0.4 : 1,
                }}>Transmit →</button>
              </div>
              <div style={{ display: 'flex', gap: 10, marginTop: 10, alignItems: 'center',
                fontFamily: 'var(--f-mono)', fontSize: 10, letterSpacing: '0.18em',
                textTransform: 'uppercase', color: 'var(--ink-3)' }}>
                <span>Gemini Key</span>
                <input
                  type="password" value={apiKey} onChange={e=>setApiKey(e.target.value)}
                  placeholder="optional · sk-..."
                  style={{
                    flex: 1, background: 'var(--paper)', border: '1px solid var(--ink)',
                    padding: '5px 8px', fontFamily: 'var(--f-mono)', fontSize: 11, outline: 'none',
                  }}
                />
                <span>·</span>
                <span>Rate limit 60/min</span>
              </div>
            </div>
          </div>"""

new_console = """          {/* Left Column (75%) — Output Pane */}
          <div style={{ borderRight: '1px solid var(--ink)', display: 'flex', flexDirection: 'column', minHeight: 560 }}>
            <div style={{
              padding: '10px 16px', borderBottom: '1px solid var(--ink)',
              fontFamily: 'var(--f-mono)', fontSize: 10, letterSpacing: '0.2em', textTransform: 'uppercase',
              color: 'var(--ink-3)', background: 'var(--paper-2)',
              display: 'flex', justifyContent: 'space-between',
            }}>
              <span>~/404anf/assistant — OUTPUT  {now()}</span>
              <span>▢ ▢ ▢</span>
            </div>
            
            <div style={{ flex: 1, overflowY: 'auto', padding: 32, maxHeight: 600 }}>
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
          </div>"""
text = text.replace(old_console, new_console)

# 4. Replace Right Column
old_aside = """          {/* Right — suggestions index */}
          <aside style={{ padding: '18px 20px', background: 'var(--paper-2)' }}>
            <div style={{
              fontFamily: 'var(--f-mono)', fontSize: 10,
              letterSpacing: '0.22em', textTransform: 'uppercase',
              color: 'var(--ink-3)', marginBottom: 10,
            }}>Index of suggestions</div>
            <h3 style={{ fontFamily: 'var(--f-display)', fontStyle: 'italic',
              fontSize: 32, lineHeight: 1.05, marginBottom: 18, color: 'var(--ink)' }}>
              Try asking <em>the assistant&nbsp;</em>
            </h3>
            <ol style={{ listStyle: 'none', padding: 0 }}>
              {SUGGESTIONS.map((s,i) => (
                <li key={i} style={{ borderTop: '1px solid var(--ink)' }}>
                  <button onClick={() => send(s.text)} style={{
                    display: 'grid', gridTemplateColumns: '28px 1fr auto',
                    gap: 10, width: '100%', textAlign: 'left',
                    padding: '12px 0', cursor: 'pointer', alignItems: 'baseline',
                  }}>
                    <span style={{ fontFamily: 'var(--f-mono)', fontSize: 10,
                      color: 'var(--ink-3)' }}>{String(i+1).padStart(2,'0')}.</span>
                    <span style={{ fontFamily: 'var(--f-body)', fontSize: 14, color: 'var(--ink)' }}>
                      {s.label}
                    </span>
                    <span style={{
                      fontFamily: 'var(--f-mono)', fontSize: 9,
                      letterSpacing: '0.2em', textTransform: 'uppercase',
                      padding: '3px 6px', border: '1px solid var(--ink)',
                      background: 'var(--paper)',
                      color: 'var(--ink-2)',
                    }}>{s.tool}</span>
                  </button>
                </li>
              ))}
              <li style={{ borderTop: '1px solid var(--ink)' }}/>
            </ol>

            <div style={{
              marginTop: 24, padding: '14px 16px',
              border: '1px solid var(--ink)', background: 'var(--paper)',
            }}>
              <div style={{ fontFamily: 'var(--f-mono)', fontSize: 10,
                letterSpacing: '0.2em', textTransform: 'uppercase',
                color: 'var(--red)', marginBottom: 8 }}>
                ✕ Handle with care
              </div>
              <p style={{ fontSize: 13, lineHeight: 1.5, color: 'var(--ink-2)' }}>
                The assistant can execute real reconnaissance tools. The demo sandbox is isolated —
                do not redirect it at live infrastructure. You are accountable for what you type.
              </p>
            </div>
          </aside>"""

new_aside = """          {/* Right Column (25%) — Chat Pane */}
          <aside style={{ display: 'flex', flexDirection: 'column', background: 'var(--paper-2)', minHeight: 560 }}>
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
              
              <div style={{ display: 'flex', alignItems: 'center', borderTop: '1px dashed var(--ink-3)' }}>
                <select 
                  onChange={e => { if (e.target.value) { setInput(e.target.value); } }}
                  style={{
                    width: '100%', padding: '10px 14px', fontFamily: 'var(--f-mono)', fontSize: 10,
                    background: 'var(--paper-2)', border: 'none', outline: 'none', color: 'var(--ink)'
                  }}
                  defaultValue=""
                >
                  <option value="" disabled>Load a suggestion...</option>
                  {SUGGESTIONS.map((s,i) => (
                    <option key={i} value={s.text}>{s.label}</option>
                  ))}
                </select>
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
          </aside>"""

text = text.replace(old_aside, new_aside)

# Finally, Msg component uses ReactMarkdown which we imported, but wait, we want to NOT use react markdown inside the short chat pane for bot messages!
# We want short plaintext summary in the short chat pane!
# The current Msg component uses <ReactMarkdown> if it's the bot!
old_msg = """        {isYou ? m.text : (
          <div className="md-body">
            <ReactMarkdown>{m.text}</ReactMarkdown>
          </div>
        )}"""
new_msg = """        {isYou ? m.text : m.text}""" # the summary isn't markdown!

text = text.replace(old_msg, new_msg)

with codecs.open(path, 'w', 'utf-8') as f:
    f.write(text)
