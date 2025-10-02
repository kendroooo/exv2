"""
Virtual Machine schemas for req-rep validation
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from app.models.vm import VMStatus

class VMBase(BaseModel):
    """Base VM schema"""
    name: str = Field(
        ..., min_length=3, max_length=100, pattern="^[a-zA-Z0-9-]+$"
    )
    memory: Optional[int] = Field(None, ge=512, le=16384, description="Memory in MB")
    cores: Optional[int] = Field(None, ge=1, le=8, description="CPU Cores")
    disk: Optional[int] = Field(None, ge=10, le=200, description="Disk size in GB")

class VMCreate(VMBase):
    """Schema for creating a new Virtual Machine"""
    pass

class VMUpdate(BaseModel):
    """Schema for updating a VM"""
    name: Optional[str] = Field(
        None, min_length=3, max_length=100
    )
    memory: Optional[int] = Field(None, ge=512, le=16384)
    cores: Optional[int] = Field(None, ge=1, le=8)
    disk: Optional[int] = Field(None, ge=10, le=200)
    
class VMAction(BaseModel):
    """Schema for VM Actions"""
    action: str = Field(..., pattern="^(start|stop|restart|suspend|delete)$")

class VMResponse(VMBase):
    """Schema for VM Response"""
    id: int
    vmid: Optional[int] = None
    node: str
    ssh_port: Optional[int] = None
    ip_address: Optional[str] = None
    status: VMStatus
    status_message: Optional[str] = None
    owner_id: int
    created_at: datetime
    updated_at: datetime
    started_at: Optional[datetime] = None
    stopped_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class VMWithOwner(VMResponse):
    """Just added owner info"""
    owner: "UserResponse"

class VMStats(BaseModel):
    """VM Stats and resource usage"""
    vmid: int
    name: str
    status: str
    cpu_usage: Optional[float] = None
    memory_usage: Optional[int] = None
    memory_total: int
    disk_usage: Optional[int] = None
    disk_total: int
    uptime: Optional[int] = None
    network_in: Optional[int] = None
    network_out: Optional[int] = None

class VMListResponse(BaseModel):
    """Response for VM List with paginator"""
    vms: List[VMResponse]
    total: int
    page: int
    page_size: int

from app.schemas.user import UserResponse
VMWithOwner.model_rebuild()