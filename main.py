from fastapi import FastAPI
from contextlib import asynccontextmanager
from config import get_setting
from database import db, Base
from sqlalchemy.ext.asyncio import AsyncConnection
from sqlalchemy import insert
from model import Account
from api import api_router
import uuid

SETTINGS = get_setting()


async def add_default_accounts(conn: AsyncConnection, cnt: int = 100):
    params = []
    for _ in range(cnt):
        params.append(
            {'name': str(uuid.uuid4())[:20], 'nickname': str(uuid.uuid4())[:20], 'description': str(uuid.uuid4())})
    await conn.execute(insert(Account), params)
    await conn.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    db.init_db(SETTINGS.DB_URL)
    # async with db.engine.connect() as conn:
    #     await conn.run_sync(Base.metadata.drop_all)
    #     await conn.run_sync(Base.metadata.create_all)
    #     await add_default_accounts(conn)
    yield
    await db.disconnect()

app = FastAPI(lifespan=lifespan)
app.include_router(api_router)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run('main:app', host='0.0.0.0', port=8000, reload=True)
