"""Power management tools."""

from fastmcp import Context, FastMCP
from loguru import logger

from mcp_server_vss.client import VssApiClient
from mcp_server_vss.exceptions import VssError
from mcp_server_vss.models.requests import VmPowerControlRequest
from mcp_server_vss.tools.common import BaseVmTool


class ManagePowerVmTool(BaseVmTool):
    """Manage power of virtual machine."""

    def __init__(self, mcp: FastMCP, auth_token: str, api_endpoint: str):
        """Initialize class."""
        super().__init__(auth_token, api_endpoint)
        mcp.tool(name="power_control_vm")(self.power_control_vm)

    async def power_control_vm(
        self, ctx: Context, request: VmPowerControlRequest
    ) -> str:
        """Control VM power state (start, stop, restart, suspend, reset).

        Use this tool when you need to:
        - Start a stopped VM
        - Stop a running VM
        - Restart a VM (graceful or forced)
        - Suspend a VM for maintenance
        - Reset a VM (forced restart)

        Power actions:
        - on: Power on the VM
        - off: Power off the VM
        - reset: Forced restart (use with caution)
        - suspend: Suspend VM to disk

        Graceful actions (requires tools to be installed and running):
        - shutdown: Graceful shutdown
        - reboot: Graceful restart

        Args:
            request: Request object with vm_id_or_name and power_action
            ctx: The context object providing access to MCP capabilities.
        Returns:
            str: Text content of the tool result
        Raises:
            Exception: If there is an error with the VSS API or the tool
            result is not in the expected format
        """
        try:
            async with VssApiClient(
                self.auth_token, self.api_endpoint
            ) as api_client:
                await ctx.info(
                    f"Powering {request.vm_id_or_name} {request.power_action}"
                )
                vm_data = await self.handle_vm_info(
                    api_client, request.vm_id_or_name, ctx
                )
                # Get the change request
                change_request = await self.handle_vm_power_state(
                    api_client, vm_data, request.power_action, ctx
                )
                # Convert to tool result format
                tool_results = change_request.to_tool_result()
                # Extract text content from tool results
                if tool_results and hasattr(tool_results[0], 'text'):
                    return tool_results[0].text
                return str(change_request)
        except VssError as e:
            logger.error(f"VSS error in power_control_vm: {str(e)}")
            raise VssError(f"VSS API error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in power_control_vm: {e}")
            raise Exception(f"Internal error: {str(e)}")
