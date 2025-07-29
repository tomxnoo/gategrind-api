"""Create system_settings table

Revision ID: create_system_settings
Revises: fix_dungeon_columns
Create Date: 2025-01-28 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'create_system_settings'
down_revision = 'fix_dungeon_columns'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create system_settings table
    op.create_table('system_settings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('setting_key', sa.String(length=255), nullable=False),
        sa.Column('setting_value', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('setting_key')
    )
    
    # Create index for faster lookups
    op.create_index('idx_system_settings_key', 'system_settings', ['setting_key'])


def downgrade() -> None:
    # Drop index
    op.drop_index('idx_system_settings_key', table_name='system_settings')
    
    # Drop table
    op.drop_table('system_settings')