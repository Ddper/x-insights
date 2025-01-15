"""add Chat model

Revision ID: 990cfd883ca4
Revises: c96bde2d8fdb
Create Date: 2025-01-14 11:18:19.242510

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '990cfd883ca4'
down_revision: Union[str, None] = 'c96bde2d8fdb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('chat',
    sa.Column('title', sa.VARCHAR(length=30), nullable=True),
    sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_table('chat_document',
    sa.Column('chat_id', sa.UUID(), nullable=True),
    sa.Column('document_id', sa.UUID(), nullable=True),
    sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['chat_id'], ['chat.id'], ),
    sa.ForeignKeyConstraint(['document_id'], ['document.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_index(op.f('ix_chat_document_chat_id'), 'chat_document', ['chat_id'], unique=False)
    op.create_index(op.f('ix_chat_document_document_id'), 'chat_document', ['document_id'], unique=False)
    op.create_unique_constraint(None, 'document', ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'document', type_='unique')
    op.drop_index(op.f('ix_chat_document_document_id'), table_name='chat_document')
    op.drop_index(op.f('ix_chat_document_chat_id'), table_name='chat_document')
    op.drop_table('chat_document')
    op.drop_table('chat')
    # ### end Alembic commands ###
