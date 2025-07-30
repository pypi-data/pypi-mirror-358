"""Get VM info tool."""

from fastmcp import Context, FastMCP
from loguru import logger

from mcp_server_vss.client import VssApiClient
from mcp_server_vss.exceptions import VssError
from mcp_server_vss.models import VmInfoRequest
from mcp_server_vss.tools.common import BaseVmTool


class GetVmInfoTool(BaseVmTool):
    """Get VM info tool."""

    def __init__(self, mcp: FastMCP, auth_token: str, api_endpoint: str):
        """Initialize class."""
        super().__init__(auth_token, api_endpoint)
        mcp.tool(name='get_vm_info')(self.get_vm_info)

    async def get_vm_info(self, request: VmInfoRequest, ctx: Context) -> str:
        """Retrieve and analyze an ITS Private Cloud VM by ID, Name, or UUID.

        Use this tool when you need to:
        - Get detailed information about a virtual machine
        - Check VM configuration and status
        - Analyze VM resource allocation

        Args:
            request: The request object containing the VM ID, UUID, or name.
            ctx: MCP context for logging and state management

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
                # Convert to tool result format
                tool_results = vm_data.to_tool_result()
                # Extract text content from tool results
                if tool_results and hasattr(tool_results[0], 'text'):
                    return tool_results[0].text
                return str(vm_data)
        except VssError as e:
            logger.error(f"VSS error in get_vm_info: {str(e)}")
            await ctx.error(f"VSS API error: {str(e)}")
            raise Exception(f"VSS API error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in get_vm_info: {e}")
            await ctx.error(f"Unexpected error: {str(e)}")
            raise Exception(f"Unexpected error: {str(e)}")
