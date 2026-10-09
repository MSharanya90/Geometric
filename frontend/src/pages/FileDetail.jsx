import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { 
  FileText, 
  Globe2, 
  Clock, 
  Layers, 
  MapPin, 
  Compass, 
  Download, 
  Maximize2, 
  CheckCircle2, 
  AlertTriangle, 
  Share2, 
  Trash2,
  FileSpreadsheet,
  FileJson,
  Map as MapIcon
} from 'lucide-react';
import api from '../services/api';
import { formatBytes, formatNumber, formatDate } from '../utils/formatters';
import StatCard from '../components/StatCard';
import MapViewer from '../components/MapViewer';
import GeometryCharts from '../components/GeometryChart';
import FeatureTable from '../components/FeatureTable';
import LoadingSpinner from '../components/LoadingSpinner';
import Toast from '../components/Toast';

export const FileDetail = () => {
  const { id } = useParams();
  const [file, setFile] = useState(null);
  const [summary, setSummary] = useState(null);
  const [geojson, setGeojson] = useState(null);
  const [measurements, setMeasurements] = useState([]);
  const [measTotal, setMeasTotal] = useState(0);
  const [measPage, setMeasPage] = useState(1);
  const [geometryFilter, setGeometryFilter] = useState(null);
  const [sortBy, setSortBy] = useState(null);
  const [sortOrder, setSortOrder] = useState('asc');
  const [loading, setLoading] = useState(true);
  const [toast, setToast] = useState(null);

  // Fetch initial file, summary, and geojson
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const [fileData, summaryData, geojsonData] = await Promise.all([
          api.getFile(id),
          api.getSummary(id),
          api.getGeoJSON(id),
        ]);
        setFile(fileData);
        setSummary(summaryData.summary);
        setGeojson(geojsonData);
      } catch (err) {
        setToast({ message: 'Error loading dataset: ' + err.message, type: 'error' });
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [id]);

  // Fetch paginated measurements when query parameters change
  const fetchMeasurements = async () => {
    try {
      const params = {
        page: measPage,
        page_size: 25,
      };
      if (geometryFilter) params.geometry_type = geometryFilter;
      if (sortBy) {
        params.sort_by = sortBy;
        params.order = sortOrder;
      }
      const data = await api.getMeasurements(id, params);
      setMeasurements(data.results);
      setMeasTotal(data.total);
    } catch (err) {
      console.error('Failed to fetch measurements:', err);
    }
  };

  useEffect(() => {
    if (id) fetchMeasurements();
  }, [id, measPage, geometryFilter, sortBy, sortOrder]);

  const handlePageChange = (newPage) => {
    setMeasPage(newPage);
  };

  const handleFilterChange = (newFilter) => {
    setGeometryFilter(newFilter);
    setMeasPage(1);
  };

  const handleSortChange = (newSort, newOrder) => {
    setSortBy(newSort);
    setSortOrder(newOrder);
    setMeasPage(1);
  };

  if (loading) {
    return <LoadingSpinner message="Calculating spatial geometries and rendering map..." />;
  }

  if (!file) {
    return (
      <div className="card" style={{ textAlign: 'center', padding: '3rem' }}>
        <h2>Dataset Not Found</h2>
        <p style={{ color: 'var(--text-muted)', marginBottom: '1.5rem' }}>
          The requested dataset ID does not exist or was deleted.
        </p>
        <Link to="/" className="btn btn-primary">Return to Dashboard</Link>
      </div>
    );
  }

  return (
    <div className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      {toast && <Toast {...toast} onClose={() => setToast(null)} />}

      {/* Top Banner: Dataset Overview & Export Action Bar */}
      <div className="card" style={{ background: 'var(--bg-glass-heavy)' }}>
        <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', justifyContent: 'space-between', gap: '1.25rem' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem', marginBottom: '0.35rem' }}>
              <h1 style={{ fontSize: '1.65rem', fontWeight: '800', letterSpacing: '-0.02em' }}>
                {file.filename}
              </h1>
              <span className={`badge ${file.file_type === 'KML' ? 'badge-info' : 'badge-warning'}`}>
                {file.file_type}
              </span>
              <span className="badge badge-success">
                {file.status}
              </span>
            </div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '1.25rem', fontSize: '0.82rem', color: 'var(--text-muted)' }}>
              <span>ID: <code style={{ color: 'var(--text-main)' }}>{file.id}</code></span>
              <span>Size: <strong>{formatBytes(file.file_size)}</strong></span>
              <span>Features: <strong>{file.feature_count}</strong></span>
              <span>Duration: <strong>{file.processing_time_ms} ms</strong></span>
              <span>Analyzed: <strong>{formatDate(file.created_at)}</strong></span>
            </div>
          </div>

          {/* Export Buttons */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', flexWrap: 'wrap' }}>
            <a
              href={api.getExportUrl(file.id, 'geojson')}
              download
              className="btn btn-secondary"
              style={{ fontSize: '0.82rem', padding: '0.55rem 0.95rem' }}
              title="Download GeoJSON FeatureCollection"
            >
              <MapIcon size={15} color="var(--accent-emerald)" />
              <span>GeoJSON</span>
            </a>
            <a
              href={api.getExportUrl(file.id, 'csv')}
              download
              className="btn btn-secondary"
              style={{ fontSize: '0.82rem', padding: '0.55rem 0.95rem' }}
              title="Download CSV measurement report"
            >
              <FileSpreadsheet size={15} color="var(--accent-cyan)" />
              <span>CSV Report</span>
            </a>
            <a
              href={api.getExportUrl(file.id, 'json')}
              download
              className="btn btn-secondary"
              style={{ fontSize: '0.82rem', padding: '0.55rem 0.95rem' }}
              title="Download structured JSON"
            >
              <FileJson size={15} color="var(--accent-indigo)" />
              <span>JSON</span>
            </a>
            <Link
              to={`/files/${file.id}/map`}
              className="btn btn-primary"
              style={{ fontSize: '0.82rem', padding: '0.55rem 0.95rem' }}
            >
              <Maximize2 size={15} />
              <span>Fullscreen Map</span>
            </Link>
          </div>
        </div>

        {/* CRS Strategy Callout */}
        <div style={{
          marginTop: '1.25rem',
          padding: '0.75rem 1rem',
          background: 'rgba(6, 182, 212, 0.08)',
          border: '1px solid rgba(6, 182, 212, 0.25)',
          borderRadius: 'var(--radius-md)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: '0.75rem',
          fontSize: '0.82rem',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Compass size={18} color="var(--accent-cyan)" />
            <span>
              <strong>CRS Transformation:</strong> Source <code style={{ color: 'var(--accent-cyan)' }}>{file.crs}</code> &rarr; Projected Measurement CRS <code style={{ color: 'var(--accent-emerald)' }}>{file.measurement_crs}</code>
            </span>
          </div>
          <div style={{ color: 'var(--text-muted)', fontStyle: 'italic' }}>
            {file.crs_strategy || 'Centroid UTM Zone Projection'}
          </div>
        </div>
      </div>

      {/* 4 Key Metric Cards */}
      {summary && (
        <div className="stats-grid">
          <StatCard
            title="Total Features"
            value={summary.total_features}
            subtitle={`${summary.number_of_polygons} Polygons • ${summary.number_of_lines} Lines • ${summary.number_of_points} Points`}
            icon={Layers}
            accentColor="var(--accent-emerald)"
            accentBg="rgba(16, 185, 129, 0.15)"
          />

          <StatCard
            title="Total Polygon Area"
            value={`${formatNumber(summary.total_polygon_area_m2)} m²`}
            subtitle={`${summary.total_polygon_area?.area_ha} ha • ${summary.total_polygon_area?.area_acres} acres • ${summary.total_polygon_area?.area_km2} km²`}
            icon={Globe2}
            accentColor="var(--accent-cyan)"
            accentBg="rgba(6, 182, 212, 0.15)"
          />

          <StatCard
            title="Total Line Length"
            value={`${formatNumber(summary.total_line_length_m)} m`}
            subtitle={`${summary.total_line_length?.length_km} km • ${summary.total_line_length?.length_miles} miles • ${summary.total_line_length?.length_feet} ft`}
            icon={Compass}
            accentColor="var(--accent-indigo)"
            accentBg="rgba(99, 102, 241, 0.15)"
          />

          <StatCard
            title="Quality & Repairs"
            value={`${summary.valid_geometry_count} Valid`}
            subtitle={`${summary.repaired_geometry_count} auto-repaired • ${summary.invalid_geometry_count} defective`}
            icon={summary.repaired_geometry_count > 0 ? AlertTriangle : CheckCircle2}
            accentColor={summary.repaired_geometry_count > 0 ? 'var(--accent-amber)' : 'var(--accent-emerald)'}
            accentBg={summary.repaired_geometry_count > 0 ? 'rgba(245, 158, 11, 0.15)' : 'rgba(16, 185, 129, 0.15)'}
          />
        </div>
      )}

      {/* Recharts Analytics Section */}
      <GeometryCharts
        geometryTypes={file.geometry_types}
        features={geojson?.features || []}
      />

      {/* Interactive Map */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <h2 style={{ fontSize: '1.25rem', fontWeight: '700' }}>Interactive Spatial Map</h2>
          <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
            Click any polygon, line, or point to inspect measured metrics and attributes
          </span>
        </div>
        <MapViewer geojsonData={geojson} height="540px" />
      </div>

      {/* Feature Measurement Table */}
      <FeatureTable
        measurements={measurements}
        total={measTotal}
        page={measPage}
        pageSize={25}
        onPageChange={handlePageChange}
        geometryFilter={geometryFilter}
        onFilterChange={handleFilterChange}
        sortBy={sortBy}
        order={sortOrder}
        onSortChange={handleSortChange}
      />
    </div>
  );
};

export default FileDetail;
