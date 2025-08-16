from fastapi import HTTPException
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.account.repositories.plan import PlanRepository
from src.account.schemas import CreatePlanSchema, UpdatePlanSchema
from src.account.models import User


class PlanService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = PlanRepository(session=session)

    async def create(self, plan_schema: CreatePlanSchema, current_user: User):
        """Создание плана подписки (только для суперпользователей)"""
        if not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only superusers can create plans"
            )
        
        return await self.repository.create(plan_schema)

    async def get_all(self):
        """Получение всех планов"""
        return await self.repository.get_all()

    async def get_active_plans(self):
        """Получение только активных планов"""
        return await self.repository.get_active_plans()

    async def get_by_id(self, plan_id: int):
        """Получение плана по ID"""
        plan = await self.repository.get_by_id(plan_id)
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Plan with id {plan_id} not found"
            )
        return plan

    async def update(self, plan_id: int, plan_schema: UpdatePlanSchema, current_user: User):
        """Обновление плана (только для суперпользователей)"""
        if not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only superusers can update plans"
            )
        
        try:
            return await self.repository.update(plan_id, plan_schema)
        except NoResultFound:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Plan with id {plan_id} not found"
            )

    async def delete(self, plan_id: int, current_user: User):
        """Удаление плана (только для суперпользователей)"""
        if not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only superusers can delete plans"
            )
        
        try:
            return await self.repository.delete(plan_id)
        except NoResultFound:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Plan with id {plan_id} not found"
            )

    async def deactivate_plan(self, plan_id: int, current_user: User):
        """Деактивация плана (только для суперпользователей)"""
        if not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only superusers can deactivate plans"
            )
        
        plan = await self.repository.get_by_id(plan_id)
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Plan with id {plan_id} not found"
            )
        
        return await self.repository.deactivate_plan(plan_id)
