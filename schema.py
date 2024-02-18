from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Literal
from datetime import datetime, date
from dataclasses import dataclass


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


class PaginationQueryBasic(BaseModel):
    """
    args
        * page : requested page
        * per_page : count of items in a single page
    """
    page: Optional[int] = Field(default=1, ge=1)
    per_page: Optional[int] = Field(default=10, ge=1)


class SortQueryBasic(BaseModel):
    """
    args
        * sort_by : field name of model
        * order_by : 'asc' or 'desc'
    """
    sort_by: Optional[str] = Field(default=None, min_length=1)
    order_by: Optional[Literal['asc', 'desc']] = Field(default=None)
