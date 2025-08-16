from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Select, Update, Delete
from sqlalchemy.exc import NoResultFound

from src.account.models import Plan
from src.account.schemas import CreatePlanSchema, UpdatePlanSchema


class PlanRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, plan_schema: CreatePlanSchema):
        plan = Plan(**plan_schema.dict())
        self.session.add(plan)
        await self.session.commit()
        await self.session.refresh(plan)
        return plan

    async def get_by_id(self, plan_id: int):
        plan = await self.session.get(Plan, plan_id)
        return plan

    async def get_all(self):
        query = Select(Plan)
        result = await self.session.execute(query)
        plans = result.scalars().all()
        return plans

    async def get_active_plans(self):
        query = Select(Plan).where(Plan.is_active == True)
        result = await self.session.execute(query)
        plans = result.scalars().all()
        return plans

    async def update(self, plan_id: int, plan_schema: UpdatePlanSchema):
        plan_dict = plan_schema.dict(exclude_unset=True)
        query = Update(Plan).where(Plan.id == plan_id).values(**plan_dict)
        await self.session.execute(query)
        await self.session.commit()
        updated_plan = await self.session.get(Plan, plan_id)
        return updated_plan

    async def delete(self, plan_id: int):
        query = Delete(Plan).where(Plan.id == plan_id)
        result = await self.session.execute(query)
        if result.rowcount == 0:
            raise NoResultFound(f"Plan with id {plan_id} not found")
        await self.session.commit()
        return {"detail": "success"}

    async def deactivate_plan(self, plan_id: int):
        query = Update(Plan).where(Plan.id == plan_id).values(is_active=False)
        await self.session.execute(query)
        await self.session.commit()
        return await self.session.get(Plan, plan_id)
