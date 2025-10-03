"""
Auth service handler for Discord OAuth and JWT tokens
"""

import httpx
from abc import ABC
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import jwt, JWTError
from fastapi import HTTPException, status

from app.config import settings
from app.models import User
from app.schemas import DiscordUser, DiscordTokenResponse

class AuthService(ABC):
    """
    Auth service for discord Oauth and session mgmt.
    """

    DISCORD_API_URL = "https://discord.com/api/v10"
    DISCORD_OAUTH_URL = "https://discord.com/api/oauth2"

    @staticmethod
    async def exchange_code_for_token(code: str) -> DiscordTokenResponse:
        """
        Exchange discord Oauth code for access token

        Args:
            code: Oauth authorization code

        Returns:
            DiscordTokenResponse
        """

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{AuthService.DISCORD_OAUTH_URL}/token",
                data={
                    "client_id": settings.discord_client_id,
                    "client_secret": settings.discord_client_secret,
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": settings.discord_redirect_uri,
                },
                headers={
                    "Content-Type": "application/x-www-form-urlencoded"
                }
            )

            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to exchange code for token"
                )

            return DiscordTokenResponse(**response.json())

    @staticmethod
    async def get_discord_user(access_token: str) -> DiscordUser:
        """
        Get discord user information using access token

        Args:
            access_token: Discord access token

        Returns:
            DiscordUser
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{AuthService.DISCORD_API_URL}/users/@me",
                headers={
                    "Authorization": f"Bearer {access_token}"
                }
            )

            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Failed to get discord user"
                )

            return DiscordUser(**response.json())

    @staticmethod
    async def create_or_update_user(d_user: DiscordUser) -> User:
        """
        Create or update user from discord information

        Args:
            d_user: discord user data

        Returns:
            User
        """

        user = await User.filter(
            discord_id=d_user.id
        ).first()

        is_admin = user.id in settings.admin_ids_list

        if user:
            user.discord_username = d_user.username
            user.discord_avatar = d_user.avatar
            user.email = d_user.email
            user.is_admin = is_admin
            await user.update_last_login()
            await user.save()

        else:
            user = await User.create(
                discord_id=d_user.id,
                discord_username=d_user.username,
                discord_avatar=d_user.avatar,
                email=d_user.email,
                is_admin=is_admin,
                last_login=datetime.utcnow()
            )

        return user

    @staticmethod
    def create_access_token(
        user: User,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create JWT access token for user

        Args:
            user: User model
            expires_delta: Token expiration delta

        Returns:
            JWT token string
        """

        if expires_delta is None:
            expires_delta = timedelta(days=30)

        expire = datetime.utcnow() + expires_delta

        tencode = {
            "sub": str(user.id),
            "discord_id": user.discord_id,
            "is_admin": user.is_admin,
            "exp": expire
        }

        encoded = jwt.encode(
            tencode,
            settings.secret_key,
            algorithm="HS256"
        )

        return encoded

    @staticmethod
    def verify_token(token: str) -> Dict[str, Any]:
        """
        Verify and decode JWT token

        Args:
            token: JWT token string

        Returns:
            Decoded token payload

        Raises:
            HTTPException: If token is invalid
        """

        try:
            payload = jwt.decode(
                token,
                settings.secret_key,
                algorithms=["HS256"]
            )
            return payload
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )