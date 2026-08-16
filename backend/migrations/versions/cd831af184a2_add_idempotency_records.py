"""add idempotency records"""
from alembic import op
import sqlalchemy as sa

revision = "cd831af184a2"
down_revision = "75da5967ea0c"
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        "tbl_idempotency_records",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("scope", sa.String(length=255), nullable=False),
        sa.Column("idempotency_key", sa.String(length=255), nullable=False),
        sa.Column("request_hash", sa.String(length=64), nullable=False),
        sa.Column("status_code", sa.Integer(), nullable=False),
        sa.Column("response_body", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("scope", "idempotency_key", name="uq_idempotency_scope_key"),
    )

def downgrade():
    op.drop_table("tbl_idempotency_records")
