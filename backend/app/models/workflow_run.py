"""
WorkflowRun SQLAlchemy ORM model.
Mirrors the `workflow_runs` table from migration 005.
Status transitions: pending → running → completed | failed | cancelled
"""

import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import TIMESTAMP, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from app.core.constants import WORKFLOW_STATUS_PENDING
from app.database.base import Base

if TYPE_CHECKING:
    from app.models.workflow_step import WorkflowStep
    from app.models.agent_execution import AgentExecution


class WorkflowRun(Base):
    __tablename__ = "workflow_runs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    module_key: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(
        String(32), nullable=False,
        server_default=WORKFLOW_STATUS_PENDING,
        default=WORKFLOW_STATUS_PENDING,
    )
    triggered_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    input_snapshot: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    error_code: Mapped[str | None] = mapped_column(String(64), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
        default=lambda: datetime.now(timezone.utc),
    )

    # ── Relationships ──────────────────────────────────────────────────────
    steps: Mapped[list["WorkflowStep"]] = relationship(
        "WorkflowStep",
        back_populates="workflow_run",
        cascade="all, delete-orphan",
        order_by="WorkflowStep.sequence",
    )
    agent_executions: Mapped[list["AgentExecution"]] = relationship(
        "AgentExecution",
        back_populates="workflow_run",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<WorkflowRun id={self.id} module={self.module_key} status={self.status}>"
