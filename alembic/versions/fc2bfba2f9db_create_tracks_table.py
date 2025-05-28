"""create tracks table

Revision ID: fc2bfba2f9db
Revises: 0256e6609de0
Create Date: 2025-05-28 08:19:02.946054

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fc2bfba2f9db'
down_revision: Union[str, None] = '0256e6609de0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
