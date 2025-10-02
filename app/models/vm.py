"""
Model[VM]

Tracks VM State, config, usage and ownership and stuff
"""

from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator
from enum import Enum, auto
from typing import Optional

class LowerStr(str, Enum):

    def _generate_next_value_(name, start, count, last_values):
        return name.lower()

class VMStatus(LowerStr):
    """VM Status Enum"""
    PENDING = auto()
    CREATING = auto()
    RUNNING = auto()
    STOPPED = auto()
    SUSPENDED = auto()
    ERROR = auto()
    DELETING = auto()
    DELETED = auto()

class VirtualMachine(models.Model):
    """
    Virtual Machine model linked to Proxmox QEMU VMs
    for tracking VM metadata and relationships
    """

    id = fields.IntField(pk=True)

    vmid = fields.IntField(
        unique=True, null=True, index=True
    )
    node = fields.CharField(max_length=100)
    name = fields.CharField(max_length=100)

    memory = fields.IntField(default=4096)
    cores = fields.IntField(default=4)
    disk = fields.IntField(default=20)

    ssh_port = fields.IntField(
        unique=True, null=True
    )
    ip_address = fields.CharField(max_length=45, null=True)

    status = fields.CharEnumField(VMStatus, default=VMStatus.PENDING)
    status_message = fields.TextField(null=True)

    owner: fields.ForeignKeyRelation["User"] = fields.ForeignKeyField(
        "models.User", related_name="virtual_machines", on_delete=fields.CASCADE
    )

    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    started_at = fields.DatetimeField(null=True)
    stopped_at = fields.DatetimeField(null=True)

    port_forwards: fields.ReverseRelation["PortForward"]

    class Meta:
        table = "virtual_machines"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"VM {self.name} (VMID: {self.vmid})"

    @property
    def is_active(self) -> bool:
        """Check if VM is in an active state"""
        return self.status in [VMStatus.RUNNING, VMStatus.CREATING]

    @property
    def can_start(self) -> bool:
        """Check if VM can be started"""
        return self.status in [VMStatus.STOPPED, VMStatus.SUSPENDED]

    @property
    def can_stop(self) -> bool:
        """Check if VM can be stopped"""
        return self.status == VMStatus.RUNNING

    @property
    def can_delete(self) -> bool:
        """Check if VM can be deleted"""
        return self.status not in [VMStatus.DELETING, VMStatus.DELETED]

    def to_dict(self) -> dict:
        """Convert VM metadata to dictionary"""

        return {
            "id": self.id,
            "vmid": self.vmid,
            "node": self.node,
            "name": self.name,
            "memory": self.memory,
            "cores": self.cores,
            "disk": self.disk,
            "ssh_port": self.ssh_port,
            "ip_address": self.ip_address,
            "status": self.status,
            "status_message": self.status_message,
            "owner_id": self.owner_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "stopped_at": self.stopped_at.isoformat() if self.stopped_at else None
        }

VirtualMachine_Pydantic = pydantic_model_creator(VirtualMachine, name="VirtualMachine")
VirtualMachineIn_Pydantic = pydantic_model_creator(
    VirtualMachine, name="VirtualMachineIn", exclude_readonly=True
)