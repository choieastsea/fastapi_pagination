from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Database:

    def __init__(self):
        self.__session = None
        self.__engine = None

    @property
    def engine(self):
        return self.__engine

    def init_db(self, DB_URL: str):
        self.__engine = create_async_engine(DB_URL, echo=True)

        self.__session = async_sessionmaker(
            bind=self.__engine,
            autocommit=False,
        )

    async def disconnect(self):
        await self.__engine.dispose()

    async def get_db(self):
        async with self.__session() as session:
            try:
                yield session
            except SQLAlchemyError as err:
                await session.rollback()
                raise err
            finally:
                await session.close()


db = Database()
