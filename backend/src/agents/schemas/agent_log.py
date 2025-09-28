from datetime import datetime
from pydantic import BaseModel


class AgentLogResponse(BaseModel):
    id: int
    agent_id: int
    text_analyzed: str
    response: str
    processing_time: float
    text_length: int
    documents_used: int
    created_at: datetime

    class Config:
        from_attributes = True
