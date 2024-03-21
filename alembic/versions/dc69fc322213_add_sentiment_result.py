"""add_sentiment_result

Revision ID: dc69fc322213
Revises: 0619bde650d8
Create Date: 2024-03-16 22:11:37.233845

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'dc69fc322213'
down_revision: Union[str, None] = '0619bde650d8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('post_comment',
                  sa.Column('sentiment_score', sa.DECIMAL(precision=10, scale=2), nullable=False, server_default='0'))
    op.add_column('post_comment',
                  sa.Column('sentiment_result', sa.String(length=10), nullable=False, server_default='NEUTRAL'))


def downgrade() -> None:
    pass
