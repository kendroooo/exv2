"""
Port Forward schemas for req-rep validation
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime

class PortForwardBase(BaseModel):
    """Base port forward schema"""
    external_port: int = Field(..., ge=1024, le=65535)
    internal_port: int = Field(default=22, ge=1, le=65535)
    internal_ip: str = Field(..., pattern="^(?:[0-9{1,3}\.){3}[0-9]{1,3}$")
    protocol: str = Field(default="tcp", pattern="^(tcp|udp|both)$")
    description: Optional[str] = Field(None, max_length=500)

class PortForwardCreate(PortForwardBase):
    """Schema for creating a port forward"""
    vm_id: int

class PortForwardUpdate(BaseModel):
    """Schema for updating a port forward"""
    is_active: Optional[bool] = None
    description: Optional[str] = Field(None, max_length=500)

class PortForwardResponse(PortForwardBase):
    """Schema for port forward response"""
    id: int
    unifi_rule_id: Optional[str] = None
    is_active: bool
    vm_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)