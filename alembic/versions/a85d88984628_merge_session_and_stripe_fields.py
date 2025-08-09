"""merge session and stripe fields

Revision ID: a85d88984628
Revises: add_stripe_fields_20250808, session_fields_001
Create Date: 2025-08-09 18:31:05.948058

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a85d88984628'
down_revision: Union[str, Sequence[str], None] = ('add_stripe_fields_20250808', 'session_fields_001')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
