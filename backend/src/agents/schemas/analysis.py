from pydantic import BaseModel, Field


class TextAnalysisRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Текст для анализа агентом")


class TextAnalysisResponse(BaseModel):
    agent_id: int
    response: str
    processing_time: float
    documents_used: int
    success: bool
    error_message: str | None = None
