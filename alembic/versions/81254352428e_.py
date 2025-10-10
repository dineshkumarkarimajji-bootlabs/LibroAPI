"""Updated migration with safe boolean conversion

Revision ID: 81254352428e
Revises: 
Create Date: 2025-10-10 12:50:05.820054
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '81254352428e'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Make audit_date NOT NULL
    op.alter_column(
        'audits',
        'audit_date',
        existing_type=postgresql.TIMESTAMP(timezone=True),
        nullable=False,
        existing_server_default=sa.text('now()')
    )

    # Safe conversion of INTEGER -> BOOLEAN for is_deleted columns
    op.execute("ALTER TABLE books ALTER COLUMN is_deleted TYPE BOOLEAN USING is_deleted::BOOLEAN;")
    op.execute("ALTER TABLE loans ALTER COLUMN is_deleted TYPE BOOLEAN USING is_deleted::BOOLEAN;")
    op.execute("ALTER TABLE users ALTER COLUMN is_deleted TYPE BOOLEAN USING is_deleted::BOOLEAN;")

    # Add is_admin column with default False
    op.add_column(
        'users',
        sa.Column('is_admin', sa.Boolean(), nullable=False, server_default=sa.false())
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Revert is_deleted columns to INTEGER safely
    op.execute("ALTER TABLE books ALTER COLUMN is_deleted TYPE INTEGER USING is_deleted::INTEGER;")
    op.execute("ALTER TABLE loans ALTER COLUMN is_deleted TYPE INTEGER USING is_deleted::INTEGER;")
    op.execute("ALTER TABLE users ALTER COLUMN is_deleted TYPE INTEGER USING is_deleted::INTEGER;")

    # Drop is_admin column
    op.drop_column('users', 'is_admin')

    # Make audit_date nullable again
    op.alter_column(
        'audits',
        'audit_date',
        existing_type=postgresql.TIMESTAMP(timezone=True),
        nullable=True,
        existing_server_default=sa.text('now()')
    )
