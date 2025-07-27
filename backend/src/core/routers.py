from fastapi import APIRouter
from src.account.routers import router as user_router

router = APIRouter(
    prefix="/api/v1",
)
router.include_router(user_router)