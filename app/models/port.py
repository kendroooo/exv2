"""
Model[PortForward]
"""

from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator
from typing import Optional

class PortForward(models.Model):
    """
    Port forwarding rules managed by UniFi controller
    """
    
    id = fields.IntField(pk=True)
    
    unifi_rule_id = fields.CharField(max_length=100, unique=True, null=True)

    external_port = fields.IntField(unique=True)
    internal_port = fields.IntField(default=22)
    internal_ip = fields.CharField(max_length=45)
    protocol = fields.CharField(max_length=10, default="tcp")

    description = fields.TextField(null=True)
    is_active = fields.BooleanField(default=True)

    virtual_machine: fields.ForeignKeyRelation["VirtualMachine"] = fields.ForeignKeyField(
        "models.VirtualMachine", related_name="port_forwards", on_delete=fields.CASCADE
    )

    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "port_forwards"
        ordering = ["-created_at"]
        unique_together = (
            ("external_port", "protocol"),
        )

    def __str__(self) -> str:
        return f"Port Forward {self.external_port} -> {self.internal_ip}:{self.internal_port}"

    def to_dict(self) -> dict:
        """Convert PortForward to dict"""

        return {
            "id": self.id,
            "unifi_rule_id": self.unifi_rule_id,
            "external_port": self.external_port,
            "internal_port": self.internal_port,
            "internal_ip": self.internal_ip,
            "protocol": self.protocol,
            "description": self.description,
            "is_active": self.is_active,
            "vm_id": self.virtual_machine_id, # type: ignore
            "created_at": self.created_at
        }

PortForward_Pydantic = pydantic_model_creator(PortForward, name="PortForward")
PortForwardIn_Pydantic = pydantic_model_creator(
    PortForward, name="PortForwardIn", exclude_readonly=True
)