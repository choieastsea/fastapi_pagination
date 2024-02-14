from fastapi import APIRouter, Depends
from model import Account
from schema import AccountCreateDto, AccountResponseDto
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select
from database import db

api_router = APIRouter(prefix='/api')


@api_router.get('/')
async def health_check(session: AsyncSession = Depends(db.get_db)):
    response = await session.scalar(text('SELECT SQL_NO_CACHE 1;'))
    assert response == 1
    return {'hello': 'world'}


@api_router.get('/accounts/', response_model=list[AccountResponseDto])
async def list(session: AsyncSession = Depends(db.get_db)) -> list[Account]:
    all_accounts = await session.scalars(select(Account).filter(Account.is_activated == True))
    return all_accounts


@api_router.post('/accounts/', response_model=AccountResponseDto)
async def create(accountCreateDto: AccountCreateDto, session: AsyncSession = Depends(db.get_db)) -> Account:
    new_account = Account(**accountCreateDto.model_dump())
    session.add(new_account)
    await session.commit()
    await session.refresh(new_account)
    return new_account
