from server.configuration.db import AsyncSession, build_async_session_maker


async def get_session() -> AsyncSession:
    session_maker = build_async_session_maker()
    async with session_maker() as session:
        yield session

