"""004 artifacts and artifact versions

Revision ID: 004
Revises: 003
Create Date: 2025-07-29
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB, UUID

revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── artifacts ────────────────────────────────────────────────────────────
    op.create_table(
        'artifacts',
        sa.Column('id', UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text('gen_random_uuid()')),
        sa.Column('project_id', UUID(as_uuid=True), nullable=False),
        sa.Column('module_key', sa.String(64), nullable=False),
        sa.Column('artifact_type', sa.String(64), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('content_json', JSONB, nullable=False, server_default='{}'),
        sa.Column('content_markdown', sa.Text, nullable=True),
        sa.Column('source', sa.String(32), nullable=False, server_default='ai'),
        sa.Column('current_version_id', UUID(as_uuid=True), nullable=True),
        sa.Column('workflow_run_id', UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False,
                  server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False,
                  server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('project_id', 'artifact_type', name='uq_artifacts_project_type'),
    )
    op.create_index('ix_artifacts_project_id', 'artifacts', ['project_id'])
    op.create_index('ix_artifacts_module_key', 'artifacts', ['module_key'])

    # ── artifact_versions ────────────────────────────────────────────────────
    op.create_table(
        'artifact_versions',
        sa.Column('id', UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text('gen_random_uuid()')),
        sa.Column('artifact_id', UUID(as_uuid=True), nullable=False),
        sa.Column('version_number', sa.Integer, nullable=False),
        sa.Column('content_json', JSONB, nullable=False, server_default='{}'),
        sa.Column('content_markdown', sa.Text, nullable=True),
        sa.Column('change_summary', sa.String(500), nullable=True),
        sa.Column('created_by', sa.String(32), nullable=False, server_default='ai'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False,
                  server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['artifact_id'], ['artifacts.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('artifact_id', 'version_number',
                            name='uq_artifact_versions_artifact_version'),
    )
    op.create_index('ix_artifact_versions_artifact_id', 'artifact_versions', ['artifact_id'])

    # Now add the FK from artifacts.current_version_id → artifact_versions.id
    op.create_foreign_key(
        'fk_artifacts_current_version',
        'artifacts', 'artifact_versions',
        ['current_version_id'], ['id'],
        ondelete='SET NULL',
    )


def downgrade() -> None:
    op.drop_constraint('fk_artifacts_current_version', 'artifacts', type_='foreignkey')
    op.drop_table('artifact_versions')
    op.drop_table('artifacts')
