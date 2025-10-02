"""
models.Model[AuditLog] idk dude
"""

from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator
from enum import Enum, auto
from typing import Optional

class LowerStr(str, Enum):

    def _generate_next_value_(name, start, count, last_values):
        return name.lower()

class AuditAction(LowerStr):
    """Audit action types"""

    USER_LOGIN = auto()
    USER_LOGOUT = auto()
    USER_CREATED = auto()
    USER_UPDATED = auto()
    USER_DELETED = auto()

    VM_CREATED = auto()
    VM_STARTED = auto()
    VM_STOPPED = auto()
    VM_RESTARTED = auto()
    VM_SUSPENDED = auto()
    VM_DELETED = auto()
    VM_UPDATED = auto()

    PORT_FORWARD_CREATED = auto()
    PORT_FORWARD_DELETED = auto()
    PORT_FORWARD_UPDATED = auto()
    
    ADMIN_ACCESS = auto()
    ADMIN_ACTION = auto()


class AuditLog(models.Model):
    """
    Audit logging model for all system actions
    """

    id = fields.IntField(pk=True)

    action = fields.CharEnumField(AuditAction)
    description = fields.TextField()

    user: fields.ForeignKeyRelation["User"] = fields.ForeignKeyField(
        "models.User", related_name="audit_logs", on_delete=fields.SET_NULL, null=True
    )

    resource_type = fields.CharField(max_length=50, null=True)
    resource_id = fields.IntField(null=True)

    ip_address = fields.CharField(max_length=45, null=True)
    user_agent = fields.TextField(null=True)
    metadata = fields.JSONField(null=True)

    created_at = fields.DatetimeField(auto_now_add=True, index=True)

    class Meta:
        table = "audit_logs"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Audit: {self.action} by {self.user_id} at {self.created_at}"

    def to_dict(self) -> dict:
        """Convert audit log model to dict sadly"""

        return {
            "id": self.id,
            "action": self.action,
            "description": self.description,
            "user_id": self.user_id,
            "resource_type": self.resource_type,
            "resource_id": self.resource_id,
            "ip_address": self.ip_address,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
AuditLog_Pydantic = pydantic_model_creator(
    AuditLog, name="AuditLog"
)
