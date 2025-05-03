import logging
import hydra
import os

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from table_models import Base


log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


@hydra.main(config_path="configs", config_name="cfg", version_base=None)
def main(cfg):

    log.info(f"Connection to the database: '{cfg.db.name}'...")
    db_name = os.getenv('DB_NAME')
    db_user = os.getenv('DB_USER')
    db_pass = os.getenv('DB_PASS')
    db_address = (
        f"{cfg.db.type}://{db_user}:"
        f"{db_pass}@{cfg.db.host}:"
        f"{cfg.db.port}/{db_name}"
    )

    engine = create_async_engine(db_address, echo=True)
    log.info("Connection established!")
    async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    async def create_tables():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    await create_tables()
    log.info("Tables created!")


if __name__ == "__main__":
    main()
