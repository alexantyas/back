"""add user_id to applications

Revision ID: 7724c86854da
Revises: e98d866058a8
Create Date: 2025-05-18 15:47:24.662794

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7724c86854da'
down_revision: Union[str, None] = 'e98d866058a8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
