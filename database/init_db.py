import logging
import hydra
import os

import pandas as pd
import asyncio


from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from table_models import Base

from log_config import LogConfig
from logging.config import dictConfig


dictConfig(LogConfig().dict())
logger = logging.getLogger("init_db")


def load_data(cfg, engine, dir_path, filename, table):
    log.info(f"Loading test file '{filename}' to the database...")
    try:
        # Чтение CSV файла
        df_users = pd.read_csv(dir_path + filename, encoding='utf8', sep=',')

        # Проверка существования таблицы
        async with AsyncSession(engine) as session:
            # Проверяем существует ли таблица
            table_exists = await session.execute(
                text(f"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = '{table}')")
            )
            if table_exists.scalar():
                log.info(f'Table "{table}" already exists!')
                raise ValueError("Table already exists")

            # Создаем таблицу и загружаем данные
            async with session.begin():
                # Используем временный sync connection для pandas to_sql
                with engine.begin() as sync_conn:
                    df_users.to_sql(
                        name=cfg.db.tables.users,
                        con=sync_conn,
                        index=False,
                        if_exists="fail"
                    )
                log.info("Successfully loaded!")

    except ValueError as e:
        log.info(f'File "{filename}" already loaded! Error: {str(e)}')
    except Exception as e:
        log.error(f"Error loading file: {str(e)}")
        raise


async def async_main(cfg):
    db_name = os.getenv('DB_NAME')
    db_user = os.getenv('DB_USER')
    db_pass = os.getenv('DB_PASS')
    log.info(f"Connection to the database: '{db_name}'...")
    db_address = (
        f"{cfg.db.type}://{db_user}:{db_pass}@{cfg.db.host}:{cfg.db.port}/{db_name}"
    )
    log.info(f"Database address: '{db_address}'...")
    engine = create_async_engine(db_address, echo=True)
    log.info("Connection established!")

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    log.info("Tables created!")

    dir_path = cfg.data.dir_path
    filenames = [
        cfg.data.filenames.users, cfg.data.filenames.tasks,
        cfg.data.filenames.task_statuses_dict, cfg.data.filenames.task_categories_dict
    ]
    tables = [
        cfg.data.tables.users, cfg.data.tables.tasks,
        cfg.data.tables.task_statuses_dict, cfg.data.tables.task_categories_dict
    ]

    for i in range(len(filenames)):
        load_data(cfg, engine, dir_path, filenames[i], tables[i])


@hydra.main(config_path="configs", config_name="cfg", version_base=None)
def main(cfg):
    # Запускаем асинхронный код
    asyncio.run(async_main(cfg))


if __name__ == "__main__":
    main()
