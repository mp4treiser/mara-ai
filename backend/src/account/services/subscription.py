from fastapi import HTTPException
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.account.repositories.subscription import SubscriptionRepository
from src.account.repositories.user import UserRepository
from src.account.schemas import CreateSubscriptionSchema, UpdateSubscriptionSchema
from src.account.models import User, Plan


class SubscriptionService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.subscription_repository = SubscriptionRepository(session=session)
        self.user_repository = UserRepository(session=session)

    async def create_subscription(self, user_id: int, subscription_schema: CreateSubscriptionSchema):
        """Создание подписки с проверкой баланса"""
        # Получаем пользователя
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {user_id} not found"
            )

        # Получаем план
        plan = await self.session.get(Plan, subscription_schema.plan_id)
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Plan with id {subscription_schema.plan_id} not found"
            )

        # Рассчитываем финальную стоимость с учетом скидки
        final_price = plan.price
        if plan.discount_percent:
            final_price = plan.price * (1 - plan.discount_percent / 100)

        # Проверяем баланс пользователя
        if user.balance < final_price:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient balance. Required: {final_price}, Available: {user.balance}"
            )

        # Списываем средства с баланса
        new_balance = user.balance - final_price
        await self.user_repository.update_balance(user_id, new_balance)

        # Создаем подписку
        subscription = await self.subscription_repository.create(user_id, subscription_schema)
        
        return subscription

    async def get_by_id(self, subscription_id: int):
        """Получение подписки по ID"""
        subscription = await self.subscription_repository.get_by_id(subscription_id)
        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Subscription with id {subscription_id} not found"
            )
        return subscription

    async def get_by_user_id(self, user_id: int):
        """Получение всех подписок пользователя"""
        return await self.subscription_repository.get_by_user_id(user_id)

    async def get_active_by_user_id(self, user_id: int):
        """Получение активных подписок пользователя"""
        return await self.subscription_repository.get_active_by_user_id(user_id)

    async def get_all(self):
        """Получение всех подписок"""
        return await self.subscription_repository.get_all()

    async def update(self, subscription_id: int, subscription_schema: UpdateSubscriptionSchema):
        """Обновление подписки"""
        try:
            return await self.subscription_repository.update(subscription_id, subscription_schema)
        except NoResultFound:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Subscription with id {subscription_id} not found"
            )

    async def delete(self, subscription_id: int):
        """Удаление подписки"""
        try:
            return await self.subscription_repository.delete(subscription_id)
        except NoResultFound:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Subscription with id {subscription_id} not found"
            )

    async def deactivate_expired_subscriptions(self):
        """Деактивация истекших подписок"""
        return await self.subscription_repository.deactivate_expired_subscriptions()

    async def get_subscription_with_details(self, subscription_id: int):
        """Получение подписки с детальной информацией"""
        details = await self.subscription_repository.get_subscription_with_details(subscription_id)
        if not details:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Subscription with id {subscription_id} not found"
            )
        return details
