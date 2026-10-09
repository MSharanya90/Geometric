import React from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  FileCode, 
  Archive, 
  ShieldCheck, 
  Sparkles, 
  Check, 
  AlertCircle 
} from 'lucide-react';
import FileUpload from '../components/FileUpload';

export const UploadPage = () => {
  const navigate = useNavigate();

  const handleSuccess = (fileRecord) => {
    navigate(`/files/${fileRecord.id}`);
  };

  return (
    <div className="animate-fade-in" style={{ maxWidth: '960px', margin: '0 auto' }}>
      <div style={{ textAlign: 'center', marginBottom: '2.5rem' }}>
        <h1 style={{ fontSize: '2.4rem', fontWeight: '800', marginBottom: '0.5rem', letterSpacing: '-0.02em' }}>
          Upload Geospatial Dataset
        </h1>
        <p style={{ fontSize: '1rem', color: 'var(--text-muted)', maxWidth: '600px', margin: '0 auto', lineHeight: 1.5 }}>
          Upload your KML or zipped Shapefile to inspect feature geometries, auto-project into UTM metric zones, and measure areas and lengths.
        </p>
      </div>

      {/* Main Upload Dropzone */}
      <div style={{ marginBottom: '2.5rem' }}>
        <FileUpload onUploadSuccess={handleSuccess} />
      </div>

      {/* Format Guidelines & Security Information */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.5rem' }}>
        <div className="card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginBottom: '0.85rem' }}>
            <FileCode size={20} color="var(--accent-cyan)" />
            <h3 style={{ fontSize: '1rem', fontWeight: '700' }}>OGC KML (.kml)</h3>
          </div>
          <ul style={{ listStyle: 'none', fontSize: '0.85rem', color: 'var(--text-muted)', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            <li style={{ display: 'flex', alignItems: 'flex-start', gap: '0.5rem' }}>
              <Check size={16} color="var(--accent-emerald)" style={{ flexShrink: 0, marginTop: '2px' }} />
              <span>Standard KML 2.0 / 2.2 schemas supported</span>
            </li>
            <li style={{ display: 'flex', alignItems: 'flex-start', gap: '0.5rem' }}>
              <Check size={16} color="var(--accent-emerald)" style={{ flexShrink: 0, marginTop: '2px' }} />
              <span>Placemarks with Polygon, LineString, and Point</span>
            </li>
            <li style={{ display: 'flex', alignItems: 'flex-start', gap: '0.5rem' }}>
              <Check size={16} color="var(--accent-emerald)" style={{ flexShrink: 0, marginTop: '2px' }} />
              <span>ExtendedData attributes extracted automatically</span>
            </li>
          </ul>
        </div>

        <div className="card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginBottom: '0.85rem' }}>
            <Archive size={20} color="var(--accent-amber)" />
            <h3 style={{ fontSize: '1rem', fontWeight: '700' }}>Shapefile Archive (.zip)</h3>
          </div>
          <ul style={{ listStyle: 'none', fontSize: '0.85rem', color: 'var(--text-muted)', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            <li style={{ display: 'flex', alignItems: 'flex-start', gap: '0.5rem' }}>
              <Check size={16} color="var(--accent-emerald)" style={{ flexShrink: 0, marginTop: '2px' }} />
              <span>Must contain <strong>.shp</strong> (geometry) & <strong>.dbf</strong> (attributes)</span>
            </li>
            <li style={{ display: 'flex', alignItems: 'flex-start', gap: '0.5rem' }}>
              <Check size={16} color="var(--accent-emerald)" style={{ flexShrink: 0, marginTop: '2px' }} />
              <span><strong>.prj</strong> coordinate file parsed for source CRS</span>
            </li>
            <li style={{ display: 'flex', alignItems: 'flex-start', gap: '0.5rem' }}>
              <Check size={16} color="var(--accent-emerald)" style={{ flexShrink: 0, marginTop: '2px' }} />
              <span>Companion files (.shx index) handled safely</span>
            </li>
          </ul>
        </div>
      </div>

      <div className="card" style={{ marginTop: '1.5rem', background: 'rgba(6, 182, 212, 0.06)', borderColor: 'rgba(6, 182, 212, 0.2)' }}>
        <div style={{ display: 'flex', alignItems: 'flex-start', gap: '0.85rem' }}>
          <ShieldCheck size={24} color="var(--accent-cyan)" style={{ flexShrink: 0, marginTop: '2px' }} />
          <div>
            <h4 style={{ fontSize: '0.95rem', fontWeight: '700', marginBottom: '0.25rem', color: 'var(--text-main)' }}>
              Security & Defense-in-Depth Architecture
            </h4>
            <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', lineHeight: 1.5 }}>
              All uploads undergo rigorous security screening: strict file size ceilings, MIME/extension verification, Zip-Slip path traversal prevention, and compression bomb ratios checking before temporary files are isolated and processed.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default UploadPage;
