"""Snapshot management tools."""
from datetime import datetime
from typing import Optional

from fastmcp import Context, FastMCP
from loguru import logger

from mcp_server_vss.client import VssApiClient
from mcp_server_vss.exceptions import VssError
from mcp_server_vss.models.requests import (
    VmInfoRequest, VmSnapshotDelRequest, VmSnapshotRequest,
    VmSnapshotRollbackRequest)
from mcp_server_vss.models.vms import VmChangeRequestResult, VMInfo
from mcp_server_vss.tools.common import BaseVmTool


class ManageSnapshotVmTool(BaseVmTool):
    """Create a snapshot of a virtual machine."""

    def __init__(self, mcp: FastMCP, auth_token: str, api_endpoint: str):
        """Initialize class."""
        super().__init__(auth_token, api_endpoint)
        mcp.tool(name='get_vm_snapshots')(self.get_vm_snapshots)
        mcp.tool(name='create_vm_snapshot')(self.create_vm_snapshot)
        mcp.tool(name='delete_vm_snapshot')(self.delete_vm_snapshot)
        mcp.tool(name='rollback_vm_snapshot')(self.rollback_vm_snapshot)

    async def create_vm_snapshot(
        self, ctx: Context, request: VmSnapshotRequest
    ) -> str:
        """Create a snapshot of a virtual machine.

        Use this tool when you need to:
        - Create backup point before changes
        - Save VM state for rollback capability
        - Document VM configuration at a specific time
        - Prepare for maintenance or updates

        Snapshot options:
        - Memory snapshots: Include RAM state (slower but complete state capture)
        - Disk-only snapshots: Faster, suitable for powered-off VMs
        - Consolidate snapshots: Combine multiple snapshots into one after deletion

        Important:
        - Snapshots are not backups. Use for short-term rollback only.
        """
        try:
            async with VssApiClient(
                self.auth_token, self.api_endpoint
            ) as api_client:
                vm_data = await self.handle_vm_info(
                    api_client, request.vm_id_or_name, ctx
                )
                # Get the VM's snapshot data
                snapshots_data = await self.handle_vm_snapshots(
                    api_client, vm_data, ctx
                )
                snapshot_count = len(snapshots_data.snapshots)

                if request.from_date is None:
                    # set Timestamp in format YYYY-MM-DD HH:MM when
                    # to take the snapshot
                    request.from_date = datetime.now().strftime(
                        "%Y-%m-%d %H:%M"
                    )

                await ctx.info(
                    f"Found {snapshot_count} snapshots for VM {vm_data.name}"
                )
                change_request = await self.handle_vm_snapshot_creation(
                    api_client, vm_data, request
                )
                response = self._format_response(
                    vm_data, request, change_request, snapshot_count
                )
                return response
        except VssError as e:
            logger.error(
                f"VSS error in create_vm_snapshot: {str(e)}", exc_info=True
            )
            raise VssError(f"VSS API error: {str(e)}")
        except Exception as e:
            logger.error(
                f"Unexpected error in create_vm_snapshot: {e}", exc_info=True
            )
            raise VssError(f"Internal error: {str(e)}")

    async def get_vm_snapshots(
        self, ctx: Context, request: VmInfoRequest
    ) -> str:
        """Retrieve and analyze an ITS Private Cloud VM Snapshots by ID, Name, or UUID.

        Use this tool when you need to:
        - Get detailed information about a virtual machine snapshots

        Args:
            request: The request object containing the VM ID, UUID, or name.
            ctx: The Context object providing access to MCP capabilities.

        Return:
            str: A string representation of the VM information.
        """

        try:
            async with VssApiClient(
                self.auth_token, self.api_endpoint
            ) as api_client:
                vm_data = await self.handle_vm_info(
                    api_client, request.vm_id_or_uuid_or_name, ctx
                )
                vm_snapshots = await self.handle_vm_snapshots(
                    api_client, vm_data, ctx
                )
                # Convert to tool result format
                tool_results = vm_snapshots.to_tool_result()
                # Extract text content from tool results
                if tool_results and hasattr(tool_results[0], 'text'):
                    return tool_results[0].text
                return str(vm_snapshots)
        except VssError as e:
            logger.error(f"VSS error in get_vm_info: {str(e)}")
            raise Exception(f"VSS API error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in get_vm_info: {e}")
            raise Exception(f"Internal error: {str(e)}")

    async def delete_vm_snapshot(
        self, ctx: Context, request: VmSnapshotDelRequest
    ) -> str:
        """Delete a VM snapshot by ID or name.

        Use this tool when you need to:
        - Delete or remove a given snapshot

        Snapshot Deletion options:
        - Consolidation: Run disk consolidation after removal

        Args:
            ctx (Context): The context object.
            request (VmSnapshotDelRequest): The request object.
        """
        try:
            async with VssApiClient(
                self.auth_token, self.api_endpoint
            ) as api_client:
                vm_data = await self.handle_vm_info(
                    api_client, request.vm_id_or_uuid_or_name, ctx
                )
                vm_snapshots = await self.handle_vm_snapshots(
                    api_client, vm_data, ctx
                )
                if not vm_snapshots:
                    await ctx.info("No snapshots found for this VM.")
                    return "No snapshots found for this VM."
                await ctx.info(f'Found snapshots for this VM: {vm_snapshots}.')
                # look for snapshot ref by id or name
                snapshot_to_delete = list(
                    filter(
                        lambda x: x.id == request.snapshot_id_or_name
                        or x.name == request.snapshot_id_or_name,
                        vm_snapshots.snapshots,
                    )
                )
                if not snapshot_to_delete:
                    await ctx.info("Snapshot not found.")
                    return "Snapshot not found."
                await ctx.info(f"Snapshot to delete: {snapshot_to_delete[0]}.")
                # delete snapshot
                request.snapshot_id_or_name = snapshot_to_delete[0].id
                change_request = await self.handle_vm_snapshot_deletion(
                    api_client,
                    vm_data,
                    request,
                )
                # Get the VM's snapshot data
                snapshots_data = await self.handle_vm_snapshots(
                    api_client, vm_data, ctx
                )
                snapshot_count = len(snapshots_data.snapshots)
                # Format the response
                response = self._format_response(
                    vm_data, request, change_request, snapshot_count
                )
                return response

        except VssError as e:
            logger.error(f"VSS error in get_vm_info: {str(e)}")
            raise Exception(f"VSS API error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in get_vm_info: {e}")
            raise Exception(f"Internal error: {str(e)}")

    async def rollback_vm_snapshot(
        self, ctx: Context, request: VmSnapshotRollbackRequest
    ) -> str:
        """Rollback a VM snapshot by ID or name."""
        # Get the VM data
        try:
            async with VssApiClient(
                self.auth_token, self.api_endpoint
            ) as api_client:
                vm_data = await self.handle_vm_info(
                    api_client, request.vm_id_or_uuid_or_name, ctx
                )
                vm_snapshots = await self.handle_vm_snapshots(
                    api_client, vm_data, ctx
                )
                if not vm_snapshots:
                    await ctx.info("No snapshots found for this VM.")
                    return "No snapshots found for this VM."
                # get all snapshots for this vm
                await ctx.info(f'Found snapshots for this VM: {vm_snapshots}.')
                # look for snapshot ref by id or name
                snapshot_to_rollback = list(
                    filter(
                        lambda x: x.id == request.snapshot_id_or_name
                        or x.name == request.snapshot_id_or_name,
                        vm_snapshots.snapshots,
                    )
                )
                if not snapshot_to_rollback:
                    await ctx.info("Snapshot not found.")
                    return "Snapshot not found."
                if len(snapshot_to_rollback) > 1:
                    await ctx.info("Multiple snapshots found.")
                    return "Multiple snapshots found."
                # get snapshot to delete
                await ctx.info(
                    f"Snapshot to rollback: {snapshot_to_rollback[0]}."
                )
                # delete snapshot
                request.snapshot_id_or_name = snapshot_to_rollback[0].id
                change_request = await self.handle_vm_snapshot_rollback(
                    api_client,
                    vm_data,
                    request,
                )
                # Get the VM's snapshot data
                snapshots_data = await self.handle_vm_snapshots(
                    api_client, vm_data, ctx
                )
                snapshot_count = len(snapshots_data.snapshots)
                # Format the response
                response = self._format_response(
                    vm_data, request, change_request, snapshot_count
                )
                return response

        except VssError as e:
            logger.error(f"VSS error in get_vm_info: {str(e)}")
            raise Exception(f"VSS API error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in get_vm_info: {e}")
            raise Exception(f"Internal error: {str(e)}")

    async def handle_vm_snapshot_creation(
        self,
        api_client: VssApiClient,
        vm_data: VMInfo,
        request: VmSnapshotRequest,
    ) -> VmChangeRequestResult:
        """Create a new snapshot for a VM by ID or name."""
        # Create the snapshot
        rv = await api_client.post(
            f"v2/vm/{vm_data.moref}/snapshot",
            json_data=request.model_dump(),
            context="creating snapshot",
        )
        result = rv.get("data", {})
        return VmChangeRequestResult.model_validate(result)

    async def handle_vm_snapshot_deletion(
        self,
        api_client: VssApiClient,
        vm_data: VMInfo,
        request: VmSnapshotDelRequest,
    ) -> VmChangeRequestResult:
        """Delete a snapshot for a VM."""
        # Delete the snapshot
        params = {'consolidate': request.consolidate}
        rv = await api_client.delete(
            f"v2/vm/{vm_data.moref}/snapshot/{request.snapshot_id_or_name}",
            context="deleting snapshot",
            params=params,
        )
        result = rv.get("data", {})
        return VmChangeRequestResult.model_validate(result)

    async def handle_vm_snapshot_rollback(
        self,
        api_client: VssApiClient,
        vm_data: VMInfo,
        request: VmSnapshotRollbackRequest,
    ):
        """Rollback to a snapshot."""
        rv = await api_client.patch(
            f"v2/vm/{vm_data.moref}/snapshot/{request.snapshot_id_or_name}",
            context="rolling back snapshot",
        )
        result = rv.get("data", {})
        return VmChangeRequestResult.model_validate(result)

    @staticmethod
    def _format_response(
        vm_data: VMInfo,
        request: VmSnapshotRequest
        | VmSnapshotDelRequest
        | VmSnapshotRollbackRequest,
        change_request: VmChangeRequestResult,
        snapshot_count: Optional[int] = 0,
    ) -> str:
        """Format response."""
        note = ''
        after_note = ''
        is_creation = isinstance(request, VmSnapshotRequest)
        is_rollback = isinstance(request, VmSnapshotRollbackRequest)
        is_deletion = isinstance(request, VmSnapshotDelRequest)
        if is_creation or is_rollback:
            response = f"VM Snapshot {'Creation' if is_creation else 'Rollback'} Summary"
            if is_creation and snapshot_count > 0:
                note += f"        Current Snapshot Count: {snapshot_count + 1}"
            # Add warnings and recommendations
            if snapshot_count >= 2:
                note += (
                    "\n⚠️ WARNING: Multiple snapshots detected. "
                    "Performance may be impacted."
                )
                note += "\n💡Recommendation: Remove old snapshots when no longer needed."
            if (
                is_creation
                and request.include_memory
                and vm_data.power_state == "poweredOn"
            ):
                note += "\n⏱️ Memory snapshot may take longer to complete."
            after_note = """NEXT STEPS:
        - Monitor snapshot completion status
        - Test rollback procedure if this is a critical change
        - Document snapshot purpose for future reference
        - Schedule snapshot cleanup after changes are validated

        IMPORTANT: Snapshots are not backups. 
          They should be temporary and removed after validation."""
        elif is_deletion:
            response = "VM Snapshot Deletion Summary"
            if vm_data.power_state == "poweredOn":
                note += (
                    "\n⚠️ WARNING: VM is powered on. "
                    "Snapshot deletion may impact performance."
                )
                note += "\n💡Recommendation: Power off the VM before deleting the snapshot."
            if request.consolidate:
                note += "\n⚠️ WARNING: Consolidation may impact performance."

        else:
            response = f"VM Snapshot Summary"

        response += f"""
        {'=' * 50}

        VM Details:
        - Name: {vm_data.name}
        - ID: {vm_data.moref}
        - Current State: {vm_data.power_state}

        {request.to_text()}

        Operation Result:
        {change_request.to_text()}
        
        Notes:
        {note}

        {after_note}
        """
        return response
