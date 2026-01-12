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

async def seed_data():
    from app.auth import get_password_hash
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy.orm import sessionmaker
    
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # 1. Create Admin
        admin = User(
            username="admin",
            password_hash=get_password_hash("adminpassword"),
            role=UserRole.ADMIN,
            full_name="System Administrator"
        )
        session.add(admin)
        await session.flush()
        
        # 2. Create Plant Manager
        pm = User(
            username="plant1",
            password_hash=get_password_hash("plant123"),
            role=UserRole.PLANT,
            full_name="Mumbai Plant Manager"
        )
        session.add(pm)
        await session.flush()
        
        # 3. Create Super Master
        sm = User(
            username="supermaster1",
            password_hash=get_password_hash("super123"),
            role=UserRole.SUPER_MASTER,
            full_name="Regional Super Master"
        )
        session.add(sm)
        await session.flush()
        
        # 4. Create Distributor
        dist = User(
            username="distributor1",
            password_hash=get_password_hash("dist123"),
            role=UserRole.DISTRIBUTOR,
            full_name="Local Distributor",
            created_by_id=sm.id
        )
        session.add(dist)
        await session.flush()
        
        # 5. Create Plant
        plant = Plant(
            name="Mumbai Plant",
            location="Mumbai Central",
            manager_id=pm.id
        )
        session.add(plant)
        
        await session.commit()
        print("Seed data created successfully.")

async def main():
    await init_models()
    await seed_data()

if __name__ == "__main__":
    import sys
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
