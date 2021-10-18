from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from functools import lru_cache
from server.dependencies.get_environment_cached import get_environment_cached


Base = declarative_base()


@lru_cache
def create_async_engine_cached():
    environment = get_environment_cached()
    return create_async_engine(
        environment.get_db_conn_async(environment.DATABASE_URL),
        echo=environment.DB_ECHO,
        pool_size=environment.DB_POOL_SIZE,
        max_overflow=environment.DB_MAX_OVERFLOW,
        pool_pre_ping=environment.DB_POOL_PRE_PING
    )


def build_async_session_maker():
    return sessionmaker(
        create_async_engine_cached(),
        expire_on_commit=False,
        class_=AsyncSession
    )

