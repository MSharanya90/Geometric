import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { 
  Globe2, 
  UploadCloud, 
  Layers, 
  MapPin, 
  FileCheck2, 
  ExternalLink, 
  Trash2, 
  ArrowRight,
  ShieldAlert,
  Zap,
  Map,
  Download
} from 'lucide-react';
import api from '../services/api';
import { formatBytes, formatDate } from '../utils/formatters';
import LoadingSpinner from '../components/LoadingSpinner';
import Toast from '../components/Toast';

export const Dashboard = () => {
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [toast, setToast] = useState(null);

  const loadFiles = async () => {
    try {
      setLoading(true);
      const data = await api.listFiles(20, 0);
      setFiles(data);
    } catch (err) {
      setToast({ message: 'Failed to load datasets: ' + err.message, type: 'error' });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadFiles();
  }, []);

  const handleDelete = async (fileId, e) => {
    e.stopPropagation();
    if (!window.confirm('Are you sure you want to delete this dataset?')) return;
    try {
      await api.deleteFile(fileId);
      setFiles((prev) => prev.filter((f) => f.id !== fileId));
      setToast({ message: 'Dataset deleted successfully.', type: 'success' });
    } catch (err) {
      setToast({ message: 'Delete failed: ' + err.message, type: 'error' });
    }
  };

  return (
    <div className="animate-fade-in">
      {toast && <Toast {...toast} onClose={() => setToast(null)} />}

      {/* Hero Section */}
      <div style={{
        background: 'linear-gradient(135deg, rgba(16, 185, 129, 0.12) 0%, rgba(6, 182, 212, 0.12) 50%, rgba(99, 102, 241, 0.08) 100%)',
        border: '1px solid var(--border-medium)',
        borderRadius: 'var(--radius-xl)',
        padding: '3rem 2rem',
        marginBottom: '2.5rem',
        position: 'relative',
        overflow: 'hidden',
      }}>
        <div style={{ maxWidth: '720px' }}>
          <div style={{ display: 'inline-flex', alignItems: 'center', gap: '0.5rem', padding: '0.3rem 0.8rem', borderRadius: '9999px', background: 'rgba(16, 185, 129, 0.18)', border: '1px solid rgba(16, 185, 129, 0.35)', color: 'var(--accent-emerald)', fontSize: '0.8rem', fontWeight: '700', marginBottom: '1.25rem' }}>
            <Zap size={14} /> Production Geospatial Measurement Engine
          </div>
          <h1 style={{ fontSize: '2.75rem', fontWeight: '800', lineHeight: 1.15, marginBottom: '1rem', letterSpacing: '-0.03em' }}>
            Accurate Geospatial Measurements & Topology Analysis
          </h1>
          <p style={{ fontSize: '1.05rem', color: 'var(--text-muted)', marginBottom: '1.75rem', lineHeight: 1.6 }}>
            Upload KML surveys or Shapefile packages. GeoMeasure automatically validates geometry topologies, projects coordinates to optimal UTM metric zones, and computes canonical polygon areas and line lengths.
          </p>
          <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
            <Link to="/upload" className="btn btn-primary" style={{ padding: '0.75rem 1.5rem', fontSize: '1rem' }}>
              <UploadCloud size={18} />
              <span>Upload New Dataset</span>
            </Link>
            <a href="http://localhost:8000/docs" target="_blank" rel="noreferrer" className="btn btn-secondary" style={{ padding: '0.75rem 1.5rem', fontSize: '1rem' }}>
              <ExternalLink size={18} />
              <span>Interactive OpenAPI Docs</span>
            </a>
          </div>
        </div>
      </div>

      {/* Feature Highlights Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '1.25rem', marginBottom: '2.5rem' }}>
        <div className="card">
          <div style={{ width: '40px', height: '40px', borderRadius: '10px', background: 'rgba(16, 185, 129, 0.15)', color: 'var(--accent-emerald)', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '1rem' }}>
            <FileCheck2 size={22} />
          </div>
          <h3 style={{ fontSize: '1.1rem', fontWeight: '700', marginBottom: '0.4rem' }}>Dual-Format Pipeline</h3>
          <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', lineHeight: 1.5 }}>
            Native parsing for OGC KML 2.2 and zipped ESRI Shapefiles (.shp, .shx, .dbf, .prj) with Zip-Slip path traversal defense.
          </p>
        </div>

        <div className="card">
          <div style={{ width: '40px', height: '40px', borderRadius: '10px', background: 'rgba(6, 182, 212, 0.15)', color: 'var(--accent-cyan)', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '1rem' }}>
            <Globe2 size={22} />
          </div>
          <h3 style={{ fontSize: '1.1rem', fontWeight: '700', marginBottom: '0.4rem' }}>UTM Auto-Projection</h3>
          <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', lineHeight: 1.5 }}>
            Automatically selects the optimal local UTM projected coordinate system (meters) based on centroid coordinates before measuring.
          </p>
        </div>

        <div className="card">
          <div style={{ width: '40px', height: '40px', borderRadius: '10px', background: 'rgba(245, 158, 11, 0.15)', color: 'var(--accent-amber)', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '1rem' }}>
            <ShieldAlert size={22} />
          </div>
          <h3 style={{ fontSize: '1.1rem', fontWeight: '700', marginBottom: '0.4rem' }}>Geometry Repair</h3>
          <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', lineHeight: 1.5 }}>
            Automatically detects and repairs unclosed rings, redundant vertices, and self-intersections without halting dataset processing.
          </p>
        </div>

        <div className="card">
          <div style={{ width: '40px', height: '40px', borderRadius: '10px', background: 'rgba(99, 102, 241, 0.15)', color: 'var(--accent-indigo)', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '1rem' }}>
            <Download size={22} />
          </div>
          <h3 style={{ fontSize: '1.1rem', fontWeight: '700', marginBottom: '0.4rem' }}>Multi-Format Export</h3>
          <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', lineHeight: 1.5 }}>
            Download complete analytics as standardized GeoJSON FeatureCollection, structured JSON, or CSV measurement reports.
          </p>
        </div>
      </div>

      {/* Datasets Table */}
      <div className="card">
        <div className="card-header">
          <div className="card-title">
            <Layers size={20} color="var(--accent-emerald)" />
            <span>Uploaded Geospatial Datasets</span>
            <span className="badge badge-neutral">{files.length} Datasets</span>
          </div>
          <Link to="/upload" className="btn btn-secondary" style={{ fontSize: '0.85rem' }}>
            <UploadCloud size={16} />
            <span>Upload New</span>
          </Link>
        </div>

        {loading ? (
          <LoadingSpinner message="Loading dataset catalog..." />
        ) : files.length > 0 ? (
          <div className="table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Filename</th>
                  <th>Format</th>
                  <th>Features</th>
                  <th>Source CRS</th>
                  <th>Measurement CRS</th>
                  <th>Status</th>
                  <th>Processing Time</th>
                  <th>Uploaded</th>
                  <th style={{ textAlign: 'right' }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {files.map((file) => (
                  <tr key={file.id}>
                    <td>
                      <Link 
                        to={`/files/${file.id}`}
                        style={{ fontWeight: '600', color: 'var(--text-main)', display: 'flex', alignItems: 'center', gap: '0.4rem' }}
                      >
                        <span>{file.filename}</span>
                        <ArrowRight size={14} color="var(--accent-emerald)" />
                      </Link>
                      <div style={{ fontSize: '0.75rem', color: 'var(--text-subtle)' }}>
                        {formatBytes(file.file_size)} &bull; ID: {file.id}
                      </div>
                    </td>
                    <td>
                      <span className={`badge ${file.file_type === 'KML' ? 'badge-info' : 'badge-warning'}`}>
                        {file.file_type}
                      </span>
                    </td>
                    <td style={{ fontWeight: '600' }}>{file.feature_count}</td>
                    <td style={{ fontFamily: 'var(--font-mono)', fontSize: '0.8rem' }}>{file.crs}</td>
                    <td style={{ fontFamily: 'var(--font-mono)', fontSize: '0.8rem', color: 'var(--accent-emerald)' }}>
                      {file.measurement_crs || 'Auto'}
                    </td>
                    <td>
                      <span className={`badge ${file.status === 'COMPLETED' ? 'badge-success' : file.status === 'PROCESSING' ? 'badge-warning' : 'badge-danger'}`}>
                        {file.status}
                      </span>
                    </td>
                    <td style={{ fontFamily: 'var(--font-mono)', fontSize: '0.8rem' }}>
                      {file.processing_time_ms ? `${file.processing_time_ms} ms` : '—'}
                    </td>
                    <td style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                      {formatDate(file.created_at)}
                    </td>
                    <td style={{ textAlign: 'right' }}>
                      <div style={{ display: 'inline-flex', gap: '0.4rem' }}>
                        <Link 
                          to={`/files/${file.id}`} 
                          className="btn btn-secondary" 
                          style={{ padding: '0.35rem 0.65rem', fontSize: '0.78rem' }}
                          title="Open analysis dashboard"
                        >
                          Analyze
                        </Link>
                        <Link 
                          to={`/files/${file.id}/map`} 
                          className="btn btn-secondary" 
                          style={{ padding: '0.35rem 0.65rem', fontSize: '0.78rem' }}
                          title="Open fullscreen map"
                        >
                          <Map size={14} />
                        </Link>
                        <button
                          onClick={(e) => handleDelete(file.id, e)}
                          className="btn btn-danger"
                          style={{ padding: '0.35rem 0.65rem', fontSize: '0.78rem' }}
                          title="Delete dataset"
                        >
                          <Trash2 size={14} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div style={{ textAlign: 'center', padding: '3.5rem 1.5rem', color: 'var(--text-muted)' }}>
            <div style={{ width: '56px', height: '56px', borderRadius: '16px', background: 'var(--bg-surface)', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 1rem', color: 'var(--text-subtle)' }}>
              <Layers size={28} />
            </div>
            <h3 style={{ fontSize: '1.1rem', fontWeight: '600', marginBottom: '0.35rem', color: 'var(--text-main)' }}>
              No Datasets Uploaded Yet
            </h3>
            <p style={{ fontSize: '0.85rem', maxWidth: '400px', margin: '0 auto 1.5rem', lineHeight: 1.4 }}>
              Upload your first KML or Shapefile dataset or test with one of our sample datasets.
            </p>
            <Link to="/upload" className="btn btn-primary">
              <UploadCloud size={16} />
              <span>Upload Dataset Now</span>
            </Link>
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
