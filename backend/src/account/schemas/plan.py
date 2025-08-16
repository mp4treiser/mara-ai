from pydantic import BaseModel, Field, validator, field_validator
from typing import Optional
from decimal import Decimal


class BasePlanSchema(BaseModel):
    id: int
    name: str
    days: int
    price: float
    discount_percent: Optional[float] = None
    description: Optional[str] = None
    is_active: bool


class CreatePlanSchema(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Название плана")
    days: int = Field(..., gt=0, description="Количество дней подписки")
    price: float = Field(..., gt=0, description="Стоимость плана")
    discount_percent: Optional[float] = Field(None, ge=0, le=100, description="Скидка в процентах")
    description: Optional[str] = Field(None, max_length=255, description="Описание плана")

    @field_validator('price')
    def validate_price(cls, v):
        if v <= 0:
            raise ValueError('Price > 0')
        return round(v, 2)

    @field_validator('discount_percent')
    def validate_discount(cls, v):
        if v is not None and (v < 0 or v > 100):
            raise ValueError('Price > 0 < 100')
        return round(v, 2) if v is not None else None


class UpdatePlanSchema(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    days: Optional[int] = Field(None, gt=0)
    price: Optional[float] = Field(None, gt=0)
    discount_percent: Optional[float] = Field(None, ge=0, le=100)
    description: Optional[str] = Field(None, max_length=255)
    is_active: Optional[bool] = None

    @field_validator('price')
    def validate_price(cls, v):
        if v is not None and v <= 0:
            raise ValueError('Price > 0')
        return round(v, 2) if v is not None else None

    @field_validator('discount_percent')
    def validate_discount(cls, v):
        if v is not None and (v < 0 or v > 100):
            raise ValueError('Price > 0 < 100')
        return round(v, 2) if v is not None else None
