"""Main server for the MCP server."""
import sys
from typing import Optional

import click
from fastmcp import FastMCP
from loguru import logger
from pydantic import Field

from mcp_server_vss import prompts as vss_prompts
from mcp_server_vss.client import VssApiClient
from mcp_server_vss.exceptions import VssError
from mcp_server_vss.models.billing import BillingClient, BillingClientsSummary
from mcp_server_vss.models.vms import (
    GuestOS, GuestOSList, NetworkInfo, NetworkList, VMInfo, VmInfoList)
from mcp_server_vss.tools.backups import BillingClientBackupsTool
from mcp_server_vss.tools.billing import (
    BillingClientInvoiceTool, BillingClientPaymentTool, BillingClientTool)
from mcp_server_vss.tools.vms import (
    GetVmConsoleTool, GetVmInfoTool, GetVmPerformanceMetricsTool,
    ManageDisksVmTool, ManagePowerVmTool, ManageSnapshotVmTool, ResizeVmTool)

VSS_API_BASE = "https://vss-api.eis.utoronto.ca"


async def handle_billing_clients(
    api_client: VssApiClient,
) -> BillingClientsSummary:
    """Retrieve billing clients summary."""
    clients_endpoint = "billing/client"
    rv = await api_client._make_request(clients_endpoint, "fetching clients")
    clients = rv.get('data', [])
    return BillingClientsSummary.model_validate(
        {
            'clients': [
                BillingClient.model_validate(client) for client in clients
            ]
        }
    )


async def handle_vms(api_client: VssApiClient, endpoint: str) -> VmInfoList:
    """List virtual machines in the ITS Private Cloud."""
    rv = await api_client.get(endpoint or 'v2/vm', context="getting VMs")
    vm_data = rv.get('data', [])
    if not vm_data:
        raise VssError("No VMs found")
    logger.info(f'VMs found: {len(vm_data)}')
    vms = [VMInfo.model_validate(vm) for vm in vm_data]
    logger.info(f'VMs found as models: {len(vms)}')
    return VmInfoList(vms=vms)


async def handle_nets(api_client: VssApiClient, endpoint: str) -> NetworkList:
    """List virtual networks in the ITS Private Cloud."""
    rv = await api_client.get(
        endpoint or 'v2/network', context="getting networks"
    )
    net_data = rv.get('data', [])
    if not net_data:
        raise VssError("No networks found")
    logger.info(f'Networks found: {len(net_data)}')
    nets = [NetworkInfo.model_validate(net) for net in net_data]
    return NetworkList(networks=nets)


async def handle_operating_systems(
    api_client: VssApiClient,
    full_name: Optional[str] = None,
    guest_id: Optional[str] = None,
    max_results: Optional[int] = 100,
) -> GuestOSList:
    """List operating systems in the ITS Private Cloud."""
    # Build endpoint with filter if provided
    endpoint = f"v2/os?per_page={max_results}"
    if full_name:
        endpoint += f"&filter=full_name,like,%{full_name}%"
    elif guest_id:
        endpoint += f"&filter=guest_id,like,%{guest_id}%"
    else:
        logger.info('No filter provided, returning all OSs')
        pass
    rv = await api_client.get(
        endpoint or 'v2/os', context="getting operating systems"
    )
    os_data = rv.get('data', [])
    if not os_data:
        raise VssError("No operating systems found")
    logger.info(f'Operating systems found: {len(os_data)}')
    oss = [GuestOS.model_validate(os) for os in os_data]
    return GuestOSList(items=oss)


def create_app(auth_token: str, api_endpoint: str) -> FastMCP:
    """Create and configure the FastMCP application."""
    if not auth_token:
        raise VssError("Authentication token is required")
    # Create FastMCP app
    mcp = FastMCP(
        "ITS Private Cloud (VSS) MCP Server",
        log_level="ERROR",
        instructions="""
Use this server for retrieving ITS Private Cloud service resources,
with a focus on virtual machines.
""",
    )
    # register tools
    for tool in [
        ResizeVmTool,
        GetVmInfoTool,
        ManageSnapshotVmTool,
        GetVmPerformanceMetricsTool,
        GetVmConsoleTool,
        ManagePowerVmTool,
        BillingClientTool,
        BillingClientPaymentTool,
        BillingClientInvoiceTool,
        BillingClientBackupsTool,
        ManageDisksVmTool,
    ]:
        reg = tool(mcp, auth_token, api_endpoint)
        logger.info(f'Tool registered: {reg}')

    @mcp.resource("its://vms")
    async def vms() -> str:
        """List virtual machines in the ITS Private Cloud.

        This resource provides an overview of VMs:
        - VM names and IDs
        - Current status (running, stopped, etc.)
        - Basic resource allocation
        - Client ownership information

        Limits:
        - Only provides a maximum of 200 instances.
        - Does not provide detailed resource allocation information.
        - Does not provide client ownership information.
        """
        try:
            async with VssApiClient(auth_token, api_endpoint) as api_client:
                # Build endpoint with filter if provided
                vms_endpoint = "v2/vm?per_page=200"
                vm_list = await handle_vms(api_client, vms_endpoint)
                # Create formatted output
                output = f"ITS Private Cloud VMs: {len(vm_list.vms)} VM(s)\n"
                output += "=" * 50 + "\n\n"
                output += vm_list.to_text()
                output += "=" * 50 + "\n\n"
                output += 'Note: Only showing first 200 VMs.'
                return output
        except VssError as e:
            logger.error(f"VSS error in list_vms resource: {str(e)}")
            return f"Error retrieving VM list: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error in list_vms resource: {e}")
            return f"Internal error retrieving VM list: {str(e)}"

    @mcp.resource("its://domains")
    async def domains() -> str:
        """List compute domains/clusters in the ITS Private Cloud.

        This resource provides an overview of all compute domains including:
        - Domain names and IDs
        - Overall status (green, yellow, red)
        - Available GPU profiles
        - Host count and resource summary
        """
        try:
            async with VssApiClient(auth_token, api_endpoint) as api_client:
                # Get list of all domains
                domains_endpoint = "v2/domain"
                rv = await api_client._make_request(
                    domains_endpoint, "fetching domain list"
                )

                domain_data = rv.get('data', [])
                if not domain_data:
                    return "No compute domains found."

                # Format the domain list for resource output
                domain_list = []
                for domain in domain_data:
                    domain_summary = {
                        'moref': domain.get('moref', 'N/A'),
                        'name': domain.get('name', 'N/A'),
                        'status': domain.get('overall_status', 'N/A'),
                        'gpu_profiles': domain.get('gpu_profiles', 'N/A'),
                        'hosts_count': domain.get('hosts_count', 'N/A'),
                        'cpu_cores': domain.get('num_cpu_cores', 'N/A'),
                        'created_on': domain.get('created_on', 'N/A'),
                    }
                    domain_list.append(domain_summary)

                # Create formatted output
                output = "ITS Private Cloud Compute Domains:\n"
                output += f"Found {len(domain_list)} domain(s)\n\n"

                for domain in domain_list:
                    output += f"• {domain['name']} (ID: {domain['moref']})\n"
                    output += f"  Status: {domain['status']}\n"

                    if domain['hosts_count'] != 'N/A':
                        output += f"  Hosts: {domain['hosts_count']}"
                        if domain['cpu_cores'] != 'N/A':
                            output += f" | CPU Cores: {domain['cpu_cores']}"
                        output += "\n"

                    # Display GPU profiles if available
                    if (
                        domain['gpu_profiles'] != 'N/A'
                        and domain['gpu_profiles']
                    ):
                        gpu_list = domain['gpu_profiles'].split(', ')
                        if len(gpu_list) > 3:
                            # Show first 3 and count
                            gpu_display = (
                                ', '.join(gpu_list[:3])
                                + f" (+{len(gpu_list)-3} more)"
                            )
                        else:
                            gpu_display = domain['gpu_profiles']
                        output += f"  GPU Profiles: {gpu_display}\n"

                    output += (
                        f"  Resource URI: its://domains/{domain['moref']}\n\n"
                    )

                return output

        except VssError as e:
            logger.error(f"VSS error in list_domains resource: {str(e)}")
            return f"Error retrieving domain list: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error in list_domains resource: {e}")
            return f"Internal error retrieving domain list: {str(e)}"

    @mcp.resource("its://vms/utorrecover")
    async def vms_utorrecover() -> str:
        """List virtual machines protected by UTORrecover.

        This resource provides an overview of VMs:
        - VM names and IDs
        - Current status (running, stopped, etc.)
        - Basic resource allocation
        """
        try:
            async with VssApiClient(auth_token, api_endpoint) as api_client:
                # Build endpoint with filter if provided
                vms_endpoint = (
                    "v2/vm?per_page=200&filter=backup_svc,eq,UTORrecover"
                )
                # Get VM list
                vm_list = await handle_vms(api_client, vms_endpoint)
                # Create formatted output
                output = (
                    f"ITS Private Cloud VMs: {len(vm_list.vms)} VM(s) "
                    f"(UTORrecover protected)\n\n"
                )
                output += "=" * 50 + "\n\n"
                output += vm_list.to_text()
                output += "=" * 50 + "\n\n"
                output += 'Note: Only showing first 200 VMs.'
                return output
        except VssError as e:
            logger.error(
                f"VSS error in list_vms_utorrecover resource: {str(e)}"
            )
            return f"Error retrieving VM list: {str(e)}"
        except Exception as e:
            logger.error(
                f"Unexpected error in list_vms_utorrecover resource: {e}"
            )
            return f"Internal error retrieving VM list: {str(e)}"

    @mcp.resource('its://networks')
    async def networks() -> str:
        """Retrieve a list of networks in the ITS Private Cloud.

        This resource provides a list of available networks with
        the following details:
        - ID
        - Name
        - VLAN ID
        - Subnet
        - Metadata: Admin, description, resource URI, status
        """
        try:
            async with VssApiClient(auth_token, api_endpoint) as api_client:
                # Build endpoint with filter if provided
                vms_endpoint = "v2/network?per_page=100"
                # Get Net list
                net_list = await handle_nets(api_client, vms_endpoint)
                # Create formatted output
                output = (
                    f"ITS Private Cloud Networks: "
                    f"{len(net_list.networks)} \n\n"
                )
                output += "=" * 50 + "\n\n"
                output += net_list.to_text()
                output += "=" * 50 + "\n\n"
                output += 'Note: Only showing first 100 Networks.'
                return output
        except VssError as e:
            logger.error(f"VSS error in list_vms resource: {str(e)}")
            return f"Error retrieving VM list: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error in list_vms resource: {e}")
            return f"Internal error retrieving VM list: {str(e)}"

    @mcp.resource("its://os")
    async def operating_systems() -> str:
        """Retrieve a list of operating systems in the ITS Private Cloud.

        This resource provides a list of supported Operating Systems with
        the following details:
        - Full Name
        - Guest ID
        - Family
        """
        try:
            async with VssApiClient(auth_token, api_endpoint) as api_client:
                # Get OS list
                max_results = 100
                os_list = await handle_operating_systems(
                    api_client, None, None, max_results=max_results
                )
                # Create formatted output
                output = (
                    f"ITS Private Cloud Supported "
                    f"OS': {len(os_list.items)} \n\n"
                )
                output += "=" * 50 + "\n\n"
                output += os_list.to_text()
                output += "=" * 50 + "\n\n"
                output += (
                    'Note: Only showing first 100 Operating Systems. '
                    'Use the full_name or family filter to retrieve more.'
                )
                return output
        except VssError as e:
            logger.error(f"VSS error in list_vms resource: {str(e)}")
            return f"Error retrieving VM list: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error in list_vms resource: {e}")
            return f"Internal error retrieving VM list: {str(e)}"

    @mcp.resource("its://os/{full_name}")
    async def operating_systems_filter(
        full_name: str | None = None,
        guest_id: str | None = None,
        max_results: int = 100,
    ) -> str:
        """Retrieve a list of operating systems in the ITS Private Cloud.

        This resource provides a list of supported Operating Systems
        with the following details:
        - Full Name
        - Guest ID
        - Family
        """
        try:
            async with VssApiClient(auth_token, api_endpoint) as api_client:
                # Get OS list
                os_list = await handle_operating_systems(
                    api_client, full_name, guest_id, max_results
                )
                # Create formatted output
                output = (
                    f"ITS Private Cloud Supported "
                    f"OS': {len(os_list.items)} \n\n"
                )
                output += "=" * 50 + "\n\n"
                output += os_list.to_text()
                output += "=" * 50 + "\n\n"
                output += (
                    'Note: Only showing first 100 Operating Systems. '
                    'Use the full_name or family filter to retrieve more.'
                )
                return output
        except VssError as e:
            logger.error(f"VSS error in list_vms resource: {str(e)}")
            return f"Error retrieving VM list: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error in list_vms resource: {e}")
            return f"Internal error retrieving VM list: {str(e)}"

    @mcp.resource('its://clients')
    async def billing_clients() -> str:
        """Retrieve a list of billing clients in the ITS Private Cloud.

        This resource provides a list of avaiable clients
        with the following details:
        - ID
        - Name
        - Description
        - Resource URI
        - Status
        - Billing Option and Frequency
        - Number of bills (debit memos/invoices)
        - Address
        """
        try:
            async with VssApiClient(auth_token, api_endpoint) as api_client:
                clients_data = await handle_billing_clients(api_client)
                return clients_data.to_text()
        except VssError as e:
            logger.error(f"VSS error in list_vms resource: {str(e)}")
            return f"Error retrieving VM list: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error in list_vms resource: {e}")
            return f"Internal error retrieving VM list: {str(e)}"

    @mcp.prompt()
    async def analyze_vm_performance(
        vm_id_or_name: str = Field(
            description="Virtual machine Moref or Name."
        ),
        time_period_in_hours: Optional[int] = Field(
            description="Analysis period (1, 24, 72, 168)", default=24
        ),
    ) -> str:
        """Analyze VM performance and provide optimization recommendations.

        This prompt provides:
        - Performance metrics analysis
        - Resource utilization trends
        - Optimization recommendations
        - Cost impact assessment

        Args:
            vm_id_or_name: VM identifier to analyze
            time_period_in_hours: Analysis period (1, 24, 72, 168)

        Returns:
            Prompt text
        """
        try:
            prompt_text = vss_prompts.vm_performance(
                vm_id_or_name,
                time_period_in_hours,
            )
            return prompt_text
        except Exception as e:
            return f"Error generating performance analysis prompt: {str(e)}"

    @mcp.prompt()
    async def troubleshoot_vm_issues(
        vm_id_or_name: str = Field(
            description="Virtual machine MOREF or Name."
        ),
        issue_description: str = Field(
            description="Detailed issue description."
        ),
    ) -> str:
        """Generate a troubleshooting guide for VM-specific issues.

        This prompt provides:
        - Diagnostic checklist
        - Common resolution steps
        - Escalation procedures

        Args:
            vm_id_or_name: VM experiencing issues
            issue_description: Description of the problem
        """
        try:
            prompt_text = vss_prompts.troubleshoot_vm_issues(
                vm_id_or_name, issue_description
            )
            return prompt_text
        except Exception as e:
            return f"Error generating troubleshooting prompt: {str(e)}"

    @mcp.prompt()
    async def cost_optimization_report(
        client_id_or_name: str = Field(description="Client ID or Name."),
        analysis_period_in_days: int = Field(
            description="Analysis period in days (30, 60, 90).", default=90
        ),
    ) -> str:
        """Generate detailed cost optimization analysis and recommendations.

        This prompt provides:
        - Cost breakdown analysis
        - Optimization opportunities
        - ROI calculations

        Args:
            client_id_or_name: Client to analyze
            analysis_period_in_days: Period for cost analysis (30, 60, 90)
        """
        try:
            prompt_text = vss_prompts.vm_cost_optimization_report(
                client_id_or_name, analysis_period_in_days
            )
            return prompt_text

        except Exception as e:
            return f"Error generating cost optimization prompt: {str(e)}"

    @mcp.prompt()
    async def backup_analysis_report(
        client_id_or_name: str = Field(description="Client ID or Name."),
        hostname: str = Field(description="Hostname to analyze."),
        start_date: Optional[str] = Field(
            description="Start date of analysis period (YYYY-MM-DD).",
            default=None,
        ),
        end_date: Optional[str] = Field(
            description="End date of analysis period (YYYY-MM-DD).",
            default=None,
        ),
    ):
        """Generate a backup analysis report for a specific client and host.

        Use this prompt to:
        - Generate a backup analysis report for a specific client and host.
        - Identify the most cost-effective backup solution for a client.
        - Analyze the backup strategy and identify areas for improvement.
        - Provide recommendations for cost optimization and backup
          strategy improvement.
        """
        try:
            prompt_text = vss_prompts.generate_backup_analysis_report(
                client_id_or_name, hostname, start_date, end_date
            )
            return prompt_text
        except Exception as e:
            return f"Error generating cost optimization prompt: {str(e)}"

    return mcp


@click.command()
@click.option(
    "--auth-token",
    envvar="MCP_VSS_API_TOKEN",
    required=True,
    help="VSS API authentication token (can also be set via "
    "MCP_VSS_API_TOKEN env var)",
)
@click.option(
    "--api-endpoint",
    envvar="MCP_VSS_API_ENDPOINT",
    default=VSS_API_BASE,
    help="VSS API endpoint URL (can also be set via "
    "MCP_VSS_API_ENDPOINT env var)",
)
@click.option(
    "--log-level",
    envvar="MCP_VSS_LOG_LEVEL",
    default="INFO",
    type=click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR']),
    help="Logging level",
)
@click.option(
    "--transport",
    type=click.Choice(['stdio', 'sse', 'http']),
    default='stdio',
    help="Transport protocol to use (stdio, sse, or http)",
)
@click.option(
    "--host",
    default="localhost",
    help="Host to bind to for HTTP/SSE transport (default: localhost)",
)
@click.option(
    "--port",
    type=int,
    default=8000,
    help="Port to bind to for HTTP/SSE transport (default: 8000)",
)
def main(
    auth_token: str,
    api_endpoint: str,
    log_level: str,
    transport: str,
    host: str,
    port: int,
):
    """VSS MCP Server - Interface with ITS Private Cloud VSS API.

    Supports multiple transport protocols:
    - stdio: Standard input/output (default, for MCP clients)
    - sse: Server-Sent Events
    - http: HTTP REST API
    """
    # Configure logging
    logger.remove()
    logger.add(sys.stderr, level=log_level)
    logger.info(f"Starting VSS MCP server with endpoint: {api_endpoint}")
    logger.info(f"Using transport: {transport}")
    # Create the FastMCP application
    try:
        mcp_server = create_app(auth_token, api_endpoint)
    except Exception as e:
        logger.error(f"Failed to create MCP app: {e}")
        raise

    # Run with the specified transport
    if transport == 'stdio':
        logger.info("Starting stdio transport...")
        mcp_server.run()
    elif transport == 'sse':
        logger.info(f"Starting SSE transport on {host}:{port}...")
        mcp_server.run(host=host, port=port, transport='sse')
    elif transport == 'http':
        logger.info(f"Starting HTTP transport on {host}:{port}...")
        import uvicorn

        http_app = mcp_server.http_app()
        uvicorn.run(http_app, host=host, port=port)
    else:
        raise ValueError(f"Unsupported transport: {transport}")


if __name__ == "__main__":
    main()
