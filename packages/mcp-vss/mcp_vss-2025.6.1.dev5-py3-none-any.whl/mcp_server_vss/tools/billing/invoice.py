"""Billing Client Invoice Tool."""
from fastmcp import Context, FastMCP

from mcp_server_vss.client import VssApiClient
from mcp_server_vss.exceptions import VssError
from mcp_server_vss.models import BillingDetailsRequest
from mcp_server_vss.models.billing import (
    BillingClient, InvoiceDetails, InvoicesSummary, InvoiceSummary,
    MultipleInvoicesDetails)
from mcp_server_vss.models.requests import (
    BillingInvoiceDetailsOverTime, BillingInvoiceDetailsRequest)
from mcp_server_vss.tools.common import BaseBillingTool


class BillingClientInvoiceTool(BaseBillingTool):
    """Billing Client Invoice Tool."""

    def __init__(self, mcp: FastMCP, auth_token: str, api_endpoint: str):
        """Initialize class."""
        super().__init__(auth_token, api_endpoint)
        mcp.tool(name='get_billing_client_invoice')(
            self.get_billing_client_invoice
        )
        mcp.tool(name='get_billing_client_invoices')(
            self.get_billing_client_invoices
        )
        mcp.tool(name='get_billing_client_invoices_over_time')(
            self.get_billing_client_invoices_over_time
        )

    async def get_billing_client_invoice(
        self, request: BillingInvoiceDetailsRequest, ctx: Context
    ) -> str:
        """Retrieve and analyze an ITS Private Cloud Billing Invoice details
        by number or ID.

        Use this tool whe you need to:
        - Analyze details of a given invoice.
        - Find billed items and resources.
        - Locate most expensive line items.
        - User asks for invoice details.

        Args:
            request: The request object containing the client_id_or_name
                     and invoice_number_or_id.
            ctx: The context object providing access to MCP capabilities.
        Return:
            str: A string representation of the billing information.
        """

        try:
            async with VssApiClient(
                self.auth_token, self.api_endpoint
            ) as api_client:
                # fetch client data
                client_data = await self.handle_client_info(
                    api_client, request.client_id_or_name, ctx
                )
                # fetch invoice data
                invoice_data = await self.handle_client_invoice_details(
                    api_client, client_data, request.invoice_number_or_id, ctx
                )
                # Convert to tool result format
                tool_results = invoice_data.to_tool_result()
                # Extract text content from tool results
                if tool_results and hasattr(tool_results[0], 'text'):
                    return tool_results[0].text
                return str(invoice_data)
        except VssError as e:
            await ctx.error(
                f"VSS error in get_billing_client_invoices: {str(e)}"
            )
            raise Exception(f"VSS API error: {str(e)}")
        except Exception as e:
            await ctx.error(
                f"Unexpected error in get_billing_client_invoices: {e}"
            )
            raise Exception(f"Internal error: {str(e)}")

    async def get_billing_client_invoices(
        self, request: BillingDetailsRequest, ctx: Context
    ) -> str:
        """Retrieve an ITS Private Cloud Client account invoices (summary).

         Use this tool whe you need to:
        - Get a list of invoices (summary) from a particular billing client
        - Analyze global cost trends
        - Get a total of cost per month

        Args:
            request: The request object containing the client_id_or_name.
            ctx: The context object providing access to MCP capabilities.
        Returns:
            str: A string representation of the billing information.
        """

        try:
            async with VssApiClient(
                self.auth_token, self.api_endpoint
            ) as api_client:
                client_data = await self.handle_client_info(
                    api_client, request.client_id_or_name, ctx
                )
                invoices_data = await self.handle_client_invoices(
                    api_client, client_data, ctx
                )
                # Convert to tool result format
                tool_results = invoices_data.to_tool_result()
                # Extract text content from tool results
                if tool_results and hasattr(tool_results[0], 'text'):
                    return tool_results[0].text
                return str(invoices_data)
        except VssError as e:
            await ctx.error(
                f"VSS error in get_billing_client_invoices: {str(e)}"
            )
            raise Exception(f"VSS API error: {str(e)}")
        except Exception as e:
            await ctx.error(
                f"Unexpected error in get_billing_client_invoices: {e}"
            )
            raise Exception(f"Internal error: {str(e)}")

    async def get_billing_client_invoices_over_time(
        self, request: BillingInvoiceDetailsOverTime, ctx: Context
    ):
        """Retrieve billing client invoices over time in detailed format.

         Use this tool whe you need to:
        - Get a list of invoices in detail from a particular billing client
        - Analyze resource and usage cost trends
        - Get a detailed of cost per month

        Args:
            request: The request object containing the client_id_or_name.
            ctx: The context object providing access to MCP capabilities.
        Returns:
            str: A string representation of the billing information.
        """
        try:
            async with VssApiClient(
                self.auth_token, self.api_endpoint
            ) as api_client:
                client_data = await self.handle_client_info(
                    api_client, request.client_id_or_name, ctx
                )
                # get invoices over time
                invoices_data = (
                    await self.handle_client_invoices_detail_period(
                        api_client,
                        client_data,
                        request.analysis_period_in_days,
                        ctx,
                    )
                )
                tool_results = invoices_data.to_tool_result()
                # Extract text content from tool results
                if tool_results and hasattr(tool_results[0], 'text'):
                    return tool_results[0].text
                return str(invoices_data)
        except VssError as e:
            await ctx.error(
                f"VSS error in get_billing_client_invoices: {str(e)}"
            )
            raise Exception(f"VSS API error: {str(e)}")
        except Exception as e:
            await ctx.error(
                f"Unexpected error in get_billing_client_invoices: {e}"
            )
            raise Exception(f"Internal error: {str(e)}")

    async def handle_client_invoice_details(
        self,
        api_client: VssApiClient,
        client_data: BillingClient,
        invoice_number_or_id: str,
        ctx: Context,
    ) -> InvoiceDetails:
        """Retrieve billing client invoice details by ID or name."""
        await ctx.info(
            f"Fetching billing invoice info for: {client_data.name}"
            f"({client_data.id}) {invoice_number_or_id}"
        )
        invoice_endpoint = (
            f"billing/client/{client_data.id}/invoice/{invoice_number_or_id}"
        )
        rv = await api_client.get(
            invoice_endpoint,
            f"fetching client info for '{client_data.id}/{invoice_number_or_id}'",
        )
        return InvoiceDetails.model_validate(rv)

    async def handle_client_invoices(
        self,
        api_client: VssApiClient,
        client_data: BillingClient,
        ctx: Context,
    ) -> InvoicesSummary:
        """Retrieve billing client invoices summary by ID or name."""
        await ctx.info(
            f"Fetching billing client invoices for: {client_data.name}"
            f"({client_data.id})"
        )
        client_endpoint = f"billing/client/{client_data.id}/invoice"
        rv = await api_client.get(
            client_endpoint,
            f"fetching client invoices for '{client_data.name}'",
        )
        invoices = rv.get('data', [])
        return InvoicesSummary.model_validate(
            {
                'invoices': [
                    InvoiceSummary.model_validate(inv) for inv in invoices
                ]
            }
        )

    async def handle_client_invoices_detail_period(
        self,
        api_client: VssApiClient,
        client_data: BillingClient,
        period_in_days: int,
        ctx: Context,
    ) -> MultipleInvoicesDetails:
        """Retrieve client invoices details per period."""
        period_in_days = self._validate_number_input(
            period_in_days, "Period in days"
        )

        await ctx.info(
            f"Fetching billing invoices details for: {client_data.name}"
            f"({client_data.id}) {period_in_days}d"
        )
        invoices_endpoint = (
            f"billing/client/{client_data.id}/invoice/period/{period_in_days}"
        )
        rv = await api_client.get(
            invoices_endpoint,
            f"fetching client invoices for '{client_data.id}'",
        )
        invoices = rv.get('data', [])
        await ctx.info(f"Fetched {len(invoices)} invoices")
        return MultipleInvoicesDetails.model_validate(
            {
                'invoices': [
                    InvoiceDetails.model_validate(inv) for inv in invoices
                ]
            }
        )
