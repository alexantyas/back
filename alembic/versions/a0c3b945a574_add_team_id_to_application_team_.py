"""add team_id to application_team_participants

Revision ID: a0c3b945a574
Revises: d8341a105d28
Create Date: 2025-05-18 00:42:43.141017

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a0c3b945a574'
down_revision: Union[str, None] = 'd8341a105d28'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column(
        'applications',
        sa.Column('user_id', sa.Integer(), nullable=True)
    )
    op.create_foreign_key(
        'fk_applications_user_id_users',
        'applications', 'users',
        ['user_id'], ['id']
    )

def downgrade():
    op.drop_constraint('fk_applications_user_id_users', 'applications', type_='foreignkey')
    op.drop_column('applications', 'user_id')



