import { motion } from 'framer-motion';
import { MapPin, TrendingUp } from 'lucide-react';
import {
  RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
  Radar, ResponsiveContainer, Tooltip,
} from 'recharts';
import { areaStats, formatNumber, getCongestionBadge, getCongestionColor } from '../data';

const chartTooltipStyle = {
  backgroundColor: '#1e293b',
  border: '1px solid rgba(255,255,255,0.1)',
  borderRadius: '8px',
  color: '#f1f5f9',
  fontSize: '13px',
  padding: '10px 14px',
};

const radarData = areaStats.map(a => ({
  area: a.name.length > 10 ? a.name.slice(0, 10) + '…' : a.name,
  Volume: Math.round(a.avgVolume / 1000),
  Congestion: a.congestion,
}));

export default function Analytics() {
  return (
    <div>
      <div className="page-header">
        <h2>Area Analytics</h2>
        <p>Deep-dive into traffic patterns across all monitored Bengaluru areas</p>
      </div>

      {/* ---- Radar Chart ---- */}
      <motion.div
        className="glass-card"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        style={{ marginBottom: 24 }}
      >
        <div className="glass-card-header">
          <span className="glass-card-title">
            <TrendingUp size={18} /> Area Comparison Radar
          </span>
        </div>
        <ResponsiveContainer width="100%" height={400}>
          <RadarChart data={radarData}>
            <PolarGrid stroke="rgba(255,255,255,0.08)" />
            <PolarAngleAxis dataKey="area" tick={{ fill: '#94a3b8', fontSize: 12 }} />
            <PolarRadiusAxis tick={{ fill: '#64748b', fontSize: 10 }} />
            <Radar
              name="Volume (K)"
              dataKey="Volume"
              stroke="#3b82f6"
              fill="#3b82f6"
              fillOpacity={0.2}
              strokeWidth={2}
            />
            <Radar
              name="Congestion %"
              dataKey="Congestion"
              stroke="#64748b"
              fill="#64748b"
              fillOpacity={0.15}
              strokeWidth={2}
            />
            <Tooltip contentStyle={chartTooltipStyle} />
          </RadarChart>
        </ResponsiveContainer>
      </motion.div>

      {/* ---- Area Cards ---- */}
      <div className="area-grid">
        {areaStats.map((area, i) => {
          const badge = getCongestionBadge(area.congestion);
          const congColor = getCongestionColor(area.congestion);
          return (
            <motion.div
              key={area.name}
              className="area-card"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.06 }}
              whileHover={{ y: -3 }}
            >
              <div className="area-card-header">
                <span className="area-card-name">
                  <MapPin size={14} style={{ marginRight: 6, verticalAlign: -2, color: 'var(--accent-purple-light)' }} />
                  {area.name}
                </span>
                <span className={`badge ${badge.className}`}>{badge.label}</span>
              </div>

              <div className="area-card-stats">
                <div className="area-stat">
                  <span className="area-stat-label">Avg Volume</span>
                  <span className="area-stat-value">{formatNumber(area.avgVolume)}</span>
                </div>
                <div className="area-stat">
                  <span className="area-stat-label">Median</span>
                  <span className="area-stat-value">{formatNumber(area.medianVolume)}</span>
                </div>
                <div className="area-stat">
                  <span className="area-stat-label">Std Dev</span>
                  <span className="area-stat-value">{formatNumber(area.stdVolume)}</span>
                </div>
                <div className="area-stat">
                  <span className="area-stat-label">Congestion</span>
                  <span className="area-stat-value">{area.congestion}%</span>
                </div>
              </div>

              <div style={{ marginTop: 16 }}>
                <div className="traffic-bar">
                  <div className={`traffic-bar-fill ${congColor}`} style={{ width: `${area.congestion}%` }} />
                </div>
              </div>

              <div style={{ marginTop: 12 }}>
                <span className="area-stat-label">Roads: </span>
                <span style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
                  {area.roads.join(' • ')}
                </span>
              </div>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}
