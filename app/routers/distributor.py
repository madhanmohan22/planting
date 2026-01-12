from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.future import select
from typing import List, Optional

from app.database import get_db
from app.models import User, UserRole, DistributorRequest
from app.schemas import DistributorRequestCreate, DistributorRequestResponse, UserResponse, UserUpdate
from app.dependencies import get_current_active_user

router = APIRouter(
    prefix="/distributor",
    tags=["distributor"],
    responses={404: {"description": "Not found"}},
)

async def check_distributor_role(current_user: User = Depends(get_current_active_user)):
    if current_user.role != UserRole.DISTRIBUTOR:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return current_user

# Profile Management
@router.get("/profile", response_model=UserResponse)
async def get_profile(current_user: User = Depends(check_distributor_role)):
    """Get distributor's own profile"""
    return current_user

@router.put("/profile", response_model=UserResponse)
async def update_profile(
    profile_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_distributor_role)
):
    """Update distributor's profile"""
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

# Order Management
@router.post("/requests", response_model=DistributorRequestResponse)
async def create_request(
    request: DistributorRequestCreate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(check_distributor_role)
):
    """Create a new order request"""
    db_request = DistributorRequest(
        distributor_id=current_user.id,
        booking_date=request.booking_date,
        filled_14kg=request.filled_14kg,
        filled_17kg=request.filled_17kg,
        filled_19kg=request.filled_19kg,
        filled_21kg=request.filled_21kg,
        empty_14kg=request.empty_14kg,
        empty_17kg=request.empty_17kg,
        empty_19kg=request.empty_19kg,
        empty_21kg=request.empty_21kg
    )
    db.add(db_request)
    await db.commit()
    await db.refresh(db_request)
    return db_request

@router.get("/requests", response_model=List[DistributorRequestResponse])
async def get_my_requests(
    db: Session = Depends(get_db), 
    current_user: User = Depends(check_distributor_role)
):
    """Get all requests (current endpoint for backwards compatibility)"""
    result = await db.execute(select(DistributorRequest).filter(DistributorRequest.distributor_id == current_user.id))
    return result.scalars().all()

@router.get("/requests/history", response_model=List[DistributorRequestResponse])
async def get_request_history(
    status_filter: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_distributor_role)
):
    """Get complete order history with optional status filter"""
    query = select(DistributorRequest).filter(DistributorRequest.distributor_id == current_user.id)
    
    if status_filter and status_filter.upper() != "ALL":
        query = query.filter(DistributorRequest.status == status_filter.upper())
    
    query = query.order_by(DistributorRequest.created_at.desc())
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/requests/{request_id}", response_model=DistributorRequestResponse)
async def get_request_details(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_distributor_role)
):
    """Get specific request details"""
    result = await db.execute(
        select(DistributorRequest).filter(
            DistributorRequest.id == request_id,
            DistributorRequest.distributor_id == current_user.id
        )
    )
    request = result.scalars().first()
    
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    
    return request

