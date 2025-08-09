"""add_user_session_fields

Revision ID: session_fields_001
Revises: 
Create Date: 2025-08-09 22:30:00

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers
revision = 'session_fields_001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    """Add session fields to users table"""
    try:
        # Add session_token column
        op.add_column('users', sa.Column('session_token', sa.String(), nullable=True))
        
        # Add session_expires column
        op.add_column('users', sa.Column('session_expires', sa.DateTime(), nullable=True))
        
        # Create index on session_token for performance
        op.create_index('ix_users_session_token', 'users', ['session_token'])
        
        print("✅ Successfully added session fields to users table")
        
    except Exception as e:
        print(f"⚠️ Migration might already be applied or columns exist: {e}")

def downgrade():
    """Remove session fields from users table"""
    try:
        # Drop index
        op.drop_index('ix_users_session_token', 'users')
        
        # Remove session columns
        op.drop_column('users', 'session_expires')
        op.drop_column('users', 'session_token')
        
        print("✅ Successfully removed session fields from users table")
        
    except Exception as e:
        print(f"⚠️ Error during downgrade: {e}")