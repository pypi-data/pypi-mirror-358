from fastmcp import Context, FastMCP

from mcp_server_vss.client import VssApiClient
from mcp_server_vss.exceptions import VssError
from mcp_server_vss.models import BillingDetailsRequest
from mcp_server_vss.models.billing import FisRecord
from mcp_server_vss.models.requests import FisUpdateRequest
from mcp_server_vss.tools.common import BaseBillingTool


class BillingClientPaymentTool(BaseBillingTool):
    """Client tool for the Billing API."""

    def __init__(self, mcp: FastMCP, auth_token: str, api_endpoint: str):
        """Initialize class."""
        super().__init__(auth_token, api_endpoint)
        mcp.tool(name='get_billing_payment_details')(
            self.get_billing_payment_details
        )
        mcp.tool(name='update_billing_payment_details')(
            self.update_billing_payment_details
        )

    async def get_billing_payment_details(
        self, request: BillingDetailsRequest, ctx: Context
    ) -> str:
        """Retrieve an ITS Private Cloud Billing account payment details.

         Also known as FIS by name or ID.

        Use this tool when you need to:
        - Get payment information about a billing client such as FIS
        - Check cost centre, commitment fund centre, fund, budget code
          bus area, assignment, commitment item

        Args:
            request: ITS Private Cloud Client ID or Name to analyze.
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
                await ctx.info('Fetching Billing client payment details')
                fis_data = await self.handle_billing_client_fis(
                    api_client, client_data, ctx
                )
                # Convert to tool result format
                tool_results = fis_data.to_tool_result()
                # Extract text content from tool results
                if tool_results and hasattr(tool_results[0], 'text'):
                    return tool_results[0].text
                return str(fis_data)
        except VssError as e:
            await ctx.error(f"VSS error in get_billing_details: {str(e)}")
            raise Exception(f"VSS API error: {str(e)}")
        except Exception as e:
            await ctx.error(f"Unexpected error in get_billing_details: {e}")
            raise Exception(f"Internal error: {str(e)}")

    async def update_billing_payment_details(
        self, request: FisUpdateRequest, ctx: Context
    ) -> str:
        """Update the billing payment details for a client.

        Also known as FIS.

        Use this tool when you need to:
        - Update payment information about a billing client such as FIS
        - Update cost centre, commitment fund centre, fund, budget code
          bus area, assignment, commitment item.

        Args:
            request (FisUpdateRequest): The request object containing the client ID or
            name, cost centre, commitment fund centre, fund, budget code, bus area,
            assignment, and commitment item.
            ctx: The context object providing access to MCP capabilities.
        Returns:
            str: The tool result in text format.
        """
        try:
            async with VssApiClient(
                self.auth_token, self.api_endpoint
            ) as api_client:
                await ctx.info(
                    f'Attempting to update {request.client_id_or_name}'
                )
                fis_data = await self.handle_billing_client_fis_update(
                    api_client, request, ctx
                )
                # Convert to tool result format
                tool_results = fis_data.to_tool_result()
                # Extract text content from tool results
                if tool_results and hasattr(tool_results[0], 'text'):
                    return tool_results[0].text
                return str(fis_data)
        except VssError as e:
            await ctx.error(
                f"VSS error in update_billing_payment_details: {str(e)}"
            )
            raise Exception(f"VSS API error: {str(e)}")
        except Exception as e:
            await ctx.error(
                f"Unexpected error in update_billing_payment_details: {e}"
            )
            raise Exception(f"Internal error: {str(e)}")

    async def handle_billing_client_fis_update(
        self, api_client: VssApiClient, request: FisUpdateRequest, ctx: Context
    ) -> FisRecord:
        """Update the billing client for a VM by ID or name."""
        client_data = await self.handle_client_info(
            api_client, request.client_id_or_name, ctx
        )
        if not client_data:
            raise VssError(
                f"No billing client found for {request.client_id_or_name}"
            )
        await ctx.info(f'Updating {client_data.name} ({client_data.id})')
        rv = await api_client.put(
            f"billing/client/{request.client_id_or_name}/fis",
            json_data=request.model_dump(
                exclude_unset=True, exclude_defaults=True, exclude_none=True
            ),
            context="updating FIS",
        )
        result = rv.get("data", {})
        return FisRecord.model_validate(result)
