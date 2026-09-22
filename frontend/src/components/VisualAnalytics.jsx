import React from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, Legend } from 'recharts';
import { BarChart3, PieChart as PieIcon, Activity } from 'lucide-react';

const COLORS = ['#6366f1', '#38bdf8', '#a855f7', '#10b981', '#f59e0b', '#f43f5e'];

export default function VisualAnalytics({ visualData, synthesis }) {
  if (!visualData || visualData.length === 0) {
    return null;
  }

  // Find bar and pie charts from visualData
  const barChartConfig = visualData.find(v => v.chart_type === 'bar');
  const pieChartConfig = visualData.find(v => v.chart_type === 'pie');
  const metricCards = visualData.find(v => v.chart_type === 'metric');

  return (
    <div className="glass-panel" style={{ padding: '1.5rem', margin: '0 1rem 1.5rem 1.5rem' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginBottom: '1.2rem' }}>
        <BarChart3 size={20} color="var(--accent-indigo)" />
        <h3 style={{ fontSize: '1rem', fontWeight: '700', color: '#ffffff' }}>
          Synthesized Intelligence & Data Visualizations
        </h3>
      </div>

      {/* Metric Cards Row */}
      {metricCards && metricCards.data && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '1rem', marginBottom: '1.5rem' }}>
          {metricCards.data.map((m, idx) => (
            <div
              key={idx}
              style={{
                background: 'rgba(15, 23, 42, 0.6)',
                border: '1px solid var(--border-subtle)',
                borderRadius: 'var(--radius-sm)',
                padding: '1rem',
                display: 'flex',
                flexDirection: 'column'
              }}
            >
              <span style={{ fontSize: '0.75rem', fontWeight: '600', color: 'var(--text-muted)' }}>{m.label}</span>
              <span style={{ fontSize: '1.6rem', fontWeight: '800', color: COLORS[idx % COLORS.length], marginTop: '0.2rem' }}>
                {m.value}
              </span>
            </div>
          ))}
        </div>
      )}

      {/* Dual Charts Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: pieChartConfig ? '1fr 1fr' : '1fr', gap: '1.5rem' }}>
        {/* Bar Chart */}
        {barChartConfig && (
          <div style={{ background: 'rgba(15, 23, 42, 0.4)', padding: '1rem', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-subtle)' }}>
            <h4 style={{ fontSize: '0.85rem', fontWeight: '600', color: 'var(--accent-blue)', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
              <Activity size={16} />
              {barChartConfig.title || 'Key Focus Breakdown'}
            </h4>
            <div style={{ width: '100%', height: 240 }}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={barChartConfig.data}>
                  <XAxis dataKey="category" stroke="#64748b" fontSize={11} tickLine={false} />
                  <YAxis stroke="#64748b" fontSize={11} tickLine={false} />
                  <Tooltip
                    contentStyle={{ background: '#0f172a', border: '1px solid #334155', borderRadius: '8px', color: '#fff' }}
                  />
                  <Bar dataKey="value" fill="#6366f1" radius={[4, 4, 0, 0]}>
                    {barChartConfig.data.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        )}

        {/* Pie Chart */}
        {pieChartConfig && (
          <div style={{ background: 'rgba(15, 23, 42, 0.4)', padding: '1rem', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-subtle)' }}>
            <h4 style={{ fontSize: '0.85rem', fontWeight: '600', color: 'var(--accent-purple)', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
              <PieIcon size={16} />
              {pieChartConfig.title || 'Sentiment & Source Distribution'}
            </h4>
            <div style={{ width: '100%', height: 240 }}>
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={pieChartConfig.data}
                    cx="50%"
                    cy="50%"
                    innerRadius={55}
                    outerRadius={80}
                    paddingAngle={5}
                    dataKey="value"
                    nameKey="category"
                  >
                    {pieChartConfig.data.map((entry, index) => (
                      <Cell key={`pie-cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip contentStyle={{ background: '#0f172a', border: '1px solid #334155', borderRadius: '8px', color: '#fff' }} />
                  <Legend verticalAlign="bottom" height={36} iconSize={10} wrapperStyle={{ fontSize: '11px', color: '#94a3b8' }} />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
