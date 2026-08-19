import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  BrainCircuit,
  BarChart3,
  Activity,
  Settings,
  Database,
  Zap,
} from 'lucide-react';
import { useEffect, useState } from 'react';
import { checkHealth } from '../data';

export default function Sidebar() {
  const [apiOnline, setApiOnline] = useState(false);

  useEffect(() => {
    let mounted = true;
    const check = async () => {
      const health = await checkHealth();
      if (mounted) setApiOnline(!!health);
    };
    check();
    const interval = setInterval(check, 15000);
    return () => { mounted = false; clearInterval(interval); };
  }, []);

  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <div className="sidebar-brand-icon">
          <Zap size={20} color="white" />
        </div>
        <div className="sidebar-brand-text">
          <h1>Traffic Intel</h1>
          <span>Bengaluru MLOps</span>
        </div>
      </div>

      <nav className="sidebar-nav">
        <span className="sidebar-section-title">Main</span>

        <NavLink to="/" end className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
          <LayoutDashboard size={18} />
          <span>Dashboard</span>
        </NavLink>

        <NavLink to="/predict" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
          <BrainCircuit size={18} />
          <span>Predict</span>
        </NavLink>

        <NavLink to="/analytics" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
          <BarChart3 size={18} />
          <span>Analytics</span>
        </NavLink>

        <span className="sidebar-section-title">System</span>

        <NavLink to="/models" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
          <Activity size={18} />
          <span>Model Performance</span>
        </NavLink>

        <NavLink to="/data" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
          <Database size={18} />
          <span>Data Pipeline</span>
        </NavLink>

        <NavLink to="/settings" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
          <Settings size={18} />
          <span>Settings</span>
        </NavLink>
      </nav>

      <div className="sidebar-footer">
        <div className="api-status">
          <span className={`api-status-dot ${apiOnline ? 'online' : 'offline'}`} />
          <span>API {apiOnline ? 'Connected' : 'Offline'}</span>
        </div>
      </div>
    </aside>
  );
}
