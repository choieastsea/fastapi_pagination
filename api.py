from fastapi import APIRouter, Depends
from database import db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

api_router = APIRouter(prefix='/api')


@api_router.get('/')
async def health_check(session: AsyncSession = Depends(db.get_db)):
    response = await session.scalar(text('SELECT SQL_NO_CACHE 1;'))
    assert response == 1
    return {'hello': 'world'}
