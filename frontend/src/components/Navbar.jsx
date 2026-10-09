import React, { useEffect, useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { 
  Globe2, 
  UploadCloud, 
  Layers, 
  Sun, 
  Moon, 
  FileText, 
  Activity, 
  CheckCircle2, 
  AlertCircle 
} from 'lucide-react';
import { useTheme } from '../context/ThemeContext';
import api from '../services/api';

export const Navbar = () => {
  const { theme, toggleTheme } = useTheme();
  const location = useLocation();
  const [healthy, setHealthy] = useState(null);

  useEffect(() => {
    const checkApi = async () => {
      try {
        const data = await api.checkHealth();
        setHealthy(data.status === 'healthy');
      } catch {
        setHealthy(false);
      }
    };
    checkApi();
    const interval = setInterval(checkApi, 30000);
    return () => clearInterval(interval);
  }, []);

  const navLinks = [
    { to: '/', label: 'Dashboard', icon: Layers },
    { to: '/upload', label: 'Upload Dataset', icon: UploadCloud },
  ];

  return (
    <header style={{
      background: 'var(--bg-glass-heavy)',
      backdropFilter: 'blur(16px)',
      WebkitBackdropFilter: 'blur(16px)',
      borderBottom: '1px solid var(--border-subtle)',
      position: 'sticky',
      top: 0,
      zIndex: 1000,
    }}>
      <div style={{
        maxWidth: '1440px',
        margin: '0 auto',
        padding: '0.85rem 1.5rem',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
      }}>
        {/* Logo */}
        <Link to="/" style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', textDecoration: 'none' }}>
          <div style={{
            width: '38px',
            height: '38px',
            borderRadius: '10px',
            background: 'linear-gradient(135deg, #10b981 0%, #06b6d4 100%)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 0 16px rgba(16, 185, 129, 0.4)',
          }}>
            <Globe2 size={22} color="#ffffff" />
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <span style={{ fontSize: '1.25rem', fontWeight: '800', letterSpacing: '-0.02em', color: 'var(--text-main)', fontFamily: 'var(--font-display)' }}>
                GeoMeasure
              </span>
              <span className="badge badge-success" style={{ fontSize: '0.65rem', padding: '0.15rem 0.45rem' }}>
                v1.0
              </span>
            </div>
            <p style={{ fontSize: '0.72rem', color: 'var(--text-muted)', margin: 0, lineHeight: 1 }}>
              Spatial Analytics & Measurement Platform
            </p>
          </div>
        </Link>

        {/* Center Nav Links */}
        <nav style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          {navLinks.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.to;
            return (
              <Link
                key={item.to}
                to={item.to}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.45rem',
                  padding: '0.55rem 0.95rem',
                  borderRadius: 'var(--radius-md)',
                  fontSize: '0.875rem',
                  fontWeight: '600',
                  color: isActive ? 'var(--text-main)' : 'var(--text-muted)',
                  background: isActive ? 'var(--border-subtle)' : 'transparent',
                  transition: 'all 0.2s ease',
                  border: isActive ? '1px solid var(--border-medium)' : '1px solid transparent',
                }}
              >
                <Icon size={16} color={isActive ? 'var(--accent-emerald)' : 'currentColor'} />
                {item.label}
              </Link>
            );
          })}
          <a
            href="http://localhost:8000/docs"
            target="_blank"
            rel="noreferrer"
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.45rem',
              padding: '0.55rem 0.95rem',
              borderRadius: 'var(--radius-md)',
              fontSize: '0.875rem',
              fontWeight: '600',
              color: 'var(--text-muted)',
              transition: 'all 0.2s ease',
            }}
          >
            <FileText size={16} />
            API Docs
          </a>
        </nav>

        {/* Right Controls: Health & Theme Toggle */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          {/* Health indicator */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.4rem',
            padding: '0.35rem 0.75rem',
            borderRadius: '9999px',
            background: 'var(--bg-card)',
            border: '1px solid var(--border-subtle)',
            fontSize: '0.78rem',
            color: 'var(--text-muted)',
          }}>
            <span style={{
              width: '8px',
              height: '8px',
              borderRadius: '50%',
              background: healthy === true ? 'var(--accent-emerald)' : healthy === false ? 'var(--accent-rose)' : 'var(--accent-amber)',
              boxShadow: healthy === true ? '0 0 8px var(--accent-emerald)' : 'none',
            }} />
            <span>{healthy ? 'API Connected' : 'Checking API...'}</span>
          </div>

          {/* Theme switcher */}
          <button
            onClick={toggleTheme}
            className="btn btn-ghost"
            title={`Switch to ${theme === 'dark' ? 'Light' : 'Dark'} mode`}
            style={{ padding: '0.55rem', borderRadius: '50%' }}
          >
            {theme === 'dark' ? <Sun size={18} color="var(--accent-amber)" /> : <Moon size={18} color="var(--accent-indigo)" />}
          </button>
        </div>
      </div>
    </header>
  );
};

export default Navbar;
