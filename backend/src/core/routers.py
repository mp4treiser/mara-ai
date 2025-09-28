import os
from fastapi import APIRouter
from src.account.routers import router as user_router
from src.account.routers.user import router as user_profile_router
from src.auth.routers import auth_router
from src.agents.routers import agent_router, document_router, analysis_router, user_agents_router, metrics_router
from src.agents.routers.telegram_config import router as telegram_config_router
from src.agents.routers.telegram_monitoring import router as telegram_monitoring_router
from src.agents.routers.aiogram_bot_management import router as aiogram_bot_management_router

router = APIRouter(
    prefix="/api/v1",
)

@router.get("/server-info")
async def get_server_info():
    """Получить информацию о сервере для проверки балансировки нагрузки"""
    import socket
    import platform
    
    return {
        "server_id": os.getenv("SERVER_ID", "unknown"),
        "hostname": socket.gethostname(),
        "platform": platform.platform(),
        "python_version": platform.python_version(),
        "process_id": os.getpid(),
        "message": f"Запрос обработан на сервере {os.getenv('SERVER_ID', 'unknown')}"
    }

router.include_router(user_router)
router.include_router(user_profile_router)
router.include_router(auth_router)
router.include_router(agent_router)
router.include_router(document_router)
router.include_router(analysis_router)
router.include_router(user_agents_router)
router.include_router(metrics_router)
router.include_router(telegram_config_router)
router.include_router(telegram_monitoring_router)
router.include_router(aiogram_bot_management_router)