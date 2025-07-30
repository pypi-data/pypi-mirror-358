"""Billing models."""
from datetime import date
from decimal import Decimal
from typing import Any, Dict, List, Literal, Optional

import mcp.types as types
from pydantic import BaseModel


class BillingClient(BaseModel):
    """Billing Client model."""

    billing_address: str
    billing_frequency: str
    billing_option: str
    created_on: str  # or use datetime if parsing to datetime
    id: int
    name: str
    needs_review: bool
    needs_review_contact: Optional[str]
    notes: str
    status: str
    updated_on: str  # or use datetime if parsing to datetime
    number_of_invoices: int
    number_of_debit_memos: int
    support_code: Optional[str]
    backup_client_id: Optional[str]

    def to_text(self) -> str:
        """Return a string representation of the model."""
        base = [
            f"Name: {self.name} (ID: {self.id})",
            f"Billing Address: {self.billing_address}",
            f"Billing Frequency: {self.billing_frequency}",
            f"Billing Option: {self.billing_option}",
            f"Created On: {self.created_on}",
            f"Updated On: {self.updated_on}",
            f"Number of Invoices: {self.number_of_invoices}",
            f"Number of Debit Memos: {self.number_of_debit_memos}",
        ]
        if self.support_code or self.backup_client_id:
            base.append("Additional Services:")
            if self.support_code:
                base.append(f"    Support Code: {self.support_code}")
            if self.backup_client_id:
                base.append(f"Backup Client ID: {self.backup_client_id}")
        base.append(f"Resource URI: Resource URI: its://client/{self.id}\n\n")
        return "\n".join(base)

    def to_prompt_result(self) -> types.GetPromptResult:
        """Return a prompt result."""
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
        """Return a tool result."""
        return [types.TextContent(type="text", text=self.to_text())]


class BillingClientsSummary(BaseModel):
    """Billing clients summary Model."""

    clients: Optional[List[BillingClient]] = []

    def to_text(self) -> str:
        """Convert billing clients summary to a readable text format."""
        if not self.clients:
            return "No billing clients found"
        return f"{'='*10}\n".join(
            [client.to_text() for client in self.clients]
        )

    def to_prompt_result(self) -> types.GetPromptResult:
        """Convert billing clients summary to a prompt result."""
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
        """Convert invoice summary to a tool result."""
        return [types.TextContent(type="text", text=self.to_text())]


class InvoiceSummary(BaseModel):
    """Invoice summary model."""

    balance: float
    date: str  # Could also use `date: date` if you want automatic date parsing
    id: int
    number: str
    subtotal: float
    type: Literal["DEBIT_MEMO", "INVOICE"]  # Assuming common invoice types

    def to_text(self) -> str:
        """Convert invoice summary to a readable text format."""
        return (
            f"Invoice Number: {self.number}\n"
            f"ID: {self.id}\n"
            f"Type: {self.type}\n"
            f"Date: {self.date}\n"
            f"Subtotal: ${self.subtotal:.2f}\n"
            f"Balance: ${self.balance:.2f}"
        )

    @classmethod
    def from_dict(cls, data: dict) -> 'InvoiceSummary':
        """Create InvoiceSummary instance from dictionary."""
        return cls.model_validate(data)

    def to_dict(self) -> dict:
        """Convert InvoiceSummary to dictionary."""
        return self.model_dump()

    def to_json(self) -> str:
        """Convert InvoiceSummary to JSON string."""
        return self.model_dump_json()

    def to_prompt_result(self) -> types.GetPromptResult:
        """Convert InvoiceSummary to PromptResult."""
        return types.GetPromptResult(
            description="Invoice: ",
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
        """Convert InvoiceSummary to ToolResult."""
        return [types.TextContent(type="text", text=self.to_text())]


class InvoicesSummary(BaseModel):
    """Invoice Summary model."""

    invoices: Optional[List[InvoiceSummary]] = []

    def to_text(self) -> str:
        """Convert invoice summary to a readable text format."""
        return '\n'.join(
            [
                f"Invoice Number: {x.number}\n"
                f"ID: {x.id}\n"
                f"Type: {x.type}\n"
                f"Date: {x.date}\n"
                f"Subtotal: ${x.subtotal:.2f}\n"
                f"Balance: ${x.balance:.2f}"
                for x in self.invoices
            ]
        )

    def to_prompt_result(self) -> types.GetPromptResult:
        """Convert invoice summary to a prompt result."""
        return types.GetPromptResult(
            description=f"Invoices: ({len(self.invoices)}) ",
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
        """Convert invoice summary to a tool result."""
        return [types.TextContent(type="text", text=self.to_text())]


class DiscountPercent(BaseModel):
    """Discount percent model."""

    cpu: int
    ip_address: int
    ip_address_nat: int
    memory: int
    storage: int
    storage_iscsi: int
    storage_ssd: int
    system_support: int


class Discount(BaseModel):
    """Discount model."""

    conditions: Dict[str, Any] = None
    expires_on: Optional[date] = None
    id: int
    name: Optional[str]
    notes: Optional[str]
    one_time: Optional[bool] = None
    percent: Optional[DiscountPercent] = None
    starts_on: Optional[date] = None
    used: Optional[bool]


class Item(BaseModel):
    """Billing item model."""

    active: bool
    id: int
    metric: str
    name: str
    price: Decimal


class InvoiceItem(BaseModel):
    """Invoice item model."""

    discount: Decimal
    discount_pct: int
    id: int
    invoice_id: int
    item: Item
    item_id: int
    quantity: Decimal
    subtotal: Decimal
    tax: Decimal
    tax_pct: Decimal
    total: Decimal


class BillingVmFolder(BaseModel):
    """Billing vm folder model."""

    moref: str
    name: str
    path: str
    recursive: bool


class BillingFolder(BaseModel):
    """Billing folder model."""

    name: str
    path: str


class BillingVmItem(BaseModel):
    """Billing vm item model."""

    backups: Optional[Any] = None
    backups_data_total: Decimal
    backups_support_total: Decimal
    cpu_count: int
    cpu_count_total: Decimal
    cpu_unit: Optional[Decimal] = None
    days: int
    dhcp_ip_addresses: Optional[Any] = None
    folder: BillingFolder
    gpu_gb: Optional[Decimal] = None
    gpu_gb_total: Decimal
    hostname: str
    ip_address: str
    ip_address_nat_total: Decimal
    ip_address_pub_total: Decimal
    is_template: bool
    mem_unit: Optional[Decimal] = None
    mem_reserved_unit: Optional[Decimal] = None
    memory_gb: Decimal
    memory_gb_reserved: Optional[Decimal] = 0
    memory_gb_reserved_total: Optional[Decimal] = 0
    memory_gb_total: Decimal
    moref: str
    name: str
    notes: List[Any]
    provisioned_gb: Decimal
    provisioned_gb_total: Decimal
    restore_hdd_total: Decimal
    restore_requests: Optional[Any] = None
    restore_ssd_total: Decimal
    stor_unit: Optional[Decimal] = None
    storage_type: Optional[Literal["ssd", "hdd"]] = None
    system_support: Optional[Any] = None
    system_support_total: Decimal
    total: Decimal
    uuid: str


class InvoiceDetails(BaseModel):
    """Invoice details model."""

    balance: Decimal
    billing_client_id: int
    billing_end_date: date
    billing_frequency: Literal["MONTHLY", "ANUAL"]
    billing_option: Literal["ARREARS", "ADVANCE"]
    billing_start_date: date
    conditions: Optional[List[Any]]
    date: date
    discount: Optional[Discount]
    file_path: str
    id: int
    items: List[InvoiceItem]
    notes: Optional[str]
    number: str
    subtotal: Decimal
    type: Literal["DEBIT_MEMO", "INVOICE"]
    vm_folders: List[BillingVmFolder]
    vm_items: List[BillingVmItem]

    class Config:
        """Pydantic config."""

        # Allow parsing string dates
        json_encoders = {
            date: lambda v: v.isoformat(),
            Decimal: lambda v: float(v),
        }

    def to_prompt_result(self) -> types.GetPromptResult:
        """Convert invoice summary to a prompt result."""
        return types.GetPromptResult(
            description=f"Invoice: {self.number}",
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
        """Convert invoice summary to a tool result."""
        return [types.TextContent(type="text", text=self.to_text())]

    def to_text(self) -> str:
        """Convert invoice summary to a readable text format."""
        lines = []

        # Header
        lines.append("=" * 60)
        lines.append(f"INVOICE: {self.number}")
        lines.append("=" * 60)

        # Basic Info
        lines.append(f"Invoice ID: {self.id}")
        lines.append(f"Type: {self.type}")
        lines.append(f"Date: {self.date}")
        lines.append(
            f"Billing Period: {self.billing_start_date} "
            f"to {self.billing_end_date}"
        )
        lines.append(f"Billing Client ID: {self.billing_client_id}")
        lines.append(f"Billing Frequency: {self.billing_frequency}")
        lines.append(f"Billing Option: {self.billing_option}")
        lines.append("")

        # Discount Information
        if self.discount:
            lines.append("DISCOUNT APPLIED:")
            lines.append(f"  Name: {self.discount.name}")
            lines.append(f"  CPU: {self.discount.percent.cpu}%")
            lines.append(f"  Memory: {self.discount.percent.memory}%")
            lines.append(
                f"  Storage SSD: {self.discount.percent.storage_ssd}%"
            )
            lines.append(f"  IP Address: {self.discount.percent.ip_address}%")
            lines.append("")

        # Financial Summary
        lines.append("FINANCIAL SUMMARY:")
        lines.append(f"  Subtotal: ${self.subtotal:.2f}")
        lines.append(f"  Total: ${self.balance:.2f}")
        lines.append("")

        # Line Items
        lines.append("LINE ITEMS:")
        lines.append("-" * 60)
        for item in self.items:
            if item.quantity > 0 or item.total > 0:
                lines.append(f"• {item.item.name}")
                lines.append(
                    f"  Quantity: {item.quantity:.4f} {item.item.metric}"
                )
                lines.append(f"  Unit Price: ${item.item.price:.2f}")
                lines.append(f"  Subtotal: ${item.subtotal:.2f}")
                if item.discount > 0:
                    lines.append(
                        f"  Discount ({item.discount_pct}%): "
                        f"-${item.discount:.2f}"
                    )
                lines.append(f"  Total: ${item.total:.2f}")
                lines.append("")

        # VM Details
        if self.vm_items:
            lines.append("VIRTUAL MACHINES:")
            lines.append("-" * 60)
            for vm in self.vm_items:
                lines.append(f"• {vm.name} ({vm.uuid})")
                lines.append(f"  Hostname: {vm.hostname}")
                lines.append(f"  IP Address: {vm.ip_address}")
                lines.append(
                    f"  Template: {'Yes' if vm.is_template else 'No'}"
                )
                lines.append(f"  Folder: {vm.folder.path}")
                lines.append(f"  CPU: {vm.cpu_count} vCPU(s)")
                lines.append(f"  Memory: {vm.memory_gb:.1f} GB")
                if vm.memory_gb_reserved > 0:
                    lines.append(
                        f"  Reserved Memory: "
                        f"{vm.memory_gb_reserved:.1f} GB"
                    )
                lines.append(
                    f"  Storage: {vm.provisioned_gb:.1f} "
                    f"GB ({vm.storage_type or 'N/A'})"
                )
                lines.append(f"  Days: {vm.days}")
                lines.append(f"  VM Total: ${vm.total:.2f}")
                lines.append("")

        # VM Folders
        if self.vm_folders:
            lines.append("VM FOLDERS:")
            lines.append("-" * 60)
            for folder in self.vm_folders:
                lines.append(f"• {folder.name}")
                lines.append(f"  Path: {folder.path}")
                lines.append(
                    f"  Recursive: {'Yes' if folder.recursive else 'No'}"
                )
                lines.append("")

        # Notes
        if self.notes:
            lines.append("NOTES:")
            lines.append("-" * 60)
            lines.append(self.notes)
            lines.append("")

        lines.append("=" * 60)

        return "\n".join(lines)


class MultipleInvoicesDetails(BaseModel):
    """Multiple invoices details model."""

    invoices: Optional[List[InvoiceDetails]] = []

    def to_text(self) -> str:
        """Convert to text."""
        return '\n'.join([x.to_text() for x in self.invoices])

    def to_prompt_result(self) -> types.GetPromptResult:
        """Convert to prompt result."""
        return types.GetPromptResult(
            description=f"Invoices: ({len(self.invoices)}) ",
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


class FisRecord(BaseModel):
    """FIS Record."""

    name: str
    id: int
    commitment_fund_centre: str
    cost_centre: str
    fund: Optional[str]
    commitment_item: Optional[str]
    assignment: Optional[str]
    budget_code: Optional[str]
    bus_area: Optional[str]
    general_ledger: Optional[str]
    invoice: Optional[bool] = False
    confirmed_on: Optional[str]
    notes: Optional[str]
    conditions: Optional[Dict[str, Any]]

    def to_text(self):
        """Convert to text."""
        if self.invoice:
            return f"{self.name} ({self.id})\n" f"Invoice: {self.invoice}\n\n"
        else:
            return (
                f"{self.name} ({self.id})\n"
                f"Cost centre: {self.cost_centre}\n"
                f"Commitment fund centre: {self.commitment_fund_centre}\n"
                f"Fund: {self.fund}\n"
                f"Commitment item: {self.commitment_item}\n"
                f"Assignment: {self.assignment}\n"
                f"Budget code: {self.budget_code}\n"
                f"Business area: {self.bus_area}\n"
                f"General ledger: {self.general_ledger}\n"
            )

    def to_prompt_result(self) -> types.GetPromptResult:
        """Convert to prompt result."""
        return types.GetPromptResult(
            description="FIS: ",
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
