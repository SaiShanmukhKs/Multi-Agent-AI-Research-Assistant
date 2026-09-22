import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import ResearchForm from './components/ResearchForm';
import AgentProgressTimeline from './components/AgentProgressTimeline';
import VisualAnalytics from './components/VisualAnalytics';
import ReportViewer from './components/ReportViewer';

const API_BASE = 'http://localhost:8000';

export default function App() {
  const [isBackendConnected, setIsBackendConnected] = useState(false);
  const [isRunning, setIsRunning] = useState(false);
  const [taskId, setTaskId] = useState(null);
  const [query, setQuery] = useState('');
  const [currentNode, setCurrentNode] = useState('init');
  const [logs, setLogs] = useState([]);
  const [status, setStatus] = useState('idle');
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  // Check health status of FastAPI backend
  useEffect(() => {
    const checkHealth = async () => {
      try {
        const res = await fetch(`${API_BASE}/api/health`);
        if (res.ok) {
          setIsBackendConnected(true);
        } else {
          setIsBackendConnected(false);
        }
      } catch (err) {
        setIsBackendConnected(false);
      }
    };

    checkHealth();
    const interval = setInterval(checkHealth, 5000);
    return () => clearInterval(interval);
  }, []);

  // Handle starting a research pipeline
  const handleStartResearch = async (searchQuery, audience) => {
    setIsRunning(true);
    setError(null);
    setResult(null);
    setQuery(searchQuery);
    setLogs([`🚀 Initiating multi-agent research for: "${searchQuery}"`]);
    setCurrentNode('search');
    setStatus('running');

    try {
      // 1. Post request to backend
      const res = await fetch(`${API_BASE}/api/research`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: searchQuery, audience }),
      });

      if (!res.ok) {
        throw new Error(`Server returned ${res.status}`);
      }

      const data = await res.json();
      const newTaskId = data.task_id;
      setTaskId(newTaskId);

      // 2. Open EventSource (SSE) stream for real-time updates
      const eventSource = new EventSource(`${API_BASE}/api/research/stream/${newTaskId}`);

      eventSource.onmessage = (event) => {
        try {
          const parsed = JSON.parse(event.data);

          if (parsed.type === 'agent_update') {
            setCurrentNode(parsed.node);
            setLogs((prev) => [...prev, parsed.log]);
          } else if (parsed.type === 'completed') {
            eventSource.close();
            setStatus('completed');
            setIsRunning(false);
            fetchFinalResult(newTaskId);
          } else if (parsed.type === 'error') {
            eventSource.close();
            setStatus('failed');
            setIsRunning(false);
            setError(parsed.error || 'Research failed');
          }
        } catch (err) {
          console.error('Error parsing SSE event', err);
        }
      };

      eventSource.onerror = (err) => {
        console.warn('SSE stream closed or error, falling back to polling...', err);
        eventSource.close();
        pollTaskStatus(newTaskId);
      };

    } catch (err) {
      console.error('Failed to start research:', err);
      setError(err.message || 'Failed to connect to backend server');
      setIsRunning(false);
      setStatus('failed');
    }
  };

  // Polling fallback if SSE disconnects
  const pollTaskStatus = async (tid) => {
    const pollInterval = setInterval(async () => {
      try {
        const res = await fetch(`${API_BASE}/api/research/status/${tid}`);
        if (!res.ok) return;

        const data = await res.json();
        setLogs(data.agent_logs || []);
        if (data.current_node) setCurrentNode(data.current_node);

        if (data.status === 'completed') {
          clearInterval(pollInterval);
          setStatus('completed');
          setIsRunning(false);
          fetchFinalResult(tid);
        } else if (data.status === 'failed') {
          clearInterval(pollInterval);
          setStatus('failed');
          setIsRunning(false);
          setError(data.error || 'Pipeline execution error');
        }
      } catch (e) {
        console.error('Polling error', e);
      }
    }, 3000);
  };

  // Fetch final research result
  const fetchFinalResult = async (tid) => {
    try {
      const res = await fetch(`${API_BASE}/api/research/result/${tid}`);
      if (res.ok) {
        const data = await res.json();
        setResult(data);
      }
    } catch (err) {
      console.error('Failed to fetch research result', err);
    }
  };

  return (
    <div style={{ maxWidth: '1300px', margin: '0 auto', paddingBottom: '3rem' }}>
      <Navbar isBackendConnected={isBackendConnected} />

      <main>
        <ResearchForm onSubmit={handleStartResearch} isRunning={isRunning} />

        {(isRunning || status === 'completed' || logs.length > 0) && (
          <AgentProgressTimeline currentNode={currentNode} logs={logs} status={status} />
        )}

        {error && (
          <div
            className="glass-panel"
            style={{
              margin: '0 1rem 1.5rem 1.5rem',
              padding: '1.2rem',
              background: 'rgba(244, 63, 94, 0.1)',
              border: '1px solid rgba(244, 63, 94, 0.4)',
              color: 'var(--accent-rose)',
              borderRadius: 'var(--radius-sm)'
            }}
          >
            <strong>Error:</strong> {error}
          </div>
        )}

        {result && (
          <>
            <VisualAnalytics visualData={result.visual_data} synthesis={result.synthesis} />
            <ReportViewer
              report={result.report}
              reportHtml={result.report_html}
              searchResults={result.search_results}
              synthesis={result.synthesis}
              query={query}
            />
          </>
        )}
      </main>
    </div>
  );
}
