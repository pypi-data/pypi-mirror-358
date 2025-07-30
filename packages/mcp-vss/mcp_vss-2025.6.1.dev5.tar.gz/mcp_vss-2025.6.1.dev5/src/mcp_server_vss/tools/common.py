from typing import Union

from fastmcp import Context
from loguru import logger

from mcp_server_vss.client import VssApiClient
from mcp_server_vss.exceptions import VssError
from mcp_server_vss.models.billing import (
    BillingClient, BillingClientsSummary, FisRecord)
from mcp_server_vss.models.vms import (
    VmChangeRequestResult, VmDisk, VmDisks, VMInfo, VmMetrics, VmOsInfo,
    VmSnapshot, VmSnapshots)


class BaseBillingTool:
    """Base class for Billing Tools."""

    def __init__(self, auth_token: str, api_endpoint: str):
        """Initialize the VM tool."""
        self.auth_token = auth_token
        self.api_endpoint = api_endpoint

    async def handle_client_info(
        self, api_client: VssApiClient, client_id_or_name: str, ctx: Context
    ) -> BillingClient:
        """Retrieve billing client information by ID or name."""
        client_identifier = self._validate_input(
            client_id_or_name, "Client identifier"
        )
        await ctx.info(
            f"Fetching billing client info for: {client_identifier}"
        )
        client_endpoint = f"billing/client/{client_identifier}"
        rv = await api_client.get(
            client_endpoint, f"fetching client info for '{client_identifier}'"
        )
        return BillingClient.model_validate(rv)

    async def handle_billing_client_fis(
        self,
        api_client: VssApiClient,
        client_data: BillingClient,
        ctx: Context,
    ) -> FisRecord:
        """Retrieve billing client FIs summary."""
        await ctx.info(
            f"Fetching billing client FIs summary for: {client_data.name} ({client_data.id})"
        )
        fis_endpoint = f"billing/client/{client_data.id}/fis"
        rv = await api_client.get(
            fis_endpoint,
            f"fetching fis info for {client_data.name} ({client_data.id})",
        )
        fis = rv.get("data", {})
        if not fis:
            raise VssError(
                f"No FIs found for client: {client_data.name} ({client_data.id})"
            )
        return FisRecord.model_validate(fis)

    async def handle_billing_clients(
        self, api_client: VssApiClient, ctx: Context
    ) -> BillingClientsSummary:
        """Retrieve billing clients summary."""
        clients_endpoint = "billing/client"
        await ctx.info("Fetching billing clients summary")
        rv = await api_client.get(clients_endpoint, "fetching clients")
        clients = rv.get('data', [])
        return BillingClientsSummary.model_validate(
            {
                'clients': [
                    BillingClient.model_validate(client) for client in clients
                ]
            }
        )

    @staticmethod
    def _validate_input(value: str, name: str) -> str:
        """Validate and sanitize input parameters."""
        if not value or not value.strip():
            raise VssError(f"{name} cannot be empty")
        return value.strip()

    @staticmethod
    def _validate_number_input(
        value: Union[float, int], name: str
    ) -> Union[float, int]:
        """Validate number inputs."""
        if not isinstance(value, (int, float)) or value <= 0:
            raise VssError(f"{name} must be a positive number")
        return value


class BaseVmTool:
    """Base class for VM tools."""

    def __init__(self, auth_token: str, api_endpoint: str):
        """Initialize the VM tool."""
        self.auth_token = auth_token
        self.api_endpoint = api_endpoint

    async def handle_vm_info(
        self,
        api_client: VssApiClient,
        vm_id_or_uuid_or_name: str,
        ctx: Context,
    ) -> VMInfo:
        """Retrieve VM information by ID, UUID, or name."""
        vm_identifier = self._validate_input(
            vm_id_or_uuid_or_name, "VM identifier"
        )

        # If not a direct ID/UUID, search by name first
        if not self._is_vm_id_or_uuid(vm_identifier):
            logger.info(f"Searching for VM by name: {vm_identifier}")
            await ctx.info(f"Searching for VM '{vm_identifier}'")
            search_endpoint = f"v2/vm?filter=name,like,%{vm_identifier}%"
            rv = await api_client.get(
                search_endpoint, f"searching for VM '{vm_identifier}'"
            )
            # retrieve data
            vm_data = rv.get('data')
            if not vm_data:
                raise VssError(f"VM with name '{vm_identifier}' not found")
            # TODO: handle multiple results
            vm_id = vm_data[0].get('moref')
            if not vm_id:
                raise VssError(
                    f"Invalid VM data returned for '{vm_identifier}'"
                )
        else:
            vm_id = vm_identifier

        logger.info(f"Fetching VM details for ID: {vm_id}")

        # Get detailed VM information
        vm_endpoint = f"v2/vm?filter=moref,eq,{vm_id}"
        rv = await api_client.get(
            vm_endpoint, f"fetching VM details for '{vm_id}'"
        )

        vm_data = rv.get('data')
        if not vm_data:
            raise VssError(f"No VM data found for ID '{vm_id}'")

        return VMInfo.model_validate(vm_data[0])

    async def handle_get_vm_os_info(
        self, api_client: VssApiClient, vm_data: VMInfo, ctx: Context
    ) -> VmOsInfo:
        """Retrieve VM OS information by ID."""
        logger.info(f"Fetching VM OS info for ID: {vm_data.moref}")
        await ctx.info(f"Fetching VM OS info for ID: {vm_data.moref}")
        # Find matching OS
        os_info = {
            'family': 'unknown',
            'is_linux_64bit': False,
            'is_windows_32bit': False,
            'guest_id': vm_data.guest_id,
        }
        try:
            os_endpoint = f"v2/os?filter=guest_id,eq,{vm_data.guest_id}"
            os_result = await api_client.get(
                os_endpoint, "fetching OS information"
            )
            os_list = os_result.get('data', [])

            for os_entry in os_list:
                if (
                    os_entry.get('guest_id', '').lower()
                    == vm_data.guest_id.lower()
                ):
                    os_info.update(os_entry)
                    break

                # Check for Linux 64-bit
            if (
                os_info.get('family', '').lower() == 'linuxguest'
                and '64 bit' in os_info.get('full_name', '').lower()
            ):
                os_info['is_linux_64bit'] = True

                # Check for Windows 7 32-bit
            if (
                'windows' in os_info.get('full_name', '').lower()
                and '7' in os_info.get('full_name', '')
                and '32' in os_info.get('full_name', '')
            ):
                os_info['is_windows_32bit'] = True
            return VmOsInfo.model_validate(os_info)
        except Exception as e:
            logger.warning(f"Could not fetch OS info: {e}")
            return VmOsInfo.model_validate(os_info)

    async def handle_vm_performance(
        self,
        api_client: VssApiClient,
        vm_data: VMInfo,
        ctx: Context,
        time_period_in_hours: int = 1,
    ) -> VmMetrics:
        """Retrieve VM performance data by ID or name."""
        interval_in_minutes = time_period_in_hours * 60
        await ctx.info(
            f"Fetching VM performance data for: {vm_data.name}({vm_data.moref}) {time_period_in_hours=}"
        )
        rv = await api_client.get(
            f"v2/vm/{vm_data.moref}/performance?interval={interval_in_minutes}",
            "fetching metrics",
        )
        metrics_data = rv.get("data")
        return VmMetrics.model_validate(metrics_data)

    async def handle_vm_snapshots(
        self, api_client: VssApiClient, vm_data: VMInfo, ctx: Context
    ) -> VmSnapshots:
        """Get VM snapshots by ID or name."""
        # If not a direct ID/UUID, search by name first
        await ctx.info(
            f'Fetching snapshots for: {vm_data.name}({vm_data.moref})'
        )
        rv = await api_client.get(
            f"v2/vm/{vm_data.moref}/snapshot", "getting snapshots"
        )
        snapshots_data = rv.get("data", {})
        return VmSnapshots.model_validate(
            {
                'snapshots': [
                    VmSnapshot.model_validate(snap) for snap in snapshots_data
                ]
            }
        )

    async def handle_vm_power_state(
        self,
        api_client: VssApiClient,
        vm_data: VMInfo,
        state: str,
        ctx: Context,
    ) -> VmChangeRequestResult:
        """Update VM power state by ID or name."""
        await ctx.info(
            f'Updating power state from: {vm_data.power_state} to {state} for:'
            f' {vm_data.name}({vm_data.moref})'
        )
        rv = await api_client.post(
            f"v2/vm/{vm_data.moref}/state/{state}", "updating power state"
        )
        result = rv.get("data", {})
        return VmChangeRequestResult.model_validate(result)

    async def handle_vm_disks(
        self, api_client: VssApiClient, vm_data: VMInfo, ctx: Context
    ) -> VmDisks:
        """Get VM disks by ID or name."""
        # If not a direct ID/UUID, search by name first
        await ctx.info(f'Fetching disks for: {vm_data.name}({vm_data.moref})')
        rv = await api_client.get(
            f"v2/vm/{vm_data.moref}/disk", "getting disks"
        )
        disks_data = rv.get("data", {})
        return VmDisks.model_validate(
            {'disks': [VmDisk.model_validate(disk) for disk in disks_data]}
        )

    @staticmethod
    def _is_vm_id_or_uuid(identifier: str) -> bool:
        """Check if identifier is a VM ID or UUID."""
        return identifier.startswith('vm-') or len(identifier) == 36

    @staticmethod
    def _validate_input(value: str, name: str) -> str:
        """Validate and sanitize input parameters."""
        if not value or not value.strip():
            raise VssError(f"{name} cannot be empty")
        return value.strip()

    @staticmethod
    def _validate_number_input(
        value: Union[float, int], name: str
    ) -> Union[float, int]:
        """Validate number inputs."""
        if not isinstance(value, (int, float)) or value <= 0:
            raise VssError(f"{name} must be a positive number")
        return value
