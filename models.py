from typing import Optional

from pydantic import BaseModel, Field, field_validator


class PipelineRequest(BaseModel):
    prompt: str = Field(
        ..., min_length=1, max_length=10000, description="发送给 Claude 的 prompt"
    )
    max_tokens: Optional[int] = Field(
        None, ge=1, le=4096, description="可选，覆盖默认 max_tokens"
    )

    @field_validator("prompt")
    @classmethod
    def _strip_and_reject_blank(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("prompt 不能为空或仅包含空白字符")
        return stripped


class PipelineResponse(BaseModel):
    result: str
    model: str
