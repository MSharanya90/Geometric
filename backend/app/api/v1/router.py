"""
API v1 Router aggregation.
"""
from fastapi import APIRouter
from app.api.v1.endpoints import files, measurements, export, health

api_router = APIRouter()
api_router.include_router(files.router)
api_router.include_router(measurements.router)
api_router.include_router(export.router)
api_router.include_router(health.router)
