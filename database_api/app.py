from fastapi import FastAPI, Depends, Query, HTTPException, Request
from fastapi.responses import JSONResponse

import time

import asyncpg

import logging
from logging.config import dictConfig

import os
from contextlib import asynccontextmanager
from pydantic import BaseModel, field_validator
from typing import Dict, Any, Optional

from log_config import LogConfig
from datetime import date, datetime
from pytz import timezone

import re


dictConfig(LogConfig().dict())
logger = logging.getLogger("db_api")

# Конфигурация подключения к БД (вынесена отдельно)
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "postgres"),
    "port": os.getenv("DB_PORT", "5432"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASS"),
    "database": os.getenv("DB_NAME"),
    "min_size": 5,
    "max_size": 20
}


# Создаем пул соединений при старте приложения
@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.pool = await asyncpg.create_pool(**DB_CONFIG)
    logger.info("Database connection pool created")
    yield
    await app.state.pool.close()
    logger.info("Database connection pool closed")

app = FastAPI(lifespan=lifespan)


class UserCreate(BaseModel):
    tg_user_id: int
    username: str
    full_name: str
    timezone: str
    lang: str


class Task(BaseModel):
    tg_user_id: int
    task_name: str
    task_status: int
    task_category: int
    task_description: str
    task_link: str
    task_start_dtm: str
    task_end_dtm: str


class UpdateTask(BaseModel):
    id: int
    tg_user_id: int
    task_name: Optional[str] = None
    task_status: Optional[int] = None
    task_category: Optional[int] = None
    task_description: Optional[str] = None
    task_link: Optional[str] = None
    task_start_dtm: Optional[str] = None
    task_end_dtm: Optional[str] = None


class TasksDelete(BaseModel):
    business_dt: date
    task_relative_id: Optional[int] = None
    tg_user_id: int


class TaskResponse(BaseModel):
    status: str
    message: str
    data: Dict[str, Any] | None = None


@field_validator('task_start_dtm', 'task_end_dtm')
def validate_datetime_format(cls, value):
    # Проверяем формат: YYYY-MM-DD HH:MM:SS.fff +ZZZZ
    if not re.match(r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3} \+\d{4}$', value):
        raise ValueError('Datetime must be in format: YYYY-MM-DD HH:MM:SS.fff +ZZZZ')
    return value


def parse_datetime(dt_str):
    dt, tz = dt_str.rsplit(' ', 1)
    dt_obj = datetime.strptime(dt, '%Y-%m-%d %H:%M:%S.%f')
    tz_obj = timezone(f'Etc/GMT{-int(tz[1:3])}')
    return dt_obj.replace(tzinfo=tz_obj)


async def get_db():
    async with app.state.pool.acquire() as connection:
        yield connection


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()

    # Логируем входящий запрос
    logger.info(f"Request: {request.method} {request.url}")
    logger.debug(f"Headers: {request.headers}")
    logger.debug(f"Query params: {request.query_params}")
    logger.debug(f"Body: {await request.body()}")

    response = await call_next(request)

    # Логируем ответ
    process_time = time.time() - start_time
    logger.info(f"Response: {response.status_code} (Time: {process_time:.2f}s)")
    logger.debug(f"Response headers: {response.headers}")

    return response


@app.get("/")
async def root():
    return JSONResponse(content={"message": "Service to transfer from/to PostgreSQL DB."})


@app.get("/users/{tg_user_id}")
async def get_user(tg_user_id: int, conn=Depends(get_db)):
    user = await conn.fetchrow("SELECT * FROM users WHERE tg_user_id = $1", tg_user_id)

    if not user:
        raise HTTPException(status_code=404, detail="No user found with this id")

    return user


# Example: /tasks/111222333?start_date=2023-05-01&end_date=2023-07-31 - query parameters
@app.get("/tasks/{tg_user_id}")
async def get_filtered_tasks(
        tg_user_id: int,
        start_date: date = Query(..., description="Start date in YYYY-MM-DD format (inclusively)"),
        end_date: date = Query(..., description="End date in YYYY-MM-DD format (inclusively)"),
        conn=Depends(get_db)
):
    start_date = start_date.isoformat()
    end_date = end_date.isoformat()
    tasks = await conn.fetch(
        """
        SELECT * FROM (
          SELECT
            *,
            to_char(
                (task_start_dtm AT TIME ZONE 'UTC') AT TIME ZONE 
                (EXTRACT(TIMEZONE_HOUR FROM task_start_dtm) || ' hours'),
                'YYYY-MM-DD'
            ) AS business_dt,
            ROW_NUMBER() OVER (
              PARTITION BY tg_user_id, (task_start_dtm::date)
              ORDER BY task_start_dtm
            ) AS task_relative_id
          FROM tasks
          WHERE
            tg_user_id = $1
        ) t
        WHERE
            1 = 1
            AND t.business_dt >= $2
            AND t.business_dt <= $3
        """,
        tg_user_id, start_date, end_date
    )

    if not tasks:
        raise HTTPException(status_code=404, detail="No tasks found in this date range")

    return tasks


@app.post("/users/add_new", status_code=201)
async def create_user(user: UserCreate, conn=Depends(get_db)):
    await conn.execute(
        """
        INSERT INTO users (
            tg_user_id, username, full_name, reg_dt, last_usage_dt, timezone, lang
        )
        VALUES ($1, $2, $3, NOW(), NOW(), $4, $5)
        ON CONFLICT (tg_user_id) DO NOTHING
        """,
        user.tg_user_id, user.username, user.full_name, user.timezone, user.lang
    )
    return {"status": "success", "message": "User created or already exists"}


@app.post("/tasks/add_new", status_code=201)
async def create_task(task: Task, conn=Depends(get_db)):
    task_start_dtm = parse_datetime(task.task_start_dtm)
    task_end_dtm = parse_datetime(task.task_end_dtm)

    if task_start_dtm > task_end_dtm:
        raise HTTPException(status_code=404, detail="Task start dtm cannot be after end dtm")

    await conn.execute(
        """
        INSERT INTO tasks (
            tg_user_id, task_name, task_status, task_category, task_description, task_link,
            task_start_dtm, task_end_dtm, created_at, updated_at
        )
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, NOW(), NOW())
        """,
        task.tg_user_id, task.task_name, task.task_status, task.task_category, task.task_description,
        task.task_link, task_start_dtm, task_end_dtm
    )
    return {"status": "success", "message": "Task created"}


@app.put("/tasks/update")
async def update_task(task: UpdateTask, conn=Depends(get_db)):
    # # Получаем текущие данные задачи
    # current_task = await conn.fetchrow(
    #     """
    #     SELECT * FROM (
    #       SELECT
    #         *,
    #         (task_start_dtm::date) AS business_dt,
    #         ROW_NUMBER() OVER (
    #           PARTITION BY tg_user_id, (task_start_dtm::date)
    #           ORDER BY task_start_dtm
    #         ) AS task_relative_id
    #       FROM tasks
    #     ) t
    #     WHERE
    #       t.tg_user_id = $1
    #       AND t.business_dt = $2::date
    #       AND t.task_relative_id = $3;
    #     """,
    #     task.tg_user_id, task.business_dt, task.task_relative_id
    # )
    # if not current_task:
    #     raise HTTPException(status_code=404, detail="Task not found")

    # if task.task_start_dtm:
    #     task.task_start_dtm = parse_datetime(task.task_start_dtm)
    # if task.task_end_dtm:
    #     task.task_end_dtm = parse_datetime(task.task_end_dtm)
    #
    # # Обновляем только переданные поля
    # updated_task = {
    #     "task_name": task.task_name or current_task["task_name"],
    #     "task_status": task.task_status or current_task["task_status"],
    #     "task_category": task.task_category or current_task["task_category"],
    #     "task_description": task.task_description or current_task["task_description"],
    #     "task_start_dtm": task.task_start_dtm or current_task["task_start_dtm"],
    #     "task_end_dtm": task.task_end_dtm or current_task["task_end_dtm"],
    # }

    if task["task_start_dtm"] > task["task_end_dtm"]:
        raise HTTPException(status_code=404, detail="Task start dtm cannot be after end dtm")

    await conn.execute(
        """
        UPDATE tasks
        SET 
          task_name = $1, 
          task_status = $2, 
          task_category = $3,
          task_description = $4, 
          task_start_dtm = $5, 
          task_end_dtm = $6,
          updated_at=NOW()
        WHERE id = $7;
        """,
        task["task_name"], task["task_status"], task["task_category"],
        task["task_description"], task["task_start_dtm"], task["task_end_dtm"],
        task.id
    )
    return {"status": "success", "message": "Task updated"}


@app.delete("/tasks/delete")
async def delete_task(tasks: TasksDelete, conn=Depends(get_db)):
    if tasks.task_relative_id:
        result = await conn.execute(
            """
            DELETE FROM tasks
            WHERE id = (
              SELECT id FROM (
                SELECT 
                  id,
                  (task_start_dtm::date) AS business_dt,
                  ROW_NUMBER() OVER (
                    PARTITION BY tg_user_id, (task_start_dtm::date)
                    ORDER BY task_start_dtm
                  ) AS task_relative_id
                FROM tasks
                WHERE tg_user_id = $1
              ) t
              WHERE t.business_dt = $2::date AND t.task_relative_id = $3
            );
            """,
            tasks.tg_user_id, tasks.business_dt, tasks.task_relative_id
        )
    else:
        result = await conn.execute(
            """
            DELETE FROM tasks
            WHERE id IN (
              SELECT id FROM (
                SELECT 
                  id,
                  (task_start_dtm::date) AS business_dt,
                  ROW_NUMBER() OVER (
                    PARTITION BY tg_user_id, (task_start_dtm::date)
                    ORDER BY task_start_dtm
                  ) AS task_relative_id
                FROM tasks
                WHERE tg_user_id = $1
              ) t
              WHERE t.business_dt = $2::date
            );
            """,
            tasks.tg_user_id, tasks.business_dt
        )
    if result == "DELETE 0":
        raise HTTPException(status_code=404, detail="Task not found")
    return {"status": "success", "message": "Task deleted"}
