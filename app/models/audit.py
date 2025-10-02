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
    