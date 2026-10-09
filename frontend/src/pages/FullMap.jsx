import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, Layers, Info, CheckCircle2, AlertTriangle, Compass } from 'lucide-react';
import api from '../services/api';
import MapViewer from '../components/MapViewer';
import LoadingSpinner from '../components/LoadingSpinner';
import { formatNumber } from '../utils/formatters';

export const FullMap = () => {
  const { id } = useParams();
  const [file, setFile] = useState(null);
  const [geojson, setGeojson] = useState(null);
  const [selectedFeature, setSelectedFeature] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const [fData, gData] = await Promise.all([
          api.getFile(id),
          api.getGeoJSON(id),
        ]);
        setFile(fData);
        setGeojson(gData);
      } catch (err) {
        console.error('Error loading full map:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [id]);

  if (loading) {
    return <LoadingSpinner message="Loading full-screen map session..." />;
  }

  return (
    <div style={{ height: 'calc(100vh - 120px)', display: 'flex', flexDirection: 'column', position: 'relative' }}>
      {/* Top Floating Header */}
      <div style={{
        position: 'absolute',
        top: '16px',
        left: '16px',
        zIndex: 1000,
        background: 'var(--bg-glass-heavy)',
        backdropFilter: 'blur(16px)',
        border: '1px solid var(--border-medium)',
        borderRadius: 'var(--radius-md)',
        padding: '0.6rem 1rem',
        display: 'flex',
        alignItems: 'center',
        gap: '1rem',
        boxShadow: 'var(--shadow-lg)',
      }}>
        <Link to={`/files/${id}`} className="btn btn-ghost" style={{ padding: '0.3rem 0.5rem' }}>
          <ArrowLeft size={18} />
          <span>Back to Analysis</span>
        </Link>
        <div style={{ height: '18px', width: '1px', background: 'var(--border-subtle)' }} />
        <div>
          <strong style={{ fontSize: '0.95rem' }}>{file?.filename}</strong>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginLeft: '0.5rem' }}>
            ({file?.feature_count} Features &bull; {file?.measurement_crs})
          </span>
        </div>
      </div>

      {/* Selected Feature Drawer */}
      {selectedFeature && (
        <div style={{
          position: 'absolute',
          bottom: '24px',
          left: '16px',
          zIndex: 1000,
          background: 'var(--bg-glass-heavy)',
          backdropFilter: 'blur(16px)',
          border: '1px solid var(--border-bright)',
          borderRadius: 'var(--radius-lg)',
          padding: '1.25rem',
          maxWidth: '380px',
          boxShadow: 'var(--shadow-lg)',
          animation: 'fadeIn 0.2s ease-out',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.65rem' }}>
            <span style={{ fontWeight: '700', fontSize: '0.95rem' }}>
              Feature #{selectedFeature.properties?.feature_index ?? selectedFeature.id}
            </span>
            <span className="badge badge-info">
              {selectedFeature.geometry?.type}
            </span>
          </div>

          {selectedFeature.properties?.area_m2 && (
            <div style={{ padding: '0.65rem', background: 'rgba(16, 185, 129, 0.12)', borderRadius: 'var(--radius-sm)', marginBottom: '0.65rem' }}>
              <div style={{ fontSize: '0.75rem', color: 'var(--accent-emerald)', fontWeight: '700' }}>AREA</div>
              <div style={{ fontSize: '1.15rem', fontWeight: '800' }}>
                {formatNumber(selectedFeature.properties.area_m2)} m²
              </div>
              <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                {selectedFeature.properties.area_ha} ha &bull; {selectedFeature.properties.area_acres} acres
              </div>
            </div>
          )}

          {selectedFeature.properties?.length_m && (
            <div style={{ padding: '0.65rem', background: 'rgba(6, 182, 212, 0.12)', borderRadius: 'var(--radius-sm)', marginBottom: '0.65rem' }}>
              <div style={{ fontSize: '0.75rem', color: 'var(--accent-cyan)', fontWeight: '700' }}>LENGTH</div>
              <div style={{ fontSize: '1.15rem', fontWeight: '800' }}>
                {formatNumber(selectedFeature.properties.length_m)} m
              </div>
              <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                {selectedFeature.properties.length_km} km &bull; {selectedFeature.properties.length_miles} miles
              </div>
            </div>
          )}

          <button
            onClick={() => setSelectedFeature(null)}
            className="btn btn-secondary"
            style={{ width: '100%', fontSize: '0.8rem', padding: '0.4rem' }}
          >
            Close Inspector
          </button>
        </div>
      )}

      {/* Map Element */}
      <div style={{ flex: 1, width: '100%', height: '100%' }}>
        <MapViewer
          geojsonData={geojson}
          height="100%"
          onFeatureSelect={(feat) => setSelectedFeature(feat)}
        />
      </div>
    </div>
  );
};

export default FullMap;
