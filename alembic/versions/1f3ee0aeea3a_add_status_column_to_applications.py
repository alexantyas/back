"""add status column to applications

Revision ID: 1f3ee0aeea3a
Revises: 7724c86854da
Create Date: 2025-05-18 17:42:17.783084
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "1f3ee0aeea3a"
down_revision = "7724c86854da"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1) Добавляем столбец status с server_default='pending'
    op.add_column(
        "applications",
        sa.Column(
            "status",
            sa.String(length=20),
            nullable=False,
            server_default="pending",
        ),
    )

    # 2) (опционально) Снимаем server_default,
    #    чтобы в дальнейшем SQLAlchemy/ORM сам ставил default
    op.alter_column(
        "applications",
        "status",
        server_default=None,
    )


def downgrade() -> None:
    # Откат: просто удаляем столбец
    op.drop_column("applications", "status")
