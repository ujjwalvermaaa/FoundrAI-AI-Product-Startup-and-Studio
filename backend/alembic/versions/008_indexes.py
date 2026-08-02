"""008 performance indexes

Revision ID: 008
Revises: 007
Create Date: 2025-07-29
"""

from alembic import op

revision = '008'
down_revision = '007'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Projects — soft-delete and user lookup
    op.create_index('ix_projects_user_id_deleted', 'projects', ['user_id', 'deleted_at'])

    # Artifacts — type and project lookup
    op.create_index('ix_artifacts_project_artifact_type', 'artifacts',
                    ['project_id', 'artifact_type'])

    # Workflow runs — project + module + status (common query pattern)
    op.create_index('ix_workflow_runs_project_module', 'workflow_runs',
                    ['project_id', 'module_key'])
    op.create_index('ix_workflow_runs_project_status', 'workflow_runs',
                    ['project_id', 'status'])

    # Memory chunks — project + source_type (RAG retrieval)
    op.create_index('ix_memory_chunks_project_source', 'memory_chunks',
                    ['project_id', 'source_type'])

    # Refresh tokens — user + revoked + expires (validity check)
    op.create_index('ix_refresh_tokens_user_revoked', 'refresh_tokens',
                    ['user_id', 'revoked', 'expires_at'])

    # Audit logs — resource type + id (resource history lookup)
    op.create_index('ix_audit_logs_resource', 'audit_logs',
                    ['resource_type', 'resource_id'])


def downgrade() -> None:
    op.drop_index('ix_audit_logs_resource', 'audit_logs')
    op.drop_index('ix_refresh_tokens_user_revoked', 'refresh_tokens')
    op.drop_index('ix_memory_chunks_project_source', 'memory_chunks')
    op.drop_index('ix_workflow_runs_project_status', 'workflow_runs')
    op.drop_index('ix_workflow_runs_project_module', 'workflow_runs')
    op.drop_index('ix_artifacts_project_artifact_type', 'artifacts')
    op.drop_index('ix_projects_user_id_deleted', 'projects')
