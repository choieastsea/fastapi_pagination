from fastapi import APIRouter, Depends, HTTPException, status
from model import Account
from schema import *
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select, between, desc
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
    list_query = queryInput.get_filtered_query(db_model=Account)
    # 2. sort
    if queryInput.sort_by:
        if not hasattr(Account, queryInput.sort_by):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f'there is no field named {queryInput.sort_by} in {Account.__tablename__}')
        model_field = getattr(Account, queryInput.sort_by)
        list_query = list_query.order_by(desc(
            model_field)) if queryInput.order_by == 'desc' else queryInput.order_by(model_field)
    # 3. pagination
    strt_idx = (queryInput.page-1) * queryInput.per_page
    list_query = list_query.offset(
        strt_idx).limit(queryInput.per_page)
    accounts = await session.scalars(list_query)
    return accounts


@api_router.post('/accounts/', response_model=AccountResponseDto)
async def create(accountCreateDto: AccountCreateDto, session: AsyncSession = Depends(db.get_db)) -> Account:
    new_account = Account(**accountCreateDto.model_dump())
    session.add(new_account)
    await session.commit()
    await session.refresh(new_account)
    return new_account
