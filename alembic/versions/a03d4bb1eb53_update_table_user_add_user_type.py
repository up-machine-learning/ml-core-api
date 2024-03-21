"""update_table_user_add_user_type

Revision ID: a03d4bb1eb53
Revises: 1337432096ef
Create Date: 2024-03-03 14:15:24.499680

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'a03d4bb1eb53'
down_revision: Union[str, None] = '1337432096ef'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('type', sa.String(length=100), nullable=True, default='USER'))
    op.create_table(
        'media',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True, primary_key=True),
        sa.Column('entity_type', sa.String(length=20), nullable=False),
        sa.Column('entity_id', sa.Integer(), nullable=False),
        sa.Column('filename', sa.String(length=255), nullable=False)
    )


def downgrade() -> None:
    pass
