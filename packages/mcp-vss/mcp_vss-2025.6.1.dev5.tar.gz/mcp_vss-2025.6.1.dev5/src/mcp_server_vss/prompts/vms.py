"""VMs prompts for the MCP server."""


def vm_performance(
    vm_id_or_name,
    time_period_in_hours,
) -> str:
    return f"""You are an expert cloud infrastructure analyst. Analyze the following VM performance data and provide actionable recommendations:

    VM INFORMATION:
    Use get_vm_info tool to get the VM "{vm_id_or_name}" details.

    PERFORMANCE METRICS ({time_period_in_hours} hours):
    Use get_vm_performance_metrics tool using moref to get the latest performance data based on the time period provided.

    VM Snapshots:
    Use get_vm_snapshots tool using moref to get the latest snapshot data.

    Please provide:
    1. PERFORMANCE SUMMARY - Current resource utilization assessment
    2. BOTTLENECK ANALYSIS - Identify any performance constraints
    3. OPTIMIZATION RECOMMENDATIONS - Specific actions to improve performance
    4. COST OPTIMIZATION - Rightsizing recommendations with cost impact
    5. MONITORING ALERTS - Suggested thresholds for proactive monitoring

    Note:
    - Multiple snapshots detected. Performance may be impacted
    - Remove old snapshots when no longer needed.
    - Tools must be running and up to date.

    Focus on actionable insights with specific values and business impact."""


def troubleshoot_vm_issues(vm_id_or_name, issue_description: str) -> str:
    return f"""You are a senior systems administrator with expertise in virtualized infrastructure troubleshooting. Help diagnose and resolve the following issue:

  ISSUE REPORTED:
  "{issue_description}"

  VM DETAILS:
  Use get_vm_info tool to get the VM "{vm_id_or_name}" details.

  RECENT PERFORMANCE DATA:
  Use get_vm_performance_metrics tool with moref to get the latest performance data based on the time period provided.

  Please provide a structured troubleshooting approach:

  1. INITIAL ASSESSMENT
  - Validate the issue description
  - Identify potential root causes
  - Determine urgency level
  - If Tools are NOT installed and not running, highlight as a possible issue
  - If Tools are Old or not running, highlight as a possible issue
  - If issue is related to slowness, consider verifying if snapshots exist

  2. DIAGNOSTIC CHECKLIST
  - Step-by-step verification procedures
  - Commands to run and values to check
  - Expected vs actual behaviors

  3. RESOLUTION STEPS
  - Immediate remediation actions
  - Progressive troubleshooting approach
  - Rollback procedures if needed

  4. MONITORING & VALIDATION
  - How to confirm resolution
  - Metrics to monitor
  - Prevention recommendations

  5. ESCALATION CRITERIA
  - When to escalate to infrastructure team
  - Required information for escalation
  - Emergency procedures

  Provide specific, actionable steps with clear success criteria for each phase."""


def vm_cost_optimization_report(
    client_id_or_name, analysis_period_in_days
) -> str:
    return f"""You are a cloud cost optimization consultant. Analyze the following infrastructure and billing data to identify cost savings opportunities:

    CLIENT: {client_id_or_name}
    ANALYSIS PERIOD: {analysis_period_in_days}

    BILLING SUMMARY:
    Use tool get_billing_details with "{client_id_or_name}" to fetch the billing summary

    INVOICE HISTORY:
    Fetch via tool get_billing_client_invoices_over_time only using client id or name: "{client_id_or_name}" 
    and analysis period: "{analysis_period_in_days}"

    Provide a comprehensive cost optimization analysis:

    1. COST BREAKDOWN ANALYSIS
    - Current spending patterns
    - Cost per resource type
    - Trend analysis over time

    2. OPTIMIZATION OPPORTUNITIES
    - Overprovisioned resources identification
    - Idle or underutilized assets
    - Right-sizing recommendations

    3. POTENTIAL SAVINGS CALCULATION
    - Immediate cost reduction opportunities
    - Monthly and annual savings projections
    - ROI timelines for optimizations

    Include specific dollar amounts, percentages, and implementation complexity for each recommendation."""
