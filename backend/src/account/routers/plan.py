from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.core.orm.database import get_async_session
from src.core.dependencies import get_current_user
from src.account.services.plan import PlanService
from src.account.schemas import CreatePlanSchema, UpdatePlanSchema, BasePlanSchema
from src.account.models import User

router = APIRouter(prefix="/plans", tags=["plans"])


@router.post("/", response_model=BasePlanSchema, status_code=status.HTTP_201_CREATED)
async def create_plan(
    plan_schema: CreatePlanSchema,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """Создание нового плана подписки (только для суперпользователей)"""
    plan_service = PlanService(session=session)
    return await plan_service.create(plan_schema, current_user)


@router.get("/", response_model=list[BasePlanSchema])
async def get_all_plans(session: AsyncSession = Depends(get_async_session)):
    """Получение всех планов подписок"""
    plan_service = PlanService(session=session)
    return await plan_service.get_all()


@router.get("/active", response_model=list[BasePlanSchema])
async def get_active_plans(session: AsyncSession = Depends(get_async_session)):
    """Получение только активных планов подписок"""
    plan_service = PlanService(session=session)
    return await plan_service.get_active_plans()


@router.get("/{plan_id}", response_model=BasePlanSchema)
async def get_plan_by_id(
    plan_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    """Получение плана подписки по ID"""
    plan_service = PlanService(session=session)
    return await plan_service.get_by_id(plan_id)


@router.put("/{plan_id}", response_model=BasePlanSchema)
async def update_plan(
    plan_id: int,
    plan_schema: UpdatePlanSchema,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """Обновление плана подписки (только для суперпользователей)"""
    plan_service = PlanService(session=session)
    return await plan_service.update(plan_id, plan_schema, current_user)


@router.delete("/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_plan(
    plan_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """Удаление плана подписки (только для суперпользователей)"""
    plan_service = PlanService(session=session)
    await plan_service.delete(plan_id, current_user)


@router.patch("/{plan_id}/deactivate", response_model=BasePlanSchema)
async def deactivate_plan(
    plan_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """Деактивация плана подписки (только для суперпользователей)"""
    plan_service = PlanService(session=session)
    return await plan_service.deactivate_plan(plan_id, current_user)
