"""change History.created_at to server default

Revision ID: d089dae9595c
Revises: 7a366b246038
Create Date: 2026-10-18 14:15:38.778129

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'd089dae9595c'
down_revision: str | Sequence[str] | None = '7a366b246038'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column(
        'history', 'created_at', existing_type=sa.DateTime(), server_default=sa.func.now()
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column('history', 'created_at', existing_type=sa.DateTime(), server_default=None)
    # ### end Alembic commands ###
