from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime
from sqlalchemy.sql import Select, desc
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy import Column
from fastapi import HTTPException, status


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
    fields
        * page : requested page
        * per_page : count of items in a single page
    """
    page: Optional[int] = Field(default=1, ge=1)
    per_page: Optional[int] = Field(default=10, ge=1)

    def get_paginated_query(self, query: Select) -> Select:
        strt_idx = (self.page-1) * self.per_page
        return query.offset(strt_idx).limit(self.per_page)


class SortQueryBasic(BaseModel):
    """
    fields
        * sort_by : field name of model
        * order_by : 'asc' or 'desc'
    """
    sort_by: Optional[str] = Field(default=None, min_length=1)
    order_by: Optional[Literal['asc', 'desc']] = Field(default=None)

    def get_sorted_query(self, query: Select, db_model: DeclarativeMeta) -> Select:
        if self.sort_by:
            if not hasattr(db_model, self.sort_by):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail=f'there is no field named {self.sort_by} in {db_model.__tablename__}')
            model_field = getattr(db_model, self.sort_by)
            query = query.order_by(desc(
                model_field)) if self.order_by == 'desc' else query.order_by(model_field)
        return query


class FilterBasic(BaseModel):
    def get_filtered_query(self, query: Select, db_model: DeclarativeMeta) -> Select:
        for field_name, field_info in self.model_fields.items():
            if field_info.json_schema_extra and 'isFilter' in field_info.json_schema_extra:  # -> filter인 field
                # hasattr은 yes지만 NonType일 수도 있음 따라서 field_name도 check
                if hasattr(self, field_name) and getattr(self, field_name):
                    raw_filter_str: str = getattr(
                        self, field_name)  # ex) like:2
                    op, value = raw_filter_str.split(':')
                    # 해당 model에 field_name 있는지 확인
                    db_field: Column = getattr(db_model, field_name)
                    if op == 'eq':
                        query = query.filter(db_field == value)
                    elif op == 'in':
                        # check value is valid list
                        in_list = value.split(',')
                        query = query.filter(db_field.in_(in_list))
                    elif op == 'not':
                        query = query.filter(db_field != value)
                    elif op == 'like':
                        query = query.filter(db_field.like(f'%{value}%'))
                    else:
                        raise Exception('something wrong on your schema')
        return query


class AccountQuery(PaginationQueryBasic, SortQueryBasic, FilterBasic):
    """
    <URL example>
    /?page={page}&per_page={per_page}&sort_by={field}&order_by=[asc/desc]
    &id=[not/in]:1/2,3,4,5
    &name=[eq/like]:foo
    &nickname=like:bar
    """
    id: Optional[str] = Field(
        default=None, pattern=r'^(not|in):.+', isFilter=True)  # function으로 선언되어 있어서 되려나 모름
    name: Optional[str] = Field(
        default=None, pattern=r'^(eq|like):.+', isFilter=True)
    nickname: Optional[str] = Field(
        default=None, pattern=r'^(like):.+', isFilter=True)
