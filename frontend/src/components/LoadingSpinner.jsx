import React from 'react';
import { Loader2 } from 'lucide-react';

export const LoadingSpinner = ({ message = 'Processing geospatial data...', size = 32 }) => {
  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '3rem 1rem',
      gap: '1rem',
      color: 'var(--text-muted)',
    }}>
      <Loader2 size={size} className="pulse-glow" style={{ animation: 'spin 1s linear infinite', color: 'var(--accent-emerald)' }} />
      <span style={{ fontSize: '0.9rem', fontWeight: '500' }}>{message}</span>
      <style>{`
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
};

export default LoadingSpinner;
