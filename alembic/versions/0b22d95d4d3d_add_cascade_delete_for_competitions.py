"""add cascade delete for competitions

Revision ID: 0b22d95d4d3d
Revises: 877844802ea3
Create Date: 2025-05-22 16:37:30.118598

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0b22d95d4d3d'
down_revision: Union[str, None] = '877844802ea3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Applications
    op.drop_constraint('applications_competition_id_fkey', 'applications', type_='foreignkey')
    op.create_foreign_key(
        'applications_competition_id_fkey',
        'applications', 'competitions',
        ['competition_id'], ['id'],
        ondelete='CASCADE'
    )

    # Matches
    op.drop_constraint('matches_competition_id_fkey', 'matches', type_='foreignkey')
    op.create_foreign_key(
        'matches_competition_id_fkey',
        'matches', 'competitions',
        ['competition_id'], ['id'],
        ondelete='CASCADE'
    )


def downgrade() -> None:
    """Downgrade schema."""
    pass
