from sqlalchemy import Column, Integer, String, BigInteger, DateTime, func
from sqlalchemy.orm import declarative_base


Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    tg_user_id = Column(BigInteger, unique=True, index=True)
    username = Column(String(50))
    full_name = Column(String(100))
    reg_dt = Column(DateTime(timezone=True), server_default=func.now())
    last_usage_dt = Column(DateTime(timezone=True), server_default=func.now())


class Task(Base):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    tg_user_id = Column(BigInteger, unique=False)
    task_name = full_name = Column(String(100))
    task_status = Column(Integer, unique=False)
    task_category = Column(Integer, unique=False)
    task_description = Column(String(300))
    task_start_dtm = Column(DateTime(timezone=True), index=True, server_default=func.now())
    task_end_dtm = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now())


class TaskStatusDict(Base):
    __tablename__ = 'task_statuses_dict'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    status_id = Column(Integer, index=True)
    status_name = task_name = full_name = Column(String(30))


class TaskCategoriesDict(Base):
    __tablename__ = 'task_categories_dict'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    category_id = Column(Integer, index=True)
    category_name = task_name = full_name = Column(String(30))
