"""006 memory chunks and knowledge documents

Revision ID: 006
Revises: 005
Create Date: 2025-07-29
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB, UUID

revision = '006'
down_revision = '005'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── knowledge_documents ───────────────────────────────────────────────────
    op.create_table(
        'knowledge_documents',
        sa.Column('id', UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text('gen_random_uuid()')),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('category', sa.String(64), nullable=True),
        sa.Column('file_path', sa.String(512), nullable=True),
        sa.Column('content_hash', sa.String(64), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False,
                  server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False,
                  server_default=sa.text('NOW()')),
    )

    # ── memory_chunks ─────────────────────────────────────────────────────────
    op.create_table(
        'memory_chunks',
        sa.Column('id', UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text('gen_random_uuid()')),
        sa.Column('project_id', UUID(as_uuid=True), nullable=True),
        sa.Column('source_type', sa.String(32), nullable=False),
        sa.Column('source_id', UUID(as_uuid=True), nullable=True),
        sa.Column('knowledge_document_id', UUID(as_uuid=True), nullable=True),
        sa.Column('module_key', sa.String(64), nullable=True),
        sa.Column('chunk_index', sa.Integer, nullable=False),
        sa.Column('content_text', sa.Text, nullable=False),
        sa.Column('content_hash', sa.String(64), nullable=False),
        sa.Column('embedding_model', sa.String(128), nullable=False),
        sa.Column('faiss_vector_id', sa.BigInteger, nullable=False),
        sa.Column('metadata_json', JSONB, nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False,
                  server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False,
                  server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(
            ['knowledge_document_id'], ['knowledge_documents.id'], ondelete='CASCADE'
        ),
    )
    op.create_index('ix_memory_chunks_project_id', 'memory_chunks', ['project_id'])
    op.create_index('ix_memory_chunks_source_type', 'memory_chunks', ['source_type'])
    op.create_index('ix_memory_chunks_faiss_vector_id', 'memory_chunks', ['faiss_vector_id'])


def downgrade() -> None:
    op.drop_table('memory_chunks')
    op.drop_table('knowledge_documents')
