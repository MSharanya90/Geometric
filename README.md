# GeoMeasure — Geospatial File Measurement & Analysis Platform

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg?style=flat&logo=fastapi)](https://fastapi.tiangolo.com)
[![React 19](https://img.shields.io/badge/React-19.2+-61DAFB.svg?style=flat&logo=react)](https://react.dev)
[![Vite](https://img.shields.io/badge/Vite-8.3+-646CFF.svg?style=flat&logo=vite)](https://vitejs.dev)
[![Python](https://img.shields.io/badge/Python-3.12+-3776AB.svg?style=flat&logo=python)](https://www.python.org)
[![Leaflet](https://img.shields.io/badge/Leaflet-1.9+-199900.svg?style=flat&logo=leaflet)](https://leafletjs.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**GeoMeasure** is a full-stack geospatial file processing, inspection, and measurement platform. It enables engineers, GIS specialists, and researchers to securely upload KML (`.kml`) and Shapefile (`.zip`) datasets, inspect topological validity, reproject coordinates into optimal local UTM metric projections, calculate accurate geodesic and planar measurements, and explore data through an interactive dashboard with Leaflet map visualization.

---

## 🌟 Key Features

- **Multi-Format Ingestion**:
  - **KML / KMZ**: OGC KML 2.0 / 2.2 Placemark extraction with support for Polygons, LineStrings, Points, and ExtendedData.
  - **ESRI Shapefiles**: Zipped archives containing `.shp`, `.shx`, `.dbf`, and `.prj` components.
- **Topological Inspection & Auto-Repair**:
  - Automatic detection and closing of unclosed polygon rings.
  - Consecutive duplicate vertex deduplication.
  - Diagnostic warnings per feature (`SUCCESS`, `WARNING`, `FAILED`).
- **Optimal UTM Reprojection**:
  - Calculates dataset centroid longitude to select the optimal Universal Transverse Mercator (UTM) zone (e.g. `EPSG:32610` for California, `EPSG:32618` for New York).
  - Handles wide-span datasets via Equal Earth (`EPSG:6933`) strategy.
- **Accurate Metric Calculations**:
  - **Polygons**: Planar shoelace area with unit conversions ($m^2$, hectares, $km^2$, acres).
  - **LineStrings**: Segment Euclidean length ($m$, $km$, miles, feet).
  - **Points**: Geodetic coordinate inspection.
- **Interactive Dashboard**:
  - Summary metrics, geometry distribution breakdown, and data quality overview.
  - Interactive Leaflet map with colored layers, popup inspection, and basemap switcher.
  - Feature Explorer with sorting, filtering by geometry type, and area/length range bounds.
  - Multi-format data export in **GeoJSON**, **CSV**, and **JSON**.
- **Enterprise-Grade Security**:
  - Zip-Slip path traversal defense during archive extraction.
  - Zip-bomb threshold mitigations (entry count, volume ceiling, compression ratio).
  - XXE-safe XML/KML parser with disabled entity resolution and external network calls.

---

## 🏗️ Architecture

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

## 📁 Repository Structure

```text
GeoMetric/
├── backend/
│   ├── app/
│   │   ├── api/v1/endpoints/  # API endpoints (files, measurements, export, health)
│   │   ├── core/              # Config, exceptions, logging
│   │   ├── db/                # SQLAlchemy session & Base
│   │   ├── models/            # UploadedFile, Feature models
│   │   ├── repositories/      # FileRepository, FeatureRepository
│   │   ├── schemas/           # Pydantic schemas
│   │   ├── services/          # KML, Shapefile, CRS, Geometry, Measurement
│   │   └── utils/             # Geodesic math, security utilities
│   ├── tests/                 # Comprehensive test suite (31 tests)
│   ├── requirements.txt       # Python dependencies
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/        # MapViewer, FileUpload, FeatureTable, etc.
│   │   ├── pages/             # Dashboard, FileDetail, FullMap, FeatureExplorer
│   │   ├── services/          # Axios API service
│   │   └── context/           # Dark / Light theme context
│   ├── package.json
│   ├── vite.config.js
│   └── Dockerfile
├── sample_data/               # Realistic KML & Shapefile test datasets
├── scripts/                   # Sample data generators
├── docker-compose.yml         # Container orchestration with PostGIS
└── docs/                      # Architecture and system documentation
```

---

## ⚡ Quick Start

### Prerequisites
- **Python 3.12+**
- **Node.js 20+** and **npm**

### 1. Run the Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Start FastAPI development server
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

- API Base: `http://127.0.0.1:8000`
- Interactive OpenAPI Docs: `http://127.0.0.1:8000/docs`
- Health Check: `http://127.0.0.1:8000/health`

### 2. Run the Frontend

```bash
cd frontend
npm install
npm run dev
```

- Web UI: `http://localhost:5173`

---

## 🐳 Running with Docker Compose

To start the full stack including PostgreSQL with PostGIS:

```bash
docker compose up --build
```

- Frontend: `http://localhost:3000`
- Backend: `http://localhost:8000`
- Database: `localhost:5432`

---

## 🧪 Running Tests

GeoMeasure includes unit and integration tests covering KML parsing, shapefile extraction, coordinate projection, geometry repair, and measurement logic:

```bash
cd backend
pytest -v
```

---

## 📄 License

This project is licensed under the MIT License.
