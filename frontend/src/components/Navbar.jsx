import React from 'react';
import { Bot, Cpu, Sparkles, CheckCircle2 } from 'lucide-react';

export default function Navbar({ isBackendConnected }) {
  return (
    <header className="glass-panel" style={{ margin: '1rem', padding: '1rem 1.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.8rem' }}>
        <div style={{
          width: '42px',
          height: '42px',
          borderRadius: '12px',
          background: 'var(--gradient-primary)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          boxShadow: 'var(--shadow-glow)'
        }}>
          <Bot size={24} color="#ffffff" />
        </div>
        <div>
          <h1 style={{ fontSize: '1.25rem', fontWeight: '700', letterSpacing: '-0.02em', background: 'linear-gradient(to right, #ffffff, #94a3b8)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
            ResearchMind AI
          </h1>
          <p style={{ fontSize: '0.75rem', color: 'var(--text-dim)', fontWeight: '500' }}>
            Decoupled Multi-Agent Autonomous Research System
          </p>
        </div>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '0.4rem',
          padding: '0.4rem 0.8rem',
          borderRadius: '20px',
          fontSize: '0.75rem',
          fontWeight: '600',
          background: 'rgba(99, 102, 241, 0.1)',
          border: '1px solid rgba(99, 102, 241, 0.3)',
          color: 'var(--accent-indigo)'
        }}>
          <Cpu size={14} />
          <span>Gemini 2.5 Flash + LangGraph</span>
        </div>

        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '0.4rem',
          padding: '0.4rem 0.8rem',
          borderRadius: '20px',
          fontSize: '0.75rem',
          fontWeight: '600',
          background: isBackendConnected ? 'rgba(16, 185, 129, 0.1)' : 'rgba(244, 63, 94, 0.1)',
          border: `1px solid ${isBackendConnected ? 'rgba(16, 185, 129, 0.3)' : 'rgba(244, 63, 94, 0.3)'}`,
          color: isBackendConnected ? 'var(--accent-emerald)' : 'var(--accent-rose)'
        }}>
          <CheckCircle2 size={14} />
          <span>{isBackendConnected ? 'FastAPI Online' : 'Connecting...'}</span>
        </div>
      </div>
    </header>
  );
}
