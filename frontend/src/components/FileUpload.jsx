import React, { useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  UploadCloud, 
  FileCode, 
  Archive, 
  CheckCircle2, 
  AlertCircle, 
  Loader2, 
  ArrowRight 
} from 'lucide-react';
import api from '../services/api';
import { formatBytes } from '../utils/formatters';

export const FileUpload = ({ onUploadSuccess }) => {
  const [isDragging, setIsDragging] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [statusState, setStatusState] = useState('idle'); // idle, uploading, processing, success, error
  const [errorMessage, setErrorMessage] = useState('');
  const fileInputRef = useRef(null);
  const navigate = useNavigate();

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const validateAndSetFile = (file) => {
    setErrorMessage('');
    if (!file) return;

    const ext = file.name.split('.').pop().toLowerCase();
    if (ext !== 'kml' && ext !== 'zip') {
      setStatusState('error');
      setErrorMessage('Invalid file type. Only KML (.kml) and Shapefile ZIP (.zip) archives are supported.');
      return;
    }

    if (file.size > 50 * 1024 * 1024) {
      setStatusState('error');
      setErrorMessage('File exceeds the 50 MB upload limit.');
      return;
    }

    setSelectedFile(file);
    setStatusState('idle');
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      validateAndSetFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      validateAndSetFile(e.target.files[0]);
    }
  };

  const startUpload = async () => {
    if (!selectedFile) return;

    setStatusState('uploading');
    setUploadProgress(0);

    try {
      const res = await api.uploadFile(selectedFile, (progressEvent) => {
        if (progressEvent.total) {
          const percent = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          setUploadProgress(percent);
          if (percent >= 100) {
            setStatusState('processing');
          }
        }
      });

      setStatusState('success');
      if (onUploadSuccess) {
        onUploadSuccess(res.file);
      } else {
        setTimeout(() => {
          navigate(`/files/${res.file.id}`);
        }, 800);
      }
    } catch (err) {
      setStatusState('error');
      const apiErr = err.response?.data?.error;
      setErrorMessage(
        apiErr?.message || err.message || 'An unexpected error occurred while processing the geospatial file.'
      );
    }
  };

  return (
    <div className="card" style={{ maxWidth: '640px', margin: '0 auto', textAlign: 'center' }}>
      <div style={{ marginBottom: '1.5rem' }}>
        <h2 style={{ fontSize: '1.4rem', fontWeight: '700', marginBottom: '0.4rem' }}>
          Upload Geospatial Dataset
        </h2>
        <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
          Drop your OGC KML or Zipped Shapefile dataset for immediate UTM reprojection & measurement.
        </p>
      </div>

      {/* Drag & Drop Area */}
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        style={{
          border: `2px dashed ${isDragging ? 'var(--accent-emerald)' : 'var(--border-medium)'}`,
          background: isDragging ? 'rgba(16, 185, 129, 0.08)' : 'var(--bg-surface)',
          borderRadius: 'var(--radius-lg)',
          padding: '2.5rem 1.5rem',
          cursor: 'pointer',
          transition: 'all 0.2s ease',
          marginBottom: '1.5rem',
          position: 'relative',
        }}
      >
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileChange}
          accept=".kml,.zip"
          style={{ display: 'none' }}
        />

        <div style={{
          width: '56px',
          height: '56px',
          borderRadius: '16px',
          background: 'rgba(16, 185, 129, 0.15)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          margin: '0 auto 1rem',
          color: 'var(--accent-emerald)',
        }}>
          <UploadCloud size={28} />
        </div>

        <h3 style={{ fontSize: '1.05rem', fontWeight: '600', marginBottom: '0.25rem' }}>
          Drag and drop your file here, or <span style={{ color: 'var(--accent-emerald)' }}>browse</span>
        </h3>
        <p style={{ fontSize: '0.78rem', color: 'var(--text-subtle)' }}>
          Supported: <strong>.kml</strong>, <strong>.zip</strong> (containing .shp, .shx, .dbf, .prj) &bull; Max 50 MB
        </p>
      </div>

      {/* Selected File Card */}
      {selectedFile && (
        <div style={{
          background: 'var(--bg-surface)',
          border: '1px solid var(--border-medium)',
          borderRadius: 'var(--radius-md)',
          padding: '0.85rem 1.2rem',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          marginBottom: '1.5rem',
          textAlign: 'left',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            {selectedFile.name.endsWith('.kml') ? (
              <FileCode size={24} color="var(--accent-cyan)" />
            ) : (
              <Archive size={24} color="var(--accent-amber)" />
            )}
            <div>
              <div style={{ fontWeight: '600', fontSize: '0.9rem', color: 'var(--text-main)' }}>
                {selectedFile.name}
              </div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                {formatBytes(selectedFile.size)} &bull; {selectedFile.name.endsWith('.kml') ? 'OGC KML' : 'Zipped Shapefile'}
              </div>
            </div>
          </div>

          <button
            onClick={startUpload}
            disabled={statusState === 'uploading' || statusState === 'processing'}
            className="btn btn-primary"
            style={{ padding: '0.55rem 1.15rem' }}
          >
            {statusState === 'uploading' || statusState === 'processing' ? (
              <>
                <Loader2 size={16} className="pulse-glow" style={{ animation: 'spin 1s linear infinite' }} />
                <span>{statusState === 'uploading' ? `${uploadProgress}%` : 'Measuring...'}</span>
              </>
            ) : (
              <>
                <span>Analyze File</span>
                <ArrowRight size={16} />
              </>
            )}
          </button>
        </div>
      )}

      {/* Progress Bar */}
      {(statusState === 'uploading' || statusState === 'processing') && (
        <div style={{ marginBottom: '1.5rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.78rem', color: 'var(--text-muted)', marginBottom: '0.4rem' }}>
            <span>{statusState === 'uploading' ? 'Uploading file...' : 'Running topology checks & UTM projection...'}</span>
            <span>{uploadProgress}%</span>
          </div>
          <div style={{ width: '100%', height: '6px', background: 'var(--border-subtle)', borderRadius: '9999px', overflow: 'hidden' }}>
            <div style={{
              width: `${uploadProgress}%`,
              height: '100%',
              background: 'linear-gradient(90deg, var(--accent-emerald) 0%, var(--accent-cyan) 100%)',
              transition: 'width 0.2s ease',
            }} />
          </div>
        </div>
      )}

      {/* Status Messages */}
      {statusState === 'error' && (
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '0.5rem',
          padding: '0.75rem 1rem',
          borderRadius: 'var(--radius-md)',
          background: 'rgba(244, 63, 94, 0.12)',
          border: '1px solid rgba(244, 63, 94, 0.3)',
          color: 'var(--accent-rose)',
          fontSize: '0.85rem',
          textAlign: 'left',
        }}>
          <AlertCircle size={18} style={{ flexShrink: 0 }} />
          <span>{errorMessage}</span>
        </div>
      )}

      {statusState === 'success' && (
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '0.5rem',
          padding: '0.75rem 1rem',
          borderRadius: 'var(--radius-md)',
          background: 'rgba(16, 185, 129, 0.12)',
          border: '1px solid rgba(16, 185, 129, 0.3)',
          color: 'var(--accent-emerald)',
          fontSize: '0.85rem',
          textAlign: 'left',
        }}>
          <CheckCircle2 size={18} style={{ flexShrink: 0 }} />
          <span>Dataset processed successfully! Opening analysis dashboard...</span>
        </div>
      )}
    </div>
  );
};

export default FileUpload;
