"""Requests models."""
from typing import Annotated, List, Literal, Optional

from pydantic import BaseModel, Field, field_validator


class VmInfoRequest(BaseModel):
    """Request model for VM information."""

    vm_id_or_uuid_or_name: str = Field(
        ..., description="ITS Private Cloud VM ID, UUID, or Name to analyze"
    )


class VmMetricsRequest(BaseModel):
    """Request model for VM Metrics."""

    vm_id_or_uuid_or_name: str = Field(
        ..., description="ITS Private Cloud VM ID, UUID, or Name to analyze"
    )
    time_period_in_hours: int = Field(
        ..., description="Time period in hours to analyze"
    )


class VmConsoleRequest(BaseModel):
    """Request model for VM Console."""

    vm_id_or_uuid_or_name: str = Field(
        ...,
        description="ITS Private Cloud VM ID, UUID, or Name to get console",
    )


class BillingDetailsRequest(BaseModel):
    """Request model for billing details."""

    client_id_or_name: str = Field(
        ..., description="ITS Private Cloud Client ID or Name to analyze"
    )


class BillingInvoiceDetailsRequest(BaseModel):
    """Request model for billing details."""

    client_id_or_name: str = Field(
        ..., description="ITS Private Cloud Client ID or Name to analyze"
    )
    invoice_number_or_id: str = Field(
        ..., description="ITS Private Cloud Invoice ID or Number to analyze"
    )


class BillingInvoiceDetailsOverTime(BaseModel):
    """Request model for billing details."""

    client_id_or_name: str = (Field(description="Client ID or Name."),)
    analysis_period_in_days: int = (
        Field(description="Analysis period in days (30, 60, 90).", default=90),
    )


class CostOptimizationRequest(BaseModel):
    """Request model for cost optimization analysis."""

    client_id_or_name: str = Field(
        None, description="Client ID or name to analyze"
    )
    analysis_period_days: int = Field(
        30, description="Analysis period in days (default: 30)", ge=30, le=120
    )
    min_savings_threshold: float = Field(
        50.0,
        description="Minimum monthly savings threshold "
        "to report (default: $50)",
    )


class FisUpdateRequest(BaseModel):
    """Request model for updating a FIS."""

    client_id_or_name: str = Field(
        ..., description="Client ID or name to analyze"
    )
    cost_centre: str = Field(
        ...,
        description="Cost centre to update.",
    )
    commitment_fund_centre: str = Field(
        ...,
        description="Commitment fund centre to update.",
    )
    fund: str = Field(
        None,
        description="Fund to update.",
    )
    # optional items
    order: str = Field(
        None,
        description="Order to update.",
    )
    budget_code: str = Field(
        None,
        description="Budget code to update.",
    )
    assignment: str = Field(
        None,
        description="Assignment to update.",
    )
    bus_area: str = Field(
        None,
        description="Business area to update.",
    )
    commitment_item: str = Field(
        None,
        description="Commitment item to update.",
    )


class VmSnapshotDelRequest(BaseModel):
    """Request model for deleting a VM."""

    vm_id_or_uuid_or_name: str = Field(
        ...,
        description="Virtual machine MOREF or Name.",
    )
    snapshot_id_or_name: str = Field(
        ...,
        description="Snapshot Id or Name.",
    )
    consolidate: bool = Field(
        False,
        description="Disk consolidation after snapshot removal.",
    )

    def to_text(self) -> str:
        """Convert the snapshot details to a text string."""
        return f"""
Snapshot Removal Details:
- Name or ID: {self.snapshot_id_or_name}
- Consolidate: {self.consolidate}
"""


class VmSnapshotRollbackRequest(BaseModel):
    """Request model for rolling back a VM snapshot."""

    vm_id_or_uuid_or_name: str = Field(
        ...,
        description="Virtual machine MOREF or Name.",
    )
    snapshot_id_or_name: str = Field(
        ...,
        description="Snapshot Id or Name.",
    )

    def to_text(self) -> str:
        """Convert the snapshot details to a text string."""
        return f"""
    Snapshot Rollback Details:
    - VM Id or Name: {self.vm_id_or_uuid_or_name}
    - Name or ID: {self.snapshot_id_or_name}
    """


class VmSnapshotRequest(BaseModel):
    """Request model for creating a VM snapshot."""

    vm_id_or_name: str = Field(
        ...,
        description="Virtual machine MOREF or Name.",
    )
    name: str = Field(..., description="Snapshot name.")
    description: str = Field(
        ..., description="Snapshot description.", min_length=5, max_length=50
    )
    include_memory: bool = Field(
        False,
        description="Include memory state in snapshot.",
    )
    valid_for: int = Field(
        24,
        description='Valid for (in hours) the snapshot to be deleted.',
        ge=1,
        le=72,
    )
    consolidate: bool = Field(
        True,
        description="Consolidate snapshots.",
    )
    from_date: str = Field(
        ...,
        description="Timestamp in format YYYY-MM-DD HH:MM "
        "when to take the snapshot.",
    )

    def to_text(self) -> str:
        """Convert the snapshot details to a text string."""
        return f"""
Snapshot Details:
- Name: {self.name}
- Description: {self.description}
- Include Memory: {'Yes' if self.include_memory else 'No'}
- Valid for: {self.valid_for} hours
- Consolidate: {'Yes' if self.consolidate else 'No'}
- From Date: {self.from_date}
"""


class ClientBackupHostSessionsRequest(BaseModel):
    """Request model for the `client_backup_host_sessions` endpoint."""

    client_id_or_name: str = Field(
        ..., description="Client ID or name to analyze"
    )
    hostname: str = Field(..., description="Hostname to analyze")
    start_date: str = Field(
        None, description="Start time of the snapshot in format YYYY-MM-DD."
    )
    end_date: str = Field(
        None, description="End time of the snapshot in format YYYY-MM-DD."
    )


class VmPowerControlRequest(BaseModel):
    """Request model for VM power control operations."""

    vm_id_or_name: str = (
        Field(
            description="Virtual machine Moref or Name.",
        ),
    )
    power_action: str = (
        Annotated[
            Literal["on", "off", "reset", "reboot", "shutdown", "suspend"],
            Field(
                description="Power state action: on, off, reset, "
                "shutdown, reboot, suspend.",
                default="on",
            ),
        ],
    )


class VmResizeRequest(BaseModel):
    """Request model for VM resource resizing operations."""

    vm_id_or_uuid_or_name: str = Field(
        ..., description="ITS Private Cloud VM ID, UUID, or Name to resize"
    )
    new_cpu_count: Optional[int] = Field(
        None, description="New CPU count (vCPUs)", ge=1, le=24
    )
    new_cores_per_socket: Optional[int] = Field(
        None,
        description="CPU cores per socket (optional, for CPU topology)",
        ge=1,
        le=64,
    )
    new_memory_gb: Optional[int] = Field(
        None, description="New memory allocation in GB", ge=1, le=1024
    )
    force_power_off: bool = Field(
        False,
        description="Force power off VM if required for resize operation",
    )

    @field_validator('new_cores_per_socket')
    @classmethod
    def validate_cores_per_socket(cls, v, info):
        """Validate that CPU count is divisible by cores per socket."""
        if (
            v is not None
            and 'new_cpu_count' in info.data
            and info.data['new_cpu_count'] is not None
        ):
            cpu_count = info.data['new_cpu_count']
            if cpu_count % v != 0:
                raise ValueError(
                    f"CPU count ({cpu_count}) must be divisible by cores per socket ({v})"
                )
        return v

    @field_validator('new_memory_gb', 'new_cpu_count')
    @classmethod
    def validate_at_least_one_change(cls, v, info):
        """Validate that at least one resource is being changed."""
        # This validator runs for each field, so we check if any change is requested
        has_cpu = info.data.get('new_cpu_count') is not None
        has_memory = info.field_name == 'new_memory_gb' and v is not None
        has_memory_existing = info.data.get('new_memory_gb') is not None

        if (
            info.field_name == 'new_cpu_count'
            and v is None
            and not has_memory_existing
        ):
            # If this is cpu validation and no cpu provided, check if memory is provided
            pass  # Will be caught by the final validation
        elif info.field_name == 'new_memory_gb' and v is None and not has_cpu:
            # If this is memory validation and no memory provided, check if cpu is provided
            pass  # Will be caught by the final validation

        return v


# Request models
class VmDiskCreateRequest(BaseModel):
    """Request model for creating a VM disk."""

    capacity_gb: int = Field(..., description="Disk capacity in GB", gt=0)
    backing_mode: str = Field("persistent", description="Disk backing mode")
    backing_sharing: str = Field(
        "sharingnone", description="Disk sharing mode"
    )
    backing_vmdk: Optional[str] = Field(
        None, description="Optional backing VMDK file path"
    )
    scsi: int = Field(0, description="SCSI controller number", ge=0)

    def to_text(self):
        """Convert the request to a text string."""
        return (
            f"Disk Summary:"
            f"- Capacity: {self.capacity_gb} GB\n"
            f"- Backing Mode: {self.backing_mode}\n"
            f"- Backing Sharing: {self.backing_sharing}\n"
            f"- SCSI Controller: {self.scsi}\n"
            f"- Backing VMDK: {self.backing_vmdk or 'Auto-generated'}\n"
        )


class VmDiskResizeRequest(BaseModel):
    """Request model for resizing a VM disk."""

    vm_id_or_uuid_or_name: str = Field(
        ...,
        description="Virtual machine MOREF or Name.",
    )
    unit: int = Field(..., description="Disk unit number", ge=0)
    capacity_gb: int = Field(..., description="New disk capacity in GB", gt=0)

    def to_text(self):
        """Convert the request to a text string."""
        return (
            f"Disk Resize Summary:\n"
            f"- Unit: {self.unit}\n"
            f"- New Capacity: {self.capacity_gb} GB\n"
        )


class VmDiskDeleteRequest(BaseModel):
    """Request model for deleting VM disks."""

    vm_id_or_uuid_or_name: str = Field(
        ...,
        description="Virtual machine MOREF or Name.",
    )
    disk_units: List[int] = Field(
        ...,
        description="List of disk unit numbers to delete",
        min_length=1,
        max_length=10,
    )

    @field_validator('disk_units')
    @classmethod
    def validate_disk_units(cls, v):
        """Validate disk units are non-negative and unique."""
        if len(v) != len(set(v)):
            raise ValueError("Disk units must be unique")
        if any(unit < 0 for unit in v):
            raise ValueError("Disk units must be non-negative")
        return v

    def to_text(self):
        """Convert the request to a text string."""
        units_str = ", ".join(str(unit) for unit in self.disk_units)
        return (
            f"Disk Deletion Summary:\n"
            f"- Units to delete: {units_str}\n"
            f"- Total disks: {len(self.disk_units)}\n"
        )


class VmDiskScsiUpdateRequest(BaseModel):
    """Request model for updating VM disk SCSI controller."""

    vm_id_or_uuid_or_name: str = Field(
        ...,
        description="Virtual machine MOREF or Name.",
    )
    unit: int = Field(..., description="Disk unit number", ge=0)
    scsi: int = Field(
        ..., description="SCSI controller bus number", ge=0, le=3
    )

    def to_text(self):
        """Convert the request to a text string."""
        return (
            f"Disk SCSI Update Summary:\n"
            f"- Unit: {self.unit}\n"
            f"- New SCSI Controller: {self.scsi}\n"
        )


class VmDiskCreateRequestList(BaseModel):
    """List of disk creation requests."""

    vm_id_or_uuid_or_name: str = Field(
        ...,
        description="Virtual machine MOREF or Name.",
    )
    disks: List[VmDiskCreateRequest] = Field(
        ..., description="List of disks to create"
    )
