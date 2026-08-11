import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { BrainCircuit, Send, RotateCcw, MapPin, Calendar, Gauge } from 'lucide-react';
import toast, { Toaster } from 'react-hot-toast';
import { areaRoads, predictTraffic, formatNumber, getCongestionBadge } from '../data';

const defaultForm = {
  date: new Date().toISOString().split('T')[0],
  area_name: 'Koramangala',
  road_name: 'Sony World Junction',
  average_speed: 35.5,
  travel_time_index: 1.5,
  congestion_level: 85,
  road_capacity_utilization: 90,
  incident_reports: 2,
  public_transport_usage: 55,
  traffic_signal_compliance: 82,
  parking_usage: 70,
  pedestrian_cyclist_count: 100,
  weather_conditions: 'Clear',
  roadwork_activity: 'No',
};

export default function Predict() {
  const [form, setForm] = useState(defaultForm);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const roads = areaRoads[form.area_name] || [];

  const handleChange = (e) => {
    const { name, value } = e.target;
    const updated = { ...form, [name]: value };

    // Reset road when area changes
    if (name === 'area_name') {
      const newRoads = areaRoads[value] || [];
      updated.road_name = newRoads[0] || '';
    }

    setForm(updated);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const payload = {
        ...form,
        average_speed: parseFloat(form.average_speed),
        travel_time_index: parseFloat(form.travel_time_index),
        congestion_level: parseFloat(form.congestion_level),
        road_capacity_utilization: parseFloat(form.road_capacity_utilization),
        incident_reports: parseInt(form.incident_reports),
        public_transport_usage: parseFloat(form.public_transport_usage),
        traffic_signal_compliance: parseFloat(form.traffic_signal_compliance),
        parking_usage: parseFloat(form.parking_usage),
        pedestrian_cyclist_count: parseInt(form.pedestrian_cyclist_count),
      };
      const res = await predictTraffic(payload);
      setResult(res);
      toast.success('Prediction successful!');
    } catch (err) {
      // Fallback demo prediction when API is offline
      const demoVolume = Math.round(
        20000 + form.congestion_level * 300 + Math.random() * 5000
      );
      setResult({
        predicted_traffic_volume: demoVolume,
        area: form.area_name,
        road: form.road_name,
        confidence_note: 'Demo prediction (API offline)',
      });
      toast('Demo mode — API is offline', { icon: '⚡' });
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setForm(defaultForm);
    setResult(null);
  };

  return (
    <div>
      <Toaster
        position="top-right"
        toastOptions={{
          style: {
            background: '#1e293b',
            color: '#f1f5f9',
            border: '1px solid rgba(255,255,255,0.1)',
            borderRadius: '12px',
            fontSize: '13px',
          },
        }}
      />

      <div className="page-header">
        <h2>Traffic Prediction</h2>
        <p>Enter road conditions to predict traffic volume using our ML model</p>
      </div>

      <div className="predict-layout">
        {/* ---- Form ---- */}
        <motion.form
          className="glass-card"
          onSubmit={handleSubmit}
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.4 }}
        >
          <div className="glass-card-header">
            <span className="glass-card-title">
              <BrainCircuit size={18} /> Input Features
            </span>
            <button type="button" className="btn btn-secondary" onClick={handleReset} style={{ padding: '6px 12px', fontSize: '12px' }}>
              <RotateCcw size={14} /> Reset
            </button>
          </div>

          <div className="form-grid">
            <div className="form-group">
              <label className="form-label">Date</label>
              <input type="date" name="date" value={form.date} onChange={handleChange} className="form-input" />
            </div>

            <div className="form-group">
              <label className="form-label">Weather</label>
              <select name="weather_conditions" value={form.weather_conditions} onChange={handleChange} className="form-select">
                {['Clear', 'Rain', 'Fog', 'Overcast', 'Windy'].map(w => (
                  <option key={w} value={w}>{w}</option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">Area</label>
              <select name="area_name" value={form.area_name} onChange={handleChange} className="form-select">
                {Object.keys(areaRoads).map(a => (
                  <option key={a} value={a}>{a}</option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">Road / Intersection</label>
              <select name="road_name" value={form.road_name} onChange={handleChange} className="form-select">
                {roads.map(r => (
                  <option key={r} value={r}>{r}</option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">Avg Speed (km/h)</label>
              <input type="number" name="average_speed" value={form.average_speed} onChange={handleChange} className="form-input" step="0.1" min="0" />
            </div>

            <div className="form-group">
              <label className="form-label">Travel Time Index</label>
              <input type="number" name="travel_time_index" value={form.travel_time_index} onChange={handleChange} className="form-input" step="0.01" min="1" />
            </div>

            <div className="form-group">
              <label className="form-label">Congestion Level (%)</label>
              <input type="number" name="congestion_level" value={form.congestion_level} onChange={handleChange} className="form-input" min="0" max="100" />
            </div>

            <div className="form-group">
              <label className="form-label">Road Capacity (%)</label>
              <input type="number" name="road_capacity_utilization" value={form.road_capacity_utilization} onChange={handleChange} className="form-input" min="0" max="100" />
            </div>

            <div className="form-group">
              <label className="form-label">Incident Reports</label>
              <input type="number" name="incident_reports" value={form.incident_reports} onChange={handleChange} className="form-input" min="0" />
            </div>

            <div className="form-group">
              <label className="form-label">Public Transport (%)</label>
              <input type="number" name="public_transport_usage" value={form.public_transport_usage} onChange={handleChange} className="form-input" step="0.1" min="0" />
            </div>

            <div className="form-group">
              <label className="form-label">Signal Compliance (%)</label>
              <input type="number" name="traffic_signal_compliance" value={form.traffic_signal_compliance} onChange={handleChange} className="form-input" step="0.1" min="0" max="100" />
            </div>

            <div className="form-group">
              <label className="form-label">Parking Usage (%)</label>
              <input type="number" name="parking_usage" value={form.parking_usage} onChange={handleChange} className="form-input" step="0.1" min="0" max="100" />
            </div>

            <div className="form-group">
              <label className="form-label">Pedestrian Count</label>
              <input type="number" name="pedestrian_cyclist_count" value={form.pedestrian_cyclist_count} onChange={handleChange} className="form-input" min="0" />
            </div>

            <div className="form-group">
              <label className="form-label">Roadwork?</label>
              <select name="roadwork_activity" value={form.roadwork_activity} onChange={handleChange} className="form-select">
                <option value="No">No</option>
                <option value="Yes">Yes</option>
              </select>
            </div>

            <div className="form-group full-width" style={{ marginTop: 8 }}>
              <button type="submit" className="btn btn-primary btn-lg" disabled={loading} style={{ width: '100%' }}>
                {loading ? <><span className="spinner" /> Predicting...</> : <><Send size={16} /> Predict Traffic Volume</>}
              </button>
            </div>
          </div>
        </motion.form>

        {/* ---- Result ---- */}
        <motion.div
          className="glass-card"
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.4 }}
        >
          <div className="glass-card-header">
            <span className="glass-card-title">
              <Gauge size={18} /> Prediction Result
            </span>
          </div>

          <AnimatePresence mode="wait">
            {result ? (
              <motion.div
                className="prediction-result"
                key="result"
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.9 }}
                transition={{ duration: 0.3 }}
              >
                <div className="prediction-result-value">
                  {formatNumber(Math.round(result.predicted_traffic_volume))}
                </div>
                <div className="prediction-result-label">
                  Predicted Traffic Volume
                </div>

                <div className="prediction-result-meta">
                  <div className="prediction-meta-item">
                    <span>Area</span>
                    <strong>{result.area}</strong>
                  </div>
                  <div className="prediction-meta-item">
                    <span>Road</span>
                    <strong>{result.road}</strong>
                  </div>
                  <div className="prediction-meta-item">
                    <span>Status</span>
                    <strong>
                      {(() => {
                        const badge = getCongestionBadge(form.congestion_level);
                        return <span className={`badge ${badge.className}`}>{badge.label}</span>;
                      })()}
                    </strong>
                  </div>
                </div>

                <p style={{ marginTop: 16, fontSize: '12px', color: 'var(--text-muted)' }}>
                  {result.confidence_note}
                </p>
              </motion.div>
            ) : (
              <motion.div
                className="prediction-empty"
                key="empty"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
              >
                <BrainCircuit size={64} />
                <p>Fill in the traffic features and click<br /><strong>Predict</strong> to see the result</p>
              </motion.div>
            )}
          </AnimatePresence>
        </motion.div>
      </div>
    </div>
  );
}
