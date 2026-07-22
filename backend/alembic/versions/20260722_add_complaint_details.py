"""Add missing extracted complaint detail fields."""

from alembic import op
import sqlalchemy as sa


revision = "20260722_add_complaint_details"
down_revision = "20260722_add_commit_fields"
branch_labels = None
depends_on = None


def upgrade() -> None:
	"""Add fields captured during complaint intake."""
	op.add_column("complaints", sa.Column("customer_name", sa.String(length=255), nullable=True))
	op.add_column("complaints", sa.Column("affected_quantity", sa.String(length=100), nullable=True))
	op.add_column("complaints", sa.Column("manufacturing_date", sa.String(length=50), nullable=True))
	op.add_column("complaints", sa.Column("expiry_date", sa.String(length=50), nullable=True))
	op.add_column("complaints", sa.Column("product_type", sa.String(length=10), nullable=True))


def downgrade() -> None:
	"""Remove fields captured during complaint intake."""
	op.drop_column("complaints", "product_type")
	op.drop_column("complaints", "expiry_date")
	op.drop_column("complaints", "manufacturing_date")
	op.drop_column("complaints", "affected_quantity")
	op.drop_column("complaints", "customer_name")