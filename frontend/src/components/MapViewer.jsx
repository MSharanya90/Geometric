import React, { useEffect, useRef, useState } from 'react';
import { 
  MapContainer, 
  TileLayer, 
  GeoJSON, 
  useMap 
} from 'react-leaflet';
import L from 'leaflet';
import { Layers, Eye, EyeOff, Maximize2 } from 'lucide-react';
import { useTheme } from '../context/ThemeContext';
import { formatNumber } from '../utils/formatters';

// Map Auto-Bounds Controller Component
const MapBoundsController = ({ geojsonData }) => {
  const map = useMap();

  useEffect(() => {
    if (!geojsonData || !geojsonData.features || geojsonData.features.length === 0) return;
    try {
      const geoLayer = L.geoJSON(geojsonData);
      const bounds = geoLayer.getBounds();
      if (bounds.isValid()) {
        map.fitBounds(bounds, { padding: [40, 40], maxZoom: 17 });
      }
    } catch (e) {
      console.warn('Could not auto-fit bounds:', e);
    }
  }, [geojsonData, map]);

  return null;
};

export const MapViewer = ({ geojsonData, height = '520px', onFeatureSelect }) => {
  const { theme } = useTheme();
  const [showPolygons, setShowPolygons] = useState(true);
  const [showLines, setShowLines] = useState(true);
  const [showPoints, setShowPoints] = useState(true);
  const [tileProvider, setTileProvider] = useState('dark');

  // Tile layer URL based on active theme
  const getTileUrl = () => {
    if (theme === 'light') {
      return 'https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png';
    }
    return 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png';
  };

  // Feature style styling function
  const styleFeature = (feature) => {
    const gType = (feature.geometry?.type || '').toLowerCase();

    if (gType.includes('polygon')) {
      const wasRepaired = feature.properties?.was_repaired;
      return {
        fillColor: wasRepaired ? '#f59e0b' : '#10b981',
        weight: 2,
        opacity: 0.9,
        color: wasRepaired ? '#f59e0b' : '#34d399',
        fillOpacity: 0.35,
      };
    }

    if (gType.includes('line')) {
      return {
        color: '#06b6d4',
        weight: 3.5,
        opacity: 0.85,
        dashArray: '4, 6',
      };
    }

    return {
      color: '#6366f1',
      weight: 2,
    };
  };

  // Filter features based on layer toggle
  const filterFeature = (feature) => {
    const gType = (feature.geometry?.type || '').toLowerCase();
    if (gType.includes('polygon') && !showPolygons) return false;
    if (gType.includes('line') && !showLines) return false;
    if (gType.includes('point') && !showPoints) return false;
    return true;
  };

  // Point to circle marker styling
  const pointToLayer = (feature, latlng) => {
    return L.circleMarker(latlng, {
      radius: 7,
      fillColor: '#38bdf8',
      color: '#ffffff',
      weight: 2,
      opacity: 1,
      fillOpacity: 0.9,
    });
  };

  // Bind interactive popup
  const onEachFeature = (feature, layer) => {
    const props = feature.properties || {};
    const gType = feature.geometry?.type || 'Geometry';

    let measurementHtml = '';
    if (props.area_m2 !== undefined && props.area_m2 !== null) {
      measurementHtml = `
        <div style="margin-top: 6px; padding: 6px 8px; background: rgba(16, 185, 129, 0.1); border-radius: 6px; border: 1px solid rgba(16, 185, 129, 0.25);">
          <strong style="color: #10b981; font-size: 11px; text-transform: uppercase;">Area Measurement:</strong>
          <div style="font-size: 13px; font-weight: 700; color: var(--text-main);">${formatNumber(props.area_m2, 2)} m²</div>
          <div style="font-size: 11px; color: var(--text-muted);">${props.area_ha || (props.area_m2 / 10000).toFixed(3)} ha &bull; ${props.area_acres || (props.area_m2 * 0.0002471).toFixed(3)} acres</div>
        </div>
      `;
    } else if (props.length_m !== undefined && props.length_m !== null) {
      measurementHtml = `
        <div style="margin-top: 6px; padding: 6px 8px; background: rgba(6, 182, 212, 0.1); border-radius: 6px; border: 1px solid rgba(6, 182, 212, 0.25);">
          <strong style="color: #06b6d4; font-size: 11px; text-transform: uppercase;">Length Measurement:</strong>
          <div style="font-size: 13px; font-weight: 700; color: var(--text-main);">${formatNumber(props.length_m, 2)} m</div>
          <div style="font-size: 11px; color: var(--text-muted);">${props.length_km || (props.length_m / 1000).toFixed(3)} km &bull; ${props.length_miles || (props.length_m * 0.0006213).toFixed(3)} miles</div>
        </div>
      `;
    } else if (gType.toLowerCase().includes('point')) {
      measurementHtml = `
        <div style="margin-top: 6px; font-size: 11px; color: var(--text-muted); font-style: italic;">
          Point coordinates (no area/length calculation required)
        </div>
      `;
    }

    const popupContent = `
      <div style="min-width: 200px; font-family: var(--font-body); padding: 4px;">
        <div style="display: flex; align-items: center; justify-content: space-between; gap: 8px; border-bottom: 1px solid var(--border-subtle); padding-bottom: 4px; margin-bottom: 6px;">
          <span style="font-size: 12px; font-weight: 700; color: var(--text-main);">Feature #${props.feature_index ?? props.feature_id ?? '1'}</span>
          <span style="font-size: 10px; font-weight: 600; padding: 2px 6px; border-radius: 4px; background: rgba(56, 189, 248, 0.15); color: #38bdf8;">${gType}</span>
        </div>
        ${props.name ? `<div style="font-size: 12px; font-weight: 600; color: var(--text-main); margin-bottom: 4px;">${props.name}</div>` : ''}
        ${props.description ? `<div style="font-size: 11px; color: var(--text-muted); margin-bottom: 4px;">${props.description}</div>` : ''}
        ${props.was_repaired ? `<div style="font-size: 11px; color: #f59e0b; margin-bottom: 4px;">&bull; Geometry was repaired</div>` : ''}
        ${measurementHtml}
      </div>
    `;

    layer.bindPopup(popupContent);

    layer.on({
      click: () => {
        if (onFeatureSelect) onFeatureSelect(feature);
      },
      mouseover: (e) => {
        const target = e.target;
        if (target.setStyle) {
          target.setStyle({ weight: 4, fillOpacity: 0.55 });
        }
      },
      mouseout: (e) => {
        const target = e.target;
        if (target.setStyle) {
          target.setStyle(styleFeature(feature));
        }
      },
    });
  };

  return (
    <div className="card" style={{ padding: 0, overflow: 'hidden', position: 'relative', height }}>
      {/* Layer Control Bar */}
      <div style={{
        position: 'absolute',
        top: '12px',
        right: '12px',
        zIndex: 500,
        background: 'var(--bg-glass-heavy)',
        backdropFilter: 'blur(12px)',
        border: '1px solid var(--border-medium)',
        borderRadius: 'var(--radius-md)',
        padding: '0.4rem 0.6rem',
        display: 'flex',
        alignItems: 'center',
        gap: '0.6rem',
        fontSize: '0.78rem',
        boxShadow: 'var(--shadow-md)',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.3rem', color: 'var(--text-muted)', fontWeight: '600' }}>
          <Layers size={14} />
          <span>Layers:</span>
        </div>

        <button
          onClick={() => setShowPolygons(!showPolygons)}
          className="btn btn-ghost"
          style={{
            padding: '0.2rem 0.5rem',
            fontSize: '0.75rem',
            background: showPolygons ? 'rgba(16, 185, 129, 0.2)' : 'transparent',
            color: showPolygons ? 'var(--accent-emerald)' : 'var(--text-muted)',
          }}
        >
          Polygons
        </button>

        <button
          onClick={() => setShowLines(!showLines)}
          className="btn btn-ghost"
          style={{
            padding: '0.2rem 0.5rem',
            fontSize: '0.75rem',
            background: showLines ? 'rgba(6, 182, 212, 0.2)' : 'transparent',
            color: showLines ? 'var(--accent-cyan)' : 'var(--text-muted)',
          }}
        >
          Lines
        </button>

        <button
          onClick={() => setShowPoints(!showPoints)}
          className="btn btn-ghost"
          style={{
            padding: '0.2rem 0.5rem',
            fontSize: '0.75rem',
            background: showPoints ? 'rgba(56, 189, 248, 0.2)' : 'transparent',
            color: showPoints ? '#38bdf8' : 'var(--text-muted)',
          }}
        >
          Points
        </button>
      </div>

      {/* Leaflet Map */}
      <MapContainer
        center={[20, 0]}
        zoom={2}
        scrollWheelZoom={true}
        style={{ width: '100%', height: '100%' }}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="https://carto.com/attributions">CARTO</a>'
          url={getTileUrl()}
        />

        {geojsonData && (
          <>
            <GeoJSON
              key={JSON.stringify(geojsonData) + showPolygons + showLines + showPoints + theme}
              data={geojsonData}
              style={styleFeature}
              filter={filterFeature}
              pointToLayer={pointToLayer}
              onEachFeature={onEachFeature}
            />
            <MapBoundsController geojsonData={geojsonData} />
          </>
        )}
      </MapContainer>
    </div>
  );
};

export default MapViewer;
