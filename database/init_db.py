import logging
import hydra
import os

import pandas as pd
import asyncio


from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from table_models import Base


log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


async def async_main():
    db_name = os.getenv('DB_NAME')
    db_user = os.getenv('DB_USER')
    db_pass = os.getenv('DB_PASS')
    db_host = os.getenv('DB_HOST')
    db_port = os.getenv('DB_PORT')
    db_type = os.getenv('DB_TYPE')

    log.info(f"Connection to the database: '{db_name}'...")
    db_address = (
        f"{db_type}://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
    )
    log.info(f"Database address: '{db_address}'...")
    engine = create_async_engine(db_address, echo=True)
    log.info("Connection established!")

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    log.info("Tables created!")

    # log.info(f"Loading test file '{cfg.data.filenames.users}' to the database...")
    # try:
    #     # Чтение CSV файла
    #     df_users = pd.read_csv(cfg.data.dir_path + cfg.data.filenames.users)
    #
    #     # Проверка существования таблицы
    #     async with AsyncSession(engine) as session:
    #         # Проверяем существует ли таблица
    #         table_exists = await session.execute(
    #             text(
    #                 f"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = '{cfg.db.tables.users}')")
    #         )
    #         if table_exists.scalar():
    #             log.info(f'Table "{cfg.db.tables.users}" already exists!')
    #             raise ValueError("Table already exists")
    #
    #         # Создаем таблицу и загружаем данные
    #         async with session.begin():
    #             # Используем временный sync connection для pandas to_sql
    #             with engine.begin() as sync_conn:
    #                 df_users.to_sql(
    #                     name=cfg.db.tables.users,
    #                     con=sync_conn,
    #                     index=False,
    #                     if_exists="fail"
    #                 )
    #             log.info("Successfully loaded!")
    #
    # except ValueError as e:
    #     log.info(f'File "{cfg.data.filenames.users}" already loaded! Error: {str(e)}')
    # except Exception as e:
    #     log.error(f"Error loading file: {str(e)}")
    #     raise
    #
    # log.info(f"Loading test file '{cfg.data.filenames.tasks}' to the database...")
    # try:
    #     # Чтение CSV файла
    #     df_tasks = pd.read_csv(cfg.data.dir_path + cfg.data.filenames.tasks)
    #
    #     # Проверка существования таблицы
    #     async with AsyncSession(engine) as session:
    #         # Проверяем существует ли таблица
    #         table_exists = await session.execute(
    #             text(
    #                 f"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = '{cfg.db.tables.df_tasks}')")
    #         )
    #         if table_exists.scalar():
    #             log.info(f'Table "{cfg.db.tables.df_tasks}" already exists!')
    #             raise ValueError("Table already exists")
    #
    #         # Создаем таблицу и загружаем данные
    #         async with session.begin():
    #             # Используем временный sync connection для pandas to_sql
    #             with engine.begin() as sync_conn:
    #                 df_tasks.to_sql(
    #                     name=cfg.db.tables.users,
    #                     con=sync_conn,
    #                     index=False,
    #                     if_exists="fail"
    #                 )
    #             log.info("Successfully loaded!")
    #
    # except ValueError as e:
    #     log.info(f'File "{cfg.data.filenames.df_tasks}" already loaded! Error: {str(e)}')
    # except Exception as e:
    #     log.error(f"Error loading file: {str(e)}")
    #     raise


if __name__ == "__main__":
    asyncio.run(async_main())
