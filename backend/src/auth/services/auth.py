from datetime import timedelta
from fastapi import HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
import logging
import time

from src.account.repositories import UserRepository
from src.auth.schemas import LoginSchema, RegisterSchema, TokenSchema, UserResponseSchema
from src.core.config import settings
from src.core.auth import AuthManager

logger = logging.getLogger(__name__)


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

    async def login(self, login_schema: LoginSchema, request: Request = None) -> TokenSchema:
        """Улучшенный метод логина с детальными сообщениями об ошибках"""
        start_time = time.time()
        
        try:
            # Логируем попытку входа
            client_ip = self._get_client_ip(request) if request else "unknown"
            logger.info(f"Попытка входа для email: {login_schema.email} с IP: {client_ip}")
            
            # Проверяем существование пользователя
            user = await self.user_repository.get_by_email(email=login_schema.email)
            if not user:
                logger.warning(f"Попытка входа с несуществующим email: {login_schema.email} с IP: {client_ip}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail={
                        "error": "authentication_failed",
                        "message": "Неверный email или пароль",
                        "field": "email",
                        "timestamp": time.time(),
                        "client_ip": client_ip
                    }
                )

            # Проверяем пароль
            if not self.auth_manager.verify_password(login_schema.password, user.password):
                logger.warning(f"Неверный пароль для пользователя {user.id} с IP: {client_ip}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail={
                        "error": "authentication_failed",
                        "message": "Неверный email или пароль",
                        "field": "password",
                        "timestamp": time.time(),
                        "client_ip": client_ip
                    }
                )

            # Проверяем активность пользователя
            if not user.is_active:
                logger.warning(f"Попытка входа неактивного пользователя {user.id} с IP: {client_ip}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail={
                        "error": "account_disabled",
                        "message": "Аккаунт заблокирован или деактивирован",
                        "field": "account",
                        "timestamp": time.time(),
                        "client_ip": client_ip
                    }
                )

            # Генерируем токен
            access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = self.auth_manager.create_access_token(
                data={"sub": str(user.id)}, expires_delta=access_token_expires
            )
            
            # Логируем успешный вход
            login_time = time.time() - start_time
            logger.info(f"Успешный вход пользователя {user.id} ({user.email}) с IP: {client_ip}, время: {login_time:.2f}с")

            return TokenSchema(
                access_token=access_token,
                token_type="bearer"
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Неожиданная ошибка при входе пользователя {login_schema.email}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "error": "internal_server_error",
                    "message": "Внутренняя ошибка сервера. Попробуйте позже",
                    "timestamp": time.time()
                }
            )
    
    def _get_client_ip(self, request: Request) -> str:
        """Получает IP адрес клиента"""
        if not request:
            return "unknown"
        
        # Проверяем заголовки прокси
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Возвращаем IP клиента
        if request.client:
            return request.client.host
        
        return "unknown"
