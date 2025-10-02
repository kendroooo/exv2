"""
Application configuration using Pydantic Settings
"""

from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator

class Settings(BaseSettings):
    """Application settings with validation"""
    
    app_name: str = Field(default="VPS BACKEND")
    app_env: str = Field(default="development")
    debug: bool = Field(default=False)
    secret_key: str = Field(..., min_length=32)
    api_url: str = Field(default="http://localhost:4835")
    frontend_url: str = Field(default="http://localhost:4773")

    database_url: str = Field(
        ...,
        description="PostgreSQL connection string"
    )

    discord_client_id: str = Field(...)
    discord_client_secret: str = Field(...)
    discord_redirect_uri: str = Field(...)

    proxmox_host: str = Field(...)
    proxmox_user: str = Field(default="root@pam")
    proxmox_password: str = Field(...)
    proxmox_verify_ssl: bool = Field(default=False)
    proxmox_node: str = Field(default="pve")

    unifi_host: str = Field(...)
    unifi_port: int = Field(default=8442)
    unifi_username: str = Field(...)
    unifi_password: str = Field(default="default")
    unifi_verify_ssl: bool = Field(default=False)

    vps_ssh_port_range_start: int = Field(default=20000)
    vps_ssh_port_range_end: int = Field(default=30000)
    vps_default_memory: int = Field(default=4096)
    vps_default_cores: int = Field(default=4)
    vps_default_disk: int = Field(default=20)
    vps_template_id: int = Field(default=9000)

    redis_url: str = Field(default="redis://localhost:6379/0")

    admin_discord_ids: str = Field(default="")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    @property
    def admin_ids_list(self) -> List[str]:
        """Parse admin Discord IDs into a list"""
        if not self.admin_discord_ids:
            return []
        return [
            i.strip() for
            i in self.admin_discord_ids.split(",")
            if i.strip()
        ]

    @property
    def is_production(self) -> bool:
        """Check if running in production"""
        return self.app_env == "production"

    @field_validator("database_url")
    def validate_database_url(cls, v: str) -> str:
        """Ensure database URL is PostgreSQL"""
        if not v.startswith(
                ("postgres://", "postgresql://")
        ):
            raise ValueError("Database URL must be PostgreSQL")

        return v

    @field_validator("secret_key")
    def validate_secret_key(cls, v: str) -> str:
        if len(v) < 32:
            raise ValueError("Secret key must be at least 32 characters")

        return v


settings = Settings()
    
