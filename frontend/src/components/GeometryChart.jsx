import React from 'react';
import {
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';
import { PieChart as PieIcon, BarChart3, TrendingUp } from 'lucide-react';
import { formatNumber } from '../utils/formatters';

const COLORS = ['#10b981', '#06b6d4', '#3b82f6', '#f59e0b', '#a855f7', '#f43f5e'];

export const GeometryCharts = ({ geometryTypes = {}, features = [] }) => {
  // 1. Prepare Donut Chart Data
  const pieData = Object.entries(geometryTypes).map(([type, count]) => ({
    name: type,
    value: count,
  }));

  // 2. Prepare Area Distribution Data (for Polygons)
  const polygonFeatures = features
    .filter((f) => f.geometry_type?.toLowerCase().includes('polygon') && f.area_m2)
    .slice(0, 8); // Top 8 features

  const areaData = polygonFeatures.map((f, idx) => ({
    name: f.properties?.name || `Poly #${f.feature_index ?? idx + 1}`,
    area_m2: Math.round(f.area_m2),
    area_ha: +(f.area_m2 / 10000).toFixed(2),
  }));

  // 3. Prepare Line Length Data (for LineStrings)
  const lineFeatures = features
    .filter((f) => f.geometry_type?.toLowerCase().includes('line') && f.length_m)
    .slice(0, 8);

  const lengthData = lineFeatures.map((f, idx) => ({
    name: f.properties?.name || `Line #${f.feature_index ?? idx + 1}`,
    length_m: Math.round(f.length_m),
    length_km: +(f.length_m / 1000).toFixed(2),
  }));

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      const data = payload[0];
      return (
        <div style={{
          background: 'var(--bg-surface)',
          border: '1px solid var(--border-medium)',
          borderRadius: 'var(--radius-sm)',
          padding: '0.5rem 0.75rem',
          fontSize: '0.8rem',
          boxShadow: 'var(--shadow-md)',
          color: 'var(--text-main)',
        }}>
          <div style={{ fontWeight: '700', marginBottom: '2px' }}>{label || data.name}</div>
          <div style={{ color: data.color || 'var(--accent-emerald)' }}>
            {data.name}: {formatNumber(data.value)}
          </div>
        </div>
      );
    }
    return null;
  };

  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.25rem', marginBottom: '1.5rem' }}>
      {/* Chart 1: Geometry Distribution */}
      <div className="card">
        <div className="card-header">
          <div className="card-title">
            <PieIcon size={18} color="var(--accent-emerald)" />
            <span>Geometry Distribution</span>
          </div>
        </div>
        <div style={{ height: '220px', width: '100%' }}>
          {pieData.length > 0 ? (
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  innerRadius={50}
                  outerRadius={75}
                  paddingAngle={4}
                  dataKey="value"
                >
                  {pieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip content={<CustomTooltip />} />
                <Legend
                  verticalAlign="bottom"
                  height={36}
                  formatter={(val) => <span style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>{val}</span>}
                />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
              No geometry data available
            </div>
          )}
        </div>
      </div>

      {/* Chart 2: Polygon Areas */}
      <div className="card">
        <div className="card-header">
          <div className="card-title">
            <BarChart3 size={18} color="var(--accent-cyan)" />
            <span>Polygon Areas (m²)</span>
          </div>
        </div>
        <div style={{ height: '220px', width: '100%' }}>
          {areaData.length > 0 ? (
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={areaData} margin={{ top: 10, right: 10, left: -10, bottom: 25 }}>
                <XAxis dataKey="name" tick={{ fill: 'var(--text-subtle)', fontSize: 10 }} interval={0} angle={-25} textAnchor="end" />
                <YAxis tick={{ fill: 'var(--text-subtle)', fontSize: 10 }} />
                <Tooltip content={<CustomTooltip />} />
                <Bar dataKey="area_m2" fill="#10b981" radius={[4, 4, 0, 0]} name="Area (m²)" />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
              No polygon measurements available
            </div>
          )}
        </div>
      </div>

      {/* Chart 3: Line Lengths */}
      <div className="card">
        <div className="card-header">
          <div className="card-title">
            <TrendingUp size={18} color="var(--accent-indigo)" />
            <span>Line Lengths (m)</span>
          </div>
        </div>
        <div style={{ height: '220px', width: '100%' }}>
          {lengthData.length > 0 ? (
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={lengthData} margin={{ top: 10, right: 10, left: -10, bottom: 25 }}>
                <XAxis dataKey="name" tick={{ fill: 'var(--text-subtle)', fontSize: 10 }} interval={0} angle={-25} textAnchor="end" />
                <YAxis tick={{ fill: 'var(--text-subtle)', fontSize: 10 }} />
                <Tooltip content={<CustomTooltip />} />
                <Bar dataKey="length_m" fill="#06b6d4" radius={[4, 4, 0, 0]} name="Length (m)" />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
              No line measurements available
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default GeometryCharts;
