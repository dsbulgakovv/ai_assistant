from sqlalchemy import Column, Integer, String, BigInteger, DateTime, func
from sqlalchemy.orm import declarative_base


Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    tg_user_id = Column(BigInteger, unique=True)
    username = Column(String(50))
    full_name = Column(String(100))
    reg_dt = Column(DateTime(timezone=True), server_default=func.now())
    last_usage_dt = Column(DateTime(timezone=True), server_default=func.now())


class Task(Base):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(BigInteger, unique=False)
    task_name = full_name = Column(String(100))
    task_description = Column(String(300))
    task_start_dtm = Column(DateTime(timezone=True), server_default=func.now())
    task_end_dtm = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now())
