from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.schemas import LoginSchema, RegisterSchema, TokenSchema, UserResponseSchema
from src.auth.services import AuthService
from src.core.orm.database import get_async_session
from src.core.middlewares.rate_limiting import rate_limiter

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

@router.get("/health")
async def auth_health_handler():
    return {"status": "success"}


@router.get("/rate-limit-info")
async def get_rate_limit_info(request: Request):
    """Получает информацию о текущих лимитах запросов"""
    try:
        limits_info = rate_limiter.get_remaining_requests(request)
        client_ip = rate_limiter._get_client_ip(request)
        
        return {
            "client_ip": client_ip,
            "rate_limits": limits_info,
            "endpoints": {
                "login": rate_limiter.default_limits["login"],
                "register": rate_limiter.default_limits["register"],
                "password_reset": rate_limiter.default_limits["password_reset"],
                "default": rate_limiter.default_limits["default"]
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "failed_to_get_rate_limit_info", "message": str(e)}
        )

@router.post("/register", response_model=UserResponseSchema, status_code=status.HTTP_201_CREATED)
async def register_handler(
    payload: RegisterSchema,
    session: AsyncSession = Depends(get_async_session)
):
    auth_service = AuthService(session=session)
    return await auth_service.register(register_schema=payload)


@router.post("/login", response_model=TokenSchema)
async def login_handler(
    payload: LoginSchema,
    request: Request,
    session: AsyncSession = Depends(get_async_session)
):
    """Обработчик входа с улучшенной валидацией и rate limiting"""
    # Проверяем rate limit для логина
    client_ip = rate_limiter._get_client_ip(request)
    if not rate_limiter.check_rate_limit(request):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "error": "rate_limit_exceeded",
                "message": "Превышен лимит попыток входа. Попробуйте позже",
                "retry_after": rate_limiter.block_duration,
                "client_ip": client_ip
            }
        )
    
    auth_service = AuthService(session=session)
    return await auth_service.login(login_schema=payload, request=request)
