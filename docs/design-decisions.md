# GeoMeasure — Design Decisions & Architectural Trade-offs

This document outlines key technical decisions made during the architecture and development of **GeoMeasure**, comparing chosen tools with evaluated alternatives.

---

## 1. Web Framework: FastAPI vs. Flask / Django

### Decision
Selected **FastAPI (Python 3.12+)**.

### Rationale
- **Asynchronous Throughput**: Native ASGI architecture enables non-blocking I/O operations during file uploads and streaming data exports.
- **Pydantic v2 Type Safety**: Provides automated schema validation, serialization, and deserialization with performance powered by compiled Rust internals.
- **Auto-Generated OpenAPI (Swagger / ReDoc)**: Produces interactive API documentation directly from type annotations without external docstrings or YAML syncing.
- **Dependency Injection**: Seamlessly manages database sessions, repository injection, and request context.

### Alternatives Considered
- *Flask*: Requires numerous external plugins for Marshmallow, OpenAPI, and async support.
- *Django*: Monolithic ORM and templating overhead exceeds the requirements of a focused REST microservice.

---

## 2. Geospatial Engine: GeoPandas, Shapely, PyProj with Dual-Engine Fallback

### Decision
Implemented a **hybrid dual-engine architecture**:
1. High-performance C-backed libraries (`geopandas`, `shapely`, `pyproj`, `fiona`) for Docker and standard Linux environments.
2. Mathematically rigorous pure-Python algorithms (`pyshp`, `lxml`, Karney Transverse Mercator formulation, Shoelace area, and Vincenty/Haversine geodesics) for constrained host environments.

### Rationale
- Production container environments utilize compiled GEOS, GDAL, and PROJ binaries for complex topological operations (`make_valid`, `reproject`).
- Constrained developer environments (e.g., Windows WDAC/AppLocker blocking unverified user `.pyd` dynamic libraries) can still run tests, parsing, and exact metric calculations without crashing.

### Alternatives Considered
- *GDAL Python Bindings Only*: Prone to fragile system-level C library dependencies that break easily across developer machines.
- *Pure Turf.js in Frontend*: Shifts measurement computation to client browsers, introducing client inconsistencies and preventing backend data exports.

---

## 3. Advanced CRS Strategy: UTM Zone Centroid Selection

### Decision
Automatically identify the dataset centroid and project coordinates into the local **Universal Transverse Mercator (UTM)** zone in meters before calculating area or length.

### Rationale
- **Geographic Coordinates (EPSG:4326)**: Latitude and longitude are angular units (degrees). Calculating area or Euclidean distance directly from degrees introduces distortion exceeding 40% away from the equator.
- **UTM Projection**: Preserves local conformality and minimizes scale distortion to less than 0.04% within each 6-degree zone, providing accurate meters and square meters.
- **Global Datasets**: If a dataset exceeds 60 degrees of longitude span, the system falls back to `EPSG:6933` (Equal Earth) and documents the strategy in `crs_strategy`.

---

## 4. Frontend: React 19 + Vite + Vanilla CSS (No Tailwind)

### Decision
Built with **React 19**, **Vite**, and **Vanilla CSS Design System**.

### Rationale
- **Vite**: Sub-second Hot Module Replacement (HMR) and optimized Rollup/ESBuild bundling.
- **No Tailwind CSS**: As specified in requirements, a bespoke CSS design system with CSS custom properties was developed. This enables complete control over glassmorphism, responsive tables, animations, and Leaflet map overrides without external utility bloat.
- **Leaflet & React-Leaflet**: Open-source, lightweight mapping library that does not require proprietary access tokens (unlike Mapbox GL).

---

## 5. Architectural Pattern: Service Layer & Repository Pattern

### Decision
Separated logic into distinct **API Routes**, **Service Layer**, and **Repository Layer**.

### Rationale
- **Single Responsibility Principle**: API routes only handle HTTP request parsing, response model wrapping, and status codes.
- **Service Layer**: Houses the business logic (parsing, geometry cleaning, CRS calculation, metric conversion).
- **Repository Layer**: Encapsulates SQLAlchemy database queries, pagination, and sorting.
- **Testability**: Services and repositories can be unit-tested in isolation without mocking HTTP requests.
