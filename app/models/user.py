"""
Model[User]
"""

from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator
from datetime import datetime
from typing import Optional

class User(models.Model):
    """
    User model with Discord OAuth integration
    Supports role-based access control
    """

    id = fields.IntField(pk=True)
    discord_id = fields.CharField(
        max_length=20,
        unique=True,
        index=True
    )
    discord_username = fields.CharField(max_length=100)
    discord_avatar = fields.CharField(
        max_length=255,
        null=True
    )
    email = fields.CharField(
        max_length=255,
        null=True
    )

    is_admin = fields.BooleanField(default=False)
    is_active = fields.BooleanField(default=True)
    is_banned = fields.BooleanField(default=False)

    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    last_login = fields.DatetimeField(null=True)

    virtual_machines = fields.ReverseRelation["VirtualMachine"]
    audit_logs: fields.ReverseRelation["AuditLog"]

    class Meta:
        table = "users"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.discord_username}"

    @property
    def display_name(self) -> str:
        return self.discord_username

    @property
    def avatar_url(self) -> Optional[str]:
        """Get user's Discord Avatar URL"""
        if self.discord_avatar:
            return f"https://cdn.discordapp.com/avatars/{self.discord_id}/{self.discord_avatar}.png"
        return None
    
    async def update_last_login(self) -> None:
        """Update last login timestamp"""
        self.last_login = datetime.utcnow()
        await self.save(
            update_fields=["last_login"]
        )

    def to_dict(self) -> dict:
        """Convert user to dictionary"""

        return {
            "id": self.id,
            "discord_id": self.discord_id,
            "username": self.discord_username,
            "avatar_url": self.avatar_url,
            "email": self.email,
            "is_admin": self.is_admin,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_login": self.last_login.isoformat() if self.created_at else None
        }

User_Pydantic = pydantic_model_creator(User, name="User")
UserIn_Pydantic = pydantic_model_creator(User, name="UserIn", exclude_readonly=True)