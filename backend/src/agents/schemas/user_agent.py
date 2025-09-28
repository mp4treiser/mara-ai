from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional


class UserAgentBase(BaseModel):
    agent_id: int = Field(..., description="ID агента")


class UserAgentCreate(UserAgentBase):
    pass


class UserAgentUpdate(BaseModel):
    is_active: Optional[bool] = Field(None, description="Активна ли связь")


class UserAgentResponse(UserAgentBase):
    id: int
    user_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    agent_name: str
    agent_prompt: str

    model_config = {
        "from_attributes": True,
        "json_encoders": {
            datetime: lambda v: v.isoformat() if v else None
        }
    }


class AgentWithUserAgentResponse(BaseModel):
    id: int
    name: str
    prompt: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    user_agent_id: Optional[int] = None
    is_user_agent: bool = False

    model_config = {
        "from_attributes": True,
        "json_encoders": {
            datetime: lambda v: v.isoformat() if v else None
        }
    }
