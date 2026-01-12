from sqlalchemy import Column, Integer, BigInteger, String, Boolean, ForeignKey, Enum, DateTime, Float, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.database import Base

class UserRole(str, enum.Enum):
    ADMIN = "ADMIN"
    SUPER_MASTER = "SUPER_MASTER"
    DISTRIBUTOR = "DISTRIBUTOR"
    PLANT = "PLANT"

class RequestStatus(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED" # Approved by SM
    REJECTED = "REJECTED"
    AGGREGATED = "AGGREGATED" # Sent to Plant
    COMPLETED = "COMPLETED"

class AggregatedStatus(str, enum.Enum):
    PENDING_PLANT = "PENDING_PLANT"
    DISPATCHED_PLANT = "DISPATCHED_PLANT" # Plant dispatched
    RECEIVED_SM = "RECEIVED_SM" # SM received, ready to distribute

class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=True)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False) 
    is_active = Column(Boolean, default=True)
    
    # Profile Information
    full_name = Column(String, nullable=True)
    company_name = Column(String, nullable=True)
    contact_number = Column(String, nullable=True)
    address = Column(String, nullable=True)
    gst_number = Column(String, nullable=True)
    
    # Hierarchy
    created_by_id = Column(BigInteger, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    requests = relationship("DistributorRequest", back_populates="distributor", foreign_keys="DistributorRequest.distributor_id")
    aggregated_orders = relationship("AggregatedRequest", back_populates="super_master")

class Plant(Base):
    __tablename__ = "plants"
    
    id = Column(BigInteger, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    location = Column(String, nullable=False)
    manager_id = Column(BigInteger, ForeignKey("users.id"), unique=True)
    
    aggregated_requests = relationship("AggregatedRequest", back_populates="plant")
    stock = relationship("PlantStock", back_populates="plant")

class PlantStock(Base):
    __tablename__ = "plant_stock"
    
    id = Column(BigInteger, primary_key=True, index=True)
    plant_id = Column(BigInteger, ForeignKey("plants.id"))
    item_name = Column(String, nullable=False)
    quantity_filled = Column(Integer, default=0)
    quantity_empty = Column(Integer, default=0)
    
    plant = relationship("Plant", back_populates="stock")

class DistributorRequest(Base):
    __tablename__ = "distributor_requests"

    id = Column(BigInteger, primary_key=True, index=True)
    distributor_id = Column(BigInteger, ForeignKey("users.id"))
    booking_date = Column(Date, nullable=False)
    status = Column(String, default=RequestStatus.PENDING)
    
    # Linked to an aggregated order once approved and processed
    aggregated_request_id = Column(BigInteger, ForeignKey("aggregated_requests.id"), nullable=True)

    # Filled Quantities
    filled_14kg = Column(Integer, default=0)
    filled_17kg = Column(Integer, default=0)
    filled_19kg = Column(Integer, default=0)
    filled_21kg = Column(Integer, default=0)

    # Empty Return Quantities
    empty_14kg = Column(Integer, default=0)
    empty_17kg = Column(Integer, default=0)
    empty_19kg = Column(Integer, default=0)
    empty_21kg = Column(Integer, default=0)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    distributor = relationship("User", back_populates="requests")
    aggregated_request = relationship("AggregatedRequest", back_populates="distributor_requests")

class AggregatedRequest(Base):
    __tablename__ = "aggregated_requests"

    id = Column(BigInteger, primary_key=True, index=True)
    super_master_id = Column(BigInteger, ForeignKey("users.id"))
    plant_id = Column(BigInteger, ForeignKey("plants.id"), nullable=True)
    status = Column(String, default=AggregatedStatus.PENDING_PLANT)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    super_master = relationship("User", back_populates="aggregated_orders")
    plant = relationship("Plant", back_populates="aggregated_requests")
    distributor_requests = relationship("DistributorRequest", back_populates="aggregated_request")

    # Helper methods to get totals
    @property
    def total_filled_cylinders(self):
        return sum(
            (r.filled_14kg or 0) + (r.filled_17kg or 0) + (r.filled_19kg or 0) + (r.filled_21kg or 0)
            for r in self.distributor_requests
        )

    @property
    def total_empty_cylinders(self):
        return sum(
            (r.empty_14kg or 0) + (r.empty_17kg or 0) + (r.empty_19kg or 0) + (r.empty_21kg or 0)
            for r in self.distributor_requests
        )

    @property
    def sum_filled_14kg(self): return sum((r.filled_14kg or 0) for r in self.distributor_requests)
    @property
    def sum_filled_17kg(self): return sum((r.filled_17kg or 0) for r in self.distributor_requests)
    @property
    def sum_filled_19kg(self): return sum((r.filled_19kg or 0) for r in self.distributor_requests)
    @property
    def sum_filled_21kg(self): return sum((r.filled_21kg or 0) for r in self.distributor_requests)

    @property
    def sum_empty_14kg(self): return sum((r.empty_14kg or 0) for r in self.distributor_requests)
    @property
    def sum_empty_17kg(self): return sum((r.empty_17kg or 0) for r in self.distributor_requests)
    @property
    def sum_empty_19kg(self): return sum((r.empty_19kg or 0) for r in self.distributor_requests)
    @property
    def sum_empty_21kg(self): return sum((r.empty_21kg or 0) for r in self.distributor_requests)
