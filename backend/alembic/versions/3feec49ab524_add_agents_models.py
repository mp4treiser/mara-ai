"""Add agents models

Revision ID: 3feec49ab524
Revises: b0df5dda50cc
Create Date: 2025-08-17 18:08:04.818380

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3feec49ab524'
down_revision: Union[str, Sequence[str], None] = 'b0df5dda50cc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
