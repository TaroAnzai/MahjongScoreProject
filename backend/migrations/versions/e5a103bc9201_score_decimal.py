"""Preserve integer scores and support five decimal places.

Downgrade is deliberately blocked: decimal or out-of-INT-range scores cannot
be safely converted while concurrent writes may occur. Restore an integer
schema only through a separately reviewed, write-paused migration.
"""
import sqlalchemy as sa
from alembic import op

revision = "e5a103bc9201"
down_revision = "cd831af184a2"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("tbl_scores") as batch_op:
        batch_op.alter_column(
            "score", existing_type=sa.Integer(), type_=sa.Numeric(15, 5),
            existing_nullable=False,
        )


def downgrade():
    raise RuntimeError("Automatic score downgrade is blocked to prevent data loss")
