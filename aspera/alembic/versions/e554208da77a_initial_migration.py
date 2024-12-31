"""Initial migration

Revision ID: e554208da77a
Revises: 
Create Date: 2024-12-26 11:50:56.928855

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'e554208da77a'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('document',
    sa.Column('hash_id', sa.VARCHAR(length=32), nullable=False),
    sa.Column('url', sa.String(), nullable=False),
    sa.Column('metadata_map', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('url')
    )
    op.create_index(op.f('ix_document_hash_id'), 'document', ['hash_id'], unique=True)
    op.create_index(op.f('ix_document_id'), 'document', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_document_id'), table_name='document')
    op.drop_index(op.f('ix_document_hash_id'), table_name='document')
    op.drop_table('document')
    # ### end Alembic commands ###
