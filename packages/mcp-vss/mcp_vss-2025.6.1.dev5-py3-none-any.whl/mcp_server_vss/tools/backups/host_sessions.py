"""Backups Client Tool."""
from datetime import datetime, timedelta
from typing import Optional

from fastmcp import Context, FastMCP

from mcp_server_vss.client import VssApiClient
from mcp_server_vss.exceptions import VssError
from mcp_server_vss.models import BackupHostSession, BillingClient
from mcp_server_vss.models.backups import BackupHostSessionList
from mcp_server_vss.models.requests import ClientBackupHostSessionsRequest
from mcp_server_vss.tools.common import BaseBillingTool


class BillingClientBackupsTool(BaseBillingTool):
    """Backups Client Tool."""

    def __init__(self, mcp: FastMCP, auth_token: str, api_endpoint: str):
        """Initialize the VM tool."""
        super().__init__(auth_token, api_endpoint)
        mcp.tool(name='get_client_backup_host_sessions')(
            self.get_client_backup_host_sessions
        )

    async def get_client_backup_host_sessions(
        self, request: ClientBackupHostSessionsRequest, ctx: Context
    ) -> str:
        """Get the UTORrecover backup host sessions for a client.

        Use this tool when you need to:
        - UTORrecover or backup data usage analysis is required.
        - Session count is required to analyze the number of sessions.
        - Overall usage is required over a period of time for a particular host.

        Args:
            request (ClientBackupHostSessionsRequest): The request object containing
             the client ID or name, hostname, start date, and end date. Start date and
             end date are optional and defaults to the past month.
            ctx (Context): Context object providing access to MCP capabilities.
        """
        try:
            async with VssApiClient(
                self.auth_token, self.api_endpoint
            ) as api_client:
                client_data = await self.handle_client_info(
                    api_client, request.client_id_or_name, ctx
                )
                if not client_data:
                    raise VssError(
                        f"Client not found: {request.client_id_or_name}"
                    )
                # Get the client backup host sessions
                sessions_data = (
                    await self.handle_get_client_backup_host_sessions(
                        api_client,
                        client_data,
                        request.hostname,
                        ctx=ctx,
                        start_date=request.start_date,
                        end_date=request.end_date,
                    )
                )
                # Convert to tool result format
                tool_results = sessions_data.to_tool_result()
                # Extract text content from tool results
                if tool_results and hasattr(tool_results[0], 'text'):
                    return tool_results[0].text
                return str(sessions_data)
        except VssError as e:
            await ctx.error(f"VSS error in get_billing_details: {str(e)}")
            raise Exception(f"VSS API error: {str(e)}")
        except Exception as e:
            await ctx.error(f"Unexpected error in get_billing_details: {e}")
            raise Exception(f"Internal error: {str(e)}")

    async def handle_get_client_backup_host_sessions(
        self,
        api_client: VssApiClient,
        client_data: BillingClient,
        host: str,
        ctx: Context,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> BackupHostSessionList:
        """Fetch backup host sessions for a client."""
        # validate start_date and end_date if not None
        if start_date and end_date:
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d')
                end_date = datetime.strptime(end_date, '%Y-%m-%d')
            except ValueError:
                raise VssError("Invalid date format. Please use YYYY-MM-DD")
        else:
            start_date = datetime.now() - timedelta(days=30)
            end_date = datetime.now()
        await ctx.info(
            f'Fetching backup host sessions for client {client_data.name}({client_data.id}) '
            f'{host=}: {start_date=} {end_date=}'
        )
        endpoint = (
            f'billing/client/{client_data.id}/service/backup/host/{host}/session?'
            f'start_date={start_date.strftime("%Y-%m-%d")}&end_date={end_date.strftime("%Y-%m-%d")}'
        )
        rv = await api_client.get(
            endpoint, context="getting backup host sessions"
        )
        sessions_data = rv.get('data', [])
        if not sessions_data:
            raise VssError("No backup host sessions found")
        await ctx.info(f'Backup host sessions found: {len(sessions_data)}')
        sessions = [
            BackupHostSession.model_validate(session)
            for session in sessions_data
        ]
        return BackupHostSessionList(items=sessions)
