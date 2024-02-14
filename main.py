from fastapi import FastAPI
from contextlib import asynccontextmanager
from config import get_setting
from database import db, Base
from api import api_router

SETTINGS = get_setting()


@asynccontextmanager
async def lifespan(app: FastAPI):
    db.init_db(SETTINGS.DB_URL)
    async with db.engine.connect() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await db.disconnect()

app = FastAPI(lifespan=lifespan)
app.include_router(api_router)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run('main:app', host='0.0.0.0', port=8000, reload=True)
