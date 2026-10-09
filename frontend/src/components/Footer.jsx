import React from 'react';
import { Compass, ShieldCheck, Terminal, Cpu } from 'lucide-react';

export const Footer = () => {
  return (
    <footer style={{
      borderTop: '1px solid var(--border-subtle)',
      background: 'var(--bg-surface)',
      padding: '2.5rem 1.5rem',
      marginTop: 'auto',
    }}>
      <div style={{
        maxWidth: '1440px',
        margin: '0 auto',
        display: 'flex',
        flexWrap: 'wrap',
        alignItems: 'center',
        justifyContent: 'space-between',
        gap: '1.5rem',
      }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.4rem' }}>
            <Compass size={18} color="var(--accent-emerald)" />
            <span style={{ fontWeight: '700', fontSize: '1rem', color: 'var(--text-main)', fontFamily: 'var(--font-display)' }}>
              GeoMeasure Platform
            </span>
          </div>
          <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', maxWidth: '420px', lineHeight: 1.4 }}>
            High-performance geospatial measurement engine powering automated KML and Shapefile topology validation, UTM projected CRS transformations, and polygon/line analytics.
          </p>
        </div>

        <div style={{ display: 'flex', gap: '2rem', fontSize: '0.82rem', color: 'var(--text-muted)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            <ShieldCheck size={16} color="var(--accent-cyan)" />
            <span>Zip-Slip & Path Traversal Protected</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            <Cpu size={16} color="var(--accent-indigo)" />
            <span>PyProj / UTM Auto-Projection</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            <Terminal size={16} color="var(--accent-amber)" />
            <span>FastAPI 3.12+ REST API</span>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
