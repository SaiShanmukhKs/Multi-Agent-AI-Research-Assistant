import React from 'react';
import { Search, FileText, Brain, PenTool, CheckCircle2, Loader2, Circle } from 'lucide-react';

const AGENTS = [
  { id: 'search', name: 'Scout Agent', role: 'Web Search & Sub-queries', icon: Search, badgeClass: 'badge-scout' },
  { id: 'reader', name: 'Analyst Agent', role: 'Doc Reading & Vector RAG', icon: FileText, badgeClass: 'badge-analyst' },
  { id: 'synthesis', name: 'Thinker Agent', role: 'Cross-Source Synthesis', icon: Brain, badgeClass: 'badge-thinker' },
  { id: 'writer', name: 'Writer Agent', role: 'Polished Report Drafting', icon: PenTool, badgeClass: 'badge-writer' }
];

export default function AgentProgressTimeline({ currentNode, logs, status }) {
  const isCompleted = status === 'completed';

  const getAgentState = (agentId) => {
    if (isCompleted) return 'completed';
    if (currentNode === agentId) return 'active';

    const order = ['search', 'reader', 'synthesis', 'writer'];
    const currentIndex = order.indexOf(currentNode);
    const agentIndex = order.indexOf(agentId);

    if (currentIndex > agentIndex) return 'completed';
    return 'pending';
  };

  return (
    <div className="glass-panel" style={{ padding: '1.5rem', margin: '0 1rem 1.5rem 1.5rem' }}>
      <h3 style={{ fontSize: '0.9rem', fontWeight: '700', textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--text-dim)', marginBottom: '1.2rem' }}>
        Agent Operations Orchestrator
      </h3>

      {/* Agents Stepper Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '1rem', marginBottom: '1.5rem' }}>
        {AGENTS.map((agent) => {
          const state = getAgentState(agent.id);
          const Icon = agent.icon;

          return (
            <div
              key={agent.id}
              style={{
                background: state === 'active' ? 'rgba(30, 41, 59, 0.9)' : 'rgba(15, 23, 42, 0.4)',
                border: state === 'active' ? '1px solid var(--accent-indigo)' : '1px solid var(--border-subtle)',
                borderRadius: 'var(--radius-sm)',
                padding: '1rem',
                transition: 'all 0.2s ease',
                position: 'relative',
                overflow: 'hidden'
              }}
            >
              {state === 'active' && (
                <div style={{
                  position: 'absolute',
                  top: 0,
                  left: 0,
                  right: 0,
                  height: '3px',
                  background: 'var(--gradient-primary)'
                }} />
              )}

              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.6rem' }}>
                <span className={agent.badgeClass} style={{ padding: '0.25rem 0.6rem', borderRadius: '12px', fontSize: '0.7rem', fontWeight: '700' }}>
                  {agent.name}
                </span>
                {state === 'completed' && <CheckCircle2 size={16} color="var(--accent-emerald)" />}
                {state === 'active' && <Loader2 size={16} className="animate-spin" color="var(--accent-indigo)" />}
                {state === 'pending' && <Circle size={14} color="var(--text-dim)" />}
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.3rem' }}>
                <Icon size={16} color={state === 'active' ? 'var(--accent-blue)' : 'var(--text-muted)'} />
                <span style={{ fontSize: '0.85rem', fontWeight: '600', color: state === 'active' ? '#ffffff' : 'var(--text-muted)' }}>
                  {agent.role}
                </span>
              </div>
            </div>
          );
        })}
      </div>

      {/* Streaming Log Stream Box */}
      <div>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
          <span style={{ fontSize: '0.75rem', fontWeight: '600', color: 'var(--text-dim)' }}>
            LIVE AGENT LOG STREAM:
          </span>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
            {logs.length} events logged
          </span>
        </div>
        <div
          style={{
            background: 'rgba(9, 13, 22, 0.95)',
            border: '1px solid var(--border-subtle)',
            borderRadius: 'var(--radius-sm)',
            padding: '0.8rem 1rem',
            maxHeight: '130px',
            overflowY: 'auto',
            fontFamily: 'JetBrains Mono, monospace',
            fontSize: '0.8rem',
            color: '#a7f3d0'
          }}
        >
          {logs.length === 0 ? (
            <div style={{ color: 'var(--text-dim)', fontStyle: 'italic' }}>
              Awaiting research execution...
            </div>
          ) : (
            logs.map((log, index) => (
              <div key={index} style={{ marginBottom: '0.3rem', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                <span style={{ color: 'var(--accent-blue)', marginRight: '0.5rem' }}>[{new Date().toLocaleTimeString()}]</span>
                <span>{log}</span>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
