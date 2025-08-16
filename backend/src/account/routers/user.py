from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.account.schemas import CreateUserSchema, UpdateUserSchema, BaseUserSchema
from src.account.services import UserService
from src.core.orm.database import get_async_session
from src.core.dependencies import get_current_user, get_current_active_user, get_current_superuser
from src.account.models import User

router = APIRouter(
    prefix="/user",
    tags=["User"]
)


@router.get("/health")
async def health_handler():
    return {"work": "success"}


# Защищенные эндпоинты (требуют аутентификации)
@router.get("/me/profile", response_model=BaseUserSchema)
async def get_my_profile_handler(current_user: User = Depends(get_current_active_user)):
    return current_user


@router.put("/me/profile", response_model=BaseUserSchema)
async def update_my_profile_handler(
        payload: UpdateUserSchema,
        current_user: User = Depends(get_current_active_user),
        session: AsyncSession = Depends(get_async_session)
):
    user_service = UserService(session=session)
    return await user_service.update(user_id=current_user.id, user_schema=payload)
