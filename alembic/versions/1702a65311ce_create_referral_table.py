"""create referral table

Revision ID: 1702a65311ce
Revises: a45325769a9f
Create Date: 2024-04-21 12:02:11.244801

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1702a65311ce'
down_revision: Union[str, None] = 'a45325769a9f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
  op.execute("""
    CREATE TABLE "referral" (
      "id" SERIAL PRIMARY KEY,
      "code" VARCHAR(255) NOT NULL,
      "click_count" BIGINT DEFAULT 0,
      "created_at" TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
  """)


def downgrade() -> None:
  op.execute("DROP TABLE referral")