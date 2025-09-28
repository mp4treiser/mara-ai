from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Select, Update, Delete, and_
from sqlalchemy.exc import NoResultFound

from src.account.models import Subscription, User, Plan
from src.account.schemas import CreateSubscriptionSchema, UpdateSubscriptionSchema


class SubscriptionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user_id: int, subscription_schema: CreateSubscriptionSchema):
        plan = await self.session.get(Plan, subscription_schema.plan_id)
        if not plan:
            raise ValueError(f"Plan with id {subscription_schema.plan_id} not found")

        start_date = datetime.now()
        end_date = start_date + timedelta(days=plan.days)

        final_price = plan.price
        if plan.discount_percent:
            final_price = plan.price * (1 - plan.discount_percent / 100)

        subscription = Subscription(
            user_id=user_id,
            plan_id=subscription_schema.plan_id,
            start_date=start_date,
            end_date=end_date,
            total_paid=final_price,
            is_active=True
        )
        
        self.session.add(subscription)
        await self.session.commit()
        await self.session.refresh(subscription)
        return subscription

    async def get_by_id(self, subscription_id: int):
        subscription = await self.session.get(Subscription, subscription_id)
        return subscription

    async def get_by_user_id(self, user_id: int):
        query = Select(Subscription).where(Subscription.user_id == user_id)
        result = await self.session.execute(query)
        subscriptions = result.scalars().all()
        return subscriptions

    async def get_active_by_user_id(self, user_id: int):
        query = Select(Subscription).where(
            and_(Subscription.user_id == user_id, Subscription.is_active == True)
        )
        result = await self.session.execute(query)
        subscriptions = result.scalars().all()
        return subscriptions

    async def get_all(self):
        query = Select(Subscription)
        result = await self.session.execute(query)
        subscriptions = result.scalars().all()
        return subscriptions

    async def update(self, subscription_id: int, subscription_schema: UpdateSubscriptionSchema):
        subscription_dict = subscription_schema.dict(exclude_unset=True)
        query = Update(Subscription).where(Subscription.id == subscription_id).values(**subscription_dict)
        await self.session.execute(query)
        await self.session.commit()
        updated_subscription = await self.session.get(Subscription, subscription_id)
        return updated_subscription

    async def delete(self, subscription_id: int):
        query = Delete(Subscription).where(Subscription.id == subscription_id)
        result = await self.session.execute(query)
        if result.rowcount == 0:
            raise NoResultFound(f"Subscription with id {subscription_id} not found")
        await self.session.commit()
        return {"detail": "success"}

    async def deactivate_expired_subscriptions(self):
        """Деактивирует истекшие подписки"""
        current_time = datetime.utcnow()
        query = Update(Subscription).where(
            and_(Subscription.end_date < current_time, Subscription.is_active == True)
        ).values(is_active=False)
        await self.session.execute(query)
        await self.session.commit()

    async def get_subscription_with_details(self, subscription_id: int):
        """Получает подписку с детальной информацией о пользователе и плане"""
        query = Select(Subscription, User, Plan).join(User).join(Plan).where(Subscription.id == subscription_id)
        result = await self.session.execute(query)
        row = result.first()
        if not row:
            return None
        
        subscription, user, plan = row
        return {
            "subscription": subscription,
            "user": user,
            "plan": plan
        }
