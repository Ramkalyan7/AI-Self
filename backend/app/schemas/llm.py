from pydantic import BaseModel, Field


class LlmGenerateRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=20_000)


class LlmGenerateResponse(BaseModel):
    text: str
