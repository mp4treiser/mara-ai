from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.account.schemas.user import CreateUserSchema, UpdateUserSchema, BaseUserSchema
from src.account.services.user import UserService
from src.core.orm.database import get_async_session

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.get("/health")
async def health_handler():
    return {"work": "success"}

@router.get("/", response_model=List[BaseUserSchema])
async def get_users_handler(session: AsyncSession = Depends(get_async_session)):
    users = UserService(session=session)
    return await users.get_all()

@router.get("/{user_id}", response_model=BaseUserSchema)
async def get_user_by_id_handler(user_id: int, session: AsyncSession = Depends(get_async_session)):
    user = UserService(session=session)
    return await user.get_by_id(user_id=user_id)

@router.post("/", response_model=BaseUserSchema)
async def create_user_handler(payload: CreateUserSchema, session: AsyncSession = Depends(get_async_session)):
    user_service = UserService(session=session)
    return await user_service.create(user_schema=payload)

@router.put("/{user_id}", response_model=BaseUserSchema)
async def update_user_handler(user_id: int, payload: UpdateUserSchema, session: AsyncSession = Depends(get_async_session)):
    user_service = UserService(session=session)
    return await user_service.update(user_id=user_id, user_schema=payload)

@router.delete("/{user_id}", response_model=None)
async def delete_user_handler(user_id: int, session: AsyncSession = Depends(get_async_session)):
    user_service = UserService(session=session)
    return await user_service.delete(user_id=user_id)
