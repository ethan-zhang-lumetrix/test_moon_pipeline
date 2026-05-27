from pydantic import BaseModel, Field


class PipelineRequest(BaseModel):
    prompt: str = Field(..., min_length=1, description="发送给 Claude 的 prompt")


class PipelineResponse(BaseModel):
    result: str
    model: str
