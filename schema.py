from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime, date


class AccountCreateDto(BaseModel):
    name: str
    nickname: str
    description: Optional[str] = Field(default=None)


class AccountResponseDto(BaseModel):
    id: int
    name: str
    nickname: str
    description: str
    created_at: datetime
    updated_at: datetime
