from fastapi import APIRouter
from .test import router as user_router

router = APIRouter(
    prefix="/user",
)
router.include_router(user_router)