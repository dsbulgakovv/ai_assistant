from fastapi import FastAPI, Depends
from fastapi.responses import JSONResponse
from fastapi import HTTPException

import asyncpg

import logging
from logging.config import dictConfig

import os
from contextlib import asynccontextmanager
from pydantic import BaseModel
from typing import Dict, Any

from log_config import LogConfig


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


class TaskCreate(BaseModel):
    tg_user_id: int
    task_name: str
    task_status: int
    task_category: int
    task_description: str
    task_start_dtm: str
    task_end_dtm: str


class TaskUpdate(BaseModel):
    tg_user_id: int
    task_name: str
    task_status: int
    task_category: int
    task_description: str
    task_start_dtm: str
    task_end_dtm: str


class TaskResponse(BaseModel):
    status: str
    message: str
    data: Dict[str, Any] | None = None


async def get_db():
    async with app.state.pool.acquire() as connection:
        yield connection


@app.get("/")
async def root():
    return JSONResponse(content={"message": "Service to transfer data between PostgreSQL and Telegram bot."})


@app.get("/users/{tg_user_id}")
async def get_user(tg_user_id: int, conn=Depends(get_db)):
    return await conn.fetchrow("SELECT * FROM users WHERE tg_user_id = $1", tg_user_id)


@app.get("/tasks/{tg_user_id}/{task_start_dtm}/{task_end_dtm}")
async def get_filtered_tasks(tg_user_id: int, task_start_dtm: str, task_end_dtm: str, conn=Depends(get_db)):
    return await conn.fetchrow(
        """
        SELECT
            *,
            (task_start_dtm::date) AS business_dt,
            ROW_NUMBER() OVER (
                PARTITION BY tg_user_id, (task_start_dtm::date)
                ORDER BY task_start_dtm
            ) AS task_relative_id
        FROM tasks
        WHERE
            tg_user_id = $1,
            AND task_start_dtm >= $2,
            AND task_end_dtm <= $3
        """,
        tg_user_id, task_start_dtm, task_end_dtm
    )


@app.post("/users/add_new", status_code=201)
async def create_user(user: UserCreate, conn=Depends(get_db)):
    try:
        await conn.execute(
            """
            INSERT INTO users (tg_user_id, username, full_name, reg_dt, last_usage_dt)
            VALUES ($1, $2, $3, NOW(), NOW())
            ON CONFLICT (tg_user_id) DO NOTHING
            """,
            user.tg_user_id, user.username, user.full_name
        )
        return {"status": "success", "message": "User created or already exists"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/tasks/add_new", status_code=201)
async def create_task(task: TaskCreate, conn=Depends(get_db)):
    try:
        await conn.execute(
            """
            INSERT INTO tasks (
                tg_user_id, task_name, task_status, task_category, task_description,
                task_start_dtm, task_end_dtm, created_at, updated_at
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            """,
            task.tg_user_id, task.task_name, task.task_status, task.task_category,
            task.task_description, task.task_start_dtm, task.task_end_dtm
        )
        return {"status": "success", "message": "Task created"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.put("/tasks/{tg_user_id}/{business_dt}/{task_relative_id}")
async def update_task(tg_user_id: int, business_dt: str, task_relative_id: int, task: TaskUpdate, conn=Depends(get_db)):
    try:
        # Получаем текущие данные задачи
        current_task = await conn.fetchrow(
            """
            SELECT * FROM (
              SELECT 
                *,
                (task_start_dtm::date) AS business_dt,
                ROW_NUMBER() OVER (
                  PARTITION BY tg_user_id, (task_start_dtm::date)
                  ORDER BY task_start_dtm
                ) AS task_relative_id
              FROM tasks
            ) t
            WHERE 
              t.tg_user_id = $1 
              AND t.business_dt = $2::date
              AND t.task_relative_id = $3;
            """,
            tg_user_id, business_dt, task_relative_id
        )
        if not current_task:
            raise HTTPException(status_code=404, detail="Task not found")

        # Обновляем только переданные поля
        updated_task = {
            "task_name": task.task_name or current_task["task_name"],
            "task_status": task.task_status or current_task["task_status"],
            "task_category": task.task_category or current_task["task_category"],
            "task_description": task.task_description or current_task["task_description"],
            "task_start_dtm": task.task_start_dtm or current_task["task_start_dtm"],
            "task_end_dtm": task.task_end_dtm or current_task["task_end_dtm"],
        }

        await conn.execute(
            """
            UPDATE tasks
            SET 
              task_name = $1, 
              task_status = $2, 
              task_category = $3,
              task_description = $4, 
              task_start_dtm = $5, 
              task_end_dtm = $6
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
                WHERE tg_user_id = $7
              ) t
              WHERE t.business_dt = $8::date AND t.task_relative_id = $9
            );
            """,
            updated_task["task_name"], updated_task["task_status"], updated_task["task_category"],
            updated_task["task_description"], updated_task["task_start_dtm"], updated_task["task_end_dtm"],
            tg_user_id, business_dt, task_relative_id
        )
        return {"status": "success", "message": "Task updated"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/tasks/{tg_user_id}/{business_dt}/{task_relative_id}")
async def delete_task(tg_user_id: int, business_dt: str, task_relative_id: int, conn=Depends(get_db)):
    try:
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
            tg_user_id, business_dt, task_relative_id
        )
        if result == "DELETE 0":
            raise HTTPException(status_code=404, detail="Task not found")
        return {"status": "success", "message": "Task deleted"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
