import asyncio
from sqlalchemy import text
from app.database import engine, Base
from app.models import User, Plant, DistributorRequest, AggregatedRequest

async def init_models():
    async with engine.begin() as conn:
        # Drop all tables aggressively to clear schema mismatch
        await conn.execute(text("DROP TABLE IF EXISTS aggregated_requests CASCADE"))
        await conn.execute(text("DROP TABLE IF EXISTS distributor_requests CASCADE"))
        await conn.execute(text("DROP TABLE IF EXISTS plant_stock CASCADE"))
        await conn.execute(text("DROP TABLE IF EXISTS plants CASCADE"))
        await conn.execute(text("DROP TABLE IF EXISTS users CASCADE"))
        
        # Legacy tables if any
        await conn.execute(text("DROP TABLE IF EXISTS orders CASCADE"))
        await conn.execute(text("DROP TABLE IF EXISTS order_items CASCADE"))
        
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    print("Tables created successfully.")

if __name__ == "__main__":
    if asyncio.get_event_loop_policy().__class__.__name__ != 'WindowsSelectorEventLoopPolicy':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(init_models())
