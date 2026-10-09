import React from 'react';

export const StatCard = ({
  title,
  value,
  subtitle,
  icon: Icon,
  accentColor = 'var(--accent-emerald)',
  accentBg = 'rgba(16, 185, 129, 0.12)',
  badgeText,
}) => {
  return (
    <div className="card" style={{ display: 'flex', flexDirection: 'column', position: 'relative', overflow: 'hidden' }}>
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: '0.85rem' }}>
        <span style={{ fontSize: '0.85rem', fontWeight: '600', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
          {title}
        </span>
        {Icon && (
          <div style={{
            width: '36px',
            height: '36px',
            borderRadius: '10px',
            background: accentBg,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: accentColor,
          }}>
            <Icon size={20} />
          </div>
        )}
      </div>

      <div style={{ display: 'flex', alignItems: 'baseline', gap: '0.5rem', marginBottom: '0.35rem' }}>
        <span style={{ fontSize: '1.85rem', fontWeight: '800', color: 'var(--text-main)', fontFamily: 'var(--font-display)', lineHeight: 1.1 }}>
          {value}
        </span>
        {badgeText && (
          <span className="badge badge-info" style={{ fontSize: '0.7rem' }}>
            {badgeText}
          </span>
        )}
      </div>

      {subtitle && (
        <span style={{ fontSize: '0.78rem', color: 'var(--text-subtle)', lineHeight: 1.3 }}>
          {subtitle}
        </span>
      )}

      {/* Subtle bottom border glow */}
      <div style={{
        position: 'absolute',
        bottom: 0,
        left: 0,
        right: 0,
        height: '2px',
        background: `linear-gradient(90deg, ${accentColor} 0%, transparent 100%)`,
        opacity: 0.6,
      }} />
    </div>
  );
};

export default StatCard;
