from fastmcp import Context, FastMCP

from mcp_server_vss.client import VssApiClient
from mcp_server_vss.exceptions import VssError
from mcp_server_vss.models import BillingDetailsRequest
from mcp_server_vss.tools.common import BaseBillingTool


class BillingClientTool(BaseBillingTool):
    """Client tool for the Billing API."""

    def __init__(self, mcp: FastMCP, auth_token: str, api_endpoint: str):
        """Initialize class."""
        super().__init__(auth_token, api_endpoint)
        mcp.tool(name='billing_client_tool')(self.get_billing_clients)
        mcp.tool(name='get_billing_details')(self.get_billing_details)

    async def get_billing_details(
        self, request: BillingDetailsRequest, ctx: Context
    ) -> str:
        """Retrieve and analyze an ITS Private Cloud Billing account by name or ID.

        Use this tool when you need to:

        - Get information about a billing client or account
        - Check billing client account details
        - Analyze cost and usage information
        - User is asking about debit memos or invoices

        Args:
            request: The request object containing the client ID or name.
            ctx: The context object providing access to MCP capabilities.

        Returns:
            str: The tool result in text format.
        """
        try:
            async with VssApiClient(
                self.auth_token, self.api_endpoint
            ) as api_client:
                client_data = await self.handle_client_info(
                    api_client, request.client_id_or_name, ctx
                )
                # Convert to tool result format
                tool_results = client_data.to_tool_result()
                # Extract text content from tool results
                if tool_results and hasattr(tool_results[0], 'text'):
                    return tool_results[0].text
                return str(client_data)
        except VssError as e:
            await ctx.error(f"VSS error in get_billing_details: {str(e)}")
            raise Exception(f"VSS API error: {str(e)}")
        except Exception as e:
            await ctx.error(f"Unexpected error in get_billing_details: {e}")
            raise Exception(f"Internal error: {str(e)}")

    async def get_billing_clients(self, ctx: Context):
        """Retrieve and analyze an ITS Private Cloud Billing accounts or clients.

        Use this tool when you need to:
        - Obtain attributes like billing account ID.
        - Get a list of billing accounts or client definition.
        - Get an overview of billing accounts or clients.
        - Get basic info like name, address, services, etc.
        """
        try:
            async with VssApiClient(
                self.auth_token, self.api_endpoint
            ) as api_client:
                clients_data = await self.handle_billing_clients(api_client)
                # Convert to tool result format
                tool_results = clients_data.to_tool_result()
                # Extract text content from tool results
                if tool_results and hasattr(tool_results[0], 'text'):
                    return tool_results[0].text
                return str(clients_data)
        except VssError as e:
            logger.error(f"VSS error in get_billing_details: {str(e)}")
            raise Exception(f"VSS API error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in get_billing_details: {e}")
            raise Exception(f"Internal error: {str(e)}")
