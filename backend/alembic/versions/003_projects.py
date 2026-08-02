"""003 projects and project modules

Revision ID: 003
Revises: 002
Create Date: 2025-07-29

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── projects ──────────────────────────────────────────────────────────
    op.create_table(
        'projects',
        sa.Column('id', UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('tagline', sa.String(500), nullable=True),
        sa.Column('idea_brief', sa.Text(), nullable=False),
        sa.Column('industry', sa.String(100), nullable=True),
        sa.Column('stage', sa.String(50), nullable=False, server_default='draft'),
        sa.Column('deleted_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False,
                  server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False,
                  server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_projects_user_id', 'projects', ['user_id'])
    op.create_index('ix_projects_deleted_at', 'projects', ['deleted_at'])

    # ── project_modules ───────────────────────────────────────────────────
    op.create_table(
        'project_modules',
        sa.Column('id', UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text('gen_random_uuid()')),
        sa.Column('project_id', UUID(as_uuid=True), nullable=False),
        sa.Column('module_key', sa.String(64), nullable=False),
        sa.Column('display_name', sa.String(128), nullable=False),
        sa.Column('status', sa.String(32), nullable=False, server_default='locked'),
        sa.Column('sort_order', sa.SmallInteger(), nullable=False),
        sa.Column('last_run_id', UUID(as_uuid=True), nullable=True),
        sa.Column('completed_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False,
                  server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False,
                  server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('project_id', 'module_key', name='uq_project_modules_project_key'),
    )
    op.create_index('ix_project_modules_project_id', 'project_modules', ['project_id'])


def downgrade() -> None:
    op.drop_table('project_modules')
    op.drop_table('projects')
