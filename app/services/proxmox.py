"""
Proxmox service for VM Management using proxmoxer
"""

import asyncio
from abc import ABC
from typing import Optional, Dict, Any, List
from proxmoxer import ProxmoxAPI
import urllib3

from app.config import settings

if not settings.proxmox_verify_ssl:
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class ProxmoxService(ABC):
    """
    Thread-safe async wrapper for proxmoxer
    """

    def __init__(self):
        """Initialize Proxmox API connection"""
        self.proxmox = ProxmoxAPI(
            settings.proxmox_host,
            user=settings.proxmox_user,
            password=settings.proxmox_password,
            verify_ssl=settings.proxmox_verify_ssl
        )
        self.node = settings.proxmox_node

    async def _run_sync(self, func, *args, **kwargs):
        """Run synchronous Proxmox API call in threadpool"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            lambda: func(*args, **kwargs)
        )

    async def get_next_vmid(self) -> int:
        """Get next available VMID from Proxmox"""
        return await self._run_sync(self.proxmox.cluster.nextid.get)

    async def clone_vm(
        self,
        vmid: int,
        name: str,
        template_id: Optional[int] = None,
        memory: Optional[int] = None,
        cores: Optional[int] = None,
        disk: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Clone a VM from template

        Returns:
            Task ID and status
        """

        template_id = template_id or settings.vps_template_id
        memory = memory or settings.vps_default_memory
        cores = cores or settings.vps_default_cores

        result = await self._run_sync(
            self.proxmox.nodes(self.node).qemu(template_id).clone.post,
            newid=vmid,
            name=name,
            full=1
        )

        await self.wait_for_task(result)

        await self._run_sync(
            self.proxmox.nodes(self.node).qemu(vmid).config.put,
            memory=memory,
            cores=cores,
            onboot=0
        )

        if disk:
            await self.resize_disk(vmid, disk)

        return result

    async def create_vm(
        self,
        vmid: int,
        name: str,
        memory: int,
        cores: int,
        disk: int
    ) -> Dict[str, Any]:
        """
        Create a new VM

        Returns:
            Creation result
        """
        return await self._run_sync(
            self.proxmox.nodes(self.node).qemu.post,
            vmid=vmid,
            name=name,
            memory=memory,
            cores=cores,
            scsihw='virtio-scsi-pci',
            scsi0=f'local-lvm:{disk}',
            net0='virtio,bridge=vmbr0',
            ostype='l26'
        )

    async def resize_disk(
        self,
        vmid: int,
        size_gb: int
    ) -> Dict[str, Any]:
        """Resize VM Disk"""
        return await self._run_sync(
            self.proxmox.nodes(self.node).qemu(vmid).resize.put,
            disk='scsi0',
            size=f"{size_gb}G"
        )

    async def wait_for_task(
        self,
        task_id: str,
        timeout: int = 60
    ) -> bool:
        """
        Wait for Proxmox task to complete
        """
        for _ in range(timeout):
            try:
                status: Optional[Dict[str, Any]] = await self._run_sync(
                    self.proxmox.nodes(self.node).tasks(task_id).status.get
                )

                if status.get('status') == 'stopped':
                    return status.get('exitstatus') == "OK"

                await asyncio.sleep(1)
            except Exception:
                return False

        return False
    
    async def start_vm(self, vmid: int) -> Dict[str, Any]:
        """Start a VM"""
        return await self._run_sync(
            self.proxmox.nodes(self.node).qemu(vmid).status.start.post
        )

    async def stop_vm(self, vmid: int) -> Dict[str, Any]:
        """Stop a VM gracefully"""
        return await self._run_sync(
            self.proxmox.nodes(self.node).qemu(vmid).status.shutdown.post
        )

    async def force_stop_vm(self, vmid: int) -> Dict[str, Any]:
        """Force stop a VM"""
        return await self._run_sync(
            self.proxmox.nodes(self.node).qemu(vmid).status.stop.post
        )

    async def restart_vm(self, vmid: int) -> Dict[str, Any]:
        """Restart a VM"""
        return await self._run_sync(
            self.proxmox.nodes(self.node).qemu(vmid).status.reboot.post
        )
    
    async def delete_vm(self, vmid: int) -> Dict[str, Any]:
        """Delete a VM"""
        return await self._run_sync(
            self.proxmox.nodes(self.node).qemu(vmid).delete
        )

    async def suspend_vm(self, vmid: int) -> Dict[str, Any]:
        """Suspend a VM"""
        return await self._run_sync(
            self.proxmox.nodes(self.node).qemu(vmid).status.suspend.post
        )

    async def get_vm_status(self, vmid: int) -> Dict[str, Any]:
        """Get VM Status"""
        return await self._run_sync(
            self.proxmox.nodes(self.node).qemu(vmid).status.current.get
        )

    async def get_vm_config(self, vmid: int) -> Dict[str, Any]:
        """Get VM Config"""
        return await self._run_sync(
            self.proxmox.nodes(self.node).qemu(vmid).config.get
        )

    async def update_vm_config(self, vmid: int, **config) -> Dict[str, Any]:
        """Update VM Config"""
        return await self._run_sync(
            self.proxmox.nodes(self.node).qemu(vmid).config.put,
            **config
        )

    async def get_vm_ip(self, vmid: int) -> Optional[str]:
        """
        Get VM IP address from QEMU agent

        Returns:
            IP address if present
        """
        try:
            result: Optional[Dict[str, Any]] = await self._run_sync(
                self.proxmox.nodes(self.node).qemu(vmid).agent('network-get-interfaces').get
            )

            for interface in result.get('result', []):
                if interface.get('name') not in ['lo', 'localhost']:
                    for ip_addr in interface.get('ip-addresses', []):
                        if ip_addr.get('ip-address-type') == 'ipv4':
                            return ip_addr.get('ip-address')

            return None

        except Exception:
            return None

    async def list_vms(self) -> List[Dict[str, Any]]:
        """List all VMs on the node"""
        return await self._run_sync(
            self.proxmox.nodes(self.node).qemu.get
        )


