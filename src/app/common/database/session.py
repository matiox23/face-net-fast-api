from sqlalchemy import URL
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.app.common.setting import base_config

database_url: URL = URL.create(
    drivername="postgresql+asyncpg",
    host=base_config.database_host,
    username=base_config.database_username,
    password=base_config.database_password,
    port=base_config.database_port,
    database=base_config.database_name,
    query={"ssl": base_config.database_ssl},
)

engine: AsyncEngine = create_async_engine(
    database_url,
    echo=base_config.database_debug,
    pool_pre_ping=True,
    pool_size=base_config.database_pool_size,
    max_overflow=base_config.database_max_overflow,
    pool_recycle=base_config.database_pool_recycle,
)

AsyncSessionLocal: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def dispose_engine() -> None:
    await engine.dispose()
