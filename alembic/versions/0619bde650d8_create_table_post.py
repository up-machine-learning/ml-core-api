"""create_table_post

Revision ID: 0619bde650d8
Revises: a03d4bb1eb53
Create Date: 2024-03-09 14:14:35.882704

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0619bde650d8'
down_revision: Union[str, None] = 'a03d4bb1eb53'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'post',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True, primary_key=True),
        sa.Column('description', sa.String(length=255), nullable=False),
        sa.Column('created_user_id', sa.Integer(), nullable=False),
        sa.Column('created_date', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['created_user_id'], ['users.id'])
    )

    op.create_table(
        'post_like',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True, primary_key=True),
        sa.Column('post_id', sa.Integer(), nullable=False),
        sa.Column('like_type', sa.String(length=20), nullable=False),
        sa.Column('created_user_id', sa.Integer(), nullable=False),
        sa.Column('created_date', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['created_user_id'], ['users.id']),
        sa.ForeignKeyConstraint(['post_id'], ['post.id']),
        sa.UniqueConstraint('post_id', 'created_user_id', name='uq_post_like_post_id_created_user_id')
    )

    op.create_table(
        'post_comment',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True, primary_key=True),
        sa.Column('post_id', sa.Integer(), nullable=False),
        sa.Column('comment', sa.String(length=255), nullable=False),
        sa.Column('created_user_id', sa.Integer(), nullable=False),
        sa.Column('created_date', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['created_user_id'], ['users.id']),
        sa.ForeignKeyConstraint(['post_id'], ['post.id'])
    )


def downgrade() -> None:
    pass
