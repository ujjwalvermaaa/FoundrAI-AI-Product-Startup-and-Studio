"""
AuditRepository — write audit log entries to the database.
"""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog


class AuditRepository:
    """Repository for creating audit log records."""

    async def create(
        self,
        session: AsyncSession,
        event_type: str,
        user_id: uuid.UUID | None = None,
        resource_type: str | None = None,
        resource_id: uuid.UUID | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> AuditLog:
        """
        Persist a single audit log entry.

        Args:
            session:       AsyncSession for DB writes.
            event_type:    e.g. "project.create", "workflow.trigger", "export"
            user_id:       UUID of the acting user (nullable).
            resource_type: e.g. "project", "workflow_run", "export"
            resource_id:   UUID of the resource affected.
            ip_address:    Client IP address (optional).
            user_agent:    Client user-agent string (optional).
            metadata:      Additional context as a JSON-serializable dict.

        Returns:
            The persisted AuditLog row.
        """
        entry = AuditLog(
            user_id=user_id,
            event_type=event_type,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=ip_address,
            user_agent=user_agent,
            metadata_json=metadata,
        )
        session.add(entry)
        await session.flush()
        return entry
