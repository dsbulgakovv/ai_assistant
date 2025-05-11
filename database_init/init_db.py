import logging
import hydra
import os

import pandas as pd
import asyncio

from sqlalchemy import text, create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from table_models import Base

from log_config import LogConfig
from logging.config import dictConfig


dictConfig(LogConfig().dict())
log = logging.getLogger("init_db")


async def is_table_empty(engine, table_name):
    async with AsyncSession(engine) as session:
        result = await session.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
        count = result.scalar()
        return count == 0


async def load_data(engine, dir_path, filename, table):
    log.info(f"Checking test file '{filename}' for table '{table}'...")
    try:
        # Check if table is empty
        if not await is_table_empty(engine, table):
            log.info(f'Table "{table}" already contains data, skipping...')
            return

        # Read CSV file
        df = pd.read_csv(os.path.join(dir_path, filename), encoding='utf8', sep=',')

        # Create a sync engine for pandas operations
        sync_engine = create_engine(engine.url.render_as_string(hide_password=False))

        # Rest of your pandas code using sync_engine
        df.to_sql(
            name=table,
            con=sync_engine,
            index=False,
            if_exists="append"
        )
    except Exception as e:
        log.info(f"Error: {e}")


async def async_main(cfg):
    db_name = os.getenv('DB_NAME')
    db_user = os.getenv('DB_USER')
    db_pass = os.getenv('DB_PASS')
    log.info(f"Connecting to database: '{db_name}'...")
    db_address = (
        f"{cfg.db.type}://{db_user}:{db_pass}@{cfg.db.host}:{cfg.db.port}/{db_name}"
    )
    log.info(f"Database address: '{db_address}'...")
    engine = create_async_engine(db_address, echo=True)
    log.info("Connection established!")

    # Создаем таблицы, если они не существуют
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    log.info("Tables verified!")

    dir_path = cfg.data.dir_path
    filenames = [
        # cfg.data.filenames.users, cfg.data.filenames.tasks,
        cfg.data.filenames.task_statuses_dict, cfg.data.filenames.task_categories_dict
    ]
    tables = [
        # cfg.db.tables.users, cfg.db.tables.tasks,
        cfg.db.tables.task_statuses_dict, cfg.db.tables.task_categories_dict
    ]

    # Загружаем данные только в пустые таблицы
    for i in range(len(filenames)):
        await load_data(engine, dir_path, filenames[i], tables[i])


@hydra.main(config_path="configs", config_name="cfg", version_base=None)
def main(cfg):
    asyncio.run(async_main(cfg))


if __name__ == "__main__":
    main()