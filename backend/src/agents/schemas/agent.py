from datetime import datetime
from pydantic import BaseModel, Field


class AgentBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Название агента")
    prompt: str = Field(..., min_length=10, description="Промпт для агента")


class AgentCreate(AgentBase):
    pass


class AgentUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255, description="Название агента")
    prompt: str | None = Field(None, min_length=10, description="Промпт для агента")
    is_active: bool | None = Field(None, description="Активен ли агент")


class AgentResponse(AgentBase):
    id: int
    user_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True,
        "json_encoders": {
            datetime: lambda v: v.isoformat() if v else None
        }
    }
