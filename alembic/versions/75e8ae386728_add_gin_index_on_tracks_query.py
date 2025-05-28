"""Add GIN index on tracks query

Revision ID: 75e8ae386728
Revises: fc2bfba2f9db
Create Date: 2025-05-28 11:18:42.214210

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '75e8ae386728'
down_revision: Union[str, None] = 'fc2bfba2f9db'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.execute("CREATE INDEX idx_tracks_query_trgm ON tracks USING gin (query gin_trgm_ops);")

def downgrade():
    op.execute("DROP INDEX IF EXISTS idx_tracks_query_trgm;")
