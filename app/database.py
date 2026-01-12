import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

# DATABASE_URL should be set as an environment variable in production (Render)
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "cockroachdb+asyncpg://noobu:yDhiczH4-4EZAsydz_Wbxg@fake-ayeaye-20209.j77.aws-ap-south-1.cockroachlabs.cloud:26257/defaultdb"
)

engine = create_async_engine(
    DATABASE_URL,
    echo=True, # Set to False in production
    connect_args={"server_settings": {"jit": "off"}}, # Optimization for CockroachDB
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession
)

Base = declarative_base()

async def get_db():
    async with SessionLocal() as session:
        yield session
