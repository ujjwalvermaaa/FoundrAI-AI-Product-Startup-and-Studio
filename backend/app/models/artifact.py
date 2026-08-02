"""
Artifact SQLAlchemy ORM model.
Mirrors the `artifacts` table from migration 004.
One artifact per (project_id, artifact_type) — UNIQUE constraint enforces this.
"""

import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import TIMESTAMP, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from app.database.base import Base

if TYPE_CHECKING:
    from app.models.artifact_version import ArtifactVersion
    from app.models.project import Project


class Artifact(Base):
    __tablename__ = "artifacts"
    __table_args__ = (
        UniqueConstraint("project_id", "artifact_type", name="uq_artifacts_project_type"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    module_key: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    artifact_type: Mapped[str] = mapped_column(String(64), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content_json: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    content_markdown: Mapped[str | None] = mapped_column(Text, nullable=True)
    source: Mapped[str] = mapped_column(
        String(32), nullable=False, server_default="ai", default="ai"
    )
    current_version_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("artifact_versions.id", ondelete="SET NULL"),
        nullable=True,
        default=None,
    )
    workflow_run_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
        default=None,
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # ── Relationships ──────────────────────────────────────────────────────
    versions: Mapped[list["ArtifactVersion"]] = relationship(
        "ArtifactVersion",
        primaryjoin="Artifact.id == ArtifactVersion.artifact_id",
        back_populates="artifact",
        cascade="all, delete-orphan",
        order_by="ArtifactVersion.version_number",
        foreign_keys="ArtifactVersion.artifact_id",
    )
    current_version: Mapped["ArtifactVersion | None"] = relationship(
        "ArtifactVersion",
        primaryjoin="Artifact.current_version_id == ArtifactVersion.id",
        foreign_keys=[current_version_id],
        lazy="select",
    )

    def __repr__(self) -> str:
        return f"<Artifact type={self.artifact_type} project={self.project_id}>"
