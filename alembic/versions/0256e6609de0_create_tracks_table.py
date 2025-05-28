"""create tracks table

Revision ID: 0256e6609de0
Revises: ce3d5c8f08b7
Create Date: 2025-05-28 08:01:17.403387

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0256e6609de0'
down_revision: Union[str, None] = 'ce3d5c8f08b7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm;")
    op.execute("""
        CREATE TABLE tracks (
            id SERIAL PRIMARY KEY,
            query VARCHAR NOT NULL,
            video_id VARCHAR NOT NULL,
            title VARCHAR NOT NULL,
            performer VARCHAR NOT NULL,
            duration INTEGER NOT NULL,
            thumbnail_url VARCHAR,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

def downgrade() -> None:
    op.execute("DROP TABLE tracks;")
