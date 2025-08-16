import os
from fastapi import APIRouter
from src.account.routers import router as user_router
from src.auth.routers import auth_router

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
router.include_router(auth_router)