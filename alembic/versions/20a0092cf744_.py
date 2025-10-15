"""Add hashed_password column with default hashing

Revision ID: 20a0092cf744
Revises: 99891a6651fe
Create Date: 2025-10-12 16:29:38.096350
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm import Session
from passlib.context import CryptContext

# revision identifiers, used by Alembic.
revision: str = '20a0092cf744'
down_revision: Union[str, Sequence[str], None] = '99891a6651fe'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def upgrade() -> None:
    """Upgrade schema."""
    # Step 1: Add column with temporary default to avoid NOT NULL violation
    op.add_column('users', sa.Column('hashed_password', sa.String(), nullable=False, server_default='TEMP_PASSWORD'))

    # Step 2: Update existing rows with hashed temporary password
    bind = op.get_bind()
    session = Session(bind=bind)
    hashed_temp = pwd_context.hash("changeme123")  # temporary hashed password
    session.execute(
        sa.text("UPDATE users SET hashed_password = :hashed_temp"),
        {"hashed_temp": hashed_temp}
    )
    session.commit()

    # Step 3: Remove the server default so future inserts must provide a real password
    op.alter_column('users', 'hashed_password', server_default=None)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('users', 'hashed_password')
