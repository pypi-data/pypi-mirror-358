"""VM performance metrics tool."""
from fastmcp import Context, FastMCP
from loguru import logger

from mcp_server_vss.client import VssApiClient
from mcp_server_vss.exceptions import VssError
from mcp_server_vss.models.requests import VmMetricsRequest
from mcp_server_vss.tools.common import BaseVmTool


class GetVmPerformanceMetricsTool(BaseVmTool):
    """Get VM performance metrics tool."""

    def __init__(self, mcp: FastMCP, auth_token: str, api_endpoint: str):
        """Initialize class."""
        super().__init__(auth_token, api_endpoint)
        mcp.tool(name='get_vm_performance_metrics')(
            self.get_vm_performance_metrics
        )

    async def get_vm_performance_metrics(
        self, request: VmMetricsRequest, ctx: Context
    ) -> str:
        """Retrieve detailed performance metrics for a VM.

        Use this tool when you need to:
        - Analyze CPU, memory, disk, network utilization
        - Identify performance bottlenecks
        - Generate performance reports
        - Monitor resource trends over time

        Args:
            request: The request object containing the VM ID, UUID, or name.
            ctx: Context

        Return:
            str: A string representation of the VM performance metrics.
        """
        try:
            async with VssApiClient(
                self.auth_token, self.api_endpoint
            ) as api_client:
                vm_data = await self.handle_vm_info(
                    api_client, request.vm_id_or_uuid_or_name, ctx
                )
                metrics = await self.handle_vm_performance(
                    api_client,
                    vm_data,
                    ctx,
                    time_period_in_hours=request.time_period_in_hours,
                )
                tool_results = metrics.to_tool_result()
                # Extract text content from tool results
                if tool_results and hasattr(tool_results[0], 'text'):
                    return tool_results[0].text
                return str(metrics)
        except VssError as e:
            logger.error(f"VSS error in get_vm_performance_metrics: {str(e)}")
            raise Exception(f"VSS API error: {str(e)}")
        except Exception as e:
            logger.error(
                f"Unexpected error in get_vm_performance_metrics: {e}"
            )
            raise Exception(f"Internal error: {str(e)}")
