import React, { useState, useEffect } from 'react';

export default function TypewriterWord({ words, typeMs = 90, backMs = 55, holdMs = 1400, style }) {
  const [i, setI] = useState(0);
  const [n, setN] = useState(0);
  const [del, setDel] = useState(false);

  useEffect(() => {
    const w = words[i % words.length];
    let t;
    if (!del && n < w.length) {
      t = setTimeout(() => setN(n + 1), typeMs);
    } else if (!del && n === w.length) {
      t = setTimeout(() => setDel(true), holdMs);
    } else if (del && n > 0) {
      t = setTimeout(() => setN(n - 1), backMs);
    } else if (del && n === 0) {
      setDel(false);
      setI(i + 1);
    }
    return () => clearTimeout(t);
  }, [i, n, del, words, typeMs, backMs, holdMs]);

  const word = words[i % words.length].slice(0, n);
  return (
    <em style={{ whiteSpace: 'nowrap', ...style }}>
      {word}
      <span style={{
        display: 'inline-block', width: '0.08em', height: '0.85em',
        background: 'currentColor', marginLeft: '0.05em',
        transform: 'translateY(0.08em)',
        animation: 'tw-blink 1s steps(2) infinite',
      }}/>
      <style>{`@keyframes tw-blink { 50% { opacity: 0; } }`}</style>
    </em>
  );
}
