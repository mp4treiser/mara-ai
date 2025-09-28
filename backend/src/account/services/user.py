from fastapi import HTTPException
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.account.repositories.user import UserRepository
from src.account.schemas import CreateUserSchema, UpdateUserSchema
from src.core.auth import AuthManager


class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = UserRepository(session=session)
        self.auth_manager = AuthManager()

    async def create(self, user_schema: CreateUserSchema):
        await self._validate_email_unique(email=user_schema.email)

        hashed_password = self.auth_manager.hash_password(user_schema.password)
        
        user_data = {
            "email": user_schema.email,
            "password": hashed_password,
            "company": user_schema.company,
            "first_name": user_schema.first_name,
            "last_name": user_schema.last_name,
            "is_active": True
        }
        
        return await self.repository.create_from_dict(user_data)

    async def get_all(self):
        return await self.repository.get_all()

    async def get_by_id(self, user_id: int):
        return await self.repository.get_by_id(user_id=user_id)

    async def update(self, user_id: int, user_schema: UpdateUserSchema):
        return await self.repository.update(user_id=user_id, user_schema=user_schema)

    async def update_profile(self, user_id: int, profile_data: dict):
        """Обновляет профиль пользователя"""
        try:
            user = await self.repository.get_by_id(user_id)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"User with id {user_id} not found"
                )
            
            # Обновляем только разрешенные поля
            for field, value in profile_data.items():
                if hasattr(user, field):
                    setattr(user, field, value)
            
            await self.session.commit()
            await self.session.refresh(user)
            return user
            
        except Exception as e:
            await self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error updating profile: {str(e)}"
            )

    async def delete(self, user_id: int):
        try:
            return await self.repository.delete(user_id=user_id)
        except NoResultFound:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {user_id} not found"
            )

    async def _validate_email_unique(self, email: str):
        if await self.repository.get_by_email(email=email) is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
