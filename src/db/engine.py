from .models import Base
from sqlalchemy.ext.asyncio import create_async_engine

import logging
logging.basicConfig()
logging.getLogger('sqlalchemy').setLevel(logging.ERROR)
logging.disable(logging.INFO)                   

engine = create_async_engine("postgresql+asyncpg://postgres:postgres@localhost:5432/postgres", echo=True, future=True)
# Base.metadata.create_all(engine)

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
