from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from sqlalchemy.future import select

from app.database import get_db
from app.models import User, UserRole
from app.schemas import Token, UserCreate, UserResponse, UserUpdate, PasswordChange
from app.auth import get_password_hash, verify_password, create_access_token
from app.core.config import settings
from app.dependencies import get_current_active_user

router = APIRouter()

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    try:
        result = await db.execute(select(User).filter(User.username == form_data.username))
        user = result.scalars().first()
        
        if not user or not verify_password(form_data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username, "role": user.role}, expires_delta=access_token_expires
        )
        
        # Convert user.id to string for serialization
        return {"access_token": access_token, "token_type": "bearer", "role": user.role, "user_id": str(user.id)}
    except Exception as e:
        print(f"LOGIN ERROR: {e}")
        import traceback
        traceback.print_exc()
        raise

@router.get("/users/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user

@router.put("/users/me", response_model=UserResponse)
async def update_user_me(user_update: UserUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    # Update allowed fields
    if user_update.full_name is not None:
        current_user.full_name = user_update.full_name
    if user_update.company_name is not None:
        current_user.company_name = user_update.company_name
    if user_update.contact_number is not None:
        current_user.contact_number = user_update.contact_number
    if user_update.address is not None:
        current_user.address = user_update.address
    if user_update.email is not None:
        current_user.email = user_update.email
    if user_update.gst_number is not None:
        current_user.gst_number = user_update.gst_number
    
    await db.commit()
    await db.refresh(current_user)
    return current_user

@router.post("/users/change-password")
async def change_password(password_data: PasswordChange, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    if not verify_password(password_data.old_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect old password")
    
    current_user.password_hash = get_password_hash(password_data.new_password)
    await db.commit()
    return {"message": "Password updated successfully"}

# Initial Admin Creation Endpoint (To be used once locally or secured)
@router.post("/admin/init", response_model=UserResponse)
async def create_init_admin(user: UserCreate, db: Session = Depends(get_db)):
    # Check if username exists
    existing = await db.execute(select(User).filter(User.username == user.username))
    existing_user = existing.scalars().first()
    if existing_user:
        return existing_user

    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        password_hash=hashed_password,
        role=user.role,
        full_name=user.full_name,
        company_name=user.company_name
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user
