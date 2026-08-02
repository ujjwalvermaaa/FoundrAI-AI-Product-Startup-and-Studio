"""005 workflow runs, steps, and agent executions

Revision ID: 005
Revises: 004
Create Date: 2025-07-29
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB, UUID

revision = '005'
down_revision = '004'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── workflow_runs ────────────────────────────────────────────────────────
    op.create_table(
        'workflow_runs',
        sa.Column('id', UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text('gen_random_uuid()')),
        sa.Column('project_id', UUID(as_uuid=True), nullable=False),
        sa.Column('module_key', sa.String(64), nullable=False),
        sa.Column('status', sa.String(32), nullable=False, server_default='pending'),
        sa.Column('triggered_by', UUID(as_uuid=True), nullable=True),
        sa.Column('input_snapshot', JSONB, nullable=False, server_default='{}'),
        sa.Column('error_code', sa.String(64), nullable=True),
        sa.Column('error_message', sa.Text, nullable=True),
        sa.Column('started_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('completed_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False,
                  server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['triggered_by'], ['users.id'], ondelete='SET NULL'),
    )
    op.create_index('ix_workflow_runs_project_id', 'workflow_runs', ['project_id'])
    op.create_index('ix_workflow_runs_status', 'workflow_runs', ['status'])

    # Now add last_run_id FK on project_modules → workflow_runs
    op.create_foreign_key(
        'fk_project_modules_last_run',
        'project_modules', 'workflow_runs',
        ['last_run_id'], ['id'],
        ondelete='SET NULL',
    )

    # Also add workflow_run_id FK on artifacts → workflow_runs
    op.create_foreign_key(
        'fk_artifacts_workflow_run',
        'artifacts', 'workflow_runs',
        ['workflow_run_id'], ['id'],
        ondelete='SET NULL',
    )

    # ── workflow_steps ────────────────────────────────────────────────────────
    op.create_table(
        'workflow_steps',
        sa.Column('id', UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text('gen_random_uuid()')),
        sa.Column('workflow_run_id', UUID(as_uuid=True), nullable=False),
        sa.Column('step_key', sa.String(64), nullable=False),
        sa.Column('status', sa.String(32), nullable=False),
        sa.Column('sequence', sa.SmallInteger, nullable=False),
        sa.Column('started_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('completed_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('metadata_json', JSONB, nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False,
                  server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['workflow_run_id'], ['workflow_runs.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_workflow_steps_run_id', 'workflow_steps', ['workflow_run_id'])

    # ── agent_executions ──────────────────────────────────────────────────────
    op.create_table(
        'agent_executions',
        sa.Column('id', UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text('gen_random_uuid()')),
        sa.Column('workflow_run_id', UUID(as_uuid=True), nullable=False),
        sa.Column('workflow_step_id', UUID(as_uuid=True), nullable=True),
        sa.Column('agent_id', sa.String(64), nullable=False),
        sa.Column('model_name', sa.String(128), nullable=False),
        sa.Column('status', sa.String(32), nullable=False),
        sa.Column('prompt_tokens', sa.Integer, nullable=True),
        sa.Column('completion_tokens', sa.Integer, nullable=True),
        sa.Column('latency_ms', sa.Integer, nullable=True),
        sa.Column('raw_output', sa.Text, nullable=True),
        sa.Column('parsed_output_json', JSONB, nullable=True),
        sa.Column('error_message', sa.Text, nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False,
                  server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['workflow_run_id'], ['workflow_runs.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['workflow_step_id'], ['workflow_steps.id'], ondelete='SET NULL'),
    )
    op.create_index('ix_agent_executions_run_id', 'agent_executions', ['workflow_run_id'])


def downgrade() -> None:
    op.drop_constraint('fk_artifacts_workflow_run', 'artifacts', type_='foreignkey')
    op.drop_constraint('fk_project_modules_last_run', 'project_modules', type_='foreignkey')
    op.drop_table('agent_executions')
    op.drop_table('workflow_steps')
    op.drop_table('workflow_runs')
