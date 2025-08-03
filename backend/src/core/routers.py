from fastapi import APIRouter
from src.account.routers import router as user_router
from src.auth.routers import auth_router

router = APIRouter(
    prefix="/api/v1",
)
router.include_router(user_router)
router.include_router(auth_router)