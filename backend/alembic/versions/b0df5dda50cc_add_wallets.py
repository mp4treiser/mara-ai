"""Add wallets

Revision ID: b0df5dda50cc
Revises: 8bc1e50004b5
Create Date: 2025-08-16 14:08:49.091768

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = 'b0df5dda50cc'
down_revision: Union[str, Sequence[str], None] = '8bc1e50004b5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    connection = op.get_bind()

    result = connection.execute(sa.text("""
        SELECT column_name FROM information_schema.columns 
        WHERE table_name = 'wallet_deposits' AND column_name = 'update_at'
    """))
    if not result.fetchone():
        op.add_column('wallet_deposits', sa.Column('update_at', sa.DateTime(), server_default=sa.text("TIMEZONE('utc', now())"), nullable=False))

    result = connection.execute(sa.text("""
        SELECT column_name FROM information_schema.columns 
        WHERE table_name = 'wallets' AND column_name = 'update_at'
    """))
    if not result.fetchone():
        op.add_column('wallets', sa.Column('update_at', sa.DateTime(), server_default=sa.text("TIMEZONE('utc', now())"), nullable=False))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('wallets', 'update_at')
    op.drop_column('wallet_deposits', 'update_at')
