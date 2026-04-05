import { useState, useEffect } from 'react';
import { Activity, ShieldAlert, Zap, Server, ChevronRight, BarChart as BarChartIcon } from 'lucide-react';
import { BarChart as RechartsBarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import './index.css';

const API_BASE = "http://localhost:8000";

function App() {
  const [runs, setRuns] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeRun, setActiveRun] = useState(null);
  const [chartData, setChartData] = useState([
    { name: 'Baseline', ASR: 0 },
    { name: 'Instructed', ASR: 0 },
  ]);
  const [activeResults, setActiveResults] = useState([]);
  const [activeTraces, setActiveTraces] = useState([]);

  const fetchStats = async () => {
    try {
        const res = await fetch(`${API_BASE}/api/stats`);
        const stats = await res.json();
        setChartData([
            { name: 'Baseline', ASR: stats.baseline_asr },
            { name: 'Instructed', ASR: stats.instructed_asr }
        ]);
    } catch (e) { console.error(e); }
  };

  useEffect(() => {
    fetchRuns();
    fetchStats();
    const interval = setInterval(() => {
        fetchRuns();
        fetchStats();
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (activeRun) {
        fetchResults(activeRun.id);
    }
  }, [activeRun?.id, runs]);

  useEffect(() => {
    if (activeResults.length > 0) {
        const target = activeResults.find(r => r.outcome !== 'incomplete') || activeResults[0];
        fetchTraces(target.id);
    } else {
        setActiveTraces([]);
    }
  }, [activeResults]);

  const fetchResults = async (runId) => {
    try {
        const res = await fetch(`${API_BASE}/api/runs/${runId}/results`);
        const data = await res.json();
        setActiveResults(data);
    } catch(e) { console.error(e); }
  };

  const fetchTraces = async (resultId) => {
    try {
        const res = await fetch(`${API_BASE}/api/results/${resultId}/traces`);
        const data = await res.json();
        setActiveTraces(data);
    } catch(e) { console.error(e); }
  };

  const fetchRuns = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/runs`);
      const data = await res.json();
      setRuns(data);
      if (data.length > 0 && !activeRun) setActiveRun(data[0]);
      setLoading(false);
    } catch (e) {
      setLoading(false);
    }
  };

  const triggerRun = async () => {
    try {
        await fetch(`${API_BASE}/api/runs`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                name: `Eval Run - ${new Date().toLocaleTimeString()}`,
                model: "gemini-2.5-flash"
            })
        });
        fetchRuns();
        fetchStats();
    } catch (e) { console.error(e); }
  };

  return (
    <div className="dashboard-container">
      <header className="header">
        <h1>AgentTrap Control Center</h1>
        <div className="action-bar">
          <button className="btn" onClick={fetchRuns}><Activity size={18}/> Refresh</button>
          <button className="btn primary" onClick={triggerRun}><Zap size={18}/> New Evaluation</button>
        </div>
      </header>

      <main className="grid">
        <section className="column">
          <div className="card">
            <h2><Server size={20} /> Latest Evaluations</h2>
            {loading ? <p>Loading data...</p> : (
              <table style={{ width: '100%', textAlign: 'left', borderCollapse: 'collapse' }}>
                <thead>
                  <tr style={{ color: '#8b92a5', borderBottom: '1px solid #2b3040' }}>
                    <th style={{ padding: '0.75rem 0' }}>Job Name</th>
                    <th>Status</th>
                    <th>ASR</th>
                  </tr>
                </thead>
                <tbody>
                  {runs.map(r => (
                    <tr 
                      key={r.id} 
                      style={{ cursor: 'pointer', background: activeRun?.id === r.id ? '#1c212e' : 'transparent' }} 
                      onClick={() => setActiveRun(r)}
                    >
                      <td style={{ padding: '0.75rem 0' }}>{r.name}</td>
                      <td>{r.completed_scenarios} / {r.total_scenarios}</td>
                      <td style={{ color: r.asr_overall > 50 ? '#ef4444' : '#22d3ee' }}>
                        {r.asr_overall != null ? `${r.asr_overall.toFixed(1)}%` : '---'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>

          <div className="card" style={{ marginTop: '2rem' }}>
            <h2><BarChartIcon size={20} /> Robustness Comparison (ASR)</h2>
            <div style={{ width: '100%', height: 250 }}>
              <ResponsiveContainer>
                <RechartsBarChart data={chartData} margin={{ top: 20, right: 30, left: 0, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#2b3040" />
                  <XAxis dataKey="name" stroke="#8b92a5" />
                  <YAxis stroke="#8b92a5" unit="%" domain={[0, 100]} />
                  <Tooltip cursor={{ fill: '#252a3b' }} contentStyle={{ background: '#181a20', borderColor: '#2b3040'}} />
                  <Bar dataKey="ASR" fill="#22d3ee" radius={[4, 4, 0, 0]} />
                </RechartsBarChart>
              </ResponsiveContainer>
            </div>
            <p style={{ color: '#8b92a5', fontSize: '0.85rem', textAlign: 'center', marginTop: '1rem'}}>
               Aggregation of historical Attack Success Rates per agent configuration.
            </p>
          </div>
        </section>

        <section className="column">
          <div className="card" style={{ minHeight: '600px' }}>
            <h2><ShieldAlert size={20} /> Execution Trace Viewer</h2>
            <p style={{ color: '#8b92a5', marginBottom: '1.5rem'}}>
                Showing traces for <b>{activeResults.length > 0 ? activeResults[0].scenario_id : 'none'}</b>
            </p>
            
            <div className="trace-sequence">
              {activeTraces.length === 0 ? (
                  <p style={{ color: '#4b5563', textAlign: 'center', marginTop: '2rem' }}>No execution traces found for this run.</p>
              ) : activeTraces.map((trace) => (
                <div key={trace.id} className={`trace-step ${trace.verdict === 'injected' ? 'injected' : ''}`}>
                    <div className="trace-header">
                      <span className="trace-tool">{trace.tool_name}</span>
                      <span>Step {trace.step_index}</span>
                    </div>
                    <div style={{ marginBottom: '0.5rem'}}>{trace.reasoning}</div>
                    <pre className="trace-params">
                        {JSON.stringify(JSON.parse(trace.parameters), null, 2)}
                    </pre>
                </div>
              ))}
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}

export default App;
