from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, selectinload
from sqlalchemy.future import select
from typing import List, Optional

from app.database import get_db
from app.models import User, UserRole, Plant, AggregatedRequest, AggregatedStatus
from app.schemas import AggregatedRequestResponse, UserResponse, UserUpdate
from app.dependencies import get_current_active_user

router = APIRouter(
    prefix="/plant",
    tags=["plant"],
    responses={404: {"description": "Not found"}},
)

async def check_plant_role(current_user: User = Depends(get_current_active_user)):
    if current_user.role != UserRole.PLANT:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return current_user

@router.get("/requests/pending", response_model=List[AggregatedRequestResponse])
async def get_plant_pending_requests(
    db: Session = Depends(get_db),
    current_user: User = Depends(check_plant_role)
):
    # Find the plant managed by this user
    plant_res = await db.execute(select(Plant).filter(Plant.manager_id == current_user.id))
    plant = plant_res.scalars().first()
    if not plant:
        return []

    # Fetch aggregated requests for this plant
    result = await db.execute(
        select(AggregatedRequest)
        .options(selectinload(AggregatedRequest.distributor_requests))
        .filter(
            AggregatedRequest.plant_id == plant.id,
            AggregatedRequest.status == AggregatedStatus.PENDING_PLANT
        )
    )
    return result.scalars().all()

@router.post("/dispatch/{request_id}")
async def dispatch_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_plant_role)
):
    # Find plant
    plant_res = await db.execute(select(Plant).filter(Plant.manager_id == current_user.id))
    plant = plant_res.scalars().first()
    if not plant:
        raise HTTPException(status_code=404, detail="Plant not found")

    # Find request
    req_res = await db.execute(select(AggregatedRequest).filter(AggregatedRequest.id == request_id))
    req = req_res.scalars().first()
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
    
    if req.plant_id != plant.id:
        raise HTTPException(status_code=403, detail="Not authorized for this request")
        
    req.status = AggregatedStatus.DISPATCHED_PLANT
    await db.commit()
    
    return {"message": "Order dispatched successfully"}

# Profile Management
@router.get("/profile", response_model=UserResponse)
async def get_profile(current_user: User = Depends(check_plant_role)):
    """Get Plant's own profile"""
    return current_user

@router.put("/profile", response_model=UserResponse)
async def update_profile(
    profile_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_plant_role)
):
    """Update Plant's profile"""
    if profile_update.full_name is not None:
        current_user.full_name = profile_update.full_name
    if profile_update.company_name is not None:
        current_user.company_name = profile_update.company_name
    if profile_update.contact_number is not None:
        current_user.contact_number = profile_update.contact_number
    if profile_update.address is not None:
        current_user.address = profile_update.address
    if profile_update.email is not None:
        current_user.email = profile_update.email
    if profile_update.gst_number is not None:
        current_user.gst_number = profile_update.gst_number
    
    await db.commit()
    await db.refresh(current_user)
    return current_user

# Get Super Masters
@router.get("/super-masters", response_model=List[UserResponse])
async def get_super_masters(
    db: Session = Depends(get_db),
    current_user: User = Depends(check_plant_role)
):
    """Get all Super Masters who have sent requests to this plant"""
    # Find the plant managed by this user
    plant_res = await db.execute(select(Plant).filter(Plant.manager_id == current_user.id))
    plant = plant_res.scalars().first()
    
    if not plant:
        return []
    
    # Get unique Super Masters who created aggregated requests for this plant
    result = await db.execute(
        select(User)
        .join(AggregatedRequest, User.id == AggregatedRequest.super_master_id)
        .filter(AggregatedRequest.plant_id == plant.id)
        .distinct()
    )
    return result.scalars().all()

# Request History
@router.get("/requests/all", response_model=List[AggregatedRequestResponse])
async def get_all_requests(
    status_filter: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_plant_role)
):
    """Get all requests history with optional status filter"""
    # Find plant
    plant_res = await db.execute(select(Plant).filter(Plant.manager_id == current_user.id))
    plant = plant_res.scalars().first()
    if not plant:
        return []
    
    query = select(AggregatedRequest).options(selectinload(AggregatedRequest.distributor_requests)).filter(AggregatedRequest.plant_id == plant.id)
    
    if status_filter and status_filter.upper() != "ALL":
        query = query.filter(AggregatedRequest.status == status_filter.upper())
    
    query = query.order_by(AggregatedRequest.created_at.desc())
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/requests/history", response_model=List[AggregatedRequestResponse])
async def get_dispatch_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(check_plant_role)
):
    """Get complete dispatch history"""
    # Find plant
    plant_res = await db.execute(select(Plant).filter(Plant.manager_id == current_user.id))
    plant = plant_res.scalars().first()
    if not plant:
        return []
    
    result = await db.execute(
        select(AggregatedRequest)
        .options(selectinload(AggregatedRequest.distributor_requests))
        .filter(AggregatedRequest.plant_id == plant.id)
        .order_by(AggregatedRequest.created_at.desc())
    )
    return result.scalars().all()
