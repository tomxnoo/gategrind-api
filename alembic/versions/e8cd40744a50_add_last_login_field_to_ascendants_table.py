"""Add last_login field to ascendants table

Revision ID: e8cd40744a50
Revises: f635a66fc269
Create Date: 2025-07-24 01:13:53.346802

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e8cd40744a50'
down_revision: Union[str, Sequence[str], None] = 'f635a66fc269'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add last_login field to ascendants table
    op.add_column('ascendants', sa.Column('last_login', sa.DateTime(timezone=True), nullable=True))
    
    # Add index for last_login field for better query performance
    op.create_index('idx_ascendant_last_login', 'ascendants', ['last_login'])


def downgrade() -> None:
    """Downgrade schema."""
    # Remove index first
    op.drop_index('idx_ascendant_last_login', table_name='ascendants')
    
    # Remove last_login column
    op.drop_column('ascendants', 'last_login')
