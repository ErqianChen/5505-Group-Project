"""Initial migration

Revision ID: initial_migration
Revises: 
Create Date: 2024-01-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'initial_migration'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Create all tables
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(80), unique=True, nullable=False),
        sa.Column('email', sa.String(120), unique=True, nullable=False),
        sa.Column('password_hash', sa.String(128), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table('sports_categories',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(80), unique=True, nullable=False),
        sa.Column('met_value', sa.Float()),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Add more table creation statements based on your models
    # ... other tables ...

def downgrade():
    # Drop all tables in reverse order
    op.drop_table('sports_categories')
    op.drop_table('users')
    # ... drop other tables ...