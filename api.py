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
async def list(sort: SortQueryBasic = Depends(), pagination: PaginationQueryBasic = Depends(), session: AsyncSession = Depends(db.get_db)) -> list[Account]:
    all_accounts_query = select(Account)
    # 1. sort
    if sort.sort_by and not hasattr(Account, sort.sort_by):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f'there is no field named {sort.sort_by} in {Account.__tablename__}')
    model_field = getattr(Account, sort.sort_by)
    sort_query = all_accounts_query.order_by(desc(
        model_field)) if sort.order_by == 'desc' else all_accounts_query.order_by(model_field)
    # TODO 2. filter
    filter_query = sort_query
    # 3. pagination
    strt_idx = (pagination.page-1) * pagination.per_page + 1

    paged_accounts_query = filter_query.offset(
        strt_idx).limit(pagination.per_page)
    accounts = await session.scalars(paged_accounts_query)
    return accounts


@api_router.post('/accounts/', response_model=AccountResponseDto)
async def create(accountCreateDto: AccountCreateDto, session: AsyncSession = Depends(db.get_db)) -> Account:
    new_account = Account(**accountCreateDto.model_dump())
    session.add(new_account)
    await session.commit()
    await session.refresh(new_account)
    return new_account
