from typing import Union
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.core.routers import router as app_router

app = FastAPI(docs_url="/api/docs")

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

