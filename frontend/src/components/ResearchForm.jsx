import React, { useState } from 'react';
import { Search, Sparkles, Send, Briefcase, GraduationCap, Coffee } from 'lucide-react';

const PRESET_QUERIES = [
  "Latest advancements in quantum error correction 2026",
  "Generative AI agent architectures & enterprise adoption",
  "Solid state battery energy density breakthroughs",
  "Autonomous AI coding agents benchmarking & tools"
];

export default function ResearchForm({ onSubmit, isRunning }) {
  const [query, setQuery] = useState('');
  const [audience, setAudience] = useState('business');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!query.trim() || isRunning) return;
    onSubmit(query.trim(), audience);
  };

  const handleSelectPreset = (text) => {
    setQuery(text);
  };

  return (
    <div className="glass-panel" style={{ padding: '1.8rem', margin: '0 1rem 1.5rem 1.5rem' }}>
      <form onSubmit={handleSubmit}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.2rem' }}>
          <div>
            <label style={{ fontSize: '0.85rem', fontWeight: '600', color: 'var(--text-muted)', display: 'block', marginBottom: '0.5rem' }}>
              RESEARCH TOPIC OR COMPLEX QUESTION
            </label>
            <div style={{ position: 'relative' }}>
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Ask any complex research question (e.g. What are the latest advancements in quantum error correction?)"
                disabled={isRunning}
                style={{
                  width: '100%',
                  padding: '1rem 3.2rem 1rem 1.2rem',
                  fontSize: '1rem',
                  borderRadius: 'var(--radius-sm)',
                  background: 'rgba(15, 23, 42, 0.8)',
                  border: '1px solid var(--border-subtle)',
                  color: 'white',
                  outline: 'none',
                  transition: 'border-color 0.2s ease'
                }}
              />
              <button
                type="submit"
                disabled={!query.trim() || isRunning}
                className="btn-primary"
                style={{
                  position: 'absolute',
                  right: '6px',
                  top: '6px',
                  bottom: '6px',
                  padding: '0 1.2rem'
                }}
              >
                {isRunning ? (
                  <>
                    <Sparkles className="animate-spin" size={18} />
                    <span>Researching...</span>
                  </>
                ) : (
                  <>
                    <Send size={18} />
                    <span>Run Agents</span>
                  </>
                )}
              </button>
            </div>
          </div>

          {/* Quick Presets */}
          <div>
            <span style={{ fontSize: '0.75rem', fontWeight: '600', color: 'var(--text-dim)', marginRight: '0.8rem' }}>
              EXAMPLE TOPICS:
            </span>
            <div style={{ display: 'inline-flex', flexWrap: 'wrap', gap: '0.5rem', marginTop: '0.4rem' }}>
              {PRESET_QUERIES.map((item, idx) => (
                <button
                  key={idx}
                  type="button"
                  onClick={() => handleSelectPreset(item)}
                  disabled={isRunning}
                  style={{
                    background: 'rgba(255, 255, 255, 0.04)',
                    border: '1px solid var(--border-subtle)',
                    color: 'var(--text-muted)',
                    padding: '0.35rem 0.75rem',
                    borderRadius: '20px',
                    fontSize: '0.75rem',
                    cursor: 'pointer',
                    transition: 'all 0.15s ease'
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.borderColor = 'var(--accent-indigo)';
                    e.currentTarget.style.color = '#ffffff';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.borderColor = 'var(--border-subtle)';
                    e.currentTarget.style.color = 'var(--text-muted)';
                  }}
                >
                  {item}
                </button>
              ))}
            </div>
          </div>

          {/* Audience Selector */}
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', paddingTop: '0.5rem', borderTop: '1px solid var(--border-subtle)' }}>
            <span style={{ fontSize: '0.8rem', fontWeight: '600', color: 'var(--text-muted)' }}>
              REPORT TONE & TARGET AUDIENCE:
            </span>
            <div style={{ display: 'flex', gap: '0.5rem' }}>
              {[
                { id: 'business', label: 'Business Executive', icon: Briefcase },
                { id: 'academic', label: 'Academic & Technical', icon: GraduationCap },
                { id: 'casual', label: 'Casual Reader', icon: Coffee }
              ].map(({ id, label, icon: Icon }) => (
                <button
                  key={id}
                  type="button"
                  onClick={() => setAudience(id)}
                  disabled={isRunning}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.4rem',
                    padding: '0.4rem 0.85rem',
                    borderRadius: 'var(--radius-sm)',
                    fontSize: '0.8rem',
                    fontWeight: '500',
                    cursor: 'pointer',
                    border: audience === id ? '1px solid var(--accent-indigo)' : '1px solid var(--border-subtle)',
                    background: audience === id ? 'rgba(99, 102, 241, 0.15)' : 'transparent',
                    color: audience === id ? '#ffffff' : 'var(--text-muted)',
                    transition: 'all 0.15s ease'
                  }}
                >
                  <Icon size={14} />
                  <span>{label}</span>
                </button>
              ))}
            </div>
          </div>
        </div>
      </form>
    </div>
  );
}
