"""
UniFi OS Controller service for automatic port forwarding
"""

import asyncio
from abc import ABC
import ssl
from loguru import logger
from typing import Optional, Dict, Any, List
import aiohttp
from aiounifi.controller import Controller, ApiRequest
from aiounifi.models.configuration import Configuration

from app.config import settings

class UnifiService(ABC):
    """
    Service for managing UniFi port forwarding rules, fully async
    """

    def __init__(self):
        """Initialize UniFi controller conn"""
        self.controller: Optional[Controller] = None
        self._session: Optional[aiohttp.ClientSession] = None
        self._connected = False
        self._ctx = ssl.create_default_context() if settings.unifi_verify_ssl else False
        self._ctx.check_hostname = False
        self._ctx.verify_mode = ssl.CERT_NONE
        self._logger = logger

    async def _ensure(self):
        """
        Ensure controller is connected
        """
        if not self._connected or not self.controller:
            await self.connect()

    async def connect(self):
        """
        Connect to UniFi controller
        """

        if self._session is None:
            connector = aiohttp.TCPConnector(ssl=self._ctx)
            self._session = aiohttp.ClientSession(connector=connector)

        config = Configuration(
            session=self._session,
            host=settings.unifi_host,
            username=settings.unifi_username,
            password=settings.unifi_password,
            port=settings.unifi_port,
            site=settings.unifi_site,
            ssl_context=self._ctx
        )

        self.controller = Controller(config)
        await self.controller.login()
        self._connected = True

    async def disconnect(self):
        """Disconnect from UniFi controller"""
        if self.controller:
            await self.controller.connectivity.config.session.close()
        if self._session:
            await self._session.close()
        self._connected = False

    async def create_port_forward(
        self,
        name: str,
        external_port: int,
        internal_ip: str,
        internal_port: int = 22,
        protocol: str = "tcp",
        enabled: bool = True
    ) -> Dict[str, Any]:
        """
        Create a port forwarding rule

        Returns:
            Dict[str, Any]
        """
        
        await self._ensure()

        protocolm = {
            "tcp": "tcp",
            "udp": "udp",
            "both": "tcp_udp",
            "tcp_udp": "tcp_udp"
        }
        
        unifi_proto = protocolm.get(
            protocol.lower(),
            "tcp"
        )
        
        portforward = {
            "name": name,
            "enabled": enabled,
            "pfwd_interfance": "wan",
            "src": "any",
            "dst_port": str(external_port),
            "fwd": internal_ip,
            "fwd_port": str(internal_port),
            "proto": unifi_proto,
            "log": False
        }

        response = await self.controller.request(
            ApiRequest(
                method="post",
                path="/api/s/{site}/rest/portforward",
                data=portforward
            )
        )

        if response and "data" in response and len(response["data"]) > 0:
            return response["data"][0]

        return {}

    async def delete_port_forward(self, rule_id: str) -> bool:
        """
        Delete a portforwarding rule

        Returns:
            bool
        """

        await self._ensure()

        try:
            await self.controller.request(
                ApiRequest(
                    method="delete",
                    path=f"/api/s/{{site}}/rest/portforward/{rule_id}"
                )
            )
            return True
        except Exception as e:
            self._logger.error(f"ERROR deleting port forward: {e}")
            return False

    async def update_port_forward(
        self,
        rule_id: str,
        enabled: Optional[bool] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Update a portforwarding rule

        Returns:
            Dict[str, Any]
        """

        await self._ensure()

        rule = self.get_port_forward(rule_id)
        if not rule:
            raise ValueError(f"Port forward rule {rule_id} not found")

        upd = dict(rule)

        if enabled is not None:
            upd["enabled"] = enabled

        upd.update(kwargs)

        response = await self.controller.request(
            ApiRequest(
                method="put",
                path=f"/api/s/{{site}}/rest/portforward/{rule_id}",
                data=upd
            )
        )

        if response and "data" in response  and len(response["data"]) > 0:
            return response["data"][0]

        return {}

    async def get_port_forward(
        self,
        rule_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get a specific port forwarding rule

        Returns:
            Optional[Dict[str, Any]]
        """

        await self._ensure()

        for rule in self.list_port_forwards():
            if rule.get("_id") == rule_id:
                return rule

        return None

    async def list_port_forwards(self) -> List[Dict[str, Any]]:
        """
        List all port forwarding rules

        Returns:
            List[Dict[str, Any]]
        """

        await self._ensure()

        try:
            response = await self.controller.request(
                ApiRequest(
                    method="get",
                    path="/api/s/{site}/rest/portforward"
                )
            )

            if response and "data" in response:
                return response["data"]

            return []

        except Exception as e:
            self._logger.error(f"ERROR Listing portforwards: {e}")
            return []