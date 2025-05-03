import logging
import hydra
import os

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
# from sqlalchemy.orm import sessionmaker

from table_models import Base


log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


@hydra.main(config_path="configs", config_name="cfg", version_base=None)
async def main(cfg):

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
    # async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    log.info("Tables created!")


if __name__ == "__main__":
    main()
