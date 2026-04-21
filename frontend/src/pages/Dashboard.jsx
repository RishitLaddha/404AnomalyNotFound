import React, { useState, useEffect } from 'react';
import TypewriterWord from '../components/TypewriterWord';



// ──────────────────────────────────────────────────────────
//  Data
// ──────────────────────────────────────────────────────────

const MITRE = [
  { id: 'T1190', name: 'Exploit Public-Facing App',   blocked: 3821 },
  { id: 'T1083', name: 'File & Directory Discovery',  blocked:  847 },
  { id: 'T1078', name: 'Valid Accounts — Admin',      blocked:  412 },
  { id: 'T1592', name: 'Gather Victim Host Info',     blocked:  203 },
  { id: 'T1552', name: 'Unsecured Credentials',       blocked:  134 },
  { id: 'T1505', name: 'Server Software Component',   blocked:   89 },
  { id: 'T1059', name: 'Command & Scripting',         blocked:   49 },
];

const INFRA = [
  { port: 8000, service: 'Uvicorn',        role: 'Transformer WAF Proxy',    tag: 'WAF',    cls: 'waf',    portCls: 'teal' },
  { port: 8080, service: 'Werkzeug 3.1.3', role: 'Target App (Unprotected)', tag: 'Target', cls: 'target', portCls: 'red'  },
  { port: 9001, service: 'nginx 1.29.4',   role: 'DVWA Proxy',               tag: 'Proxy',  cls: 'proxy',  portCls: 'blue' },
  { port: 9002, service: 'nginx 1.29.4',   role: 'Juice Shop Proxy',         tag: 'Proxy',  cls: 'proxy',  portCls: 'blue' },
  { port: 9003, service: 'nginx 1.29.4',   role: 'WebGoat Proxy',            tag: 'Proxy',  cls: 'proxy',  portCls: 'blue' },
];

const PIPELINE = [
  { label: 'Traffic Gen',     desc: 'Locust simulates real users across DVWA, Juice Shop, WebGoat targets.' },
  { label: 'Nginx Logging',   desc: 'Requests proxied through Nginx with a structured log format.' },
  { label: 'Safe Filtering',  desc: 'Whitelist DVWA, exclude WebGoat; attack-surface endpoints removed.' },
  { label: 'Tokenization',    desc: 'Path segments, methods, status codes → discrete token sequences.' },
  { label: 'Transformer',     desc: 'Autoencoder learns benign patterns via reconstruction loss.' },
  { label: 'Anomaly Score',   desc: 'Unknown patterns score high — flagged as attacks automatically.' },
  { label: 'Realtime Proxy',  desc: 'FastAPI scores every request, blocks anomalies, maps to MITRE.' },
];

const LOSS = [
  { epoch:  1, loss: 0.1826,  pct: 100 },
  { epoch:  5, loss: 0.0005,  pct:  40 },
  { epoch: 10, loss: 0.0002,  pct:  25 },
  { epoch: 15, loss: 0.0001,  pct:  15 },
  { epoch: 20, loss: 0.00005, pct:   8 },
  { epoch: 26, loss: 0.00001, pct:   2 },
];

const MODEL = [
  ['Architecture',    'Transformer Autoencoder'],
  ['d_model',         '128'],
  ['Attention Heads', '4'],
  ['Encoder Layers',  '3'],
  ['Decoder Layers',  '3'],
  ['Feed-forward',    '512'],
  ['Dropout',         '0.3'],
  ['Max Seq Length',  '12 tokens'],
  ['Optimizer',       'Adam · lr 0.0001'],
  ['Loss',            'CrossEntropyLoss'],
  ['Threshold',       '1.5 (calibrated)'],
];

const NIKTO_BAD = [
  ['Scan Status',     'Completed · 64s'],
  ['Requests Tested', '8,211'],
  ['Vulnerabilities', '9 found'],
  ['Server Exposed',  'Werkzeug/3.1.3'],
  ['Python Version',  'Leaked (3.12.4)'],
  ['Missing Headers', 'CSP · HSTS · XCT'],
];

const NIKTO_GOOD = [
  ['Scan Status',     'TIMED OUT (blocked)'],
  ['Requests Tested', 'Dropped by WAF'],
  ['Vulnerabilities', '0 useful findings'],
  ['Server Exposed',  'ARRAY(garbage)'],
  ['Python Version',  'NOT LEAKED'],
  ['Attack Score',    '4.18 vs 1.5 thr'],
];

// ──────────────────────────────────────────────────────────
//  Dashboard
// ──────────────────────────────────────────────────────────

function Dashboard() {
  const [blocked, setBlocked] = useState(0);

  useEffect(() => {
    const t = 5555;
    const step = Math.ceil(t / 80);
    const id = setInterval(() => {
      setBlocked(c => (c + step >= t ? (clearInterval(id), t) : c + step));
    }, 18);
    return () => clearInterval(id);
  }, []);

  const max = Math.max(...MITRE.map(m => m.blocked));

  return (
    <div className="page">

      {/* ─── BANNER ─── */}
      <section className="banner">
        <div className="banner-top">
          <span>Filed under · Adversarial ML / Network Defense</span>
          <span>Printed in Mumbai · Single copy</span>
        </div>

        <h1 className="banner-title">
          A Firewall That&nbsp;<TypewriterWord words={['Reads', 'Blocks', 'Monitors']} /><br/>
          Its Own Traffic.
        </h1>

        <div className="banner-sub">
          <div className="cell">
            <span className="label">Abstract</span>
            An unsupervised Transformer autoencoder trained <em>exclusively</em> on benign traffic.
            It detects zero-shot attacks through reconstruction loss — no labelled attack data required.
          </div>
          <div className="cell">
            <span className="label">Problem · SIH 25172</span>
            Conventional WAFs rely on signatures and rules, leaving a persistent window for unseen
            attacks. This bulletin documents a self-supervised alternative, in production.
          </div>
          <div className="cell">
            <span className="label">At a glance</span>
            <div style={{ fontFamily: 'var(--f-mono)', fontSize: 12, lineHeight: 1.9, marginTop: 2 }}>
              → 5,555 / 8,180 attacks blocked<br/>
              → 10,000× benign-vs-attack separation<br/>
              → 1.41M params · 77,004 training seqs
            </div>
          </div>
        </div>

        <div className="colophon">
          <span>404AnomalyNotFound · Vol. I</span>
          <span>Issue 04 · Ser. A</span>
          <span>Author · R.L.</span>
          <span>PyTorch · FastAPI · Kali</span>
          <span className="blink">● Live · 21·IV·2026</span>
        </div>
      </section>

      {/* ─── §01 KEY NUMBERS ─── */}
      <section className="section">
        <header className="section-head">
          <div className="section-num">§ Section<b>01</b></div>
          <h2 className="section-title">The numbers, first.</h2>
          <div className="section-kicker">
            A single session on 21 April. Attacks fired, attacks stopped, in plain figures.
          </div>
        </header>

        <div className="stats-strip">
          <div className="stat">
            <div className="v red">{blocked.toLocaleString()}</div>
            <div className="k">Attacks<br/>Blocked</div>
            <div className="corner">i.</div>
          </div>
          <div className="stat">
            <div className="v">67.<em>9</em>%</div>
            <div className="k">Block<br/>Rate</div>
            <div className="corner">ii.</div>
          </div>
          <div className="stat">
            <div className="v gold">10,000×</div>
            <div className="k">Score<br/>Separation</div>
            <div className="corner">iii.</div>
          </div>
          <div className="stat">
            <div className="v blue">77,004</div>
            <div className="k">Training<br/>Sequences</div>
            <div className="corner">iv.</div>
          </div>
          <div className="stat">
            <div className="v">1.<em>41</em>M</div>
            <div className="k">Model<br/>Parameters</div>
            <div className="corner">v.</div>
          </div>
          <div className="stat">
            <div className="v teal">26</div>
            <div className="k">Training<br/>Epochs</div>
            <div className="corner">vi.</div>
          </div>
        </div>
      </section>

      {/* ─── §02 ARCHITECTURE ─── */}
      <section className="section">
        <header className="section-head">
          <div className="section-num">§ Section<b>02</b></div>
          <h2 className="section-title">How the&nbsp;<em>pipeline</em>&nbsp;runs.</h2>
          <div className="section-kicker">
            End-to-end, from captured packet to blocked request. Seven stages, one loop.
          </div>
        </header>

        <div className="pipeline">
          {PIPELINE.map((s, i) => (
            <div className="pipe-step" key={i}>
              <div className="pnum">{String(i+1).padStart(2,'0')}</div>
              <div className="plabel">{s.label}</div>
              <div className="pdesc">{s.desc}</div>
            </div>
          ))}
        </div>

        <div style={{ marginTop: 14, display: 'flex', justifyContent: 'space-between',
          fontFamily: 'var(--f-mono)', fontSize: 10, letterSpacing: '0.2em',
          textTransform: 'uppercase', color: 'var(--ink-3)' }}>
          <span>Fig. 1 · System pipeline, left → right</span>
          <span>Trained on Kaggle T4 GPU · ≈ 18 min</span>
        </div>
      </section>

      {/* ─── §03 TRAINING ─── */}
      <section className="section">
        <header className="section-head">
          <div className="section-num">§ Section<b>03</b></div>
          <h2 className="section-title">Training&nbsp;<em>diary.</em></h2>
          <div className="section-kicker">
            Loss against epoch. Config beside it. No ceremony.
          </div>
        </header>

        <div className="grid-2">
          <div className="fig" style={{ borderRight: 'none' }}>
            <div className="fig-head">
              <div className="fig-num">Fig. 2 — Loss Curve</div>
              <div className="fig-title"><em>99.99%</em> reduction</div>
            </div>
            {LOSS.map(l => (
              <div className="loss-row" key={l.epoch}>
                <span className="ep">ep · {String(l.epoch).padStart(2,'0')}</span>
                <div className="lb"><span style={{ width: l.pct + '%' }}/></div>
                <span className="val">{l.loss}</span>
              </div>
            ))}
            <div className="fig-cap">
              y-axis: cross-entropy loss · x-axis: epoch · 26 epochs total
            </div>
          </div>

          <div className="fig">
            <div className="fig-head">
              <div className="fig-num">Fig. 3 — Model</div>
              <div className="fig-title"><em>Transformer</em> AE</div>
            </div>
            <div className="kv">
              {MODEL.map(([k,v]) => (
                <div className="kv-row" key={k}>
                  <span className="k">{k}</span>
                  <span className="v">{v}</span>
                </div>
              ))}
            </div>
            <div className="fig-cap">
              Encoder-decoder · benign-only supervision · no labelled attacks
            </div>
          </div>
        </div>
      </section>

      {/* ─── §04 WAF EFFECTIVENESS ─── */}
      <section className="section">
        <header className="section-head">
          <div className="section-num">§ Section<b>04</b></div>
          <h2 className="section-title">Nikto vs.&nbsp;<em>the wall.</em></h2>
          <div className="section-kicker">
            Eight thousand probes. Side by side: naked server against the same server behind the WAF.
          </div>
        </header>

        <div className="cmp">
          <div className="cmp-col bad">
            <div className="cmp-head">
              <span>Port 8080 · no WAF</span>
              <span className="stamp">Exposed</span>
            </div>
            {NIKTO_BAD.map(([k,v]) => (
              <div className="cmp-row" key={k}><span className="k">{k}</span><span className="v">{v}</span></div>
            ))}
          </div>
          <div className="cmp-col good">
            <div className="cmp-head">
              <span>Port 8000 · Transformer WAF</span>
              <span className="stamp teal">Defended</span>
            </div>
            {NIKTO_GOOD.map(([k,v]) => (
              <div className="cmp-row" key={k}><span className="k">{k}</span><span className="v">{v}</span></div>
            ))}
          </div>
        </div>
        <div style={{ marginTop: 10, fontFamily: 'var(--f-mono)', fontSize: 10,
          letterSpacing: '0.2em', textTransform: 'uppercase', color: 'var(--ink-3)' }}>
          Fig. 4 · Nikto fired 8,211 vulnerability probes
        </div>
      </section>

      {/* ─── §05 MITRE ─── */}
      <section className="section">
        <header className="section-head">
          <div className="section-num">§ Section<b>05</b></div>
          <h2 className="section-title">MITRE&nbsp;<em>att&amp;ck</em>&nbsp;coverage.</h2>
          <div className="section-kicker">
            Every blocked request carries a technique label. These are the top seven.
          </div>
        </header>

        <div className="data-table">
          <div className="data-head">
            <span>Technique</span>
            <span>Name</span>
            <span>Distribution</span>
            <span style={{textAlign:'right'}}>Blocked</span>
          </div>
          {MITRE.map(m => (
            <div className="data-row" key={m.id}>
              <span className="id">{m.id}</span>
              <span>{m.name}</span>
              <div className="bar"><span style={{ width: (m.blocked/max*100).toFixed(1)+'%' }}/></div>
              <span className="num">{m.blocked.toLocaleString()}</span>
            </div>
          ))}
          <div className="data-row" style={{ background: 'var(--ink)', color: 'var(--paper)' }}>
            <span className="id" style={{ color: 'var(--gold)' }}>Σ</span>
            <span style={{ fontFamily: 'var(--f-mono)', fontSize: 11,
              letterSpacing: '0.18em', textTransform: 'uppercase' }}>
              Total blocked · 67.9% rate over 8,180 requests
            </span>
            <span />
            <span className="num" style={{ color: 'var(--gold)' }}>5,555</span>
          </div>
        </div>
      </section>

      {/* ─── §06 INFRA ─── */}
      <section className="section">
        <header className="section-head">
          <div className="section-num">§ Section<b>06</b></div>
          <h2 className="section-title">Live&nbsp;<em>infrastructure.</em></h2>
          <div className="section-kicker">
            Discovered by Kali nmap. Five open ports in the demo sandbox.
          </div>
        </header>

        <div className="infra">
          <div className="infra-head">
            <span>Port</span><span>Service</span><span>Role</span><span style={{textAlign:'right'}}>Status</span>
          </div>
          {INFRA.map(i => (
            <div className="infra-row" key={i.port}>
              <span className={'port ' + i.portCls}>{i.port}</span>
              <span>{i.service}</span>
              <span className="role">{i.role}</span>
              <span style={{ textAlign: 'right' }}>
                <span className={'tag ' + i.cls}>{i.tag}</span>
              </span>
            </div>
          ))}
        </div>
      </section>

      {/* ─── FOOTER ─── */}
      <footer className="foot">
        <div>
          <h4>404AnomalyNotFound — an anomaly bulletin.</h4>
          <p style={{ maxWidth: 480, fontSize: 14, color: 'var(--ink-2)', marginTop: 6 }}>
            Composed in warm paper and ink, set in Instrument Serif and JetBrains Mono. Printed digitally
            for the committee of Smart India Hackathon · Problem ID 25172.
          </p>
        </div>
        <div>
          <div className="mono" style={{ marginBottom: 8 }}>Correspondence</div>
          <div style={{ fontSize: 14, fontFamily: 'var(--f-mono)' }}>
            rladofficiel00@gmail.com<br/>
            PyTorch · FastAPI · Kali<br/>
            404anomalynotfound.vercel.app
          </div>
        </div>
        <div>
          <div className="mono" style={{ marginBottom: 8 }}>Sections</div>
          <div style={{ fontFamily: 'var(--f-mono)', fontSize: 12, lineHeight: 2 }}>
            01 · Dashboard<br/>
            02 · AI Assistant<br/>
            03 · About Me<br/>
            04 · GitHub ↗
          </div>
        </div>
      </footer>
      <div className="colophon" style={{ marginTop: 24 }}>
        <span>— End of bulletin —</span>
        <span>Set in Instrument Serif &amp; IBM Plex</span>
        <span>© MMXXVI 404AnomalyNotFound</span>
      </div>
    </div>
  );
}

export default Dashboard;
