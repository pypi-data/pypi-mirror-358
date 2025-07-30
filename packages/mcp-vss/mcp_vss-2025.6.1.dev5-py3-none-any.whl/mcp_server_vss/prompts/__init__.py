"""Prompts for the MCP Server."""
from mcp_server_vss.prompts.backups import generate_backup_analysis_report
from mcp_server_vss.prompts.vms import (
    troubleshoot_vm_issues, vm_cost_optimization_report, vm_performance)

__all__ = [
    "vm_performance",
    "vm_cost_optimization_report",
    "troubleshoot_vm_issues",
    "generate_backup_analysis_report",
]
