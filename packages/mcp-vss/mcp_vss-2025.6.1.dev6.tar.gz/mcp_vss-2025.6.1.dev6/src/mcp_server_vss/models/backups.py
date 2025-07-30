"""Backups models."""
from typing import List, Optional

import mcp.types as types
from pydantic import BaseModel


class BackupHostSummary(BaseModel):
    """Backup Host Summary."""

    annual_support: float
    price_per_gb: float
    host: str
    id: int
    ip_address: Optional[str]
    vm_id: Optional[str]
    vm_name: Optional[str]

    def to_text(self) -> str:
        """Convert to text."""
        return (
            f"UTORrecover Host:\n"
            f"Host: {self.host} ({self.id})\n"
            f"IP Address: {self.ip_address}\n"
            f"VM: {self.vm_name or 'N/A'} ({self.vm_id or 'N/A'})\n"
            f"Annual Fees: ${self.price_per_gb} per GB\n"
            f"             ${self.annual_support} per support\n"
            f"Resource URI: its://backup/host/{self.host}\n\n"
        )

    def to_tool_result(
        self,
    ) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
        """Convert to tool result."""
        return [types.TextContent(type="text", text=self.to_text())]

    def to_prompt_result(self) -> types.GetPromptResult:
        """Convert to prompt result."""
        return types.GetPromptResult(
            description=f"UTORrecover Host: {self.full_name}"
            f" ({self.guest_id})",
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text", text=self.to_text()
                    ),
                )
            ],
        )


class BackupHostSummaryList(BaseModel):
    """List of backup host summaries."""

    items: Optional[List[BackupHostSummary]] = []

    def to_text(self) -> str:
        """Convert to text."""
        return f"{'='*20}\n".join([x.to_text() for x in self.items])

    def to_prompt_result(self) -> types.GetPromptResult:
        """Convert to prompt result."""
        return types.GetPromptResult(
            description=f"UTORrecover Hosts: ({len(self.items)})",
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


class BackupHostSession(BaseModel):
    """Backup host session."""

    session_count: int = 0
    timestamp: str
    total_size_gb: float

    def to_text(self) -> str:
        """Convert to text."""
        return (
            f"Sessions: {self.session_count}\n"
            f"Timestamp: {self.timestamp}\n"
            f"Total Size: {self.total_size_gb} GB\n\n"
        )

    def to_prompt_result(self) -> types.GetPromptResult:
        """Convert to prompt result."""
        return types.GetPromptResult(
            description="Backup Host Session: ",
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


class BackupHostSessionList(BaseModel):
    """Backup Host Session List."""

    items: Optional[List[BackupHostSession]] = []

    def to_text(self) -> str:
        """Convert to text."""
        return f"{'='*20}\n".join([x.to_text() for x in self.items])

    def to_prompt_result(self) -> types.GetPromptResult:
        """Convert to prompt result."""
        return types.GetPromptResult(
            description=f"Backup Sessions: ({len(self.items)})",
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
