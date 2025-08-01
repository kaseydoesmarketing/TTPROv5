"""merge_heads

Revision ID: 3e7a8467480a
Revises: 4a2ebf0c26e2, billing_fields_001
Create Date: 2025-07-31 14:55:20.365574

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3e7a8467480a'
down_revision: Union[str, Sequence[str], None] = ('4a2ebf0c26e2', 'billing_fields_001')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
