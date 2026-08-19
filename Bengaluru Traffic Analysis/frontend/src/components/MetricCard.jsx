import { motion } from 'framer-motion';

export default function MetricCard({ icon, label, value, change, color = 'purple' }) {
  return (
    <motion.div
      className={`metric-card ${color}`}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      whileHover={{ y: -3 }}
    >
      <div className={`metric-card-icon ${color}`}>
        {icon}
      </div>
      <div className="metric-card-label">{label}</div>
      <div className="metric-card-value">{value}</div>
      {change && (
        <span className={`metric-card-change ${change >= 0 ? 'positive' : 'negative'}`}>
          {change >= 0 ? '↑' : '↓'} {Math.abs(change)}%
        </span>
      )}
    </motion.div>
  );
}
