import { Car, TrendingUp, MapPin, AlertTriangle, CloudRain } from 'lucide-react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  LineChart, Line, AreaChart, Area, PieChart, Pie, Cell, Legend,
} from 'recharts';
import { motion } from 'framer-motion';
import MetricCard from '../components/MetricCard';
import {
  areaStats, monthlyTrends, weatherDistribution, hourlyPattern,
  formatNumber, getCongestionBadge,
} from '../data';

const chartTooltipStyle = {
  backgroundColor: '#1e293b',
  border: '1px solid rgba(255,255,255,0.1)',
  borderRadius: '8px',
  color: '#f1f5f9',
  fontSize: '13px',
  padding: '10px 14px',
};

export default function Dashboard() {
  const totalVolume = areaStats.reduce((s, a) => s + a.avgVolume, 0);
  const avgCongestion = Math.round(areaStats.reduce((s, a) => s + a.congestion, 0) / areaStats.length);

  return (
    <div>
      <div className="page-header">
        <h2>Traffic Dashboard</h2>
        <p>Real-time traffic intelligence across Bengaluru's major corridors</p>
      </div>

      {/* ---- Metric Cards ---- */}
      <div className="metrics-grid">
        <MetricCard
          icon={<Car size={20} />}
          label="Total Avg Volume"
          value={formatNumber(totalVolume)}
          change={3.2}
          color="purple"
        />
        <MetricCard
          icon={<TrendingUp size={20} />}
          label="Avg Congestion"
          value={`${avgCongestion}%`}
          change={-1.8}
          color="cyan"
        />
        <MetricCard
          icon={<MapPin size={20} />}
          label="Areas Monitored"
          value="8"
          color="emerald"
        />
        <MetricCard
          icon={<AlertTriangle size={20} />}
          label="Incident Avg"
          value="1.5 / day"
          change={5.1}
          color="amber"
        />
        <MetricCard
          icon={<CloudRain size={20} />}
          label="Weather Impact"
          value="Low"
          color="rose"
        />
      </div>

      {/* ---- Charts Row 1: Area Volume + Hourly Pattern ---- */}
      <div className="charts-grid">
        <motion.div
          className="glass-card"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.15 }}
        >
          <div className="glass-card-header">
            <span className="glass-card-title">
              <MapPin size={18} /> Traffic Volume by Area
            </span>
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={areaStats} layout="vertical" margin={{ left: 20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
              <XAxis type="number" tick={{ fill: '#94a3b8', fontSize: 12 }} />
              <YAxis
                dataKey="name"
                type="category"
                tick={{ fill: '#94a3b8', fontSize: 12 }}
                width={110}
              />
              <Tooltip contentStyle={chartTooltipStyle} />
              <Bar dataKey="avgVolume" name="Avg Volume" radius={[0, 6, 6, 0]}>
                {areaStats.map((_, i) => (
                  <Cell key={i} fill={`hsl(215, 20%, ${35 + i * 5}%)`} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </motion.div>

        <motion.div
          className="glass-card"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.25 }}
        >
          <div className="glass-card-header">
            <span className="glass-card-title">
              <TrendingUp size={18} /> Hourly Traffic Pattern
            </span>
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={hourlyPattern}>
              <defs>
                <linearGradient id="hourlyGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#3b82f6" stopOpacity={0.2} />
                  <stop offset="100%" stopColor="#3b82f6" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
              <XAxis dataKey="hour" tick={{ fill: '#a1a1aa', fontSize: 11 }} />
              <YAxis tick={{ fill: '#a1a1aa', fontSize: 12 }} />
              <Tooltip contentStyle={chartTooltipStyle} />
              <Area
                type="monotone"
                dataKey="volume"
                name="Volume"
                stroke="#3b82f6"
                fill="url(#hourlyGradient)"
                strokeWidth={2}
              />
            </AreaChart>
          </ResponsiveContainer>
        </motion.div>
      </div>

      {/* ---- Charts Row 2: Monthly Trends + Weather ---- */}
      <div className="charts-grid">
        <motion.div
          className="glass-card"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.35 }}
        >
          <div className="glass-card-header">
            <span className="glass-card-title">
              <TrendingUp size={18} /> Monthly Traffic Trends
            </span>
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={monthlyTrends}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
              <XAxis dataKey="month" tick={{ fill: '#a1a1aa', fontSize: 12 }} />
              <YAxis tick={{ fill: '#a1a1aa', fontSize: 12 }} />
              <Tooltip contentStyle={chartTooltipStyle} />
              <Legend wrapperStyle={{ fontSize: '12px', color: '#a1a1aa' }} />
              <Line type="monotone" dataKey="Koramangala" stroke="#3b82f6" strokeWidth={2} dot={false} />
              <Line type="monotone" dataKey="M.G. Road" stroke="#6366f1" strokeWidth={2} dot={false} />
              <Line type="monotone" dataKey="Indiranagar" stroke="#10b981" strokeWidth={2} dot={false} />
              <Line type="monotone" dataKey="Hebbal" stroke="#a8a29e" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </motion.div>

        <motion.div
          className="glass-card"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.45 }}
        >
          <div className="glass-card-header">
            <span className="glass-card-title">
              <CloudRain size={18} /> Weather Distribution
            </span>
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={weatherDistribution}
                cx="50%"
                cy="50%"
                innerRadius={65}
                outerRadius={110}
                paddingAngle={4}
                dataKey="count"
                nameKey="name"
                strokeWidth={0}
              >
                {weatherDistribution.map((entry, i) => (
                  <Cell key={i} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip contentStyle={chartTooltipStyle} />
              <Legend wrapperStyle={{ fontSize: '12px', color: '#94a3b8' }} />
            </PieChart>
          </ResponsiveContainer>
        </motion.div>
      </div>

      {/* ---- Area Status Table ---- */}
      <motion.div
        className="glass-card"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.55 }}
      >
        <div className="glass-card-header">
          <span className="glass-card-title">
            <MapPin size={18} /> Area Congestion Overview
          </span>
        </div>
        <table className="data-table">
          <thead>
            <tr>
              <th>Area</th>
              <th>Avg Volume</th>
              <th>Congestion</th>
              <th>Status</th>
              <th>Level</th>
            </tr>
          </thead>
          <tbody>
            {areaStats.map((area) => {
              const badge = getCongestionBadge(area.congestion);
              return (
                <tr key={area.name}>
                  <td style={{ fontWeight: 600, color: '#f1f5f9' }}>{area.name}</td>
                  <td>{area.avgVolume.toLocaleString()}</td>
                  <td>{area.congestion}%</td>
                  <td>
                    <span className={`badge ${badge.className}`}>{badge.label}</span>
                  </td>
                  <td style={{ width: '150px' }}>
                    <div className="traffic-bar">
                      <div
                        className={`traffic-bar-fill ${area.congestion >= 80 ? 'high' : area.congestion >= 50 ? 'medium' : 'low'}`}
                        style={{ width: `${area.congestion}%` }}
                      />
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </motion.div>
    </div>
  );
}
