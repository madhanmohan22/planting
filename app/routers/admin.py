from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.future import select
from typing import List, Optional

from app.database import get_db
from app.models import User, UserRole, Plant
from app.schemas import UserCreate, UserResponse, PlantCreate, PlantResponse, UserUpdate
from app.auth import get_password_hash
from app.dependencies import get_current_active_user

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    responses={404: {"description": "Not found"}},
)

async def check_admin_role(current_user: User = Depends(get_current_active_user)):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return current_user

@router.post("/super-masters", response_model=UserResponse)
async def create_super_master(user: UserCreate, db: Session = Depends(get_db), admin: User = Depends(check_admin_role)):
    import traceback
    try:
        # Check username
        result = await db.execute(select(User).filter(User.username == user.username))
        if result.scalars().first():
            raise HTTPException(status_code=400, detail="Username already registered")
            
        # Check email
        result = await db.execute(select(User).filter(User.email == user.email))
        if result.scalars().first():
            raise HTTPException(status_code=400, detail="Email already registered")
        
        if user.role != UserRole.SUPER_MASTER:
            raise HTTPException(status_code=400, detail="Role must be SUPER_MASTER")

        hashed_password = get_password_hash(user.password)
        db_user = User(
            username=user.username,
            email=user.email,
            password_hash=hashed_password,
            role=UserRole.SUPER_MASTER.value, # Explicitly use .value just in case
            full_name=user.full_name,
            company_name=user.company_name,
            contact_number=user.contact_number,
            address=user.address,
            created_by_id=admin.id
        )
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        return db_user
    except Exception as e:
        with open("error.log", "w") as f:
            f.write(traceback.format_exc())
        raise e

@router.post("/plants", response_model=PlantResponse)
async def create_plant(plant: PlantCreate, db: Session = Depends(get_db), admin: User = Depends(check_admin_role)):
    # Check plant name
    result = await db.execute(select(Plant).filter(Plant.name == plant.name))
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Plant already exists")
        
    db_plant = Plant(
        name=plant.name,
        location=plant.location,
        manager_id=plant.manager_id 
    )
    db.add(db_plant)
    await db.commit()
    await db.refresh(db_plant)
    return db_plant

@router.post("/plant-managers", response_model=UserResponse)
async def create_plant_manager(user: UserCreate, db: Session = Depends(get_db), admin: User = Depends(check_admin_role)):
    # Check username
    result = await db.execute(select(User).filter(User.username == user.username))
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Username already registered")

    # Check email
    result = await db.execute(select(User).filter(User.email == user.email))
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    if user.role != UserRole.PLANT:
        raise HTTPException(status_code=400, detail="Role must be PLANT")

    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        password_hash=hashed_password,
        role=UserRole.PLANT,
        full_name=user.full_name,
        company_name=user.company_name,
        contact_number=user.contact_number,
        address=user.address,
        created_by_id=admin.id
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

# User Management
@router.get("/users", response_model=List[UserResponse])
async def get_all_users(
    role_filter: Optional[str] = None,
    status_filter: Optional[str] = None,
    db: Session = Depends(get_db),
    admin: User = Depends(check_admin_role)
):
    """Get all users with optional filters"""
    query = select(User)
    
    if role_filter and role_filter.upper() != "ALL":
        query = query.filter(User.role == role_filter.upper())
    
    if status_filter:
        is_active = status_filter.lower() == "active"
        query = query.filter(User.is_active == is_active)
    
    query = query.order_by(User.created_at.desc())
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user_details(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(check_admin_role)
):
    """Get specific user details"""
    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalars().first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user

@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(check_admin_role)
):
    """Update user profile (admin override)"""
    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalars().first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update fields
    if user_update.full_name is not None:
        user.full_name = user_update.full_name
    if user_update.company_name is not None:
        user.company_name = user_update.company_name
    if user_update.contact_number is not None:
        user.contact_number = user_update.contact_number
    if user_update.address is not None:
        user.address = user_update.address
    if user_update.email is not None:
        user.email = user_update.email
    if user_update.gst_number is not None:
        user.gst_number = user_update.gst_number
    
    await db.commit()
    await db.refresh(user)
    return user

@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(check_admin_role)
):
    """Soft delete user (deactivate)"""
    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalars().first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.role == UserRole.ADMIN:
        raise HTTPException(status_code=400, detail="Cannot delete admin users")
    
    user.is_active = False
    await db.commit()
    
    return {"message": "User deactivated successfully"}

@router.post("/users/{user_id}/reactivate")
async def reactivate_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(check_admin_role)
):
    """Reactivate a deactivated user"""
    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalars().first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.is_active = True
    await db.commit()
    
    return {"message": "User reactivated successfully"}
