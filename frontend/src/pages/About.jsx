import React, { useState, useEffect } from 'react';
import TypewriterWord from '../components/TypewriterWord';


function About() {
  const TIMELINE = [
    { yr: '2023', t: 'Began B.Tech in Computer Science — AI & ML — at ATLAS SkillTech University.' },
    { yr: '2024', t: 'First AI internship at Codsoft. Built chatbots (85% query accuracy) and a movie recommender (+20% relevance).' },
    { yr: '2025', t: 'Interned at Runway Technologies and TEACH NGO. Shipped document-parsing models, +30% faster retrieval.' },
    { yr: '2025', t: 'Forward-Deployed Engineer Intern at Supervity — Command Center work for Japanese enterprise clients.' },
    { yr: '2026', t: 'Stellar Student — All Rounder award. Perfect 10.0 SGPA. 404AnomalyNotFound WAF for SIH 25172.' },
    { yr: '2027', t: 'Graduation (expected). Until then: more models, more miles on the compute bill.' },
  ];

  const STACK = [
    ['PyTorch',       'From-scratch ResNet-50, BhashaNet, 404AnomalyNotFound'],
    ['TensorFlow',    'Occasional second opinion'],
    ['AWS',           'EC2 g6.xlarge training, S3, Lambda'],
    ['Azure · GCP',   'Azure ML, Vertex AI when required'],
    ['HuggingFace',   'Spaces, Inference APIs, Model Hub'],
    ['Docker · K8s',  'Reproducible environments, deployment'],
    ['Spark · Hadoop','Big-data pipelines, batch jobs'],
    ['Pandas · sklearn','The bread and butter'],
  ];

  const PRINCIPLES = [
    ['01', 'Train from first principles', 'Fine-tuning teaches you how to drive. Training from scratch teaches you what a car is.'],
    ['02', 'Measure, then move', 'BLEU 6.42 after 5 epochs, 76.77% Top-1 on ImageNet — numbers first, opinions after.'],
    ['03', 'Ship the prototype anyway', 'Huggingface Space, AWS Lambda demo, public repo. If it isn\'t online, it didn\'t happen.'],
    ['04', 'Design matters, even in ML', 'Dashboards, papers, READMEs — the way you present a result shapes whether anyone reads it.'],
  ];

  const PROJECTS = [
    {
      name: 'VisionForge — ResNet-50 on ImageNet-1K',
      blurb: 'Trained ResNet-50 from random init on 1.28M images across 1000 classes — 90 epochs, ~4 days on an AWS EC2 g6.xlarge GPU. Hit 76.77% Top-1 / 93.51% Top-5. Full pipeline: ingestion, MixUp/CutMix, mixed-precision, cosine LR, WandB monitoring, HuggingFace + AWS Lambda demos.',
      stack: 'PyTorch · AWS · WandB · HuggingFace',
    },
    {
      name: 'BhashaNet — EN→GU neural machine translation',
      blurb: 'Transformer NMT built from scratch. No pre-training, no transfer learning. 285K parallel pairs from AI4Bharat Samanantar, BPE (SentencePiece, 16K vocab). BLEU 6.42 after 5 epochs, scalable to the full 3M+ set. Live Huggingface + AWS Lambda deployments.',
      stack: 'PyTorch · Transformers · SentencePiece · Lambda',
    },
    {
      name: 'MockMate — AI interview avatar',
      blurb: 'Voice-first mock interviews with JD-driven scoring, emotion-aware follow-ups, and a dashboard. RAG + local-first inference via Ollama. Priced at ₹19–₹50/session. 3rd place CIEL HR Live Project; top 3 in batch.',
      stack: 'Python · Flask · Unity · Ollama · LangChain',
    },
    {
      name: 'Inkspire — book recommender',
      blurb: 'Five approaches in one app: popularity, user-CF, content-based, matrix factorisation, hybrid. Trained on a 1M+ Kaggle corpus, deployed on Streamlit. ~11% CTR lift and 7% longer sessions in A/B testing.',
      stack: 'Python · Streamlit · scikit-learn',
    },
    {
      name: 'Customer Churn Prediction',
      blurb: '10,000-row banking dataset. Preprocessing, balancing, oversampling, multiple models compared. Random Forest hit 86% test accuracy. Also a mid-sem research paper.',
      stack: 'scikit-learn · Random Forest · XGBoost',
    },
    {
      name: 'Data Transformer · Chore Ditch AI',
      blurb: 'Prompt-engineered pipelines for cleaning and integrating datasets (~40% less prep time) and a Python automation system for personal task + file organisation. The boring infrastructure that actually ships.',
      stack: 'Python · NLP · Google APIs · Automation',
    },
  ];

  return (
    <div className="page">

      {/* Masthead */}
      <section className="banner">
        <div className="banner-top">
          <span>Colophon · Author Biography</span>
          <span>Mumbai, India · MMXXVI</span>
        </div>
        <h1 className="banner-title" style={{ fontSize: 'clamp(64px,11vw,140px)' }}>
          The&nbsp;<TypewriterWord words={['Author.', 'Builder.', 'Student Researcher.']} />
        </h1>
        <div style={{ fontFamily: 'var(--f-display)', fontStyle: 'italic',
          fontSize: 'clamp(28px, 3.4vw, 44px)', color: 'var(--red)',
          marginTop: -6, marginBottom: 18, letterSpacing: '0.005em' }}>
          Rishit Laddha
        </div>
        <div className="banner-sub">
          <div className="cell">
            <span className="label">Who</span>
            Third-year B.Tech student in <em>Computer Science (AI & ML)</em> at ATLAS SkillTech University, Mumbai.
            I train models from first principles — ResNet-50 on ImageNet, a Transformer NMT for Gujarati — and ship
            them to the internet. 10.0 / 9.75 SGPA last two semesters; top of batch.
          </div>
          <div className="cell">
            <span className="label">Recognition</span>
            <em>Stellar Student — The All Rounder</em>, 2026. Third place, CIEL HR Live Project.
            Top 3 in batch for MockMate. Internships at Supervity, Runway Technologies, and TEACH NGO —
            prototypes that cut manual effort by 30–40% and turnaround by ~25%.
          </div>
          <div className="cell">
            <span className="label">Currently</span>
            Building 404AnomalyNotFound — a transformer WAF that reads its own traffic. Reading papers after midnight.
            Writing the occasional mid-semester research note. Always a little undercaffeinated.
          </div>
        </div>
      </section>

      {/* §α Portrait + bio */}
      <section className="section">
        <header className="section-head">
          <div className="section-num">§ Section<b>α</b></div>
          <h2 className="section-title">A short&nbsp;<em>biography.</em></h2>
          <div className="section-kicker">
            Four paragraphs, plain English. The receipts are further down.
          </div>
        </header>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1.7fr', gap: 0, border: '1px solid var(--ink)' }}>
          <div style={{
            borderRight: '1px solid var(--ink)',
            minHeight: 500, position: 'relative',
            background: 'var(--paper-2)',
            overflow: 'hidden',
          }}>
            <img
              src="assets/rishit.png"
              alt="Rishit Laddha — Stellar Student, ATLAS SkillTech University, 2026"
              style={{
                width: '100%', height: '100%', minHeight: 500,
                objectFit: 'cover', objectPosition: 'center top',
                display: 'block',
                filter: 'grayscale(1) contrast(1.08) brightness(0.98) sepia(0.18)',
                mixBlendMode: 'multiply',
              }}
            />
            {/* paper-grain overlay to match the bulletin */}
            <div style={{
              position: 'absolute', inset: 0, pointerEvents: 'none',
              background: 'repeating-linear-gradient(0deg, rgba(58,46,36,0.06) 0 1px, transparent 1px 3px)',
              mixBlendMode: 'multiply',
            }}/>
            <div style={{
              position: 'absolute', left: 18, bottom: 18,
              fontFamily: 'var(--f-mono)', fontSize: 10,
              letterSpacing: '0.22em', textTransform: 'uppercase',
              background: 'var(--paper)', border: '1px solid var(--ink)',
              padding: '6px 10px', color: 'var(--ink-2)',
            }}>
              Fig. α — R. Laddha, Mumbai 2026
            </div>
            <span className="stamp" style={{ position: 'absolute', top: 18, right: 18, background: 'var(--paper)' }}>
              Stellar · 2026
            </span>
          </div>

          <div style={{ padding: '32px 36px', background: 'var(--paper)' }}>
            <p style={{ fontFamily: 'var(--f-display)', fontStyle: 'italic',
              fontSize: 26, lineHeight: 1.3, marginBottom: 18,
              color: 'var(--ink)', textWrap: 'pretty' }}>
              "I build AI systems from first principles — one tokenizer, one optimiser,
              one training loop at a time — because the field rewards people who have
              actually held the gradients in their hands."
            </p>

            <p style={{ fontSize: 15, lineHeight: 1.65, marginBottom: 14 }}>
              I'm an AI &amp; ML researcher and third-year B.Tech student at ATLAS SkillTech
              University in Mumbai. My work has spanned computer vision, NLP, recommendation
              systems, and AI automation — with a particular interest in training end-to-end
              systems from scratch rather than fine-tuning someone else's weights.
            </p>
            <p style={{ fontSize: 15, lineHeight: 1.65, marginBottom: 14 }}>
              Over the last two years I have trained ResNet-50 on ImageNet-1K from random
              initialisation (76.77% Top-1, 93.51% Top-5), built <em>BhashaNet</em> — a
              Transformer NMT for English → Gujarati on 285K parallel pairs (BLEU 6.42 after
              five epochs), and shipped <em>MockMate</em>, an AI interview avatar that placed
              third in the CIEL HR live competition.
            </p>
            <p style={{ fontSize: 15, lineHeight: 1.65, marginBottom: 14 }}>
              In industry I have interned as a Forward-Deployed Engineer at Supervity on
              Command Center work for Japanese enterprise clients, as an AI Engineer at
              Runway Technologies building document-parsing and search systems, and as a
              Research &amp; Tech intern at TEACH NGO — each engagement cutting manual
              effort by ~30–40% and response time by ~15–25%.
            </p>
            <p style={{ fontSize: 15, lineHeight: 1.65 }}>
              Academically I hold a 10.0 and 9.75 SGPA across my last two semesters (top of
              batch), an overall 8.9 CGPA, and the <em>Stellar Student — All Rounder</em>
              award for 2026. If you'd like to talk — about ML, deployment, or why a
              transformer is a useful anomaly detector — my inbox is open.
            </p>

            <div style={{ display: 'flex', gap: 10, marginTop: 22, flexWrap: 'wrap',
              paddingTop: 16, borderTop: '1px solid var(--ink)' }}>
              <a href="https://github.com/RishitLaddha/404AnomalyNotFound" target="_blank" rel="noopener"
                 className="stamp blue"
                 style={{ transform: 'rotate(0)', textDecoration: 'none' }}>GitHub ↗</a>
              <a href="mailto:rladofficiel00@gmail.com"
                 className="stamp teal"
                 style={{ transform: 'rotate(0)', textDecoration: 'none' }}>
                rladofficiel00@gmail.com
              </a>
              <span className="stamp gold" style={{ transform: 'rotate(0)' }}>
                LinkedIn · Medium
              </span>
              <span className="stamp" style={{ transform: 'rotate(0)' }}>
                Student ID · 10929050
              </span>
            </div>
          </div>
        </div>
      </section>

      {/* §β Education */}
      <section className="section">
        <header className="section-head">
          <div className="section-num">§ Section<b>β</b></div>
          <h2 className="section-title"><em>Education,</em>&nbsp;on record.</h2>
          <div className="section-kicker">Degree, grades, coursework — in that order.</div>
        </header>

        <div style={{ border: '1px solid var(--ink)', padding: '28px 32px', background: 'var(--paper)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline',
            paddingBottom: 14, borderBottom: '1px solid var(--ink)', marginBottom: 18 }}>
            <div>
              <div style={{ fontFamily: 'var(--f-mono)', fontSize: 10,
                letterSpacing: '0.22em', textTransform: 'uppercase', color: 'var(--ink-3)' }}>
                2023 · July &nbsp;—&nbsp;  2027 · June (expected)
              </div>
              <h3 style={{ fontFamily: 'var(--f-display)', fontSize: 40,
                lineHeight: 1, margin: '6px 0 4px' }}>
                ATLAS SkillTech University, <em>Mumbai.</em>
              </h3>
              <div style={{ fontSize: 15, color: 'var(--ink-2)' }}>
                Bachelor of Technology · Computer Science, AI &amp; ML
              </div>
            </div>
            <div style={{ textAlign: 'right' }}>
              <div style={{ fontFamily: 'var(--f-display)', fontStyle: 'italic',
                fontSize: 56, lineHeight: 1, color: 'var(--red)' }}>8.9</div>
              <div style={{ fontFamily: 'var(--f-mono)', fontSize: 10,
                letterSpacing: '0.22em', textTransform: 'uppercase', color: 'var(--ink-3)' }}>
                CGPA · cumulative
              </div>
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr',
            gap: 0, borderTop: '1px solid var(--ink)', borderBottom: '1px solid var(--ink)',
            marginBottom: 18 }}>
            {[
              ['Sem 4 · SGPA', '10.0',  'Top 1 in batch'],
              ['Sem 5 · SGPA', '9.75',  'Top 1 in batch'],
              ['Sem 3 · SGPA', '9.2',   'Top 5 in batch'],
            ].map(([k,v,note],i) => (
              <div key={k} style={{
                padding: '16px 18px',
                borderRight: i < 2 ? '1px solid var(--ink)' : 'none',
              }}>
                <div style={{ fontFamily: 'var(--f-mono)', fontSize: 10,
                  letterSpacing: '0.22em', textTransform: 'uppercase', color: 'var(--ink-3)' }}>
                  {k}
                </div>
                <div style={{ fontFamily: 'var(--f-display)', fontStyle: 'italic',
                  fontSize: 46, lineHeight: 1, margin: '4px 0',
                  color: i === 0 ? 'var(--teal)' : 'var(--ink)' }}>{v}</div>
                <div style={{ fontFamily: 'var(--f-mono)', fontSize: 11,
                  color: 'var(--ink-2)' }}>{note}</div>
              </div>
            ))}
          </div>

          <div className="kv-row" style={{ paddingTop: 6 }}>
            <span className="k">Relevant Coursework</span>
            <span className="v" style={{ fontFamily: 'var(--f-body)', fontSize: 14, color: 'var(--ink-2)' }}>
              Machine Learning · Data Engineering &amp; Large-Scale Storage · DS &amp; Algorithms · DevOps &amp; MLOps
            </span>
          </div>
          <div className="kv-row">
            <span className="k">Grade O (highest) in</span>
            <span className="v" style={{ fontFamily: 'var(--f-body)', fontSize: 14, color: 'var(--ink-2)' }}>
              Cross-domain electives — Stocks Lab &amp; Finance Lab
            </span>
          </div>
        </div>
      </section>

      {/* §γ Experience */}
      <section className="section">
        <header className="section-head">
          <div className="section-num">§ Section<b>γ</b></div>
          <h2 className="section-title"><em>Experience,</em>&nbsp;dated.</h2>
          <div className="section-kicker">Four internships. Each ended with a completion letter.</div>
        </header>

        {[
          {
            role: 'Forward-Deployed Engineer Intern',
            org: 'Supervity',
            when: 'Nov 2025 — Dec 2025',
            color: 'var(--red)',
            notes: [
              'Worked on Command Center solutions — Marketing CC for internal sprint execution, Financial & Research CCs for Japanese enterprise clients.',
              'Delivered client-facing AI dashboards and workflow agents that reduced manual operational effort by ~30–40% and shortened decision cycles by ~25%.',
              'Contributed to production deployments and client-specific customisation for financial domains.',
            ],
          },
          {
            role: 'AI Engineer Intern',
            org: 'Supervity',
            when: 'up to Oct 2025',
            color: 'var(--red)',
            notes: [
              'Designed and implemented workflow-based AI agents on the Supervity platform.',
              'Delivered rapid prototypes and solution proposals for US-based and Japanese clients, supporting pre-sales and technical discovery.',
              'Worked closely with stakeholders: requirement translation → prototype → proposal finalisation.',
            ],
          },
          {
            role: 'AI Engineer Intern',
            org: 'Runway Technologies',
            when: 'Apr 2025 — Oct 2025',
            color: 'var(--blue)',
            notes: [
              'Researched and prototyped AI solutions for the Runway tender platform.',
              'Built document-parsing models for tender notices and BOQs, improving summarisation accuracy by ~20%.',
              'Enhanced search relevance and keyword matching — ~15% faster results, ~18% user-efficiency lift.',
            ],
          },
          {
            role: 'Research & Tech Intern',
            org: 'TEACH NGO — Training & Educational Centre for Hearing Impaired',
            when: 'Jun 2025 — Jul 2025',
            color: 'var(--teal)',
            notes: [
              'Researched and implemented AI/ML techniques to support educational accessibility initiatives.',
              'Improved backend workflows — 30% faster information retrieval for staff and students.',
              'Automated reporting tasks, reducing manual effort by ~40%.',
            ],
          },
          {
            role: 'AI Intern',
            org: 'Codsoft',
            when: 'May 2024 — Jun 2024',
            color: 'var(--gold)',
            notes: [
              'Developed chatbots (85% query accuracy), game AI, and a movie recommender that improved relevance by 20%.',
            ],
          },
        ].map((x,i) => (
          <div key={i} style={{
            border: '1px solid var(--ink)',
            borderTop: i === 0 ? '1px solid var(--ink)' : 'none',
            padding: '22px 26px',
            background: 'var(--paper)',
          }}>
            <div style={{ display: 'grid', gridTemplateColumns: '180px 1fr', gap: 28, alignItems: 'flex-start' }}>
              <div>
                <div style={{ fontFamily: 'var(--f-mono)', fontSize: 9,
                  letterSpacing: '0.24em', textTransform: 'uppercase', color: 'var(--ink-3)' }}>
                  {x.when}
                </div>
                <div style={{ fontFamily: 'var(--f-display)', fontStyle: 'italic',
                  fontSize: 28, lineHeight: 1.05, color: x.color, marginTop: 6 }}>
                  {x.org}
                </div>
                <div style={{ fontFamily: 'var(--f-mono)', fontSize: 11,
                  color: 'var(--ink-2)', marginTop: 6 }}>
                  Completion Letter ✓
                </div>
              </div>
              <div>
                <h3 style={{ fontFamily: 'var(--f-body)', fontSize: 18, fontWeight: 600,
                  marginBottom: 10 }}>{x.role}</h3>
                <ul style={{ listStyle: 'none', padding: 0 }}>
                  {x.notes.map((n,k) => (
                    <li key={k} style={{ display: 'grid', gridTemplateColumns: '24px 1fr',
                      gap: 8, fontSize: 14, lineHeight: 1.6, color: 'var(--ink-2)',
                      marginBottom: 6 }}>
                      <span style={{ color: x.color, fontFamily: 'var(--f-mono)' }}>→</span>
                      <span>{n}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        ))}
      </section>

      {/* §δ Projects */}
      <section className="section">
        <header className="section-head">
          <div className="section-num">§ Section<b>δ</b></div>
          <h2 className="section-title">Selected&nbsp;<em>projects.</em></h2>
          <div className="section-kicker">From-scratch systems, shipped to the public internet.</div>
        </header>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr',
          gap: 0, border: '1px solid var(--ink)' }}>
          {PROJECTS.map((p,i) => (
            <div key={i} style={{
              padding: '24px 26px',
              borderRight: i % 2 === 0 ? '1px solid var(--ink)' : 'none',
              borderTop: i > 1 ? '1px solid var(--ink)' : 'none',
              background: 'var(--paper)',
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between',
                alignItems: 'baseline', marginBottom: 10 }}>
                <span style={{ fontFamily: 'var(--f-mono)', fontSize: 10,
                  letterSpacing: '0.22em', textTransform: 'uppercase', color: 'var(--ink-3)' }}>
                  Proj · {String(i+1).padStart(2,'0')}
                </span>
                <span style={{ fontFamily: 'var(--f-mono)', fontSize: 9,
                  letterSpacing: '0.2em', textTransform: 'uppercase', color: 'var(--ink-3)' }}>
                  repo · demo ↗
                </span>
              </div>
              <h3 style={{ fontFamily: 'var(--f-display)', fontStyle: 'italic',
                fontSize: 26, lineHeight: 1.1, marginBottom: 10, color: 'var(--ink)' }}>
                {p.name}
              </h3>
              <p style={{ fontSize: 14, lineHeight: 1.6, color: 'var(--ink-2)',
                marginBottom: 12 }}>{p.blurb}</p>
              <div style={{ paddingTop: 10, borderTop: '1px dotted var(--ink-3)',
                fontFamily: 'var(--f-mono)', fontSize: 10,
                letterSpacing: '0.18em', textTransform: 'uppercase', color: 'var(--ink-3)' }}>
                {p.stack}
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* §ε Stack + principles */}
      <section className="section">
        <header className="section-head">
          <div className="section-num">§ Section<b>ε</b></div>
          <h2 className="section-title">Tools &amp;&nbsp;<em>principles.</em></h2>
          <div className="section-kicker">What I reach for, and why.</div>
        </header>

        <div className="grid-2">
          <div className="fig" style={{ borderRight: 'none' }}>
            <div className="fig-head">
              <div className="fig-num">Tab. I — Stack</div>
              <div className="fig-title"><em>Tools</em> in use</div>
            </div>
            <div className="kv">
              {STACK.map(([k,v]) => (
                <div className="kv-row" key={k}>
                  <span className="k">{k}</span>
                  <span className="v" style={{ color: 'var(--ink-2)', textAlign: 'right' }}>{v}</span>
                </div>
              ))}
            </div>
            <div className="fig-cap">
              Also — SQL, MongoDB, Redis, Cassandra · Jenkins · Matplotlib / Seaborn
            </div>
          </div>

          <div className="fig">
            <div className="fig-head">
              <div className="fig-num">Tab. II — Principles</div>
              <div className="fig-title"><em>Four</em> rules</div>
            </div>
            {PRINCIPLES.map(([n,h,b]) => (
              <div key={n} style={{
                padding: '14px 0',
                borderBottom: '1px dotted var(--ink-3)',
              }}>
                <div style={{ display: 'flex', alignItems: 'baseline', gap: 12, marginBottom: 4 }}>
                  <span style={{
                    fontFamily: 'var(--f-display)', fontStyle: 'italic',
                    fontSize: 28, color: 'var(--blue)',
                  }}>{n}.</span>
                  <span style={{ fontFamily: 'var(--f-body)', fontSize: 16, fontWeight: 600 }}>{h}</span>
                </div>
                <p style={{ fontSize: 14, lineHeight: 1.55,
                  color: 'var(--ink-2)', paddingLeft: 42 }}>{b}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* §ζ Chronology */}
      <section className="section">
        <header className="section-head">
          <div className="section-num">§ Section<b>ζ</b></div>
          <h2 className="section-title">A brief&nbsp;<em>chronology.</em></h2>
          <div className="section-kicker">Years, and the thing that happened inside them.</div>
        </header>

        <div style={{ border: '1px solid var(--ink)' }}>
          {TIMELINE.map((r, i) => (
            <div key={i} style={{
              display: 'grid', gridTemplateColumns: '140px 1fr 60px',
              padding: '18px 24px',
              borderTop: i === 0 ? 'none' : '1px solid var(--ink)',
              alignItems: 'baseline', gap: 24,
            }}>
              <div style={{
                fontFamily: 'var(--f-display)', fontStyle: 'italic',
                fontSize: 44, lineHeight: 1, color: 'var(--red)',
              }}>{r.yr}</div>
              <div style={{ fontSize: 17, lineHeight: 1.5, color: 'var(--ink)' }}>{r.t}</div>
              <div style={{ fontFamily: 'var(--f-mono)', fontSize: 10,
                color: 'var(--ink-3)', textAlign: 'right' }}>
                · {String(i+1).padStart(2,'0')} ·
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* §η Achievements + certs */}
      <section className="section">
        <header className="section-head">
          <div className="section-num">§ Section<b>η</b></div>
          <h2 className="section-title">Awards &amp;&nbsp;<em>certifications.</em></h2>
          <div className="section-kicker">Brief, for the committee.</div>
        </header>

        <div className="grid-2">
          <div className="fig" style={{ borderRight: 'none' }}>
            <div className="fig-head">
              <div className="fig-num">Tab. III — Awards</div>
              <div className="fig-title"><em>Recognition</em></div>
            </div>
            {[
              ['Stellar Student — All Rounder · 2026',   'ATLAS SkillTech University'],
              ['3rd Place · CIEL HR Live Project',        'MockMate — AI Interview Avatar'],
              ['Top 3 in batch',                          'MockMate, AI mock-interview platform'],
              ['Top 1 in batch · Sem 4 & 5',              '10.0 / 9.75 SGPA'],
              ['Top 5 in batch · Sem 3',                  '9.2 SGPA'],
              ['Grade O · Stocks Lab / Finance Lab',       'Cross-domain electives'],
            ].map(([k,v]) => (
              <div className="kv-row" key={k}>
                <span className="k" style={{ fontFamily: 'var(--f-body)', fontSize: 14,
                  letterSpacing: 'normal', textTransform: 'none', color: 'var(--ink)' }}>{k}</span>
                <span className="v" style={{ color: 'var(--ink-3)', textAlign: 'right' }}>{v}</span>
              </div>
            ))}
          </div>

          <div className="fig">
            <div className="fig-head">
              <div className="fig-num">Tab. IV — Certifications</div>
              <div className="fig-title"><em>On file</em></div>
            </div>
            {[
              ['School of AI — EPAI v5', 'Applied AI · neural nets, optimisation, deployment'],
              ['School of AI — EAG v1',  'Generative AI · prompts, multimodal, ethics'],
              ['IEEE Student Member',    'Active in the IEEE student community'],
            ].map(([k,v]) => (
              <div key={k} style={{ padding: '14px 0', borderBottom: '1px dotted var(--ink-3)' }}>
                <div style={{ fontFamily: 'var(--f-body)', fontSize: 16,
                  fontWeight: 600, marginBottom: 4 }}>{k}</div>
                <div style={{ fontSize: 14, color: 'var(--ink-2)' }}>{v}</div>
              </div>
            ))}
            <div className="fig-cap">
              Leadership &amp; volunteering · Research/Tech Intern, TEACH NGO — AI for educational accessibility
            </div>
          </div>
        </div>
      </section>

      {/* Contact strip */}
      <section className="section" style={{ marginTop: 56 }}>
        <div style={{
          border: '1px solid var(--ink)',
          background: 'var(--ink)', color: 'var(--paper)',
          padding: '28px 32px',
          display: 'grid', gridTemplateColumns: '2fr 1fr 1fr', gap: 40,
        }}>
          <div>
            <div style={{ fontFamily: 'var(--f-mono)', fontSize: 10,
              letterSpacing: '0.24em', textTransform: 'uppercase',
              color: 'var(--gold)', marginBottom: 12 }}>
              ※ Correspondence
            </div>
            <div style={{ fontFamily: 'var(--f-display)',
              fontStyle: 'italic', fontSize: 42, lineHeight: 1.05 }}>
              Write to me.<br/>
              <span style={{ color: 'var(--gold)' }}>Punctually.</span>
            </div>
          </div>
          <div style={{ fontFamily: 'var(--f-mono)', fontSize: 13, lineHeight: 2 }}>
            <div style={{ color: 'var(--gold)', fontSize: 10, letterSpacing: '0.22em', textTransform: 'uppercase', marginBottom: 6 }}>Direct</div>
            rladofficiel00@gmail.com<br/>
            github.com · linkedin<br/>
            medium · on request
          </div>
          <div style={{ fontFamily: 'var(--f-mono)', fontSize: 13, lineHeight: 2 }}>
            <div style={{ color: 'var(--gold)', fontSize: 10, letterSpacing: '0.22em', textTransform: 'uppercase', marginBottom: 6 }}>Identifiers</div>
            Student ID · 10929050<br/>
            ATLAS SkillTech · Mumbai<br/>
            B.Tech CS · AI &amp; ML
          </div>
        </div>
      </section>

      <div className="colophon" style={{ marginTop: 32 }}>
        <span>Set in Instrument Serif, IBM Plex Serif, JetBrains Mono</span>
        <span>Paper: warm cream · ink: warm black</span>
        <span>© MMXXVI · 404AnomalyNotFound</span>
      </div>
    </div>
  );
}

export default About;
