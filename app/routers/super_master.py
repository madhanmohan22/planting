from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, selectinload
from sqlalchemy.future import select
from typing import List, Optional
from pydantic import BaseModel

from app.database import get_db
from app.models import User, UserRole, DistributorRequest, Plant, AggregatedRequest, RequestStatus, AggregatedStatus
from app.schemas import UserCreate, UserResponse, DistributorRequestResponse, PlantResponse, AggregationRequest, AggregatedRequestResponse, UserUpdate
from app.auth import get_password_hash
from app.dependencies import get_current_active_user

router = APIRouter(
    prefix="/super-master",
    tags=["super-master"],
    responses={404: {"description": "Not found"}},
)

async def check_super_master_role(current_user: User = Depends(get_current_active_user)):
    if current_user.role != UserRole.SUPER_MASTER and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return current_user

@router.post("/distributors", response_model=UserResponse)
async def create_distributor(user: UserCreate, db: Session = Depends(get_db), current_user: User = Depends(check_super_master_role)):
    # Check username
    result = await db.execute(select(User).filter(User.username == user.username))
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Username already registered")
    
    if user.role != UserRole.DISTRIBUTOR:
        raise HTTPException(status_code=400, detail="Role must be DISTRIBUTOR")

    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        password_hash=hashed_password,
        role=UserRole.DISTRIBUTOR,
        full_name=user.full_name,
        company_name=user.company_name,
        contact_number=user.contact_number,
        address=user.address,
        created_by_id=current_user.id
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

@router.get("/requests/pending", response_model=List[DistributorRequestResponse])
async def get_pending_requests(
    db: Session = Depends(get_db),
    current_user: User = Depends(check_super_master_role)
):
    # If SM or Admin, show all pending requests in this environment
    query = select(DistributorRequest).join(User, DistributorRequest.distributor_id == User.id).filter(
        DistributorRequest.status == RequestStatus.PENDING
    )
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/plants", response_model=List[PlantResponse])
async def get_plants(
    db: Session = Depends(get_db),
    current_user: User = Depends(check_super_master_role)
):
    result = await db.execute(select(Plant))
    return result.scalars().all()

@router.post("/aggregate", response_model=AggregatedRequestResponse)
async def aggregate_requests(
    payload: AggregationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_super_master_role)
):
    plant_id_int = int(payload.plant_id)
    dist_req_ids_int = [int(x) for x in payload.distributor_request_ids]

    plant_res = await db.execute(select(Plant).filter(Plant.id == plant_id_int))
    plant = plant_res.scalars().first()
    if not plant:
        raise HTTPException(status_code=404, detail="Plant not found")

    aggregated_req = AggregatedRequest(
        super_master_id=current_user.id,
        plant_id=plant_id_int,
        status=AggregatedStatus.PENDING_PLANT
    )
    db.add(aggregated_req)
    await db.flush()

    # If SM or Admin, allow aggregation of any APPROVED request in this environment
    stmt = select(DistributorRequest).join(User).filter(
        DistributorRequest.id.in_(dist_req_ids_int),
        DistributorRequest.status == RequestStatus.APPROVED
    )
    result = await db.execute(stmt)
    requests_to_update = result.scalars().all()

    if len(requests_to_update) != len(payload.distributor_request_ids):
        raise HTTPException(status_code=400, detail="Some requests are invalid or not under your control")

    for req in requests_to_update:
        req.status = RequestStatus.AGGREGATED
        req.aggregated_request_id = aggregated_req.id
    
    await db.commit()
    await db.refresh(aggregated_req)
    return aggregated_req

@router.get("/profile", response_model=UserResponse)
async def get_profile(current_user: User = Depends(check_super_master_role)):
    return current_user

@router.put("/profile", response_model=UserResponse)
async def update_profile(
    profile_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_super_master_role)
):
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

@router.get("/distributors", response_model=List[UserResponse])
async def get_distributors(
    db: Session = Depends(get_db),
    current_user: User = Depends(check_super_master_role)
):
    query = select(User).filter(User.role == UserRole.DISTRIBUTOR)
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/distributors/{distributor_id}", response_model=UserResponse)
async def get_distributor_details(
    distributor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_super_master_role)
):
    query = select(User).filter(User.id == distributor_id, User.role == UserRole.DISTRIBUTOR)
    result = await db.execute(query)
    distributor = result.scalars().first()
    if not distributor:
        raise HTTPException(status_code=404, detail="Distributor not found")
    return distributor

@router.delete("/distributors/{distributor_id}")
async def deactivate_distributor(
    distributor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_super_master_role)
):
    query = select(User).filter(User.id == distributor_id, User.role == UserRole.DISTRIBUTOR)
    result = await db.execute(query)
    distributor = result.scalars().first()
    if not distributor:
        raise HTTPException(status_code=404, detail="Distributor not found")
    distributor.is_active = False
    await db.commit()
    return {"message": "Distributor deactivated successfully"}

class RequestApproval(BaseModel):
    approved: bool
    rejection_reason: Optional[str] = None

@router.put("/requests/{request_id}/approve")
async def approve_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_super_master_role)
):
    query = select(DistributorRequest).join(User, DistributorRequest.distributor_id == User.id).filter(
        DistributorRequest.id == request_id,
        DistributorRequest.status == RequestStatus.PENDING
    )
    result = await db.execute(query)
    request = result.scalars().first()
    
    if not request:
        raise HTTPException(status_code=404, detail="Request not found or already processed")
    
    request.status = RequestStatus.APPROVED
    await db.commit()
    return {"message": "Request approved successfully", "request_id": request_id}

@router.put("/requests/{request_id}/reject")
async def reject_request(
    request_id: int,
    rejection_data: RequestApproval,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_super_master_role)
):
    query = select(DistributorRequest).join(User, DistributorRequest.distributor_id == User.id).filter(
        DistributorRequest.id == request_id,
        DistributorRequest.status == RequestStatus.PENDING
    )
    result = await db.execute(query)
    request = result.scalars().first()
    
    if not request:
        raise HTTPException(status_code=404, detail="Request not found or already processed")
    
    request.status = RequestStatus.REJECTED
    await db.commit()
    return {"message": "Request rejected", "request_id": request_id, "reason": rejection_data.rejection_reason}

@router.get("/requests/all", response_model=List[DistributorRequestResponse])
async def get_all_requests(
    status_filter: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(check_super_master_role)
):
    query = select(DistributorRequest).join(User, DistributorRequest.distributor_id == User.id)
    if status_filter and status_filter.upper() != "ALL":
        query = query.filter(DistributorRequest.status == status_filter.upper())
    result = await db.execute(query.order_by(DistributorRequest.created_at.desc()))
    return result.scalars().all()

@router.get("/history", response_model=List[AggregatedRequestResponse])
async def get_aggregation_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(check_super_master_role)
):
    query = select(AggregatedRequest).options(selectinload(AggregatedRequest.distributor_requests))
    result = await db.execute(query.order_by(AggregatedRequest.created_at.desc()))
    return result.scalars().all()
