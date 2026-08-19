import { Activity, Target, Zap, Clock } from 'lucide-react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  Cell, ReferenceLine,
} from 'recharts';
import { motion } from 'framer-motion';
import { modelMetrics } from '../data';
import MetricCard from '../components/MetricCard';

const chartTooltipStyle = {
  backgroundColor: '#1e293b',
  border: '1px solid rgba(255,255,255,0.1)',
  borderRadius: '8px',
  color: '#f1f5f9',
  fontSize: '13px',
  padding: '10px 14px',
};

// Transform metrics into array for charts
const metricsData = Object.entries(modelMetrics).map(([name, metrics]) => ({
  name: name.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()),
  id: name,
  ...metrics
}));

export default function Models() {
  const bestModel = metricsData.reduce((prev, curr) => (prev.rmse < curr.rmse) ? prev : curr);

  return (
    <div>
      <div className="page-header">
        <h2>Model Performance</h2>
        <p>Evaluation metrics across trained machine learning models</p>
      </div>

      <div className="metrics-grid">
        <MetricCard
          icon={<Target size={20} />}
          label="Best Model"
          value={bestModel.name}
          color="purple"
        />
        <MetricCard
          icon={<Zap size={20} />}
          label="Best RMSE"
          value={bestModel.rmse.toLocaleString(undefined, { maximumFractionDigits: 1 })}
          color="cyan"
        />
        <MetricCard
          icon={<Activity size={20} />}
          label="Best R² Score"
          value={bestModel.r2.toFixed(4)}
          color="emerald"
        />
        <MetricCard
          icon={<Clock size={20} />}
          label="Optuna Trials"
          value="50"
          color="amber"
        />
      </div>

      <div className="charts-grid full">
        {/* ---- R2 Score Comparison ---- */}
        <motion.div
          className="glass-card"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
        >
          <div className="glass-card-header">
            <span className="glass-card-title">
              <Activity size={18} /> R² Score (Higher is better)
            </span>
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={metricsData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
              <XAxis dataKey="name" tick={{ fill: '#94a3b8', fontSize: 12 }} />
              <YAxis domain={[0, 1]} tick={{ fill: '#94a3b8', fontSize: 12 }} />
              <Tooltip contentStyle={chartTooltipStyle} cursor={{ fill: 'rgba(255,255,255,0.02)' }} />
              <ReferenceLine y={0.9} stroke="rgba(16, 185, 129, 0.5)" strokeDasharray="3 3" />
              <Bar dataKey="r2" name="R² Score" radius={[4, 4, 0, 0]} maxBarSize={60}>
                {metricsData.map((entry, index) => (
                  <Cell 
                    key={`cell-${index}`} 
                    fill={entry.id === bestModel.id ? '#10b981' : 'rgba(16, 185, 129, 0.2)'} 
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </motion.div>
      </div>

      <div className="charts-grid">
        {/* ---- RMSE Comparison ---- */}
        <motion.div
          className="glass-card"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <div className="glass-card-header">
            <span className="glass-card-title">
              <Target size={18} /> RMSE (Lower is better)
            </span>
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={metricsData} layout="vertical" margin={{ top: 20, right: 30, left: 40, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
              <XAxis type="number" tick={{ fill: '#94a3b8', fontSize: 12 }} />
              <YAxis dataKey="name" type="category" tick={{ fill: '#94a3b8', fontSize: 12 }} />
              <Tooltip contentStyle={chartTooltipStyle} cursor={{ fill: 'rgba(255,255,255,0.02)' }} />
              <Bar dataKey="rmse" name="RMSE" radius={[0, 4, 4, 0]} maxBarSize={40}>
                {metricsData.map((entry, index) => (
                  <Cell 
                    key={`cell-${index}`} 
                    fill={entry.id === bestModel.id ? '#3b82f6' : 'rgba(59, 130, 246, 0.2)'} 
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </motion.div>

        {/* ---- MAPE Comparison ---- */}
        <motion.div
          className="glass-card"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
        >
          <div className="glass-card-header">
            <span className="glass-card-title">
              <Zap size={18} /> MAPE % (Lower is better)
            </span>
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={metricsData} layout="vertical" margin={{ top: 20, right: 30, left: 40, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
              <XAxis type="number" tick={{ fill: '#94a3b8', fontSize: 12 }} />
              <YAxis dataKey="name" type="category" tick={{ fill: '#94a3b8', fontSize: 12 }} />
              <Tooltip contentStyle={chartTooltipStyle} cursor={{ fill: 'rgba(255,255,255,0.02)' }} />
              <Bar dataKey="mape" name="MAPE (%)" radius={[0, 4, 4, 0]} maxBarSize={40}>
                {metricsData.map((entry, index) => (
                  <Cell 
                    key={`cell-${index}`} 
                    fill={entry.id === bestModel.id ? '#6366f1' : 'rgba(99, 102, 241, 0.2)'} 
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </motion.div>
      </div>
      
      {/* Table */}
      <motion.div
        className="glass-card"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
      >
        <div className="glass-card-header">
          <span className="glass-card-title">
            <Activity size={18} /> Detailed Metrics
          </span>
        </div>
        <table className="data-table">
          <thead>
            <tr>
              <th>Model Name</th>
              <th>RMSE</th>
              <th>MAE</th>
              <th>R² Score</th>
              <th>MAPE (%)</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {metricsData.map((model) => (
              <tr key={model.id}>
                <td style={{ fontWeight: 600, color: '#f1f5f9' }}>{model.name}</td>
                <td>{model.rmse.toLocaleString(undefined, { maximumFractionDigits: 2 })}</td>
                <td>{model.mae.toLocaleString(undefined, { maximumFractionDigits: 2 })}</td>
                <td>{model.r2.toFixed(4)}</td>
                <td>{model.mape.toFixed(2)}%</td>
                <td>
                  {model.id === bestModel.id ? (
                    <span className="badge green">Production</span>
                  ) : (
                    <span className="badge" style={{ background: 'var(--bg-glass)', color: 'var(--text-muted)' }}>Experiment</span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </motion.div>
    </div>
  );
}
