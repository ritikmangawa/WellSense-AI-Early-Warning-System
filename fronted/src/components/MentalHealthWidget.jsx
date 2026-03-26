import React, { useState, useEffect } from 'react';
import { 
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  Area, AreaChart, BarChart, Bar, Cell
} from 'recharts';
import '../index.css';

export default function MentalHealthWidget() {
  const [formData, setFormData] = useState({
    sleep: 7,
    screenTime: 5,
    study: 3,
    activity: 1, 
    stress: 1 
  });

  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [historyData, setHistoryData] = useState([]);
  const [theme, setTheme] = useState('default');

  useEffect(() => {
    document.body.setAttribute('data-theme', theme);
  }, [theme]);

  const fetchHistory = async () => {
    try {
      const response = await fetch("http://localhost:5000/api/history/user_123");
      if (response.ok) {
        const data = await response.json();
        const reversedHistory = data.history.reverse();
        const formattedData = reversedHistory.map((item) => {
           const dateObj = new Date(item.date);
           return {
             ...item,
             displayDate: `${dateObj.getMonth()+1}/${dateObj.getDate()} ${dateObj.getHours()}:${String(dateObj.getMinutes()).padStart(2, '0')}`,
             riskPercent: parseFloat((item.prediction_score * 100).toFixed(1))
           };
        });
        setHistoryData(formattedData);
        
        // If no current result, but history exists, show the latest result
        if (!result && formattedData.length > 0) {
          const latest = formattedData[formattedData.length - 1];
          setResult({
            risk_score: latest.prediction_score,
            message: latest.risk_message,
            explanation: latest.explanation
          });
        }
      }
    } catch (error) {
      console.error("Failed to fetch history:", error);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: Number(e.target.value) });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    const todaysData = [
      formData.sleep,
      formData.screenTime,
      formData.study,
      formData.activity,
      formData.stress
    ];

    // Repeat today's data across all 7 days so the GRU model sees a sustained pattern
    const fullSequence = Array(7).fill(todaysData);

    try {
      const response = await fetch("http://localhost:5000/api/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id: "user_123", sequence: fullSequence })
      });
      
      const data = await response.json();
      setResult(data);
      fetchHistory(); 
    } catch (error) {
      console.error("Error connecting to Node backend:", error);
      alert("⚠️ Could not connect to API. Is the backend running?");
    }

    setLoading(false);
  };

  // Set chart dynamic colors based on the theme
  const themeColors = {
    default: { primary: '#818cf8', secondary: '#f472b6', tertiary: '#38bdf8' },
    ocean: { primary: '#38bdf8', secondary: '#22d3ee', tertiary: '#818cf8' },
    sunset: { primary: '#fb923c', secondary: '#f87171', tertiary: '#fcd34d' },
    nature: { primary: '#34d399', secondary: '#a3e635', tertiary: '#6ee7b7' }
  };
  const activeColor = themeColors[theme] || themeColors.default;

  // Prepare data for Vertical Bar Chart (making it extremely easy to understand)
  // Mapping the raw values to an intuitive 0-100% "Intensity" scale for visualization
  const metricsData = [
    { name: 'Sleep', intensity: (formData.sleep / 12) * 100, actual: `${formData.sleep} hrs`, color: activeColor.primary },
    { name: 'Screen', intensity: (formData.screenTime / 16) * 100, actual: `${formData.screenTime} hrs`, color: activeColor.secondary },
    { name: 'Study', intensity: (formData.study / 14) * 100, actual: `${formData.study} hrs`, color: activeColor.tertiary },
    { name: 'Activity', intensity: formData.activity === 1 ? 100 : 15, actual: formData.activity ? 'Yes' : 'No', color: '#10b981' },
    { name: 'Stress', intensity: formData.stress === 0 ? 15 : (formData.stress === 1 ? 50 : 100), actual: ['Low', 'Med', 'High'][formData.stress], color: '#f59e0b' },
  ];

  return (
    <div className="dashboard-container">
      <div className="header-section">
        <h1>WellSense AI</h1>
        <p className="subtitle">Mental Health Early Warning System</p>
        <div className="theme-switcher">
          <button className={`theme-btn ${theme === 'default' ? 'active' : ''}`} style={{background: 'linear-gradient(to right, #6366f1, #ec4899)'}} onClick={() => setTheme('default')} title="Galactic"></button>
          <button className={`theme-btn ${theme === 'ocean' ? 'active' : ''}`} style={{background: 'linear-gradient(to right, #0ea5e9, #06b6d4)'}} onClick={() => setTheme('ocean')} title="Ocean"></button>
          <button className={`theme-btn ${theme === 'sunset' ? 'active' : ''}`} style={{background: 'linear-gradient(to right, #f97316, #ef4444)'}} onClick={() => setTheme('sunset')} title="Sunset"></button>
          <button className={`theme-btn ${theme === 'nature' ? 'active' : ''}`} style={{background: 'linear-gradient(to right, #10b981, #84cc16)'}} onClick={() => setTheme('nature')} title="Nature"></button>
        </div>
      </div>

      <div className="dashboard-grid">
        
        {/* LEFT COLUMN: FORM */}
        <div className="glass-card form-section">
          <h2 style={{marginTop: 0, marginBottom: '20px', fontSize: '1.4rem'}}>Daily Input</h2>
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label>Hours of Sleep (Last Night)</label>
              <input type="number" step="0.1" name="sleep" value={formData.sleep} onChange={handleChange} required />
            </div>

            <div className="form-group">
              <label>Screen Time (Hours Today)</label>
              <input type="number" step="0.1" name="screenTime" value={formData.screenTime} onChange={handleChange} required />
            </div>

            <div className="form-group">
              <label>Study / Work (Hours Today)</label>
              <input type="number" step="0.1" name="study" value={formData.study} onChange={handleChange} required />
            </div>

            <div className="form-group">
              <label>Did you exercise today?</label>
              <select name="activity" value={formData.activity} onChange={handleChange}>
                <option value={1}>Yes, I was active</option>
                <option value={0}>No, sedentary</option>
              </select>
            </div>

            <div className="form-group">
              <label>Current Stress Level</label>
              <select name="stress" value={formData.stress} onChange={handleChange}>
                <option value={0}>Low (Relaxed)</option>
                <option value={1}>Medium (Manageable)</option>
                <option value={2}>High (Overwhelmed)</option>
              </select>
            </div>

            <button type="submit" className="btn-primary" disabled={loading}>
              {loading ? "Analyzing Neural Network..." : "Generate AI Prediction"}
            </button>
          </form>
        </div>

        {/* RIGHT COLUMN: ANALYTICS DASHBOARD */}
        <div className="analytics-section">
          
          {/* Top Row: Main Status */}
          {result ? (
            <div className={`glass-card main-result-card ${result.risk_score > 0.7 ? 'result-high' : result.risk_score > 0.4 ? 'result-medium' : 'result-low'}`}>
              <div className="result-content">
                <span className="stat-label">Current Risk Assessment</span>
                <span className="stat-value" style={{fontSize: '4rem', display: 'block', margin: '10px 0'}}>
                  {(result.risk_score * 100).toFixed(1)}%
                </span>
                <span style={{fontSize: '1.2rem', fontWeight: 600, letterSpacing: '0.5px'}}>{result.message}</span>
                
                {result.explanation && (
                  <div className="insight-box">
                    <span style={{color: '#818cf8', fontWeight: 'bold', marginRight: '8px'}}>⚡ AI Insight:</span> 
                    {result.explanation}
                  </div>
                )}
              </div>
            </div>
          ) : (
            <div className="glass-card" style={{display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '200px', opacity: 0.6}}>
              <h2>Enter data to see your AI risk assessment.</h2>
            </div>
          )}

          {/* Bottom Row: Charts */}
          <div className="charts-row">
            
            {/* Chart 1: Timeline */}
            <div className="chart-wrapper">
              <h3 className="chart-title">Risk Timeline Overview</h3>
              {historyData.length > 0 ? (
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={historyData} margin={{ top: 20, right: 20, left: -20, bottom: 20 }}>
                    <defs>
                      <linearGradient id="colorRisk" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor={activeColor.primary} stopOpacity={0.6}/>
                        <stop offset="95%" stopColor={activeColor.primary} stopOpacity={0}/>
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.08)" vertical={false} />
                    <XAxis 
                       dataKey="displayDate" 
                       stroke="#cbd5e1" 
                       fontSize={10} 
                       tickLine={false} 
                       axisLine={false} 
                       angle={-25}
                       textAnchor="end"
                       dy={10}
                    />
                    <YAxis stroke="#cbd5e1" fontSize={11} domain={[0, 100]} tickLine={false} axisLine={false} />
                    <Tooltip 
                       contentStyle={{ backgroundColor: 'rgba(15, 15, 25, 0.95)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '12px', color: '#fff', boxShadow: '0 10px 15px -3px rgba(0,0,0,0.5)' }}
                       formatter={(value) => [`${value}%`, 'Risk Score']}
                       labelStyle={{ color: '#94a3b8', marginBottom: '5px' }}
                    />
                    <Area 
                       type="monotone" 
                       dataKey="riskPercent" 
                       stroke={activeColor.primary} 
                       strokeWidth={4} 
                       fillOpacity={1} 
                       fill="url(#colorRisk)" 
                       activeDot={{ r: 6, fill: '#fff', stroke: activeColor.primary, strokeWidth: 2 }}
                       dot={{ r: 3, fill: activeColor.primary, strokeWidth: 0 }}
                    />
                  </AreaChart>
                </ResponsiveContainer>
              ) : (
                <div style={{display:'flex', alignItems:'center', justifyContent:'center', height:'100%', color:'#64748b'}}>No history available.</div>
              )}
            </div>

            {/* Chart 2: Daily Metrics Breakdown */}
            <div className="chart-wrapper">
              <h3 className="chart-title">Today's Daily Metrics</h3>
              <ResponsiveContainer width="100%" height="85%">
                <BarChart data={metricsData} layout="vertical" margin={{ top: 5, right: 30, left: 10, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" horizontal={false} />
                  <XAxis type="number" domain={[0, 100]} hide />
                  <YAxis dataKey="name" type="category" axisLine={false} tickLine={false} tick={{ fill: '#e2e8f0', fontSize: 12, fontWeight: 500 }} width={60} />
                  <Tooltip 
                     cursor={{fill: 'rgba(255,255,255,0.05)'}}
                     contentStyle={{ backgroundColor: 'rgba(15, 15, 25, 0.95)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '12px', color: '#fff', boxShadow: '0 10px 15px -3px rgba(0,0,0,0.5)' }}
                     formatter={(value, name, props) => [props.payload.actual, 'Recorded']}
                  />
                  <Bar dataKey="intensity" radius={[0, 8, 8, 0]} barSize={20}>
                    {metricsData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>

          </div>

        </div>
      </div>
    </div>
  );
}
