from datetime import timedelta
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.account.repositories import UserRepository
from src.auth.schemas import LoginSchema, RegisterSchema, TokenSchema, UserResponseSchema
from src.core.config import settings
from src.core.auth import AuthManager


class AuthService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repository = UserRepository(session=session)
        self.auth_manager = AuthManager()

    async def register(self, register_schema: RegisterSchema) -> UserResponseSchema:
        if register_schema.password != register_schema.confirm_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The passwords do not match"
            )

        existing_user = await self.user_repository.get_by_email(email=register_schema.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )

        hashed_password = self.auth_manager.hash_password(register_schema.password)
        
        user_data = {
            "email": register_schema.email,
            "password": hashed_password,
            "company": register_schema.company,
            "first_name": register_schema.first_name,
            "last_name": register_schema.last_name,
            "is_active": True
        }
        
        user = await self.user_repository.create_from_dict(user_data)
        await self.session.commit()
        
        return UserResponseSchema(
            id=user.id,
            email=user.email,
            company=user.company,
            first_name=user.first_name,
            last_name=user.last_name,
            is_active=user.is_active
        )

    async def login(self, login_schema: LoginSchema) -> TokenSchema:
        user = await self.user_repository.get_by_email(email=login_schema.email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )

        if not self.auth_manager.verify_password(login_schema.password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User is not active"
            )

        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = self.auth_manager.create_access_token(
            data={"sub": str(user.id)}, expires_delta=access_token_expires
        )

        return TokenSchema(
            access_token=access_token,
            token_type="bearer"
        )
