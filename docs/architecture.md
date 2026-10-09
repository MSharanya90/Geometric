# GeoMeasure — Architecture Documentation

This document describes the architectural topology, data flow pipelines, design patterns, and system components of **GeoMeasure (Geospatial File Measurement & Analysis Platform)**.

---

## 1. High-Level Architecture Overview

GeoMeasure is built using an asynchronous, layered service-oriented architecture designed to process spatial vector data safely, normalize spatial reference frames, compute geodesic metrics, and present interactive analytics.

```text
┌─────────────────────────────────────────────────────────────┐
│                       Client Layer                          │
│             React 19 + Vite + Leaflet Dashboard             │
└──────────────────────────────┬──────────────────────────────┘
                               │ HTTPS / JSON / Multi-Part
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                      FastAPI API Gateway                    │
│   CORS Middleware • Timing Middleware • Global Exception    │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                   Validation & Security Layer               │
│  MIME & Extension Checks • Path Traversal • Zip-Bomb Limits │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                   File Processing Service                   │
│   Format Detection • Isolation Sandbox • Pipeline Control   │
└──────────────┬──────────────────────────────┬───────────────┘
               │                              │
               ▼                              ▼
┌──────────────────────────────┐ ┌─────────────────────────────┐
│          KML Service         │ │      Shapefile Service      │
│  lxml OGC Parser • Entities  │ │  .shp/.shx/.dbf/.prj Engine │
└──────────────┬───────────────┘ └────────────┬────────────────┘
               └──────────────┬───────────────┘
                              │ Standardized Feature Dictionaries
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   Geometry Validation Service               │
│  Topology Check • Ring Closure • Vertex Deduplication       │
└──────────────────────────────┬──────────────────────────────┘
                               │ Repaired WGS84 Geometries
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                          CRS Service                        │
│   Source CRS Detection • Bbox Centroid • UTM Zone Selection │
│              Forward Transverse Mercator Reprojection        │
└──────────────────────────────┬──────────────────────────────┘
                               │ Metric Projected Coordinates (Meters)
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                      Measurement Engine                     │
│  Polygon Shoelace Area (m²) • Line Euclidean Length (m)     │
│        Unit Conversions (ha, km², acres, miles, feet)       │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                      Persistence Layer                      │
│        SQLAlchemy 2.0 • PostgreSQL + PostGIS (or SQLite)    │
│              FileRepository • FeatureRepository             │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. End-to-End Processing Flow

The core geospatial pipeline follows 10 discrete stages:

1. **Upload**: Client streams `.kml` or `.zip` via `POST /api/v1/files/`.
2. **Metadata Validation**: The server enforces file size thresholds (default 50MB) and whitelisted extensions.
3. **Secure Extraction**:
   - For `.zip`, safe traversal checks prevent Zip-Slip vulnerabilities.
   - Compression ratios are monitored against zip-bomb thresholds.
4. **Format Detection & Feature Extraction**:
   - KML placemarks are parsed with entity expansion disabled.
   - Shapefiles extract geometries from `.shp` and attributes from `.dbf`.
5. **Topological Validation & Repair**:
   - Features undergo geometry validation.
   - Unclosed rings are closed; consecutive duplicate vertices are removed.
   - Self-intersections are cleaned via `make_valid()` when available.
6. **Centroid & Measurement CRS Determination**:
   - Dataset bounding box is computed across all valid features.
   - Longitude and latitude centroids determine the optimal Universal Transverse Mercator (UTM) zone.
7. **Coordinate Transformation**:
   - Features are projected from geographic degrees (EPSG:4326) into projected meters (e.g. EPSG:32610).
8. **Measurement Calculation**:
   - Polygons are measured for area in square meters.
   - LineStrings are measured for length in meters.
   - Points are marked with `measurement_available: false`.
9. **Persistence**:
   - File metadata and all features are persisted in relational tables.
10. **GeoJSON & Summary Output**:
    - Returns structured responses and enables interactive Leaflet rendering.

---

## 3. Advanced CRS Strategy

Calculating area or distance directly on latitude/longitude degree coordinates (`EPSG:4326`) is mathematically flawed because degree spacing converges towards the poles:

$$\Delta x = R \cdot \cos(\phi) \cdot \Delta \lambda$$

GeoMeasure enforces a **strict projection-before-measurement protocol**:
1. Centroid Longitude $\lambda_c$ is determined from the dataset bounding box.
2. The optimal UTM Zone is computed:
   $$\text{Zone} = \lfloor \frac{\lambda_c + 180}{6} \rfloor + 1$$
3. Hemispheric EPSG code is assigned:
   - Northern Hemisphere ($\phi \ge 0$): $\text{EPSG:32600} + \text{Zone}$
   - Southern Hemisphere ($\phi < 0$): $\text{EPSG:32700} + \text{Zone}$
4. If a dataset spans more than $60^\circ$ of longitude (continental/global span), the service automatically selects `EPSG:6933` (Equal Earth) or a global cylindrical equal-area projection and records the limitation in `crs_strategy`.

---

## 4. Feature-Level Fault Isolation

In production environments, a corrupted feature in an enterprise dataset should not abort processing for the remaining thousands of features. GeoMeasure implements **feature-level fault isolation**:
- Each feature maintains its own status (`SUCCESS`, `WARNING`, `FAILED`).
- Non-fatal topological anomalies trigger automatic repair and record clear diagnostic warnings (e.g., `["Unclosed polygon ring was automatically closed."]`).
- Corrupt features have their error noted without failing the global dataset transaction.

---

## 5. Security & Defense-in-Depth

- **Filename Sanitization**: Original user filenames are stripped of path delimiters and special characters; random alphanumeric UUIDs are generated for filesystem paths.
- **Path Traversal (Zip-Slip) Defense**: All archive member destinations are verified to remain strictly within the sandboxed extraction target directory.
- **Zip Bomb Mitigations**: Maximum uncompressed expansion ratio (100x), entry count limits (200), and cumulative uncompressed volume ceilings (250MB) are strictly enforced.
- **Safe XML Parsing**: KML parsing disables external network access and entity resolution to mitigate XXE (XML External Entity) attacks.
- **Safe Temporary Storage**: Extraction folders are created in isolated temporary paths and cleaned up via `finally` blocks.
