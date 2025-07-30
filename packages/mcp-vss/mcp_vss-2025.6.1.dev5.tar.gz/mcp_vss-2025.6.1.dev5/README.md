# ITS Private Cloud MCP Server (Beta)

A Model Context Protocol (MCP) server that provides seamless integration with the 
University of Toronto's ITS Private Cloud Virtual Server Service (VSS). This server
enables AI assistants to manage virtual machines, analyze billing data, 
monitor performance, and optimize cloud resources through natural language interactions.

## What is Model Context Protocol?

The Model Context Protocol (MCP) is an open standard that enables AI assistants 
to securely connect to external data sources and tools. 
Think of it as a universal translator that allows AI models to:

- **Access Real-time Data**: Connect to live systems and databases
- **Execute Actions**: Perform operations like creating snapshots or managing VMs
- **Maintain Context**: Keep track of resources and relationships across conversations
- **Ensure Security**: Authenticate and authorize access to sensitive systems

With MCP, your AI assistant becomes a powerful interface to your cloud infrastructure, 
capable of understanding complex queries like "Show me the most expensive VMs this month 
and suggest cost optimizations" or "Create a snapshot of the database server before the 
maintenance window.

## Getting Started

### Prerequisites

- Python 3.10 or higher
- ITS Private Cloud VSS API access token
- MCP-compatible AI client (Claude Desktop, etc.)

### Installation

#### Using `uvx`
1. Install `uv` from [Astral](https://docs.astral.sh/uv/getting-started/installation/) or the [GitHub README](https://github.com/astral-sh/uv#installation)
2. Install Python using `uv python install 3.10`
```bash
uvx mcp-vss
```

### Configuration

Add the server to your MCP client configuration:

```json
{
  "mcpServers": {
    "vss": {
      "command": "uvx",
      "args": ["mcp-vss"],
      "env": {
        "MCP_VSS_API_TOKEN": "your-api-token-here"
      }
    }
  }
}
```

## Workflows

### 🖥️ **Virtual Machine Management**
- **VM Discovery**: Find VMs by name, ID, or properties
- **Health Monitoring**: Check VM status, performance, and resource utilization
- **Snapshot Management**: Create point-in-time backups before changes
- **Power Control**: Start, stop, restart, or suspend virtual machines
- **Console Access**: Get emergency console links for troubleshooting
- **Storage Management**: Create, resize, delete, and reorganize virtual disks

### 💰 **Cost Analysis & Optimization**
- **Billing Analysis**: Review invoices and identify cost drivers
- **Resource Rightsizing**: Find overprovisioned or idle resources
- **Trend Analysis**: Track spending patterns over time
- **Optimization Reports**: Get actionable recommendations to reduce costs

### 🔍 **Performance Monitoring**
- **Real-time Metrics**: Monitor CPU, memory, disk, and network usage
- **Trend Analysis**: Identify performance patterns and bottlenecks
- **Capacity Planning**: Forecast resource needs based on historical data
- **Alerting**: Get notifications about performance issues

### 🛠️ **Infrastructure Operations**
- **Backup Analysis**: Monitor UTORrecover backup sessions and data usage
- **Network Management**: View available networks and configurations
- **OS Catalog**: Browse supported operating systems for deployments
- **Domain Management**: Monitor compute clusters and resource allocation

### 🎯 **Troubleshooting & Support**
- **Diagnostic Workflows**: Automated troubleshooting guides
- **Issue Resolution**: Step-by-step problem-solving assistance
- **Performance Tuning**: Optimization recommendations based on metrics
- **Change Management**: Safe deployment practices with snapshot integration

## Available Tools

### Virtual Machine Tools
- **`get_vm_info`** - Retrieve detailed VM information by ID, name, or UUID
- **`get_vm_snapshots`** - List all snapshots for a virtual machine
- **`get_vm_performance_metrics`** - Get CPU, memory, disk, and network metrics
- **`get_vm_console_access`** - Generate console access URLs for emergency access
- **`create_vm_snapshot`** - Create point-in-time VM snapshots with memory options
- **`power_control_vm`** - Control VM power state (start, stop, restart, suspend)
- **`resize_vm_resources`** - Manage VM CPU and memory
- **`get_vm_disks`** - Get VM disk layout and configuration
- **`create_vm_disks`** - Create new virtual disks for VMs
- **`resize_vm_disks`** - Expand virtual disk capacity (cannot shrink)
- **`delete_vm_disks`** - Remove virtual disks from VMs (up to 10 at once)
- **`update_vm_disk_scsi`** - Move disks between SCSI controllers (VM must be powered off)

### Billing & Cost Management Tools
- **`get_billing_clients`** - List all billing accounts and clients
- **`get_billing_details`** - Get detailed billing account information
- **`get_billing_client_invoices`** - Retrieve invoice summaries for cost analysis
- **`get_billing_client_invoice`** - Get detailed invoice breakdown and line items
- **`get_billing_payment_details`** - View FIS payment information and cost centers
- **`update_billing_payment_details`** - Update billing payment details and cost centers

### Backup & Data Management Tools
- **`get_client_backup_host_sessions`** - Analyze UTORrecover backup sessions and data usage
- **`analyze_cost_optimization`** - Generate cost optimization recommendations (planned)

## Available Prompts

### Performance Analysis
- **`analyze_vm_performance`** - Comprehensive performance analysis with optimization recommendations
- **`troubleshoot_vm_issues`** - Generate diagnostic guides for specific VM problems

### Cost & Financial Analysis
- **`cost_optimization_report`** - Detailed cost analysis with ROI calculations and savings opportunities
- **`backup_analysis_report`** - Backup strategy analysis and cost optimization for UTORrecover


## Available Resources

### Infrastructure Resources
- **`its://vms`** - Complete virtual machine inventory (up to 200 VMs)
- **`its://vms/{vm_id}`** - Detailed information for specific virtual machines
- **`its://vms/utorrecover`** - VMs protected by UTORrecover backup service
- **`its://domains`** - Compute domains and cluster information
- **`its://networks`** - Available network configurations and VLANs
- **`its://os`** - Supported operating system catalog
- **`its://os/{full_name}`** - Filtered OS listings by name or family

### Billing Resources
- **`its://clients`** - Complete billing client directory with account details

## Example Usage

### VM Management
```
# Find and analyze a specific VM
"Show me details about the VM-Name and its recent performance"

# Create a snapshot before maintenance
"Create a snapshot of vm-12345 named 'pre-maintenance' before tomorrow's update"

# Monitor performance issues
"Check the CPU and memory usage for VM-12345 in the last 24 hours"

# Storage management
"Show me the disk layout for VM-12345 and add a 100GB disk"
"Resize the disk on unit 2 of vm-web-server to 500GB"
"Move disk unit 3 to SCSI controller 1 for better load balancing"
```

### Cost Analysis
```
# Monthly cost review
"Show me this month's billing for client DEPT-IT and identify the top cost drivers"

# Optimization opportunities
"Analyze our VM costs over the last 90 days and suggest optimization opportunities"

# Budget planning
"What's our trending monthly spend and projected costs for next quarter?"
```

### Operations & Troubleshooting
```
# Backup analysis
"Review the UTORrecover backup sessions for db-server-01.utoronto.ca in the last month"

# Performance troubleshooting
"The application server is running slowly - help me diagnose the issue"

# Resource planning
"Show me available networks and OS options for deploying a new development environment"
```

## Security & Best Practices

- **API Token Security**: Store tokens securely using environment variables
- **Least Privilege**: Request only necessary permissions for your use case
- **Snapshot Hygiene**: Remove temporary snapshots after validation
- **Cost Monitoring**: Regularly review billing and set up alerts for unusual spending
- **Change Management**: Always create snapshots before making significant changes

## Support & Documentation

- **API Documentation**: [VSS API Reference](https://vss-api.eis.utoronto.ca/docs)
- **MCP Specification**: [Model Context Protocol](https://modelcontextprotocol.io/)
- **Issue Tracking**: Report bugs and feature requests through appropriate channels
- **Best Practices**: Follow University of Toronto IT policies and procedures

## License

This project follows University of Toronto software licensing policies.

---

**Note**: This is a beta release. Features and APIs may change. Please test thoroughly in non-production environments.