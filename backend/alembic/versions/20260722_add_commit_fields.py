"""Add QMS commit and CAPA fields to complaints."""

from alembic import op
import sqlalchemy as sa


revision = "20260722_add_commit_fields"
down_revision = "00000000_create_initial_tables"
branch_labels = None
depends_on = None


def upgrade() -> None:
	"""Add fields needed to finalize a complaint."""
	op.add_column("complaints", sa.Column("capa_priority", sa.String(length=50), nullable=True))
	op.add_column("complaints", sa.Column("corrective_action", sa.Text(), nullable=True))
	op.add_column("complaints", sa.Column("preventive_action", sa.Text(), nullable=True))
	op.add_column("complaints", sa.Column("committed_at", sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
	"""Remove QMS commit and CAPA fields."""
	op.drop_column("complaints", "committed_at")
	op.drop_column("complaints", "preventive_action")
	op.drop_column("complaints", "corrective_action")
	op.drop_column("complaints", "capa_priority")
