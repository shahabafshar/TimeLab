"""rename metadata column to meta_data

Revision ID: 001_rename_metadata
Revises: 
Create Date: 2025-01-17

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001_rename_metadata'
down_revision = '000_initial'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Rename metadata column to meta_data (metadata is reserved by SQLAlchemy)
    # Check if the old column exists before attempting rename
    # For SQLite, we need to handle this more carefully
    from sqlalchemy import inspect
    from alembic import context
    
    bind = context.get_bind()
    inspector = inspect(bind)
    columns = [col['name'] for col in inspector.get_columns('datasets')]
    
    if 'metadata' in columns and 'meta_data' not in columns:
        # SQLite doesn't support ALTER COLUMN RENAME directly
        # We need to use a workaround: create new table, copy data, drop old, rename
        if bind.dialect.name == 'sqlite':
            # For SQLite, use batch operations
            with op.batch_alter_table('datasets', schema=None) as batch_op:
                batch_op.alter_column('metadata', new_column_name='meta_data')
        else:
            op.alter_column('datasets', 'metadata', new_column_name='meta_data')


def downgrade() -> None:
    # Rename back to metadata
    from sqlalchemy import inspect
    from alembic import context
    
    bind = context.get_bind()
    inspector = inspect(bind)
    columns = [col['name'] for col in inspector.get_columns('datasets')]
    
    if 'meta_data' in columns and 'metadata' not in columns:
        if bind.dialect.name == 'sqlite':
            with op.batch_alter_table('datasets', schema=None) as batch_op:
                batch_op.alter_column('meta_data', new_column_name='metadata')
        else:
            op.alter_column('datasets', 'meta_data', new_column_name='metadata')

