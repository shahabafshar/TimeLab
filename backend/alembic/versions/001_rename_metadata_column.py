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
    try:
        op.alter_column('datasets', 'metadata', new_column_name='meta_data')
    except Exception:
        # Column might not exist yet (new database) or already renamed
        pass


def downgrade() -> None:
    # Rename back to metadata
    try:
        op.alter_column('datasets', 'meta_data', new_column_name='metadata')
    except Exception:
        pass

