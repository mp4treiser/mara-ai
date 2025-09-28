from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class BaseSubscriptionSchema(BaseModel):
    id: int
    user_id: int
    plan_id: int
    start_date: datetime
    end_date: datetime
    is_active: bool
    total_paid: float
    created_at: datetime
    updated_at: datetime


class CreateSubscriptionSchema(BaseModel):
    plan_id: int = Field(..., description="ID плана подписки")


class UpdateSubscriptionSchema(BaseModel):
    is_active: Optional[bool] = None


class SubscriptionWithDetailsSchema(BaseSubscriptionSchema):
    user_email: str
    user_name: str
    plan_name: str
    plan_days: int
    plan_price: float
    plan_discount: Optional[float] = None
