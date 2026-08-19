// Mock data and API utilities for the Bengaluru Traffic Dashboard

// ================================================
// Area traffic statistics (pre-computed from dataset)
// ================================================
export const areaStats = [
  { name: 'Koramangala', avgVolume: 40832, medianVolume: 43310, stdVolume: 14131, roads: ['Sony World Junction', 'Sarjapur Road'], congestion: 92 },
  { name: 'M.G. Road', avgVolume: 35300, medianVolume: 37330, stdVolume: 11896, roads: ['Trinity Circle', 'Anil Kumble Circle'], congestion: 87 },
  { name: 'Indiranagar', avgVolume: 32284, medianVolume: 33838, stdVolume: 11270, roads: ['100 Feet Road', 'CMH Road'], congestion: 83 },
  { name: 'Hebbal', avgVolume: 26533, medianVolume: 27575, stdVolume: 9711, roads: ['Hebbal Flyover', 'Ballari Road'], congestion: 74 },
  { name: 'Jayanagar', avgVolume: 24601, medianVolume: 25348, stdVolume: 8598, roads: ['Jayanagar 4th Block', 'South End Circle'], congestion: 70 },
  { name: 'Whitefield', avgVolume: 21295, medianVolume: 21655, stdVolume: 7826, roads: ['Marathahalli Bridge', 'ITPL Main Road'], congestion: 62 },
  { name: 'Yeshwanthpur', avgVolume: 18932, medianVolume: 18892, stdVolume: 7085, roads: ['Yeshwanthpur Circle', 'Tumkur Road'], congestion: 55 },
  { name: 'Electronic City', avgVolume: 16347, medianVolume: 16073, stdVolume: 6219, roads: ['Hosur Road', 'Electronic City Flyover'], congestion: 48 },
];

// ================================================
// Monthly traffic trends
// ================================================
export const monthlyTrends = [
  { month: 'Jan', Koramangala: 39500, 'M.G. Road': 34200, Indiranagar: 31800, Hebbal: 25900 },
  { month: 'Feb', Koramangala: 40100, 'M.G. Road': 34800, Indiranagar: 32100, Hebbal: 26200 },
  { month: 'Mar', Koramangala: 41200, 'M.G. Road': 35500, Indiranagar: 32600, Hebbal: 26800 },
  { month: 'Apr', Koramangala: 40800, 'M.G. Road': 35100, Indiranagar: 32300, Hebbal: 26500 },
  { month: 'May', Koramangala: 41500, 'M.G. Road': 35800, Indiranagar: 32900, Hebbal: 27000 },
  { month: 'Jun', Koramangala: 40200, 'M.G. Road': 34700, Indiranagar: 31900, Hebbal: 26100 },
  { month: 'Jul', Koramangala: 39800, 'M.G. Road': 34400, Indiranagar: 31600, Hebbal: 25800 },
  { month: 'Aug', Koramangala: 41000, 'M.G. Road': 35300, Indiranagar: 32500, Hebbal: 26700 },
  { month: 'Sep', Koramangala: 41800, 'M.G. Road': 36000, Indiranagar: 33100, Hebbal: 27200 },
  { month: 'Oct', Koramangala: 42200, 'M.G. Road': 36400, Indiranagar: 33400, Hebbal: 27500 },
  { month: 'Nov', Koramangala: 41100, 'M.G. Road': 35400, Indiranagar: 32700, Hebbal: 26900 },
  { month: 'Dec', Koramangala: 40500, 'M.G. Road': 34900, Indiranagar: 32200, Hebbal: 26400 },
];

// ================================================
// Weather distribution
// ================================================
export const weatherDistribution = [
  { name: 'Clear', count: 5426, avgVolume: 29167, color: '#f59e0b' },
  { name: 'Overcast', count: 1296, avgVolume: 29053, color: '#94a3b8' },
  { name: 'Fog', count: 959, avgVolume: 29183, color: '#7c3aed' },
  { name: 'Rain', count: 827, avgVolume: 29559, color: '#06b6d4' },
  { name: 'Windy', count: 428, avgVolume: 30163, color: '#10b981' },
];

// ================================================
// Model performance metrics
// ================================================
export const modelMetrics = {
  linear_regression: { rmse: 8245.12, mae: 6521.34, r2: 0.5982, mape: 28.45 },
  random_forest: { rmse: 3012.45, mae: 2134.67, r2: 0.9463, mape: 8.92 },
  xgboost: { rmse: 2587.23, mae: 1876.45, r2: 0.9604, mape: 7.34 },
  lightgbm: { rmse: 2643.89, mae: 1923.12, r2: 0.9587, mape: 7.56 },
};

// ================================================
// Hourly pattern (synthetic for visualization)
// ================================================
export const hourlyPattern = [
  { hour: '6 AM', volume: 12000 },
  { hour: '7 AM', volume: 28000 },
  { hour: '8 AM', volume: 45000 },
  { hour: '9 AM', volume: 52000 },
  { hour: '10 AM', volume: 38000 },
  { hour: '11 AM', volume: 32000 },
  { hour: '12 PM', volume: 30000 },
  { hour: '1 PM', volume: 28000 },
  { hour: '2 PM', volume: 29000 },
  { hour: '3 PM', volume: 31000 },
  { hour: '4 PM', volume: 35000 },
  { hour: '5 PM', volume: 48000 },
  { hour: '6 PM', volume: 55000 },
  { hour: '7 PM', volume: 50000 },
  { hour: '8 PM', volume: 38000 },
  { hour: '9 PM', volume: 25000 },
  { hour: '10 PM', volume: 18000 },
];

// ================================================
// Road mapping
// ================================================
export const areaRoads = {
  'Koramangala': ['Sony World Junction', 'Sarjapur Road'],
  'M.G. Road': ['Trinity Circle', 'Anil Kumble Circle'],
  'Indiranagar': ['100 Feet Road', 'CMH Road'],
  'Hebbal': ['Hebbal Flyover', 'Ballari Road'],
  'Jayanagar': ['Jayanagar 4th Block', 'South End Circle'],
  'Whitefield': ['Marathahalli Bridge', 'ITPL Main Road'],
  'Yeshwanthpur': ['Yeshwanthpur Circle', 'Tumkur Road'],
  'Electronic City': ['Hosur Road', 'Electronic City Flyover'],
};

// ================================================
// API Service
// ================================================
const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export async function checkHealth() {
  try {
    const res = await fetch(`${API_BASE}/health`);
    if (!res.ok) throw new Error('API unreachable');
    return await res.json();
  } catch {
    return null;
  }
}

export async function predictTraffic(features) {
  const res = await fetch(`${API_BASE}/predict`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(features),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || 'Prediction failed');
  }
  return res.json();
}

export async function getModelInfo() {
  try {
    const res = await fetch(`${API_BASE}/model/info`);
    if (!res.ok) throw new Error('Failed to get model info');
    return await res.json();
  } catch {
    return null;
  }
}

// ================================================
// Helpers
// ================================================
export function formatNumber(num) {
  if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
  return num.toLocaleString();
}

export function getCongestionColor(level) {
  if (level >= 80) return 'high';
  if (level >= 50) return 'medium';
  return 'low';
}

export function getCongestionBadge(level) {
  if (level >= 80) return { label: 'Heavy', className: 'red' };
  if (level >= 60) return { label: 'Moderate', className: 'yellow' };
  if (level >= 40) return { label: 'Light', className: 'green' };
  return { label: 'Free Flow', className: 'blue' };
}
