"""Get VM info tool."""

from fastmcp import Context, FastMCP
from loguru import logger

from mcp_server_vss.client import VssApiClient
from mcp_server_vss.exceptions import VssError
from mcp_server_vss.models.requests import VmConsoleRequest
from mcp_server_vss.models.vms import VmConsoleLink, VMInfo
from mcp_server_vss.tools.common import BaseVmTool


class GetVmConsoleTool(BaseVmTool):
    """Get VM info tool."""

    def __init__(self, mcp: FastMCP, auth_token: str, api_endpoint: str):
        """Initialize class."""
        super().__init__(auth_token, api_endpoint)
        mcp.tool(name='get_vm_console_access')(self.get_vm_console_access)

    async def get_vm_console_access(
        self, ctx: Context, request: VmConsoleRequest
    ) -> str:
        """Get console access URL for a virtual machine.

        Use this tool when you need to:
        - Access VM when network is unavailable
        - Troubleshoot boot issues
        - Perform emergency administration

        Args:
            request: The request object containing the VM ID, UUID, or name.
            ctx: The context object providing access to MCP capabilities.

        Return:
            str: A string representation of the VM console link.
        """
        try:
            async with VssApiClient(
                self.auth_token, self.api_endpoint
            ) as api_client:
                vm_data = await self.handle_vm_info(
                    api_client, request.vm_id_or_uuid_or_name, ctx
                )
                # Handle VM console access
                console_url = await self.handle_vm_console_access(
                    api_client, vm_data, ctx
                )
                tool_results = console_url.to_tool_result()
                # Extract text content from tool results
                if tool_results and hasattr(tool_results[0], 'text'):
                    return tool_results[0].text
                return str(console_url)
        except VssError as e:
            e_msg = f"VSS error in get_vm_console_access: {str(e)}"
            await ctx.error(e_msg)
            logger.error(e_msg)
            raise VssError(f"VSS API error: {str(e)}")
        except Exception as e:
            await ctx.error(f"Unexpected error in get_vm_console_access: {e}")
            raise Exception(f"Internal error: {str(e)}")

    async def handle_vm_console_access(
        self, api_client: VssApiClient, vm_data: VMInfo, ctx: Context
    ) -> VmConsoleLink:
        """Retrieve VM console access URL by ID or name."""
        await ctx.info(f"Retrieving VM console access for '{vm_data.name}'")
        vm_endpoint = f'v2/vm/{vm_data.moref}/vcenter'
        rv = await api_client.get(
            vm_endpoint,
            f"fetching VM console access for '{vm_data.name} "
            f"({vm_data.moref})'",
        )
        return VmConsoleLink.model_validate(rv.get('data', {}))
