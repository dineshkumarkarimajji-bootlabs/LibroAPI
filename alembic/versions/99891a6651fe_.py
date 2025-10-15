"""add role column with default and remove is_admin

Revision ID: 99891a6651fe
Revises: 81254352428e
Create Date: 2025-10-12 10:27:40.745888
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '99891a6651fe'
down_revision: Union[str, Sequence[str], None] = '81254352428e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Step 1: Add column with a temporary default (so existing rows get a value)
    op.add_column(
        'users',
        sa.Column(
            'role',
            sa.Enum('USER', 'ADMIN', name='roles'),
            nullable=False,
            server_default='USER'   # ✅ Default for existing rows
        )
    )

    # Step 2: Remove the old 'is_admin' column
    op.drop_column('users', 'is_admin')

    # Step 3 (optional cleanup): Remove server default constraint
    op.alter_column('users', 'role', server_default=None)


def downgrade() -> None:
    """Downgrade schema."""
    # Re-add is_admin column
    op.add_column(
        'users',
        sa.Column(
            'is_admin',
            sa.BOOLEAN(),
            server_default=sa.text('false'),
            autoincrement=False,
            nullable=False
        )
    )

    # Drop the role column
    op.drop_column('users', 'role')
