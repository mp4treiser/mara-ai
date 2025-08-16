from fastapi import APIRouter
from .user import router as user_router
from .admin import router as admin_router
from .plan import router as plan_router
from .subscription import router as subscription_router
from .wallet import router as wallet_router

router = APIRouter()
router.include_router(user_router)
router.include_router(admin_router)
router.include_router(plan_router)
router.include_router(subscription_router)
router.include_router(wallet_router)