import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, Filter, SlidersHorizontal, RefreshCw } from 'lucide-react';
import api from '../services/api';
import FeatureTable from '../components/FeatureTable';
import LoadingSpinner from '../components/LoadingSpinner';

export const FeatureExplorer = () => {
  const { id } = useParams();
  const [file, setFile] = useState(null);
  const [measurements, setMeasurements] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(50);
  const [geometryFilter, setGeometryFilter] = useState(null);
  const [sortBy, setSortBy] = useState(null);
  const [order, setOrder] = useState('asc');
  const [minArea, setMinArea] = useState('');
  const [maxArea, setMaxArea] = useState('');
  const [loading, setLoading] = useState(true);

  const loadData = async () => {
    try {
      setLoading(true);
      const [fData, mData] = await Promise.all([
        api.getFile(id),
        api.getMeasurements(id, {
          page,
          page_size: pageSize,
          geometry_type: geometryFilter || undefined,
          sort_by: sortBy || undefined,
          order,
          min_area: minArea ? parseFloat(minArea) : undefined,
          max_area: maxArea ? parseFloat(maxArea) : undefined,
        }),
      ]);
      setFile(fData);
      setMeasurements(mData.results);
      setTotal(mData.total);
    } catch (err) {
      console.error('Error in feature explorer:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (id) loadData();
  }, [id, page, pageSize, geometryFilter, sortBy, order]);

  const handleApplyRangeFilters = (e) => {
    e.preventDefault();
    setPage(1);
    loadData();
  };

  return (
    <div className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* Top Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <Link to={`/files/${id}`} className="btn btn-ghost" style={{ padding: '0.3rem 0.5rem', marginBottom: '0.5rem' }}>
            <ArrowLeft size={16} />
            <span>Back to File Analysis</span>
          </Link>
          <h1 style={{ fontSize: '1.75rem', fontWeight: '800' }}>
            Feature Explorer — {file?.filename}
          </h1>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
            Detailed tabular inspector with numeric metric boundaries and geometry filtering.
          </p>
        </div>
      </div>

      {/* Advanced Filter Panel */}
      <div className="card" style={{ padding: '1rem 1.25rem' }}>
        <form onSubmit={handleApplyRangeFilters} style={{ display: 'flex', alignItems: 'center', gap: '1rem', flexWrap: 'wrap' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: 'var(--text-muted)', fontSize: '0.85rem', fontWeight: '600' }}>
            <SlidersHorizontal size={16} />
            <span>Area Filters (m²):</span>
          </div>

          <input
            type="number"
            className="input-control"
            placeholder="Min area..."
            value={minArea}
            onChange={(e) => setMinArea(e.target.value)}
            style={{ width: '130px' }}
          />

          <input
            type="number"
            className="input-control"
            placeholder="Max area..."
            value={maxArea}
            onChange={(e) => setMaxArea(e.target.value)}
            style={{ width: '130px' }}
          />

          <button type="submit" className="btn btn-secondary" style={{ fontSize: '0.85rem' }}>
            <Filter size={14} /> Apply Bounds
          </button>

          {(minArea || maxArea) && (
            <button
              type="button"
              onClick={() => { setMinArea(''); setMaxArea(''); setPage(1); }}
              className="btn btn-ghost"
              style={{ fontSize: '0.85rem' }}
            >
              Reset
            </button>
          )}
        </form>
      </div>

      {/* Main Table */}
      {loading ? (
        <LoadingSpinner message="Filtering features..." />
      ) : (
        <FeatureTable
          measurements={measurements}
          total={total}
          page={page}
          pageSize={pageSize}
          onPageChange={(p) => setPage(p)}
          geometryFilter={geometryFilter}
          onFilterChange={(f) => { setGeometryFilter(f); setPage(1); }}
          sortBy={sortBy}
          order={order}
          onSortChange={(s, o) => { setSortBy(s); setOrder(o); setPage(1); }}
        />
      )}
    </div>
  );
};

export default FeatureExplorer;
