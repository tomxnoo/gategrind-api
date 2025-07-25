"""add_node_id_to_skill_tree_nodes

Revision ID: 1731f4e90808
Revises: a8295dbe4f85
Create Date: 2025-07-25 02:36:09.405656

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1731f4e90808'
down_revision: Union[str, Sequence[str], None] = 'a8295dbe4f85'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add node_id column to skill_tree_nodes table
    op.add_column('skill_tree_nodes', sa.Column('node_id', sa.String(length=50), nullable=True))
    
    # Create unique index on node_id
    op.create_index(op.f('ix_skill_tree_nodes_node_id'), 'skill_tree_nodes', ['node_id'], unique=True)


def downgrade() -> None:
    """Downgrade schema."""
    # Drop index and column
    op.drop_index(op.f('ix_skill_tree_nodes_node_id'), table_name='skill_tree_nodes')
    op.drop_column('skill_tree_nodes', 'node_id')
