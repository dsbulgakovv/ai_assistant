import logging
import hydra
import os
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from table_models import Base
from log_config import LogConfig
from logging.config import dictConfig

dictConfig(LogConfig().dict())
log = logging.getLogger("init_db")


def is_table_empty(engine, table_name):
    """Проверяет, пустая ли таблица (синхронная версия)"""
    with engine.connect() as conn:
        result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
        count = result.scalar()
        return count == 0


def load_data(engine, dir_path, filename, table):
    """Загружает данные из CSV в таблицу (синхронная версия)"""
    log.info(f"Checking test file '{filename}' for table '{table}'...")
    try:
        # Проверяем, пустая ли таблица
        if not is_table_empty(engine, table):
            log.info(f'Table "{table}" already contains data, skipping...')
            return

        # Читаем CSV файл
        file_path = os.path.join(dir_path, filename)
        df = pd.read_csv(file_path, encoding='utf8', sep=',')

        # Загружаем данные в БД
        with engine.begin() as conn:  # Автоматически коммитит транзакцию
            df.to_sql(
                name=table,
                con=conn,
                index=False,
                if_exists="append"
            )
        log.info(f"Data loaded successfully into {table}")

    except Exception as e:
        log.error(f"Error loading data into {table}: {e}")
        raise


def main(cfg):
    """Основная синхронная функция"""
    db_name = os.getenv('DB_NAME')
    db_user = os.getenv('DB_USER')
    db_pass = os.getenv('DB_PASS')

    log.info(f"Connecting to database: '{db_name}'...")
    db_address = f"postgresql://{db_user}:{db_pass}@{cfg.db.host}:{cfg.db.port}/{db_name}"
    log.info(f"Database address: '{db_address}'...")

    engine = create_engine(db_address, echo=True)

    try:
        # Проверяем соединение
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        log.info("Connection established!")

        # Создаем таблицы, если они не существуют
        Base.metadata.create_all(engine)
        log.info("Tables verified!")

        dir_path = cfg.data.dir_path
        filenames = [
            cfg.data.filenames.task_statuses_dict,
            cfg.data.filenames.task_categories_dict
        ]
        tables = [
            cfg.db.tables.task_statuses_dict,
            cfg.db.tables.task_categories_dict
        ]

        # Загружаем данные
        for filename, table in zip(filenames, tables):
            load_data(engine, dir_path, filename, table)

    except Exception as e:
        log.error(f"Error in main: {e}")
        raise
    finally:
        engine.dispose()
        log.info("Database connection closed.")


@hydra.main(config_path="configs", config_name="cfg", version_base=None)
def hydra_main(cfg):
    main(cfg)


if __name__ == "__main__":
    hydra_main()
