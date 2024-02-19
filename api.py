from fastapi import APIRouter, Depends, HTTPException, status
from model import Account
from schema import *
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from database import db

api_router = APIRouter(prefix='/api')


@api_router.get('/')
async def health_check(session: AsyncSession = Depends(db.get_db)):
    response = await session.scalar(text('SELECT SQL_NO_CACHE 1;'))
    assert response == 1
    return {'hello': 'world'}


@api_router.get('/accounts/', response_model=list[AccountResponseDto])
async def list(queryInput: AccountQuery = Depends(), session: AsyncSession = Depends(db.get_db)) -> list[Account]:
    # 1. filter
    list_query = Select(Account)
    list_query = queryInput.get_filtered_query(
        query=list_query, db_model=Account)
    # 2. sort
    list_query = queryInput.get_sorted_query(
        query=list_query, db_model=Account)
    # 3. pagination
    list_query = queryInput.get_paginated_query(list_query)
    accounts = await session.scalars(list_query)
    return accounts


@api_router.post('/accounts/', response_model=AccountResponseDto)
async def create(accountCreateDto: AccountCreateDto, session: AsyncSession = Depends(db.get_db)) -> Account:
    new_account = Account(**accountCreateDto.model_dump())
    session.add(new_account)
    await session.commit()
    await session.refresh(new_account)
    return new_account
