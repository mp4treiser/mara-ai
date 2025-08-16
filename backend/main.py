from typing import Union
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import generate_latest
from starlette.responses import Response

from src.core.middlewares import PrometheusMiddleware
from src.core.routers import router as app_router

app = FastAPI(docs_url="/api/docs")
app.add_middleware(PrometheusMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(app_router)

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type="text/plain")

@app.get("/health")
async def health_check():
    """Health check endpoint для Docker"""
    return {"status": "healthy", "timestamp": "2025-08-16T13:41:47+03:00"}