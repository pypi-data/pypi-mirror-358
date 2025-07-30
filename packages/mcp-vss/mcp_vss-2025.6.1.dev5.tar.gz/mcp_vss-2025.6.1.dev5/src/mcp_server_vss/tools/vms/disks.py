from typing import cast

from fastmcp import Context, FastMCP
from loguru import logger

from mcp_server_vss.client import VssApiClient
from mcp_server_vss.exceptions import VssError
from mcp_server_vss.models.requests import (
    VmDiskCreateRequest, VmDiskCreateRequestList, VmDiskDeleteRequest,
    VmDiskResizeRequest, VmDiskScsiUpdateRequest, VmInfoRequest)
from mcp_server_vss.models.vms import VmChangeRequestResult, VMInfo
from mcp_server_vss.tools.common import BaseVmTool


class ManageDisksVmTool(BaseVmTool):
    """Create a snapshot of a virtual machine."""

    def __init__(self, mcp: FastMCP, auth_token: str, api_endpoint: str):
        """Initialize class."""
        super().__init__(auth_token, api_endpoint)
        mcp.tool(name='get_vm_disks')(self.get_vm_disks)
        mcp.tool(name='create_vm_disks')(self.create_vm_disks)
        mcp.tool(name='resize_vm_disks')(self.resize_vm_disks)
        mcp.tool(name='delete_vm_disks')(self.delete_vm_disks)
        mcp.tool(name='update_vm_disk_scsi')(self.update_vm_disk_scsi)

    async def get_vm_disks(self, ctx: Context, request: VmInfoRequest) -> str:
        """Retrieve virtual machine disks information.

        Use this tool when:
        - You need to retrieve virtual machine disks layout.
        - Query is related to disks and SCSI controller relationship.

        """
        try:
            async with VssApiClient(
                self.auth_token, self.api_endpoint
            ) as api_client:
                vm_data = await self.handle_vm_info(
                    api_client, request.vm_id_or_uuid_or_name, ctx
                )
                vm_disks = await self.handle_vm_disks(api_client, vm_data, ctx)
                # Convert to tool result format
                tool_results = vm_disks.to_tool_result()
                # Extract text content from tool results
                if tool_results and hasattr(tool_results[0], 'text'):
                    return tool_results[0].text
                return str(vm_disks)
        except VssError as e:
            logger.error(f"VSS error in get_vm_disks: {str(e)}")
            raise Exception(f"VSS API error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in get_vm_disks: {e}")
            raise Exception(f"Internal error: {str(e)}")

    async def create_vm_disks(
        self, ctx: Context, request: VmDiskCreateRequestList
    ) -> str:
        """Create a new virtual machine disk.

        Use this tool when:
        - You want to create a new virtual machine disk.
        - You want to import an existing vmdk file.

        Important:
        - No VM snapshots must exist to create a new disk.

        Args:
            ctx (Context): The context object.
            request (VmDiskCreateRequestList): The request object with the vm id and
             single or multiple disks o create.
        """
        try:
            async with VssApiClient(
                self.auth_token, self.api_endpoint
            ) as api_client:
                vm_data = await self.handle_vm_info(
                    api_client, request.vm_id_or_uuid_or_name, ctx
                )
                # Create the disk
                # Get the VM's snapshot data
                snapshots_data = await self.handle_vm_snapshots(
                    api_client, vm_data, ctx
                )
                snapshot_count = len(snapshots_data.snapshots)
                # Check if there are any snapshots
                if snapshot_count > 0:
                    raise Exception(
                        "No VM snapshots must exist to create a new disk."
                    )
                await ctx.info("Attempting to create disks.")
                # Create the disks
                change_request = await self.handle_vm_disks_creation(
                    api_client, vm_data, request
                )
                response = self._format_response(
                    vm_data, request, change_request
                )
                return response
        except VssError as e:
            logger.error(f"VSS error in get_vm_disks: {str(e)}")
            raise Exception(f"VSS API error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in get_vm_disks: {e}")
            raise Exception(f"Internal error: {str(e)}")

    async def resize_vm_disks(
        self, ctx: Context, request: VmDiskResizeRequest
    ) -> str:
        """Resize a virtual machine disk capacity.

        Use this tool when:
        - You want to increase the capacity of an existing virtual machine disk.
        - You need to expand disk space for a VM.

        Important:
        - A virtual disk cannot be shrunk, only expanded.
        - The VM may need to be powered off depending on the disk configuration.

        Args:
            ctx (Context): The context object.
            request (VmDiskResizeRequest): The request object with the vm id, disk unit, and new capacity.
        """
        try:
            async with VssApiClient(
                self.auth_token, self.api_endpoint
            ) as api_client:
                vm_data = await self.handle_vm_info(
                    api_client, request.vm_id_or_uuid_or_name, ctx
                )
                await ctx.info(
                    f"Attempting to resize disk unit {request.unit} to {request.capacity_gb}GB."
                )

                # Resize the disk
                change_request = await self.handle_vm_disk_resize(
                    api_client, vm_data, request
                )
                response = self._format_resize_response(
                    vm_data, request, change_request
                )
                return response
        except VssError as e:
            logger.error(f"VSS error in resize_vm_disks: {str(e)}")
            raise Exception(f"VSS API error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in resize_vm_disks: {e}")
            raise Exception(f"Internal error: {str(e)}")

    async def delete_vm_disks(
        self, ctx: Context, request: VmDiskDeleteRequest
    ) -> str:
        """Delete virtual machine disks.

        Use this tool when:
        - You want to remove one or more virtual machine disks.
        - You need to free up storage space.

        Important:
        - Cannot delete more than 10 disks at a time.
        - The VM may need to be powered off depending on the disk configuration.
        - Be careful as this operation is irreversible.

        Args:
            ctx (Context): The context object.
            request (VmDiskDeleteRequest): The request object with the vm id and disk units to delete.
        """
        try:
            async with VssApiClient(
                self.auth_token, self.api_endpoint
            ) as api_client:
                vm_data = await self.handle_vm_info(
                    api_client, request.vm_id_or_uuid_or_name, ctx
                )
                units_str = ", ".join(str(unit) for unit in request.disk_units)
                await ctx.info(f"Attempting to delete disk units: {units_str}")

                # Delete the disks
                change_request = await self.handle_vm_disk_deletion(
                    api_client, vm_data, request
                )
                response = self._format_deletion_response(
                    vm_data, request, change_request
                )
                return response
        except VssError as e:
            logger.error(f"VSS error in delete_vm_disks: {str(e)}")
            raise Exception(f"VSS API error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in delete_vm_disks: {e}")
            raise Exception(f"Internal error: {str(e)}")

    async def update_vm_disk_scsi(
        self, ctx: Context, request: VmDiskScsiUpdateRequest
    ) -> str:
        """Update virtual machine disk SCSI controller assignment.

        Use this tool when:
        - You want to move a disk to a different SCSI controller.
        - You need to balance the disk load across SCSI controllers.

        Important:
        - VM must be powered off for this operation.
        - A virtual machine can have a maximum of four SCSI controllers (0-3).
        - Each SCSI controller can support a maximum of 15 virtual disks.

        Args:
            ctx (Context): The context object.
            request (VmDiskScsiUpdateRequest): The request object with the vm id, disk unit, and new SCSI controller.
        """
        try:
            async with VssApiClient(
                self.auth_token, self.api_endpoint
            ) as api_client:
                vm_data = await self.handle_vm_info(
                    api_client, request.vm_id_or_uuid_or_name, ctx
                )

                # Check if VM is powered off
                if vm_data.power_state.lower() != "poweredoff":
                    raise Exception(
                        f"VM must be powered off to update disk SCSI controller. "
                        f"Current state: {vm_data.power_state}"
                    )

                await ctx.info(
                    f"Attempting to move disk unit {request.unit} to SCSI controller {request.scsi}"
                )

                # Update the disk SCSI controller
                change_request = await self.handle_vm_disk_scsi_update(
                    api_client, vm_data, request
                )
                response = self._format_scsi_update_response(
                    vm_data, request, change_request
                )
                return response
        except VssError as e:
            logger.error(f"VSS error in update_vm_disk_scsi: {str(e)}")
            raise Exception(f"VSS API error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in update_vm_disk_scsi: {e}")
            raise Exception(f"Internal error: {str(e)}")

    async def handle_vm_disks_creation(
        self,
        api_client: VssApiClient,
        vm_data: VMInfo,
        request: VmDiskCreateRequestList,
    ) -> VmChangeRequestResult:
        """Handle the creation of VM disks."""
        rv = await api_client.post(
            f"v2/vm/{vm_data.moref}/disk",
            json_data={
                "value": [
                    disk.model_dump(exclude_none=True)
                    for disk in request.disks
                ]
            },
            context="creating vm disks",
        )
        result = rv.get("data", {})
        return VmChangeRequestResult.model_validate(result)

    async def handle_vm_disk_resize(
        self,
        api_client: VssApiClient,
        vm_data: VMInfo,
        request: VmDiskResizeRequest,
    ) -> VmChangeRequestResult:
        """Handle the resizing of a VM disk."""
        rv = await api_client.put(
            f"v2/vm/{vm_data.moref}/disk/{request.unit}",
            json_data={"attribute": "capacity", "value": request.capacity_gb},
            context="resizing vm disk",
        )
        result = rv.get("data", {})
        return VmChangeRequestResult.model_validate(result)

    async def handle_vm_disk_deletion(
        self,
        api_client: VssApiClient,
        vm_data: VMInfo,
        request: VmDiskDeleteRequest,
    ) -> VmChangeRequestResult:
        """Handle the deletion of VM disks."""
        rv = await api_client.delete(
            f"v2/vm/{vm_data.moref}/disk",
            json_data={"value": request.disk_units},
            context="deleting vm disks",
        )
        result = rv.get("data", {})
        return VmChangeRequestResult.model_validate(result)

    async def handle_vm_disk_scsi_update(
        self,
        api_client: VssApiClient,
        vm_data: VMInfo,
        request: VmDiskScsiUpdateRequest,
    ) -> VmChangeRequestResult:
        """Handle the SCSI controller update of a VM disk."""
        rv = await api_client.put(
            f"v2/vm/{vm_data.moref}/disk/{request.unit}/scsi",
            json_data={
                "unit": request.unit,
                "property": "scsi",
                "scsi": request.scsi,
            },
            context="updating vm disk scsi controller",
        )
        result = rv.get("data", {})
        return VmChangeRequestResult.model_validate(result)

    @staticmethod
    def _format_scsi_update_response(
        vm_data: VMInfo,
        request: VmDiskScsiUpdateRequest,
        change_request: VmChangeRequestResult,
    ) -> str:
        """Format SCSI update response."""
        response = f"{vm_data.name} disk SCSI controller updated successfully"
        response += f"""
         {'=' * 50}

         VM Details:
         - Name: {vm_data.name}
         - ID: {vm_data.moref}
         - Current State: {vm_data.power_state}
         
         Disk SCSI Update Details:
         {request.to_text()}
         
         Operation Result:
         {change_request.to_text()}
         """
        return response

    @staticmethod
    def _format_deletion_response(
        vm_data: VMInfo,
        request: VmDiskDeleteRequest,
        change_request: VmChangeRequestResult,
    ) -> str:
        """Format deletion response."""
        response = f"{vm_data.name} disks deleted successfully"
        response += f"""
         {'=' * 50}

         VM Details:
         - Name: {vm_data.name}
         - ID: {vm_data.moref}
         - Current State: {vm_data.power_state}
         
         Disk Deletion Details:
         {request.to_text()}
         
         Operation Result:
         {change_request.to_text()}
         """
        return response

    @staticmethod
    def _format_resize_response(
        vm_data: VMInfo,
        request: VmDiskResizeRequest,
        change_request: VmChangeRequestResult,
    ) -> str:
        """Format resize response."""
        response = f"{vm_data.name} disk resized successfully"
        response += f"""
         {'=' * 50}

         VM Details:
         - Name: {vm_data.name}
         - ID: {vm_data.moref}
         - Current State: {vm_data.power_state}
         
         Disk Resize Details:
         {request.to_text()}
         
         Operation Result:
         {change_request.to_text()}
         """
        return response

    @staticmethod
    def _format_response(
        vm_data: VMInfo,
        request: VmDiskCreateRequestList,
        change_request: VmChangeRequestResult,
    ) -> str:
        """Format response."""
        is_creation = isinstance(request, VmDiskCreateRequestList)
        # is_deletion = isinstance(request, VmDiskDeleteRequestList)
        # is_update = isinstance(request, VmDiskUpdateRequest)
        response = ''
        body = ''
        if is_creation:
            response = f"{vm_data.name} disks created successfully"
            body = ''
            for disk in request.disks:
                disk = cast(VmDiskCreateRequest, disk)
                body += disk.to_text()
        # elif is_deletion:
        response += f"""
         {'=' * 50}

         VM Details:
         - Name: {vm_data.name}
         - ID: {vm_data.moref}
         - Current State: {vm_data.power_state}
         
         Disk(s) details:
         {body}
         
         Operation Result:
         {change_request.to_text()}
         """
        return response
