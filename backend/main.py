from typing import Union
from src.core.routers import router as app_router
from fastapi import FastAPI

app = FastAPI(docs_url="/api/docs")
app.include_router(app_router)

