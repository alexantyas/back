"""add judges and referees tables

Revision ID: add_judges_and_referees
Revises: fd5f5e18a062
Create Date: 2024-06-05 15:50:00

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_judges_and_referees'
down_revision = 'fd5f5e18a062'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'judges',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('name', sa.String, nullable=False),
        sa.Column('category', sa.String, nullable=True),
        sa.Column('tatami', sa.Integer, nullable=True),
        sa.Column('competition_id', sa.Integer, sa.ForeignKey('competitions.id', ondelete='CASCADE'), nullable=False),
    )
    op.create_table(
        'referees',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('name', sa.String, nullable=False),
        sa.Column('category', sa.String, nullable=True),
        sa.Column('competition_id', sa.Integer, sa.ForeignKey('competitions.id', ondelete='CASCADE'), nullable=False),
    )

def downgrade():
    op.drop_table('referees')
    op.drop_table('judges')

