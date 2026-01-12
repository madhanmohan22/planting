from pydantic import BaseModel, EmailStr, BeforeValidator
from pydantic import BaseModel, EmailStr, BeforeValidator
from typing import Optional, List
try:
    from typing import Annotated
except ImportError:
    from typing_extensions import Annotated
from datetime import date, datetime
from enum import Enum

class UserRole(str, Enum):
    ADMIN = "ADMIN"
    SUPER_MASTER = "SUPER_MASTER"
    DISTRIBUTOR = "DISTRIBUTOR"
    PLANT = "PLANT"

CoercedString = Annotated[str, BeforeValidator(str)]

class Token(BaseModel):
    access_token: str
    token_type: str
    role: str
    user_id: str


class TokenData(BaseModel):
    username: Optional[str] = None


class UserBase(BaseModel):
    username: str
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    company_name: Optional[str] = None
    contact_number: Optional[str] = None
    address: Optional[str] = None
    gst_number: Optional[str] = None

class UserCreate(UserBase):
    password: str
    role: UserRole

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    company_name: Optional[str] = None
    contact_number: Optional[str] = None
    address: Optional[str] = None
    email: Optional[EmailStr] = None
    gst_number: Optional[str] = None

class PasswordChange(BaseModel):
    old_password: str
    new_password: str

class UserResponse(UserBase):
    id: CoercedString

    role: UserRole
    is_active: bool
    created_at: Optional[datetime]
    
    class Config:
        from_attributes = True

# Plant Schemas
class PlantBase(BaseModel):
    name: str
    location: str
    manager_id: Optional[int] = None

class PlantCreate(PlantBase):
    pass

class PlantResponse(PlantBase):
    id: CoercedString
    manager_id: Optional[CoercedString] = None

    class Config:
        from_attributes = True

# Request Schemas
class DistributorRequestCreate(BaseModel):
    booking_date: date
    filled_14kg: int = 0
    filled_17kg: int = 0
    filled_19kg: int = 0
    filled_21kg: int = 0
    empty_14kg: int = 0
    empty_17kg: int = 0
    empty_19kg: int = 0
    empty_21kg: int = 0

class DistributorRequestResponse(DistributorRequestCreate):
    id: CoercedString

    distributor_id: CoercedString
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class AggregationRequest(BaseModel):
    distributor_request_ids: List[str]
    plant_id: str

class AggregatedRequestResponse(BaseModel):
    id: CoercedString
    super_master_id: CoercedString
    plant_id: CoercedString
    status: str
    created_at: datetime
    total_filled_cylinders: int = 0
    total_empty_cylinders: int = 0
    
    sum_filled_14kg: int = 0
    sum_filled_17kg: int = 0
    sum_filled_19kg: int = 0
    sum_filled_21kg: int = 0
    
    sum_empty_14kg: int = 0
    sum_empty_17kg: int = 0
    sum_empty_19kg: int = 0
    sum_empty_21kg: int = 0
    
    class Config:
        from_attributes = True

