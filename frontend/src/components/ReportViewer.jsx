import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { FileText, Copy, Download, ExternalLink, Check, Bookmark, Layers } from 'lucide-react';

export default function ReportViewer({ report, reportHtml, searchResults, synthesis, query }) {
  const [activeTab, setActiveTab] = useState('report');
  const [copied, setCopied] = useState(false);

  if (!report) return null;

  const handleCopyMarkdown = () => {
    navigator.clipboard.writeText(report);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownloadHtml = () => {
    const htmlContent = reportHtml || `<!DOCTYPE html><html><head><title>${query}</title></head><body>${report}</body></html>`;
    const blob = new Blob([htmlContent], { type: 'text/html' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `research_report_${Date.now()}.html`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleDownloadMarkdown = () => {
    const blob = new Blob([report], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `research_report_${Date.now()}.md`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="glass-panel" style={{ padding: '1.8rem', margin: '0 1rem 2rem 1.5rem' }}>
      {/* Header & Export Actions */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.2rem', pb: '1rem', borderBottom: '1px solid var(--border-subtle)' }}>
        {/* Tabs */}
        <div style={{ display: 'flex', gap: '0.5rem' }}>
          {[
            { id: 'report', label: 'Full Research Report', icon: FileText },
            { id: 'sources', label: `Extracted Sources (${searchResults?.length || 0})`, icon: ExternalLink },
            { id: 'insights', label: 'Synthesized Insights', icon: Layers }
          ].map(({ id, label, icon: Icon }) => (
            <button
              key={id}
              onClick={() => setActiveTab(id)}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.4rem',
                padding: '0.5rem 1rem',
                borderRadius: 'var(--radius-sm)',
                fontSize: '0.85rem',
                fontWeight: '600',
                cursor: 'pointer',
                border: activeTab === id ? '1px solid var(--accent-indigo)' : '1px solid transparent',
                background: activeTab === id ? 'rgba(99, 102, 241, 0.2)' : 'transparent',
                color: activeTab === id ? '#ffffff' : 'var(--text-muted)',
                transition: 'all 0.15s ease'
              }}
            >
              <Icon size={16} />
              <span>{label}</span>
            </button>
          ))}
        </div>

        {/* Action Buttons */}
        <div style={{ display: 'flex', gap: '0.6rem' }}>
          <button
            onClick={handleCopyMarkdown}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.4rem',
              padding: '0.4rem 0.8rem',
              borderRadius: 'var(--radius-sm)',
              fontSize: '0.8rem',
              background: 'rgba(255, 255, 255, 0.05)',
              border: '1px solid var(--border-subtle)',
              color: 'var(--text-main)',
              cursor: 'pointer'
            }}
          >
            {copied ? <Check size={14} color="var(--accent-emerald)" /> : <Copy size={14} />}
            <span>{copied ? 'Copied!' : 'Copy MD'}</span>
          </button>

          <button
            onClick={handleDownloadMarkdown}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.4rem',
              padding: '0.4rem 0.8rem',
              borderRadius: 'var(--radius-sm)',
              fontSize: '0.8rem',
              background: 'rgba(99, 102, 241, 0.15)',
              border: '1px solid rgba(99, 102, 241, 0.4)',
              color: 'var(--accent-blue)',
              cursor: 'pointer'
            }}
          >
            <Download size={14} />
            <span>Markdown</span>
          </button>

          <button
            onClick={handleDownloadHtml}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.4rem',
              padding: '0.4rem 0.8rem',
              borderRadius: 'var(--radius-sm)',
              fontSize: '0.8rem',
              background: 'rgba(16, 185, 129, 0.15)',
              border: '1px solid rgba(16, 185, 129, 0.4)',
              color: 'var(--accent-emerald)',
              cursor: 'pointer'
            }}
          >
            <Download size={14} />
            <span>HTML</span>
          </button>
        </div>
      </div>

      {/* Tab Content */}
      {activeTab === 'report' && (
        <div className="markdown-body" style={{ background: 'rgba(9, 13, 22, 0.6)', padding: '1.8rem', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-subtle)' }}>
          <ReactMarkdown remarkPlugins={[remarkGfm]}>
            {report}
          </ReactMarkdown>
        </div>
      )}

      {activeTab === 'sources' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.8rem' }}>
          {searchResults?.map((src, index) => (
            <div
              key={index}
              style={{
                background: 'rgba(15, 23, 42, 0.6)',
                border: '1px solid var(--border-subtle)',
                borderRadius: 'var(--radius-sm)',
                padding: '1rem 1.2rem',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'flex-start'
              }}
            >
              <div>
                <h4 style={{ fontSize: '0.95rem', fontWeight: '600', color: 'var(--accent-blue)', marginBottom: '0.3rem' }}>
                  {src.title || 'Extracted Source'}
                </h4>
                <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>
                  {src.snippet || 'No snippet available'}
                </p>
                <a
                  href={src.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  style={{ fontSize: '0.75rem', color: 'var(--accent-indigo)', display: 'inline-flex', alignItems: 'center', gap: '0.3rem' }}
                >
                  <span>{src.url}</span>
                  <ExternalLink size={12} />
                </a>
              </div>
              <span style={{ fontSize: '0.7rem', color: 'var(--text-dim)', background: 'rgba(255,255,255,0.05)', padding: '0.2rem 0.5rem', borderRadius: '4px' }}>
                Score: {src.relevance_score || 'N/A'}
              </span>
            </div>
          ))}
        </div>
      )}

      {activeTab === 'insights' && (
        <div style={{ background: 'rgba(9, 13, 22, 0.6)', padding: '1.5rem', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-subtle)' }}>
          <h4 style={{ fontSize: '1rem', fontWeight: '700', color: 'var(--accent-purple)', marginBottom: '1rem' }}>
            Executive Synthesis & Strategic Themes
          </h4>
          {synthesis?.themes?.map((theme, idx) => (
            <div key={idx} style={{ marginBottom: '1rem', paddingBottom: '0.8rem', borderBottom: '1px solid var(--border-subtle)' }}>
              <h5 style={{ fontSize: '0.9rem', fontWeight: '600', color: '#ffffff' }}>
                {idx + 1}. {theme.title || theme.name || 'Key Theme'}
              </h5>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: '0.3rem' }}>
                {theme.description || theme.summary || JSON.stringify(theme)}
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
