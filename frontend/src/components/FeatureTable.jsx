import React, { useState } from 'react';
import { 
  Search, 
  Filter, 
  ArrowUpDown, 
  CheckCircle, 
  AlertTriangle, 
  Info, 
  ChevronLeft, 
  ChevronRight,
  Sparkles
} from 'lucide-react';
import { formatNumber } from '../utils/formatters';

export const FeatureTable = ({
  measurements = [],
  total = 0,
  page = 1,
  pageSize = 50,
  onPageChange,
  geometryFilter,
  onFilterChange,
  sortBy,
  order,
  onSortChange,
  onFeatureClick,
}) => {
  const [searchTerm, setSearchTerm] = useState('');

  // Local filter for search term
  const filteredItems = measurements.filter((m) => {
    if (!searchTerm) return true;
    const term = searchTerm.toLowerCase();
    const idMatch = String(m.feature_id || m.feature_index).includes(term);
    const typeMatch = (m.geometry_type || '').toLowerCase().includes(term);
    return idMatch || typeMatch;
  });

  const totalPages = Math.ceil(total / pageSize) || 1;

  const renderMeasurement = (m) => {
    if (m.area) {
      return (
        <div>
          <div style={{ fontWeight: '600', color: 'var(--accent-emerald)' }}>
            {formatNumber(m.area.area_m2)} m²
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
            {m.area.area_ha} ha &bull; {m.area.area_acres} acres
          </div>
        </div>
      );
    }

    if (m.length) {
      return (
        <div>
          <div style={{ fontWeight: '600', color: 'var(--accent-cyan)' }}>
            {formatNumber(m.length.length_m)} m
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
            {m.length.length_km} km &bull; {m.length.length_miles} mi
          </div>
        </div>
      );
    }

    return (
      <span style={{ fontSize: '0.8rem', color: 'var(--text-subtle)', fontStyle: 'italic' }}>
        {m.reason || 'No calculation required'}
      </span>
    );
  };

  const renderStatus = (status, warnings) => {
    const hasWarnings = warnings && warnings.length > 0;
    if (status === 'SUCCESS' && !hasWarnings) {
      return (
        <span className="badge badge-success">
          <CheckCircle size={12} /> Valid
        </span>
      );
    }
    if (status === 'WARNING' || hasWarnings) {
      return (
        <span className="badge badge-warning" title={warnings?.join('; ')}>
          <AlertTriangle size={12} /> Repaired
        </span>
      );
    }
    if (status === 'SKIPPED') {
      return (
        <span className="badge badge-neutral">
          <Info size={12} /> Point
        </span>
      );
    }
    return (
      <span className="badge badge-danger">
        Failed
      </span>
    );
  };

  return (
    <div className="card">
      <div className="card-header" style={{ flexWrap: 'wrap', gap: '1rem' }}>
        <div className="card-title">
          <span>Feature Measurements Explorer</span>
          <span className="badge badge-neutral" style={{ fontSize: '0.75rem' }}>
            {total} Features
          </span>
        </div>

        {/* Filter & Search Bar */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flexWrap: 'wrap' }}>
          {/* Search Input */}
          <div style={{ position: 'relative', display: 'flex', alignItems: 'center' }}>
            <Search size={15} color="var(--text-muted)" style={{ position: 'absolute', left: '10px' }} />
            <input
              type="text"
              className="input-control"
              placeholder="Search index or type..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              style={{ paddingLeft: '32px', width: '180px' }}
            />
          </div>

          {/* Geometry Filter Buttons */}
          <div style={{ display: 'flex', gap: '0.35rem', background: 'var(--bg-surface)', padding: '3px', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)' }}>
            {['All', 'Polygon', 'LineString', 'Point'].map((type) => {
              const active = (type === 'All' && !geometryFilter) || geometryFilter === type;
              return (
                <button
                  key={type}
                  onClick={() => onFilterChange && onFilterChange(type === 'All' ? null : type)}
                  className="btn btn-ghost"
                  style={{
                    padding: '0.3rem 0.65rem',
                    fontSize: '0.78rem',
                    background: active ? 'var(--accent-emerald)' : 'transparent',
                    color: active ? '#ffffff' : 'var(--text-muted)',
                    borderRadius: 'var(--radius-sm)',
                  }}
                >
                  {type}
                </button>
              );
            })}
          </div>

          {/* Sort trigger */}
          <button
            onClick={() => {
              if (onSortChange) {
                const nextSort = sortBy === 'area' ? 'length' : sortBy === 'length' ? null : 'area';
                onSortChange(nextSort, order === 'asc' ? 'desc' : 'asc');
              }
            }}
            className="btn btn-secondary"
            style={{ fontSize: '0.8rem', padding: '0.5rem 0.8rem' }}
            title="Sort by measurement value"
          >
            <ArrowUpDown size={14} />
            <span>Sort: {sortBy || 'Default'} ({order})</span>
          </button>
        </div>
      </div>

      {/* Table */}
      <div className="table-container">
        <table className="data-table">
          <thead>
            <tr>
              <th style={{ width: '80px' }}>Index</th>
              <th>Geometry</th>
              <th>Measurements</th>
              <th>Quality Status</th>
              <th>Warnings & Topology Notes</th>
            </tr>
          </thead>
          <tbody>
            {filteredItems.length > 0 ? (
              filteredItems.map((item) => (
                <tr 
                  key={item.feature_id || item.feature_index}
                  onClick={() => onFeatureClick && onFeatureClick(item)}
                  style={{ cursor: onFeatureClick ? 'pointer' : 'default' }}
                >
                  <td style={{ fontFamily: 'var(--font-mono)', fontWeight: '600', color: 'var(--text-muted)' }}>
                    #{item.feature_index ?? item.feature_id}
                  </td>
                  <td>
                    <span style={{
                      fontWeight: '600',
                      color: item.geometry_type.toLowerCase().includes('poly') ? 'var(--accent-emerald)' : item.geometry_type.toLowerCase().includes('line') ? 'var(--accent-cyan)' : '#38bdf8'
                    }}>
                      {item.geometry_type}
                    </span>
                  </td>
                  <td>{renderMeasurement(item)}</td>
                  <td>{renderStatus(item.status, item.warnings)}</td>
                  <td style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                    {item.warnings && item.warnings.length > 0 ? (
                      <span style={{ color: 'var(--accent-amber)' }}>
                        {item.warnings.join(' • ')}
                      </span>
                    ) : (
                      <span style={{ color: 'var(--text-subtle)' }}>None</span>
                    )}
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan={5} style={{ textAlign: 'center', padding: '2.5rem', color: 'var(--text-muted)' }}>
                  No features match current search and filter criteria.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination Controls */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginTop: '1.25rem', fontSize: '0.85rem', color: 'var(--text-muted)' }}>
        <div>
          Showing page <strong>{page}</strong> of <strong>{totalPages}</strong> ({total} total features)
        </div>
        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <button
            onClick={() => onPageChange && onPageChange(page - 1)}
            disabled={page <= 1}
            className="btn btn-secondary"
            style={{ padding: '0.4rem 0.75rem', fontSize: '0.8rem', opacity: page <= 1 ? 0.5 : 1 }}
          >
            <ChevronLeft size={16} /> Previous
          </button>
          <button
            onClick={() => onPageChange && onPageChange(page + 1)}
            disabled={page >= totalPages}
            className="btn btn-secondary"
            style={{ padding: '0.4rem 0.75rem', fontSize: '0.8rem', opacity: page >= totalPages ? 0.5 : 1 }}
          >
            Next <ChevronRight size={16} />
          </button>
        </div>
      </div>
    </div>
  );
};

export default FeatureTable;
