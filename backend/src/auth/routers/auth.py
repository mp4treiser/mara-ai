from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.schemas import LoginSchema, RegisterSchema, TokenSchema, UserResponseSchema
from src.auth.services import AuthService
from src.core.orm.database import get_async_session

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
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
    session: AsyncSession = Depends(get_async_session)
):
    auth_service = AuthService(session=session)
    return await auth_service.login(login_schema=payload)


@router.get("/health")
async def auth_health_handler():
    return {"status": "auth module is working"}
