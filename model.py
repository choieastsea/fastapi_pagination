from sqlalchemy import Column, String, Text, BigInteger, DateTime, Boolean
from database import Base
from sqlalchemy.sql import func, text
from datetime import datetime


class Account(Base):
    __tablename__ = 'accounts'

    id: int = Column(BigInteger, autoincrement=True,
                     nullable=False, primary_key=True)
    name: str = Column(String(20), nullable=False)
    nickname: str = Column(String(20), nullable=False, unique=True)
    description: str = Column(Text, nullable=True, default='')
    created_at: datetime = Column(
        DateTime, server_default=func.now())
    updated_at: datetime = Column(DateTime, server_default=text(
        'CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))
    is_activated: bool = Column(Boolean, default=True)
