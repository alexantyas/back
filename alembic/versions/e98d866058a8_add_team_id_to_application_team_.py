"""add team_id to application_team_participants

Revision ID: e98d866058a8
Revises: a0c3b945a574
Create Date: 2025-05-18 00:44:48.936680

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e98d866058a8'
down_revision: Union[str, None] = 'a0c3b945a574'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
