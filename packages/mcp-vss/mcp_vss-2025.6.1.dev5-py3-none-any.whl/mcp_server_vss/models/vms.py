"""Data models for the MCP Server."""

from decimal import Decimal
from typing import Any, List, Optional

import mcp.types as types
from pydantic import BaseModel, Field


class Datastore(BaseModel):
    """Datastore model."""

    created_on: str
    moref: str
    name: str
    ssd_backed: bool
    type: str
    updated_on: str
    vim_type: str


class Controller(BaseModel):
    """Controller model."""

    bus: int
    label: str
    type: str


class Disk(BaseModel):
    """Disk model."""

    backing_uuid: str
    capacity_bytes: float
    capacity_gib: float
    controller: Controller
    file_name: str
    ide: Optional[int] = None
    is_encrypted: bool
    key: int
    label: str
    moref: str
    notes: Optional[str] = None
    scsi: int


class Domain(BaseModel):
    """Domain model."""

    created_on: str
    hosts_count: int
    moref: str
    name: str
    num_cpu_cores: int
    num_cpu_sockets: int
    num_cpu_threads: int
    overall_status: str
    updated_on: str
    vim_type: str
    gpu_profiles_bound: Optional[str] = None


class Folder(BaseModel):
    """Folder model."""

    created_on: str
    has_children: bool
    has_parent: bool
    moref: str
    name: str
    parent_moref: str
    path: str
    updated_on: str
    vim_type: str


class Host(BaseModel):
    """Host model."""

    created_on: str
    domain: Domain
    gpu_profiles: Optional[str] = None
    gpu_profiles_bound: Optional[str] = None
    moref: str
    name: str
    num_cpu_cores: int
    num_cpu_sockets: int
    num_cpu_threads: int
    overall_status: str
    product_full_name: str
    updated_on: str
    vim_type: str
    vm_count: int


class NetworkInfo(BaseModel):
    """NetworkInfo model."""

    admin: Optional[str]
    created_on: str
    description: Optional[str]
    label: Optional[str]
    mac_allow_promiscuous: Optional[bool]
    mac_changes: Optional[bool]
    mac_forged_transmits: Optional[bool]
    moref: str
    name: str
    ports: int
    subnet: Optional[str]
    updated_on: str
    vim_type: str
    vlan_id: Optional[str]
    vms: Optional[int] = 0

    def to_text(self) -> str:
        """Return a string representation of the model."""
        return f"""Name: {self.name} ({self.moref})
Label: {self.label}
VLAN ID: {self.vlan_id}
Description: {self.description or 'N/A'}
Admin: {self.admin or 'N/A'}
Subnet: {self.subnet or 'N/A'}
Ports: {self.ports}
VMs: {self.vms}
MAC Security:
  - Allow Promiscuous: {self.mac_allow_promiscuous}
  - MAC Changes: {self.mac_changes}
  - Forged Transmits: {self.mac_forged_transmits}
Resource URI: its://networks/{self.moref}
"""

    def to_prompt_result(self) -> types.GetPromptResult:
        """Return a prompt result."""
        return types.GetPromptResult(
            description=f"Network: {self.name}",
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text", text=self.to_text()
                    ),
                )
            ],
        )

    def to_tool_result(
        self,
    ) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
        """Return a tool result."""
        return [types.TextContent(type="text", text=self.to_text())]


class NetworkList(BaseModel):
    """List of networks model."""

    networks: Optional[List[NetworkInfo]] = []

    def to_text(self) -> str:
        """Convert to text."""
        return f"{'='*20}\n".join([x.to_text() for x in self.networks])

    def to_prompt_result(self) -> types.GetPromptResult:
        """Convert to prompt result."""
        return types.GetPromptResult(
            description=f"Networks: ({len(self.networks)})",
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text", text=self.to_text()
                    ),
                )
            ],
        )

    def to_tool_result(
        self,
    ) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
        """Convert to tool result."""
        return [types.TextContent(type="text", text=self.to_text())]


class VMInfo(BaseModel):
    """VMInfo model."""

    admin: Optional[str]
    backup_svc: Optional[str] = None
    cbt_enabled: bool
    client: Optional[str]
    committed_bytes: int
    committed_gb: float
    cores_per_socket: int
    cpu_count: int
    cpu_hotadd: bool
    create_date: Optional[str] = ''
    created_on: str
    datastores: List[Datastore]
    decommissioned_on: Optional[str] = None
    description: Optional[str]
    disks: Optional[List[Disk]] = None
    domain: Domain
    domain_moref: str
    firmware: str
    folder: Folder
    folder_moref: str
    ft_encryption_mode: str
    gpu: Optional[List[str]] = ''
    gpu_gb: int
    gpu_profiles: str
    guest_detailed_data: Optional[str]
    guest_full_name: str
    guest_full_name_run: Optional[str] = None
    guest_id: str
    guest_id_run: Optional[str] = None
    has_snapshot: bool
    host: Host
    host_moref: str
    hostname: Optional[str] = ''
    inform: Optional[str]
    ip_address: Optional[str] = ''
    is_encrypted: bool
    is_template: bool
    last_powered_off: Optional[str] = None
    last_powered_on: Optional[str] = None
    last_shutdown: Optional[str] = None
    mac_address: Optional[str] = None
    memory_gb: float
    memory_gb_reserved: Optional[Decimal] = 0.0
    memory_hotadd: bool
    memory_mb: int
    memory_mb_reserved: int
    migrate_encryption_mode: str
    moref: str
    name: str
    networks: Optional[List[NetworkInfo]] = None
    notes: str
    options: str
    overall_status: str
    power_state: str
    preferences: str
    provisioned_gb: float
    secure_boot: bool
    storage_type: str
    support_code: Optional[str]
    tools_running_status: str
    tools_version: str
    tools_version_status: str
    tpm: Optional[List[Any]]  # Appears to be empty list in example
    ubuntu_pro: Optional[bool] = False
    uncommitted_bytes: int
    unshared_bytes: int
    updated_on: str
    usage: Optional[str]
    uuid: str
    vbs_enabled: bool
    version: str
    vim_type: str

    def to_text(self) -> str:
        """Convert VM info to a readable text format."""
        return (
            f"Name: {self.name} ({self.moref})\n"
            f"Folder: {self.folder.path}\n"
            f"State: {self.power_state} | CPU: {self.cpu_count} "
            f"| Memory: {self.memory_gb}GB\n"
            f"Storage: {self.provisioned_gb} GB ({self.storage_type})\n"
            f"Guest OS: {self.guest_full_name}/{self.guest_full_name_run}\n"
            f"IP Address: {self.ip_address}\n"
            f"MAC Address: {self.mac_address}\n"
            f"Domain: {self.domain.name} ({self.host.name})\n"
            f"Encrypted: {self.is_encrypted}\n"
            f"Template: {self.is_template}\n"
            f"VM Tools: {self.tools_running_status} "
            f"({self.tools_version_status})\n"
            f"Virtual Hardware: {self.version}\n"
            f"Backup Service: {self.backup_svc or 'N/A'}\n"
            f"Notes: {self.notes}\n"
            f"Resource URI: its://vms/{self.moref}\n"
        )

    @classmethod
    def from_dict(cls, data: dict) -> 'VMInfo':
        """Create VMInfo instance from dictionary."""
        return cls.model_validate(data)

    def to_dict(self) -> dict:
        """Convert VMInfo to dictionary."""
        return self.model_dump()

    def to_json(self) -> str:
        """Convert VMInfo to JSON string."""
        return self.model_dump_json()

    def to_prompt_result(self) -> types.GetPromptResult:
        """Convert VMInfo to GetPromptResult."""
        return types.GetPromptResult(
            description=f"VM: {self.name}",
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text", text=self.to_text()
                    ),
                )
            ],
        )

    def to_tool_result(
        self,
    ) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
        """Convert VMInfo to ToolResult."""
        return [types.TextContent(type="text", text=self.to_text())]

    def to_resource_result(self) -> List[types.TextContent]:
        """Convert VMInfo to ResourceResult."""
        return [types.TextContent(type="text", text=self.to_text())]


class VmChangeRequestResultRequest(BaseModel):
    """VM Change Request Result Request."""

    id: Optional[int]
    status: Optional[str]
    task_id: Optional[str]
    action: Optional[str] = ''


class VmChangeRequestResult(BaseModel):
    """VM Change Request Result."""

    message: Optional[str]
    request: Optional[VmChangeRequestResultRequest]
    name: Optional[str]
    status: Optional[int]

    def to_text(self) -> str:
        """Convert the result to text."""
        return (
            f"{self.message}\n"
            f"Task ID: {self.request.task_id}\n"
            f"Status: {self.request.status}"
            f"Action: {self.request.action or 'N/A'}"
        )

    def to_prompt_result(self) -> types.GetPromptResult:
        """Convert the result to a prompt result."""
        return types.GetPromptResult(
            description=f"Client: {self.name}",
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text", text=self.to_text()
                    ),
                )
            ],
        )

    def to_tool_result(
        self,
    ) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
        """Convert the result to a tool result."""
        return [types.TextContent(type="text", text=self.to_text())]


class VmConsoleLink(BaseModel):
    """VM console link model."""

    value: Optional[str]

    def to_text(self) -> str:
        """Convert the result to a text."""
        return (
            f"Console link: {self.value}\n"
            "Note that: \n"
            "- ITS Private Cloud VPN access is required \n"
            "- Authentication will be prompted"
        )

    def to_prompt_result(self) -> types.GetPromptResult:
        """Convert the result to a prompt result."""
        return types.GetPromptResult(
            description=f"Client: {self.name}",
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text", text=self.to_text()
                    ),
                )
            ],
        )

    def to_tool_result(
        self,
    ) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
        """Convert the result to a tool result."""
        return [types.TextContent(type="text", text=self.to_text())]


class CpuMetrics(BaseModel):
    """CPU performance metrics."""

    ready_avg_pct: float = Field(
        ..., description="Average CPU ready percentage"
    )
    ready_max_pct: float = Field(
        ..., description="Maximum CPU ready percentage"
    )
    usage_pct: float = Field(..., description="CPU usage percentage")


class DatastoreMetrics(BaseModel):
    """Datastore/Storage performance metrics."""

    io_read_iops: int = Field(
        ..., description="Read I/O operations per second"
    )
    io_write_iops: int = Field(
        ..., description="Write I/O operations per second"
    )
    lat_read_ms: float = Field(..., description="Read latency in milliseconds")
    lat_write_ms: float = Field(
        ..., description="Write latency in milliseconds"
    )


class MemoryMetrics(BaseModel):
    """Memory performance metrics."""

    active_mb: float = Field(..., description="Active memory in MB")
    active_pct: float = Field(..., description="Active memory percentage")
    balloon_mb: float = Field(..., description="Ballooned memory in MB")
    balloon_pct: float = Field(..., description="Ballooned memory percentage")
    shared_mb: float = Field(..., description="Shared memory in MB")
    shared_pct: float = Field(..., description="Shared memory percentage")
    swapped_mb: float = Field(..., description="Swapped memory in MB")
    swapped_pct: float = Field(..., description="Swapped memory percentage")
    usage_pct: float = Field(..., description="Memory usage percentage")


class NetworkMetrics(BaseModel):
    """Network performance metrics."""

    rx_errors: int = Field(..., description="Receive errors count")
    rx_mbps: float = Field(..., description="Receive throughput in Mbps")
    tx_errors: int = Field(..., description="Transmit errors count")
    tx_mbps: float = Field(..., description="Transmit throughput in Mbps")


class DiskDetail(BaseModel):
    capacity_gb: float
    filename: str
    label: str


class DiskSummary(BaseModel):
    disk_count: int
    is_active: bool
    performance_issues: bool
    total_capacity_gb: float


class DiskMetrics(BaseModel):
    avg_max_latency_ms: float
    disk_details: List[DiskDetail]
    max_latency_ms: int
    read_throughput_kbps: float
    read_throughput_mbps: float
    summary: DiskSummary
    throughput_contention: float
    throughput_usage: float
    total_capacity_gb: float
    total_throughput_kbps: float
    total_throughput_mbps: float
    write_throughput_kbps: float
    write_throughput_mbps: float


class VmMetrics(BaseModel):
    """Virtual Machine performance metrics."""

    name: str = Field(..., description="VM name")
    cpu: CpuMetrics = Field(..., description="CPU performance metrics")
    disk: DiskMetrics = Field(..., description="Disk performance metrics")
    memory: MemoryMetrics = Field(
        ..., description="Memory performance metrics"
    )
    network: NetworkMetrics = Field(
        ..., description="Network performance metrics"
    )
    timestamp: Optional[str] = Field(
        None, description="Metrics collection timestamp"
    )

    def to_text(self) -> str:
        """Convert VM metrics to human-readable text format."""

        def format_pct_with_status(
            value: float,
            warning_threshold: float = 80.0,
            critical_threshold: float = 90.0,
        ) -> str:
            """Format a percentage value with a status indicator."""
            if value >= critical_threshold:
                status = "🔴"
            elif value >= warning_threshold:
                status = "🟡"
            else:
                status = "🟢"
            return f"{value:.1f}% {status}"

        # Helper function to format latency with status
        def format_latency_with_status(
            value: float,
            warning_threshold: float = 10.0,
            critical_threshold: float = 20.0,
        ) -> str:
            """Format a latency value with a status indicator."""
            if value >= critical_threshold:
                status = "🔴"
            elif value >= warning_threshold:
                status = "🟡"
            else:
                status = "🟢"
            return f"{value:.1f}ms {status}"

        text = f"""VM Performance Metrics: {self.name}
{'=' * 50}

# CPU PERFORMANCE
  Usage: {format_pct_with_status(self.cpu.usage_pct)}
  Ready (Avg): {self.cpu.ready_avg_pct:.2f}%
  Ready (Max): {self.cpu.ready_max_pct:.2f}%
  
# MEMORY UTILIZATION
  Usage: {format_pct_with_status(self.memory.usage_pct)}
  Active: {self.memory.active_mb:.1f} MB ({self.memory.active_pct:.1f}%)
  Shared: {self.memory.shared_mb:.1f} MB ({self.memory.shared_pct:.3f}%)
  Ballooned: {self.memory.balloon_mb:.1f} MB ({self.memory.balloon_pct:.1f}%)
  Swapped: {self.memory.swapped_mb:.1f} MB ({self.memory.swapped_pct:.1f}%)

# DISK PERFORMANCE
  Read Throughput: {self.disk.read_throughput_kbps:,}
  Write Throughput: {self.disk.write_throughput_kbps:,}
  Total Throughput: {self.disk.total_throughput_kbps:,}
  Max Latency: {format_latency_with_status(self.disk.max_latency_ms)}

# NETWORK PERFORMANCE
  RX Throughput: {self.network.rx_mbps:.2f} Mbps
  TX Throughput: {self.network.tx_mbps:.2f} Mbps
  RX Errors: {self.network.rx_errors:,}
  TX Errors: {self.network.tx_errors:,}

# PERFORMANCE SUMMARY
{self._generate_performance_summary()}
"""

        if self.timestamp:
            text += f"\n⏰ Metrics collected at: {self.timestamp}"

        return text

    def _generate_performance_summary(self) -> str:
        """Generate a performance summary with recommendations."""
        issues = []
        recommendations = []

        # CPU Analysis
        if self.cpu.usage_pct > 90:
            issues.append("🔴 High CPU usage detected")
            recommendations.append("• Consider increasing vCPU allocation")
        elif self.cpu.usage_pct > 80:
            issues.append("🟡 Elevated CPU usage")
            recommendations.append(
                "• Monitor CPU trends for capacity planning"
            )

        if self.cpu.ready_avg_pct > 5:
            issues.append(
                "🔴 High CPU ready time indicates resource contention"
            )
            recommendations.append(
                "• Check host CPU allocation and VM density"
            )

        # Memory Analysis
        if self.memory.usage_pct > 90:
            issues.append("🔴 High memory usage detected")
            recommendations.append("• Consider increasing memory allocation")
        elif self.memory.usage_pct > 80:
            issues.append("🟡 Elevated memory usage")

        if self.memory.balloon_pct > 0:
            issues.append("🟡 Memory ballooning active")
            recommendations.append(
                "• Host memory pressure detected - consider memory upgrade"
            )

        if self.memory.swapped_pct > 0:
            issues.append("🔴 Memory swapping detected")
            recommendations.append(
                "• Critical: Increase memory allocation immediately"
            )

        # Storage Analysis
        if self.disk.avg_max_latency_ms > 20:
            issues.append("🔴 High storage disk latency detected")
            recommendations.append(
                "• Check storage performance and consider SSD upgrade"
            )
        elif self.disk.avg_max_latency_ms > 10:
            issues.append("🟡 Elevated disk latency")
            recommendations.append("• Monitor storage performance trends")

        # Network Analysis
        if self.network.rx_errors > 0 or self.network.tx_errors > 0:
            issues.append("🟡 Network errors detected")
            recommendations.append(
                "• Check network configuration and connectivity"
            )

        # Generate summary
        if not issues:
            summary = (
                "🟢 Overall Status: HEALTHY - All metrics within normal ranges"
            )
        else:
            summary = f"⚠️  Issues Identified ({len(issues)}):\n"
            summary += "\n".join(f"  {issue}" for issue in issues)

            if recommendations:
                summary += "\n\n💡 Recommendations:\n"
                summary += "\n".join(f"  {rec}" for rec in recommendations)

        return summary

    def to_prompt_result(self) -> List[types.PromptMessage]:
        """Convert VM metrics to MCP prompt result format."""
        prompt_content = f"""VM Performance Analysis Data for {self.name}

CURRENT METRICS:
{self.to_text()}

PERFORMANCE CONTEXT:
This VM's performance data shows the following key indicators:

CPU Health: {"Critical" if self.cpu.usage_pct > 90 else "Warning" if self.cpu.usage_pct > 80 else "Good"}
- Current utilization at {self.cpu.usage_pct:.1f}%
- CPU ready time averaging {self.cpu.ready_avg_pct:.2f}% (lower is better)

Memory Health: {"Critical" if self.memory.usage_pct > 90 else "Warning" if self.memory.usage_pct > 80 else "Good"}
- Memory utilization at {self.memory.usage_pct:.1f}%
- {"Memory pressure detected" if self.memory.balloon_pct > 0 or self.memory.swapped_pct > 0 else "No memory pressure"}

Storage Performance: {"Poor" if self.disk.max_latency_ms > 20 else "Fair" if self.disk.max_latency_ms > 10 else "Good"}
- Read/Write Throughput Mpbs: {self.disk.read_throughput_mbps}/{self.disk.write_throughput_mbps}
- Max latency: {self.disk.max_latency_ms:.1f}ms
- Avg Max latency: {self.disk.avg_max_latency_ms:.1f}ms

Network Status: {"Issues detected" if self.network.rx_errors > 0 or self.network.tx_errors > 0 else "Healthy"}
- Throughput: {self.network.rx_mbps:.1f} Mbps RX, {self.network.tx_mbps:.1f} Mbps TX

Use this data to provide specific, actionable performance analysis and optimization recommendations for this virtual machine."""

        return [
            types.PromptMessage(
                role="user",
                content=types.TextContent(type="text", text=prompt_content),
            )
        ]

    def get_performance_score(self) -> float:
        """Calculate an overall performance score (0-100, higher is better)."""
        scores = []

        # CPU Score (inverse of usage, accounting for ready time)
        cpu_score = max(
            0, 100 - self.cpu.usage_pct - (self.cpu.ready_avg_pct * 10)
        )
        scores.append(cpu_score)

        # Memory Score (inverse of usage, penalize balloon/swap)
        memory_penalty = (
            self.memory.balloon_pct + self.memory.swapped_pct
        ) * 2
        memory_score = max(0, 100 - self.memory.usage_pct - memory_penalty)
        scores.append(memory_score)

        # Storage Score (based on latency)
        avg_latency = self.disk.avg_max_latency_ms
        storage_score = max(0, 100 - (avg_latency * 2))  # 50ms = 0 score
        scores.append(storage_score)

        # Network Score (errors impact score)
        total_errors = self.network.rx_errors + self.network.tx_errors
        network_score = max(0, 100 - (total_errors * 5))  # 20 errors = 0 score
        scores.append(network_score)

        return sum(scores) / len(scores)

    def is_healthy(self) -> bool:
        """Determine if VM is in a healthy state."""
        return (
            self.cpu.usage_pct < 90
            and self.memory.usage_pct < 90
            and self.memory.swapped_pct == 0
            and self.disk.avg_max_latency_ms < 20
            and self.network.rx_errors == 0
            and self.network.tx_errors == 0
        )

    def get_alerts(self) -> List[str]:
        """Get list of performance alerts for this VM."""
        alerts = []

        if self.cpu.usage_pct > 95:
            alerts.append(
                f"CRITICAL: CPU usage extremely high "
                f"({self.cpu.usage_pct:.1f}%)"
            )
        elif self.cpu.usage_pct > 90:
            alerts.append(
                f"WARNING: CPU usage high ({self.cpu.usage_pct:.1f}%)"
            )

        if self.memory.swapped_pct > 0:
            alerts.append(
                f"CRITICAL: Memory swapping detected "
                f"({self.memory.swapped_mb:.1f} MB)"
            )
        elif self.memory.usage_pct > 95:
            alerts.append(
                f"CRITICAL: Memory usage extremely high "
                f"({self.memory.usage_pct:.1f}%)"
            )
        elif self.memory.usage_pct > 90:
            alerts.append(
                f"WARNING: Memory usage high "
                f"({self.memory.usage_pct:.1f}%)"
            )

        if self.memory.balloon_pct > 5:
            alerts.append(
                f"WARNING: Significant memory ballooning "
                f"({self.memory.balloon_pct:.1f}%)"
            )

        if self.disk.avg_max_latency_ms > 50:
            alerts.append(
                f"CRITICAL: Very high storage latency ({self.disk.avg_max_latency_m:.1f}ms)"
            )
        elif self.disk.avg_max_latency_ms > 20:
            alerts.append(
                f"WARNING: High storage latency "
                f"({self.disk.avg_max_latency_m:.1f}ms)"
            )

        if self.network.rx_errors > 10 or self.network.tx_errors > 10:
            alerts.append(
                f"WARNING: Network errors detected "
                f"(RX:{self.network.rx_errors}, "
                f"TX:{self.network.tx_errors})"
            )

        return alerts

    def to_tool_result(
        self,
    ) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
        """Return a list of tool results for the VM."""
        return [types.TextContent(type="text", text=self.to_text())]


class VmSnapshot(BaseModel):
    """VM snapshot model."""

    age: str
    description: str
    id: int
    label: str
    name: str

    def to_text(self) -> str:
        """Return a human-readable text representation of the VM snapshot."""
        return (
            f"VM Snapshot: {self.name}\n"
            f"ID: {self.id}\n"
            f"Age: {self.age}\n"
            f"Description: {self.description}\n"
            f"Label: {self.label}\n\n"
        )

    def to_tool_result(
        self,
    ) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
        """Return a tool result representation of the VM snapshot."""
        return [types.TextContent(type="text", text=self.to_text())]

    def to_prompt_result(self) -> types.GetPromptResult:
        """Return a prompt result representation of the VM snapshot."""
        return types.GetPromptResult(
            description=f"VM Snapshot: {self.name}",
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text", text=self.to_text()
                    ),
                )
            ],
        )


class VmSnapshots(BaseModel):
    """VM Snapshots model."""

    snapshots: Optional[List[VmSnapshot]] = []

    def to_text(self) -> str:
        """Convert to text."""
        return '\n'.join([x.to_text() for x in self.snapshots])

    def to_prompt_result(self) -> types.GetPromptResult:
        """Convert to prompt result."""
        return types.GetPromptResult(
            description=f"Snapshots: ({len(self.snapshots)})",
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text", text=self.to_text()
                    ),
                )
            ],
        )

    def to_tool_result(
        self,
    ) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
        """Convert to tool result."""
        return [types.TextContent(type="text", text=self.to_text())]


class VmInfoList(BaseModel):
    """VM Info list model."""

    vms: Optional[List[VMInfo]] = []

    def to_text(self) -> str:
        """Convert to text."""
        return f"{'='*20}\n".join([x.to_text() for x in self.vms])

    def to_prompt_result(self) -> types.GetPromptResult:
        """Convert to prompt result."""
        return types.GetPromptResult(
            description=f"Virtual Machines: ({len(self.vms)})",
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text", text=self.to_text()
                    ),
                )
            ],
        )

    def to_tool_result(
        self,
    ) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
        """Convert to tool result."""
        return [types.TextContent(type="text", text=self.to_text())]


class GuestOS(BaseModel):
    """Guest OS model."""

    family: str
    full_name: str
    guest_id: str
    id: int

    def to_text(self) -> str:
        """Convert to text."""
        return (
            f"Operating System:\n"
            f"Full Namee: {self.full_name}\n"
            f"Guest ID: {self.guest_id}\n"
            f"Family: {self.family}\n"
            f"Resource URI: its://os/{self.full_name}\n\n"
        )

    def to_tool_result(
        self,
    ) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
        """Convert to tool result."""
        return [types.TextContent(type="text", text=self.to_text())]

    def to_prompt_result(self) -> types.GetPromptResult:
        """Convert to prompt result."""
        return types.GetPromptResult(
            description=f"VM OS: {self.full_name} ({self.guest_id})",
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text", text=self.to_text()
                    ),
                )
            ],
        )


class GuestOSList(BaseModel):
    """Guest OS List model."""

    items: Optional[List[GuestOS]] = []

    def to_text(self) -> str:
        """Convert to text."""
        return f"{'='*20}\n".join([x.to_text() for x in self.items])

    def to_prompt_result(self) -> types.GetPromptResult:
        """Convert to prompt result."""
        return types.GetPromptResult(
            description=f"Operating Systems: {len(self.items)} ",
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text", text=self.to_text()
                    ),
                )
            ],
        )

    def to_tool_result(
        self,
    ) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
        """Convert to tool result."""
        return [types.TextContent(type="text", text=self.to_text())]


class VmOsInfo(BaseModel):
    """VM OS info."""

    family: str
    is_linux_64bit: Optional[bool] = False
    is_windows_32bit: Optional[bool] = False
    guest_id: str


class VmController(BaseModel):
    """VM disk controller information."""

    bus: int = Field(..., description="Controller bus number")
    label: str = Field(..., description="Controller label identifier")
    type: str = Field(..., description="Controller type (e.g., lsilogicsas)")

    def to_text(self) -> str:
        """Convert controller information to human-readable text."""
        return f"Controller: {self.label} (Type: {self.type}, Bus: {self.bus})"

    def to_tool_result(
        self,
    ) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
        """Convert to tool result."""
        return [types.TextContent(type="text", text=self.to_text())]


class VmDisk(BaseModel):
    """Individual VM disk configuration."""

    backing_mode: str = Field(
        ..., description="Disk backing mode (e.g., persistent)"
    )
    backing_sharing: str = Field(
        ..., description="Disk sharing mode (e.g., sharingnone)"
    )
    capacity_gib: float = Field(..., description="Disk capacity in GiB", gt=0)
    controller: VmController = Field(
        ..., description="Disk controller information"
    )
    file_name: str = Field(..., description="Virtual disk file path")
    is_encrypted: bool = Field(
        ..., description="Whether the disk is encrypted"
    )
    label: str = Field(..., description="Disk label (e.g., Hard disk 1)")
    notes: Optional[str] = Field(None, description="Optional disk notes")
    unit: int = Field(..., description="Disk unit number", ge=0)

    def to_text(self) -> str:
        """Convert disk information to human-readable text."""
        encryption_status = (
            "Encrypted" if self.is_encrypted else "Not encrypted"
        )
        notes_text = f" (Notes: {self.notes})" if self.notes else ""

        return (
            f"{self.label}: {self.capacity_gib} GiB - {self.backing_mode} mode\n"
            f"  File: {self.file_name}\n"
            f"  {self.controller.to_text()}\n"
            f"  Unit: {self.unit}, Sharing: {self.backing_sharing}, {encryption_status}{notes_text}"
        )

    def to_tool_result(
        self,
    ) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
        """Convert to tool result."""
        return [types.TextContent(type="text", text=self.to_text())]


class VmDisks(BaseModel):
    """Collection of VM disks for MCP server tool."""

    disks: List[VmDisk] = Field(..., description="List of VM disks")

    def to_text(self) -> str:
        """Convert all disks information to human-readable text."""
        if not self.disks:
            return "No disks found."

        total_capacity = sum(disk.capacity_gib for disk in self.disks)
        disk_count = len(self.disks)

        header = f"VM Disks Summary ({disk_count} disks, {total_capacity} GiB total capacity):\n"
        header += "=" * 60 + "\n"

        disk_details = "\n\n".join(disk.to_text() for disk in self.disks)

        return header + disk_details

    def to_tool_result(
        self,
    ) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
        """Convert to tool result."""
        return [types.TextContent(type="text", text=self.to_text())]
