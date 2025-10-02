"""
Database configuration and utilities using Tortoise ORM
"""

from tortoise import Tortoise
from tortoise.contrib.fastapi import register_tortoise
from fastapi import FastAPI
from app.config import settings


TORTOISE = {
    "connections": {
        "default": settings.database_url
    },
    "apps": {
        "models": {
            "models": ["app.models", "aerich.models"],
            "default_connection": "default",
        }
    },
    "use_tz": True,
    "timezone": "Australia/Melbourne"
}

async def init_db(app: FastAPI) -> None:
    """Initialize database connection with Tortoise"""

    register_tortoise(
        app,
        config=TORTOISE,
        generate_schemas=True,
        add_exception_handlers=True,
    )

async def close_db() -> None:
    """Close database connections gracefully"""
    await Tortoise.close_connections()

async def get_db_connection():
    """Get database connection for manual queries"""
    conn = Tortoise.get_connection("default")

    try:
        yield conn
    finally:
        pass