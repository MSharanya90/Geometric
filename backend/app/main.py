"""
Main entry point for GeoMeasure FastAPI application.
Configures CORS, routers, exception handlers, middlewares, and lifecycle events.
"""
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.exceptions import GeoMeasureException
from app.core.logging import logger
from app.db.session import init_db
from app.api.v1.endpoints.health import router as health_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events."""
    logger.info("Initializing GeoMeasure Platform...")
    init_db()
    logger.info("Database initialized. Ready for geospatial analysis.")
    yield
    logger.info("Shutting down GeoMeasure Platform...")


app = FastAPI(
    title="GeoMeasure — Geospatial File Measurement & Analysis Platform",
    description=(
        "Production-quality full-stack geospatial file processing API. "
        "Allows users to securely upload KML and Shapefile archives, "
        "inspect geometry topologies, detect CRS, reproject into optimal UTM metric zones, "
        "and calculate accurate area and length measurements."
    ),
    version=settings.VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {
            "name": "Files",
            "description": "Secure geospatial file upload, inspection, and lifecycle operations.",
        },
        {
            "name": "Measurements",
            "description": "Paginated feature measurements, summary statistics, and GeoJSON endpoints.",
        },
        {
            "name": "Export",
            "description": "Data export services in JSON, GeoJSON, and CSV formats.",
        },
        {
            "name": "Health",
            "description": "System health and readiness probes.",
        },
    ],
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permits local development, Docker, and previews
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log incoming requests and compute execution duration."""
    start_time = time.perf_counter()
    response = await call_next(request)
    duration_ms = (time.perf_counter() - start_time) * 1000
    logger.info(
        "%s %s -> status %d (%.2f ms)",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )
    return response


# Global Exception Handlers
@app.exception_handler(GeoMeasureException)
async def geomeasure_exception_handler(request: Request, exc: GeoMeasureException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details,
            }
        },
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled server exception on %s %s: %s", request.method, request.url.path, str(exc))
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected server error occurred while processing the request.",
                "details": {},
            }
        },
    )


# Root level health routes for container probes
app.include_router(health_router)

# Mount API v1 router
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/", tags=["Health"])
def root_info():
    """Root info endpoint."""
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "documentation": "/docs",
        "health": "/health",
    }
