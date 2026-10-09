import React, { useEffect } from 'react';
import { CheckCircle2, AlertTriangle, XCircle, Info, X } from 'lucide-react';

export const Toast = ({ message, type = 'info', onClose, duration = 4000 }) => {
  useEffect(() => {
    if (duration > 0 && onClose) {
      const timer = setTimeout(onClose, duration);
      return () => clearTimeout(timer);
    }
  }, [duration, onClose]);

  const config = {
    success: { icon: CheckCircle2, color: 'var(--accent-emerald)', border: 'rgba(16, 185, 129, 0.4)' },
    error: { icon: XCircle, color: 'var(--accent-rose)', border: 'rgba(244, 63, 94, 0.4)' },
    warning: { icon: AlertTriangle, color: 'var(--accent-amber)', border: 'rgba(245, 158, 11, 0.4)' },
    info: { icon: Info, color: 'var(--accent-cyan)', border: 'rgba(6, 182, 212, 0.4)' },
  }[type] || { icon: Info, color: 'var(--accent-cyan)', border: 'rgba(6, 182, 212, 0.4)' };

  const Icon = config.icon;

  return (
    <div style={{
      position: 'fixed',
      bottom: '1.5rem',
      right: '1.5rem',
      zIndex: 9999,
      display: 'flex',
      alignItems: 'center',
      gap: '0.75rem',
      padding: '0.85rem 1.25rem',
      background: 'var(--bg-surface)',
      border: `1px solid ${config.border}`,
      borderRadius: 'var(--radius-md)',
      boxShadow: 'var(--shadow-lg)',
      color: 'var(--text-main)',
      maxWidth: '420px',
      animation: 'slideUp 0.25s ease-out',
    }}>
      <Icon size={20} color={config.color} style={{ flexShrink: 0 }} />
      <span style={{ fontSize: '0.875rem', fontWeight: '500', lineHeight: 1.3 }}>{message}</span>
      {onClose && (
        <button
          onClick={onClose}
          style={{
            background: 'transparent',
            border: 'none',
            color: 'var(--text-muted)',
            cursor: 'pointer',
            padding: '2px',
            marginLeft: 'auto',
          }}
        >
          <X size={16} />
        </button>
      )}
      <style>{`
        @keyframes slideUp {
          from { opacity: 0; transform: translateY(12px); }
          to { opacity: 1; transform: translateY(0); }
        }
      `}</style>
    </div>
  );
};

export default Toast;
